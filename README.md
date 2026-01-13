# EU Public Consultations Scraper (2025)

A web scraper that extracts data from all closed EU public consultations from 2025 on the Better Regulation portal.

## Features

This scraper navigates through the three-level structure of the EU consultation system:
1. Search results page (82 consultations)
2. Individual initiative overview pages
3. Public consultation detail pages

## Extracted Data

For each consultation, the scraper extracts:

- **Initiative ID**: Numeric identifier from the URL
- **Initiative Name**: Title of the consultation
- **Initiative URL**: Link to the overview page
- **Consultation URL**: Link to the public consultation page
- **Topic**: Subject area (e.g., Taxation, Competition, Food safety)
- **Consultation Period**: Date range when consultation was open
- **Total Feedback**: Number of valid feedback instances received
- **Summary Report**: Whether a summary report is available and its download URL
- **Contributions ZIP**: Whether contributions are available as a ZIP file and its download URL
- **Documents Annexed**: Whether additional documents are available and their download URL

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install Playwright browsers:
```bash
playwright install chromium
```

## Usage

### Step 1: Scrape Consultation Metadata

Run the scraper:
```bash
python scraper.py
```

The scraper will:
- Navigate through all 82 consultations from the search results
- Extract data from each consultation page
- Save results to both CSV and JSON formats with timestamps

### Step 2: Analyze Data Availability Patterns

Analyze the results to understand data sharing patterns:
```bash
python analyze_results.py eu_consultations_2025_YYYYMMDD_HHMMSS.json
```

This will show:
- Data availability statistics (full data vs summary only vs nothing)
- Patterns by response volume (do high-response consultations get less data sharing?)
- Patterns by topic (which topics share data more openly?)
- Patterns by timing (does data availability change over time?)

### Output Files

- `eu_consultations_2025_YYYYMMDD_HHMMSS.csv` - CSV format with all consultation data
- `eu_consultations_2025_YYYYMMDD_HHMMSS.json` - JSON format with all consultation data

Each record includes URLs for downloading contribution files and summary reports where available.

## Configuration

You can modify the scraper behavior by adjusting the initialization parameters:

```python
scraper = EUConsultationScraper(
    headless=True,   # Set to False to see the browser
    slow_mo=500      # Milliseconds delay between actions
)
```

## Technical Details

- **Browser Automation**: Uses Playwright for handling JavaScript-rendered pages
- **Async Processing**: Asynchronous operation for efficient scraping
- **Error Handling**: Comprehensive error handling with logging
- **Respectful Scraping**: Includes delays between requests
- **Status Tracking**: Each record includes scrape status and error messages

## Data Structure

Each consultation record contains:

```python
@dataclass
class ConsultationData:
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
```

## Troubleshooting

- **Timeout errors**: The scraper includes generous timeouts (60s for page loads), but if you experience issues, you can increase them in the code
- **Missing data**: Some consultations may not have all fields available - these are marked as `None` or `False`
- **Network issues**: The scraper will log errors and continue with remaining consultations

## Notes

- The scraper is designed specifically for the 2025 consultation period
- It handles pagination automatically if there are multiple pages of results
- All data is saved with timestamps for tracking
- The scraper respects the website with appropriate delays between requests
