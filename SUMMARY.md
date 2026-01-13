# EU Public Consultations Data Availability Scraper - Summary

## What This Does

This scraper collects metadata from all 82 closed EU public consultations from 2025 to analyze **data availability patterns** - specifically, understanding when and why the EU Commission shares full consultation data versus just summary reports.

## Key Features

### 1. Data Collection (scraper.py)
- Navigates through 3-level page structure (search → initiative → consultation)
- Extracts for each consultation:
  - Name, ID, topic, dates
  - Total number of responses received
  - **Whether full contribution data (ZIP) is available**
  - **Whether only a summary report is available**
  - **Whether nothing is shared**
  - Download URLs for all available files

### 2. Pattern Analysis (analyze_results.py)
Answers your key questions:

**"How often does the EU share full data vs summary only vs nothing?"**
- Categorizes all 82 consultations
- Shows percentages for each category

**"Are consultations with more responses less likely to share data?"**
- Groups consultations by response volume (low/medium/high)
- Shows data sharing rates for each volume category
- Tests hypothesis: high-response consultations → less data sharing

**"Do certain topics share data more openly?"**
- Breaks down data sharing by topic (Taxation, Competition, etc.)
- Identifies which policy areas are more transparent

**"Does timing matter?"**
- Analyzes data sharing by consultation start month
- Shows if older consultations are more likely to have published data

## Test Results

Successfully tested on three consultations:

1. **EU antitrust (27 responses)**: ✓ Full data available (contributions ZIP + documents)
2. **VAT tourism (244 responses)**: ✓ Summary report only
3. **Border Guard (19 responses)**: ✓ No data shared

All fields extracted correctly:
- Initiative name and ID
- Topic (e.g., "Competition", "Taxation", "Home affairs")
- Consultation period
- Total feedback count
- Data availability flags
- Download URLs (captured via network interception)

## Technical Approach

- **Playwright** for JavaScript-rendered pages
- **Network request interception** to capture download URLs (they're generated dynamically by Angular, not in HTML)
- **Async/await** for efficient scraping
- **Respectful delays** between requests

## Usage

```bash
# 1. Scrape all consultations (~10-15 minutes)
python scraper.py

# 2. Analyze patterns
python analyze_results.py eu_consultations_2025_*.json
```

## Output

CSV and JSON files with complete data, plus analysis showing:
- Overall data sharing statistics
- Correlation between response volume and data sharing
- Topic-based patterns
- Temporal patterns

This helps answer: **When does the EU Commission actually share the raw consultation data, and when do they only provide summaries or nothing at all?**
