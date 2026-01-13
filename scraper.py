"""
EU Public Consultations Scraper for 2025
Scrapes consultation data from the EU Better Regulation portal
"""

import asyncio
import csv
import json
import re
from datetime import datetime
from typing import Dict, List, Optional
from playwright.async_api import async_playwright, Page, Browser
from dataclasses import dataclass, asdict
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ConsultationData:
    """Data structure for consultation information"""
    initiative_id: str
    initiative_name: str
    initiative_url: str
    consultation_url: str
    topic: Optional[str]
    consultation_period: Optional[str]
    total_feedback: Optional[int]
    has_summary_report: bool
    summary_report_url: Optional[str]
    has_contributions_zip: bool
    contributions_zip_url: Optional[str]
    has_documents_annexed: bool
    documents_annexed_url: Optional[str]
    scrape_timestamp: str
    scrape_status: str
    error_message: Optional[str]


class EUConsultationScraper:
    """Scraper for EU public consultations"""

    BASE_URL = "https://ec.europa.eu/info/law/better-regulation/have-your-say"
    SEARCH_URL = (
        "https://ec.europa.eu/info/law/better-regulation/have-your-say/"
        "initiatives_en?frontEndStage=OPC_LAUNCHED&feedbackStatus=CLOSED"
        "&feedbackOpenDateFrom=01-01-2025&feedbackOpenDateClosedBy=31-12-2025"
    )

    def __init__(self, headless: bool = True, slow_mo: int = 500):
        self.headless = headless
        self.slow_mo = slow_mo
        self.results: List[ConsultationData] = []

    async def wait_for_page_load(self, page: Page, timeout: int = 30000):
        """Wait for page to be fully loaded"""
        try:
            await page.wait_for_load_state("networkidle", timeout=timeout)
        except Exception as e:
            logger.warning(f"Network idle timeout: {e}")
            await page.wait_for_load_state("domcontentloaded")

    async def scrape_all_consultations(self) -> List[ConsultationData]:
        """Main method to scrape all consultations"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless, slow_mo=self.slow_mo)
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = await context.new_page()

            try:
                # Get all initiative URLs from search results
                initiative_urls = await self.get_initiative_urls(page)
                logger.info(f"Found {len(initiative_urls)} initiatives")

                # Process each initiative
                for idx, initiative_url in enumerate(initiative_urls, 1):
                    logger.info(f"Processing {idx}/{len(initiative_urls)}: {initiative_url}")
                    consultation_data = await self.scrape_consultation(page, initiative_url)
                    self.results.append(consultation_data)

                    # Small delay to be respectful
                    await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"Error in main scraping process: {e}")
            finally:
                await browser.close()

        return self.results

    async def get_initiative_urls(self, page: Page) -> List[str]:
        """Extract all initiative URLs from the search results page"""
        initiative_urls = []

        try:
            logger.info(f"Loading search results page: {self.SEARCH_URL}")
            await page.goto(self.SEARCH_URL, wait_until="domcontentloaded", timeout=60000)
            await self.wait_for_page_load(page)

            # Wait for results to load
            await page.wait_for_selector('.ecl-card', timeout=30000)

            # Handle pagination if needed
            page_num = 1
            while True:
                logger.info(f"Extracting URLs from page {page_num}")

                # Extract links from current page
                # The cards contain links to initiative pages
                cards = await page.query_selector_all('.ecl-card')
                logger.info(f"Found {len(cards)} cards on page {page_num}")

                for card in cards:
                    link_element = await card.query_selector('a[href*="/initiatives/"]')
                    if link_element:
                        href = await link_element.get_attribute('href')
                        if href:
                            # Convert relative to absolute URL
                            if href.startswith('/'):
                                full_url = f"https://ec.europa.eu{href}"
                            else:
                                full_url = href

                            # Remove the _en suffix and any query params for consistency
                            full_url = full_url.split('?')[0]
                            if full_url not in initiative_urls:
                                initiative_urls.append(full_url)

                # Check if there's a next page button
                next_button = await page.query_selector('button[aria-label*="next" i], a[aria-label*="next" i], .ecl-pagination__link--next')

                if next_button:
                    is_disabled = await next_button.get_attribute('disabled')
                    if is_disabled:
                        break

                    try:
                        await next_button.click()
                        await self.wait_for_page_load(page)
                        page_num += 1
                        await asyncio.sleep(2)
                    except Exception as e:
                        logger.info(f"No more pages or error clicking next: {e}")
                        break
                else:
                    break

        except Exception as e:
            logger.error(f"Error getting initiative URLs: {e}")

        return initiative_urls

    async def scrape_consultation(self, page: Page, initiative_url: str) -> ConsultationData:
        """Scrape a single consultation"""

        # Initialize with defaults
        data = ConsultationData(
            initiative_id="",
            initiative_name="",
            initiative_url=initiative_url,
            consultation_url="",
            topic=None,
            consultation_period=None,
            total_feedback=None,
            has_summary_report=False,
            summary_report_url=None,
            has_contributions_zip=False,
            contributions_zip_url=None,
            has_documents_annexed=False,
            documents_annexed_url=None,
            scrape_timestamp=datetime.now().isoformat(),
            scrape_status="pending",
            error_message=None
        )

        try:
            # Extract initiative ID from URL
            id_match = re.search(r'/initiatives/(\d+)', initiative_url)
            if id_match:
                data.initiative_id = id_match.group(1)

            # Step 1: Go to initiative overview page
            logger.info(f"Loading initiative page: {initiative_url}")
            await page.goto(initiative_url, wait_until="domcontentloaded", timeout=60000)
            await self.wait_for_page_load(page)

            # Get initiative name from the page
            try:
                name_element = await page.query_selector('h1, .ecl-page-header__title')
                if name_element:
                    data.initiative_name = (await name_element.inner_text()).strip()
            except Exception as e:
                logger.warning(f"Could not extract initiative name: {e}")

            # Step 2: Construct public consultation URL directly
            consultation_link = None
            try:
                # Direct construction is most reliable
                base = initiative_url.rstrip('/')
                if base.endswith('_en'):
                    base = base[:-3]
                consultation_link = f"{base}/public-consultation_en"

            except Exception as e:
                logger.warning(f"Error constructing consultation link: {e}")

            if not consultation_link:
                data.scrape_status = "error"
                data.error_message = "Could not find public consultation link"
                return data

            data.consultation_url = consultation_link

            # Step 3: Go to public consultation page
            logger.info(f"Loading consultation page: {consultation_link}")
            await page.goto(consultation_link, wait_until="domcontentloaded", timeout=60000)
            await self.wait_for_page_load(page)

            # Extract data from consultation page
            await self.extract_consultation_data(page, data)

            data.scrape_status = "success"

        except Exception as e:
            logger.error(f"Error scraping consultation {initiative_url}: {e}")
            data.scrape_status = "error"
            data.error_message = str(e)

        return data

    async def extract_consultation_data(self, page: Page, data: ConsultationData):
        """Extract all required data from the consultation page"""

        # Extract Topic
        try:
            topic_elements = await page.query_selector_all('dt.ecl-description-list__term')
            for dt in topic_elements:
                text = await dt.inner_text()
                if 'topic' in text.lower():
                    dd_handle = await dt.evaluate_handle('node => node.nextElementSibling')
                    dd_element = dd_handle.as_element()
                    if dd_element:
                        topic_text = await dd_element.inner_text()
                        if topic_text:
                            data.topic = topic_text.strip()
                        break
        except Exception as e:
            logger.warning(f"Error extracting topic: {e}")

        # Extract Consultation Period
        try:
            period_element = await page.query_selector('span.ecl-u-type-capitalize')
            if period_element:
                data.consultation_period = (await period_element.inner_text()).strip()
        except Exception as e:
            logger.warning(f"Error extracting consultation period: {e}")

        # Extract Total Feedback
        try:
            # Look through all h4 elements for the feedback count
            h4_elements = await page.query_selector_all('h4')
            for h4 in h4_elements:
                feedback_text = await h4.inner_text()
                if 'feedback' in feedback_text.lower() and 'received' in feedback_text.lower():
                    # Extract number from text like "Total of valid feedback instances received: 244"
                    match = re.search(r':\s*(\d+)', feedback_text)
                    if match:
                        data.total_feedback = int(match.group(1))
                    break
        except Exception as e:
            logger.warning(f"Error extracting total feedback: {e}")

        # Extract Consultation Outcome section data
        try:
            # Get all h3 headings to understand the page structure
            h3_elements = await page.query_selector_all('h3')
            h3_texts = []
            for h3 in h3_elements:
                text = await h3.inner_text()
                h3_texts.append(text.strip())

            has_summary_section = "Summary report" in h3_texts
            has_contributions_section = "Contributions to the consultation" in h3_texts

            # Get all files on the page
            file_elements = await page.query_selector_all('ecl-file')

            # Storage for captured download URLs
            captured_urls = {}

            # Set up request interceptor to capture download URLs
            def handle_request(request):
                if '/api/download/' in request.url:
                    captured_urls[request.url] = request.url

            page.on("request", handle_request)

            for idx, file_elem in enumerate(file_elements):
                title_elem = await file_elem.query_selector('.ecl-file__title')
                if title_elem:
                    title = (await title_elem.inner_text()).strip()
                    title_lower = title.lower()

                    # Get download link and click it to trigger the URL
                    download_link = await file_elem.query_selector('a')
                    if download_link:
                        try:
                            # Click to trigger the download request (but don't actually download)
                            await download_link.click(timeout=3000)
                            await asyncio.sleep(0.5)  # Give time for request to be captured

                            # Find the URL that was just captured
                            if captured_urls:
                                latest_url = list(captured_urls.values())[-1]

                                # Determine file type based on context and title
                                if has_contributions_section and 'contribution' in title_lower and 'annex' not in title_lower:
                                    # This is the main contributions ZIP
                                    data.has_contributions_zip = True
                                    data.contributions_zip_url = latest_url

                                elif has_contributions_section and 'document' in title_lower and 'annex' in title_lower:
                                    # This is documents annexed
                                    data.has_documents_annexed = True
                                    data.documents_annexed_url = latest_url

                                elif has_summary_section:
                                    # This is a summary report
                                    data.has_summary_report = True
                                    data.summary_report_url = latest_url

                        except Exception as click_error:
                            logger.warning(f"Error clicking download link for '{title}': {click_error}")

            # Remove the event listener
            page.remove_listener("request", handle_request)

        except Exception as e:
            logger.warning(f"Error extracting consultation outcome data: {e}")

    def save_results(self, output_format: str = 'both'):
        """Save results to CSV and/or JSON"""

        if not self.results:
            logger.warning("No results to save")
            return

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Save as CSV
        if output_format in ['csv', 'both']:
            csv_filename = f'eu_consultations_2025_{timestamp}.csv'
            with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=asdict(self.results[0]).keys())
                writer.writeheader()
                for result in self.results:
                    writer.writerow(asdict(result))
            logger.info(f"Results saved to {csv_filename}")

        # Save as JSON
        if output_format in ['json', 'both']:
            json_filename = f'eu_consultations_2025_{timestamp}.json'
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump([asdict(r) for r in self.results], f, indent=2, ensure_ascii=False)
            logger.info(f"Results saved to {json_filename}")


async def main():
    """Main execution function"""
    scraper = EUConsultationScraper(headless=True, slow_mo=500)

    logger.info("Starting EU Consultations Scraper for 2025")
    results = await scraper.scrape_all_consultations()

    logger.info(f"Scraping completed. Total consultations processed: {len(results)}")

    # Print summary
    success_count = sum(1 for r in results if r.scrape_status == 'success')
    error_count = sum(1 for r in results if r.scrape_status == 'error')

    logger.info(f"Successful: {success_count}, Errors: {error_count}")

    # Save results
    scraper.save_results(output_format='both')

    return results


if __name__ == "__main__":
    asyncio.run(main())
