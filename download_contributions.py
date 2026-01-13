"""
Download contribution ZIP files from scraped consultation data
"""

import json
import csv
import os
import asyncio
import aiohttp
from pathlib import Path
import logging
from typing import List, Dict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ContributionDownloader:
    """Download contribution files from scraped data"""

    def __init__(self, output_dir: str = "contributions"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    async def download_file(self, session: aiohttp.ClientSession, url: str, filename: str) -> bool:
        """Download a single file"""
        filepath = self.output_dir / filename

        if filepath.exists():
            logger.info(f"File already exists: {filename}")
            return True

        try:
            logger.info(f"Downloading: {filename}")
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=300)) as response:
                if response.status == 200:
                    content = await response.read()
                    with open(filepath, 'wb') as f:
                        f.write(content)
                    logger.info(f"Successfully downloaded: {filename} ({len(content)} bytes)")
                    return True
                else:
                    logger.error(f"Failed to download {filename}: HTTP {response.status}")
                    return False
        except Exception as e:
            logger.error(f"Error downloading {filename}: {e}")
            return False

    async def download_from_json(self, json_file: str):
        """Download contributions from JSON results file"""

        with open(json_file, 'r') as f:
            data = json.load(f)

        await self._download_from_data(data)

    async def download_from_csv(self, csv_file: str):
        """Download contributions from CSV results file"""

        data = []
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)

        await self._download_from_data(data)

    async def _download_from_data(self, data: List[Dict]):
        """Download contributions from parsed data"""

        # Collect all download tasks
        download_tasks = []

        async with aiohttp.ClientSession() as session:
            for idx, record in enumerate(data, 1):
                initiative_id = record.get('initiative_id', f'unknown_{idx}')
                initiative_name = record.get('initiative_name', 'Unknown')

                # Clean filename
                safe_name = "".join(c for c in initiative_name if c.isalnum() or c in (' ', '-', '_')).strip()
                safe_name = safe_name[:50]  # Limit length

                # Download contributions ZIP
                contributions_url = record.get('contributions_zip_url')
                has_contributions = record.get('has_contributions_zip')

                # Handle boolean from CSV (string 'True'/'False')
                if isinstance(has_contributions, str):
                    has_contributions = has_contributions.lower() == 'true'

                if has_contributions and contributions_url and contributions_url.lower() != 'none':
                    filename = f"{initiative_id}_{safe_name}_contributions.zip"
                    task = self.download_file(session, contributions_url, filename)
                    download_tasks.append(task)

                    # Add small delay between requests
                    await asyncio.sleep(0.5)

                # Download documents annexed
                documents_url = record.get('documents_annexed_url')
                has_documents = record.get('has_documents_annexed')

                if isinstance(has_documents, str):
                    has_documents = has_documents.lower() == 'true'

                if has_documents and documents_url and documents_url.lower() != 'none':
                    filename = f"{initiative_id}_{safe_name}_documents.zip"
                    task = self.download_file(session, documents_url, filename)
                    download_tasks.append(task)

                    await asyncio.sleep(0.5)

                # Download summary reports
                summary_url = record.get('summary_report_url')
                has_summary = record.get('has_summary_report')

                if isinstance(has_summary, str):
                    has_summary = has_summary.lower() == 'true'

                if has_summary and summary_url and summary_url.lower() != 'none':
                    # Determine file extension from URL or default to PDF
                    ext = 'pdf'
                    if '.' in summary_url:
                        ext = summary_url.rsplit('.', 1)[-1].split('?')[0][:10]

                    filename = f"{initiative_id}_{safe_name}_summary.{ext}"
                    task = self.download_file(session, summary_url, filename)
                    download_tasks.append(task)

                    await asyncio.sleep(0.5)

            # Execute all downloads
            if download_tasks:
                logger.info(f"Starting download of {len(download_tasks)} files")
                results = await asyncio.gather(*download_tasks, return_exceptions=True)

                success_count = sum(1 for r in results if r is True)
                logger.info(f"Downloads completed: {success_count}/{len(download_tasks)} successful")
            else:
                logger.warning("No files to download")


async def main():
    """Main execution"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python download_contributions.py <json_or_csv_file>")
        print("\nExample:")
        print("  python download_contributions.py eu_consultations_2025_20240113_123456.json")
        sys.exit(1)

    input_file = sys.argv[1]

    if not os.path.exists(input_file):
        print(f"Error: File not found: {input_file}")
        sys.exit(1)

    downloader = ContributionDownloader(output_dir="contributions")

    logger.info(f"Reading data from: {input_file}")

    if input_file.endswith('.json'):
        await downloader.download_from_json(input_file)
    elif input_file.endswith('.csv'):
        await downloader.download_from_csv(input_file)
    else:
        print("Error: File must be .json or .csv")
        sys.exit(1)

    logger.info(f"All downloads completed. Files saved to: {downloader.output_dir}")


if __name__ == "__main__":
    asyncio.run(main())
