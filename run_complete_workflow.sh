#!/bin/bash

# Complete workflow script for EU consultations scraper
# This script runs all steps: scraping, analysis, and downloading

set -e  # Exit on error

echo "=========================================="
echo "EU Public Consultations Scraper Workflow"
echo "=========================================="
echo ""

# Check if dependencies are installed
echo "Checking dependencies..."
if ! python3 -c "import playwright" 2>/dev/null; then
    echo "Error: Playwright not installed"
    echo "Run: pip install -r requirements.txt && playwright install chromium"
    exit 1
fi

# Step 1: Run the scraper
echo ""
echo "Step 1: Scraping consultation data..."
echo "This will take 10-15 minutes..."
python3 scraper.py

if [ $? -ne 0 ]; then
    echo "Error: Scraping failed"
    exit 1
fi

# Find the most recent output file
LATEST_JSON=$(ls -t eu_consultations_2025_*.json 2>/dev/null | head -1)

if [ -z "$LATEST_JSON" ]; then
    echo "Error: No output file found"
    exit 1
fi

echo "Scraping completed: $LATEST_JSON"

# Step 2: Analyze results
echo ""
echo "Step 2: Analyzing results..."
python3 analyze_results.py "$LATEST_JSON"

# Step 3: Ask if user wants to download files
echo ""
read -p "Do you want to download all contribution files? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Step 3: Downloading contribution files..."
    python3 download_contributions.py "$LATEST_JSON"

    if [ $? -eq 0 ]; then
        echo ""
        echo "All downloads completed!"
        echo "Files saved to: contributions/"
    fi
fi

echo ""
echo "=========================================="
echo "Workflow completed successfully!"
echo "=========================================="
echo ""
echo "Your data files:"
echo "  - $LATEST_JSON"
echo "  - ${LATEST_JSON%.json}.csv"
echo ""
echo "To analyze again: python3 analyze_results.py $LATEST_JSON"
echo "To download files: python3 download_contributions.py $LATEST_JSON"
echo ""
