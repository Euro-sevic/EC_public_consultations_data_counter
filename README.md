# EU Public Consultations Data (2016-2026)

[**📊 View Interactive Analysis & Visualization**](https://euro-sevic.github.io/EC_public_consultations_data_counter/)

This repository contains datasets of public consultations from the European Commission, scraped from the official [Have Your Say](https://ec.europa.eu/info/law/better-regulation/have-your-say) portal.

## Datasets

The following datasets are available in this repository:

- **`eu_consultations_2016_2026_20260113_152839.csv`**: A CSV file containing the structured data of consultations.
- **`eu_consultations_2016_2026_20260113_152839.json`**: A JSON file containing the same data in JSON format.

### How to Download

You can download the files directly by clicking on them in the file list above and selecting "Download raw file", or by cloning this repository:

```bash
git clone https://github.com/Euro-sevic/EC_public_consultations_data_counter.git
```

## Methodology

### Scraping Process

The data was collected using the Python scripts included in this repository (`scraper_2016_2026.py`, `scraper.py`, `download_contributions.py`).

1.  **Source**: The scraper targets the European Commission's "Have Your Say" search pages.
2.  **Parameters**: It filters for consultations within the period from 2016 to 2026.
3.  **Extraction**: The scripts iterate through the pagination of search results, extracting key metadata for each consultation, including titles, dates, reference numbers, and status.
4.  **Output**: The collected raw data is processed and saved into CSV and JSON formats for ease of use.