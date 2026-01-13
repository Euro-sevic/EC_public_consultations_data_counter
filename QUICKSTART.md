# Quick Start Guide

## Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
playwright install chromium
```

## Testing

2. **Test with a single consultation (recommended first step):**
```bash
python test_single.py
```

This will:
- Open a visible browser window
- Scrape one consultation (VAT package for travel and tourism)
- Show you exactly what data is being extracted
- Help you verify everything works before running the full scraper

## Running the Full Scraper

3. **Scrape all 82 consultations:**
```bash
python scraper.py
```

This will:
- Run in headless mode (no visible browser)
- Process all 82 consultations from 2025
- Save results to both CSV and JSON files
- Take approximately 10-15 minutes to complete

## Output

You'll get two files with timestamps:
- `eu_consultations_2025_YYYYMMDD_HHMMSS.csv`
- `eu_consultations_2025_YYYYMMDD_HHMMSS.json`

## What Data is Collected

For each consultation:
- ✓ Initiative name and ID
- ✓ URLs (initiative and consultation pages)
- ✓ Topic category
- ✓ Consultation period dates
- ✓ Total number of feedback responses
- ✓ Summary report availability and download URL
- ✓ Contributions ZIP file availability and download URL
- ✓ Documents annexed availability and download URL

## Troubleshooting

**If you get timeout errors:**
- Check your internet connection
- The scraper will continue with remaining consultations

**If some fields are empty:**
- This is normal - not all consultations have summary reports or contribution files
- Empty fields will show as `None` (JSON) or empty cells (CSV)

**To see what's happening:**
- Change `headless=True` to `headless=False` in scraper.py line 344
- This will show the browser window

## Next Steps

After running the scraper:

**4. Analyze the results:**
```bash
python analyze_results.py eu_consultations_2025_YYYYMMDD_HHMMSS.json
```

This will show you:
- Total number of consultations processed
- Topics breakdown
- Feedback statistics
- Data availability summary
- Top consultations by response count

**5. Download contribution files:**
```bash
python download_contributions.py eu_consultations_2025_YYYYMMDD_HHMMSS.json
```

This will:
- Download all available contribution ZIP files
- Download summary reports
- Download annexed documents
- Save everything to a `contributions/` folder

**6. Extract and analyze:**
- Unzip the contribution files
- Each ZIP typically contains CSV files with all responses
- Analyze the individual consultation responses
