# Temporal Analysis (2016-2026)

## Overview

This extended analysis covers **675 closed public consultations** from April 2016 to January 2026, testing the hypothesis that the EU Commission became less transparent over time despite the Better Regulation initiative.

## The Hypothesis

The **Better Law-Making** initiative came into force in April 2016, committing the EU Commission to share consultation data publicly. However, since it's non-binding, we want to test whether the Commission gradually gave up on this commitment.

## Running the Extended Scraper

**⚠️ Warning**: This will take **1-2 hours** to scrape 675 consultations.

```bash
python3 scraper_2016_2026.py
```

Features:
- Scrapes all 675 consultations from 2016-2026
- Saves intermediate results every 50 consultations (in case it crashes)
- Extracts consultation start/end dates for temporal analysis
- Parses consultation year for trend analysis

## Running the Temporal Analysis

After scraping completes:

```bash
python3 analyze_temporal.py eu_consultations_2016_2026_*.json
```

## What the Analysis Shows

### 1. Consultation Duration Analysis
- **Average duration** in weeks
- **Distribution**: How many are short (< 8 weeks), standard (8-11 weeks), or long (12+ weeks)
- **Trends over time**: Has consultation duration changed?

### 2. Data Sharing Trends Over Time
**Year-by-year breakdown** showing:
- Total consultations
- % with full data (contributions ZIP)
- % with summary only
- % with no data shared

### 3. Hypothesis Test: Early vs Recent Years

Compares **2016-2018** (early years) vs **2023-2025** (recent years):
- Did data sharing improve or decline?
- By how many percentage points?
- Does this support or contradict the hypothesis?

### 4. Additional Insights
- **Duration vs Data Sharing**: Do longer consultations share more/less data?
- **Topic trends over time**: Which topics became more/less transparent?

## Expected Findings

If your hypothesis is correct, we should see:
- ✓ Higher data sharing rates in 2016-2018
- ✓ Lower data sharing rates in 2023-2025
- ✓ A declining trend line

If the hypothesis is wrong:
- ✗ Data sharing improved or stayed constant
- ✗ No clear temporal pattern

## Output Example

```
TREND ANALYSIS: Early years (2016-2018) vs Recent years (2023-2025)
================================================================================

Early years (2016-2018):
  Full data sharing: 45/120 (37.5%)

Recent years (2023-2025):
  Full data sharing: 18/150 (12.0%)

→ CHANGE:
  ⚠️  DECREASE of 25.5 percentage points
  This supports the hypothesis that data sharing has DECLINED over time.
```

## Files Generated

- `eu_consultations_2016_2026_YYYYMMDD_HHMMSS.csv` - Full dataset
- `eu_consultations_2016_2026_YYYYMMDD_HHMMSS.json` - Full dataset (JSON)
- `eu_consultations_2016_2026_partial_50_*.json` - Intermediate saves
- `eu_consultations_2016_2026_partial_100_*.json`
- etc.

## Note on the 2025-only Scraper

The original `scraper.py` still works for just 2025 data (81 consultations, ~10 minutes). Use that for quick tests.
