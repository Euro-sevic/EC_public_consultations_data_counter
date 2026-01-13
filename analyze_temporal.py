"""
Temporal analysis of EU consultation data (2016-2026)
Includes analysis of consultation duration and data sharing trends over time
"""

import json
import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path
from datetime import datetime
import re


def parse_date(date_str):
    """Parse date string like '24 July 2025' to datetime"""
    if not date_str:
        return None

    try:
        # Handle different date formats
        # "24 July 2025", "24 July 2025  (midnight Brussels time)", etc.
        clean_date = date_str.strip().split('(')[0].strip()

        # Try different formats
        for fmt in ['%d %B %Y', '%d %b %Y']:
            try:
                return datetime.strptime(clean_date, fmt)
            except:
                continue
    except Exception as e:
        pass

    return None


def calculate_weeks(start_date_str, end_date_str):
    """Calculate consultation period in weeks"""
    start = parse_date(start_date_str)
    end = parse_date(end_date_str)

    if start and end:
        delta = end - start
        weeks = delta.days / 7
        return round(weeks)  # Round to nearest week

    return None


def analyze_json(filepath: str):
    """Analyze JSON results file"""
    with open(filepath, 'r') as f:
        data = json.load(f)
    return analyze_data(data)


def analyze_csv(filepath: str):
    """Analyze CSV results file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        data = list(reader)
    return analyze_data(data)


def analyze_data(data: list):
    """Generate comprehensive temporal analysis"""

    print("\n" + "="*80)
    print("EU PUBLIC CONSULTATIONS 2016-2026 - TEMPORAL ANALYSIS")
    print("="*80 + "\n")

    total = len(data)
    print(f"Total consultations analyzed: {total}")

    # Helper function to check boolean fields
    def is_true(value):
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() == 'true'
        return False

    # Calculate consultation durations
    durations = []
    for record in data:
        weeks = calculate_weeks(
            record.get('consultation_start_date'),
            record.get('consultation_end_date')
        )
        if weeks is not None:
            durations.append(weeks)

    if durations:
        print(f"\n" + "="*80)
        print("CONSULTATION DURATION ANALYSIS")
        print("="*80)

        print(f"\nTotal consultations with duration data: {len(durations)}/{total}")
        print(f"Average duration: {sum(durations)/len(durations):.1f} weeks")
        print(f"Median duration: {sorted(durations)[len(durations)//2]} weeks")
        print(f"Shortest: {min(durations)} weeks")
        print(f"Longest: {max(durations)} weeks")

        # Distribution
        duration_buckets = defaultdict(int)
        for w in durations:
            if w < 4:
                duration_buckets['< 4 weeks'] += 1
            elif w < 8:
                duration_buckets['4-7 weeks'] += 1
            elif w < 12:
                duration_buckets['8-11 weeks'] += 1
            elif w < 16:
                duration_buckets['12-15 weeks'] += 1
            else:
                duration_buckets['16+ weeks'] += 1

        print(f"\nDuration distribution:")
        for bucket in ['< 4 weeks', '4-7 weeks', '8-11 weeks', '12-15 weeks', '16+ weeks']:
            if bucket in duration_buckets:
                count = duration_buckets[bucket]
                pct = (count / len(durations)) * 100
                print(f"  {bucket}: {count} ({pct:.1f}%)")

    # TEMPORAL ANALYSIS: Data sharing over time
    print(f"\n" + "="*80)
    print("DATA SHARING TRENDS OVER TIME")
    print("="*80)
    print("\nTesting hypothesis: Did the EU Commission become more secretive after 2016?")
    print("(Better Regulation initiative came into force April 2016)")

    yearly_data = defaultdict(lambda: {'total': 0, 'full_data': 0, 'summary_only': 0, 'no_data': 0})

    for record in data:
        year = record.get('consultation_year')
        if year:
            try:
                year = int(year)
            except:
                continue

            yearly_data[year]['total'] += 1

            has_contributions = is_true(record.get('has_contributions_zip'))
            has_summary = is_true(record.get('has_summary_report'))

            if has_contributions:
                yearly_data[year]['full_data'] += 1
            elif has_summary:
                yearly_data[year]['summary_only'] += 1
            else:
                yearly_data[year]['no_data'] += 1

    print(f"\nData sharing by year:")
    print(f"\n{'Year':<8} {'Total':<8} {'Full Data':<15} {'Summary Only':<17} {'No Data':<15}")
    print("-" * 80)

    for year in sorted(yearly_data.keys()):
        counts = yearly_data[year]
        total_year = counts['total']

        if total_year > 0:
            full_pct = (counts['full_data'] / total_year) * 100
            summary_pct = (counts['summary_only'] / total_year) * 100
            no_data_pct = (counts['no_data'] / total_year) * 100

            print(f"{year:<8} {total_year:<8} {counts['full_data']:<6} ({full_pct:>5.1f}%)  "
                  f"{counts['summary_only']:<6} ({summary_pct:>5.1f}%)  "
                  f"{counts['no_data']:<6} ({no_data_pct:>5.1f}%)")

    # Calculate trend
    early_years = [2016, 2017, 2018]  # First 3 years
    recent_years = [2023, 2024, 2025]  # Last 3 years

    early_full_data = sum(yearly_data[y]['full_data'] for y in early_years if y in yearly_data)
    early_total = sum(yearly_data[y]['total'] for y in early_years if y in yearly_data)

    recent_full_data = sum(yearly_data[y]['full_data'] for y in recent_years if y in yearly_data)
    recent_total = sum(yearly_data[y]['total'] for y in recent_years if y in yearly_data)

    if early_total > 0 and recent_total > 0:
        early_pct = (early_full_data / early_total) * 100
        recent_pct = (recent_full_data / recent_total) * 100
        change = recent_pct - early_pct

        print(f"\n" + "="*80)
        print("TREND ANALYSIS: Early years (2016-2018) vs Recent years (2023-2025)")
        print("="*80)
        print(f"\nEarly years (2016-2018):")
        print(f"  Full data sharing: {early_full_data}/{early_total} ({early_pct:.1f}%)")

        print(f"\nRecent years (2023-2025):")
        print(f"  Full data sharing: {recent_full_data}/{recent_total} ({recent_pct:.1f}%)")

        print(f"\n{'→ CHANGE: '}")
        if change < 0:
            print(f"  ⚠️  DECREASE of {abs(change):.1f} percentage points")
            print(f"  This supports the hypothesis that data sharing has DECLINED over time.")
        elif change > 0:
            print(f"  ✓ INCREASE of {change:.1f} percentage points")
            print(f"  This contradicts the hypothesis - data sharing has actually IMPROVED.")
        else:
            print(f"  No significant change in data sharing rates.")

    # Duration trends over time
    print(f"\n" + "="*80)
    print("CONSULTATION DURATION TRENDS OVER TIME")
    print("="*80)

    yearly_durations = defaultdict(list)

    for record in data:
        year = record.get('consultation_year')
        weeks = calculate_weeks(
            record.get('consultation_start_date'),
            record.get('consultation_end_date')
        )

        if year and weeks:
            try:
                year = int(year)
                yearly_durations[year].append(weeks)
            except:
                continue

    print(f"\n{'Year':<8} {'Consultations':<15} {'Avg Duration':<15} {'Median Duration':<15}")
    print("-" * 60)

    for year in sorted(yearly_durations.keys()):
        durations_year = yearly_durations[year]
        avg_duration = sum(durations_year) / len(durations_year)
        median_duration = sorted(durations_year)[len(durations_year)//2]

        print(f"{year:<8} {len(durations_year):<15} {avg_duration:<15.1f} {median_duration:<15}")

    # Correlation: Does consultation duration affect data sharing?
    print(f"\n" + "="*80)
    print("CORRELATION: Consultation Duration vs Data Sharing")
    print("="*80)

    duration_vs_sharing = defaultdict(lambda: {'full_data': 0, 'summary_only': 0, 'no_data': 0, 'total': 0})

    for record in data:
        weeks = calculate_weeks(
            record.get('consultation_start_date'),
            record.get('consultation_end_date')
        )

        if weeks:
            if weeks < 8:
                bucket = 'Short (< 8 weeks)'
            elif weeks < 12:
                bucket = 'Standard (8-11 weeks)'
            else:
                bucket = 'Long (12+ weeks)'

            duration_vs_sharing[bucket]['total'] += 1

            has_contributions = is_true(record.get('has_contributions_zip'))
            has_summary = is_true(record.get('has_summary_report'))

            if has_contributions:
                duration_vs_sharing[bucket]['full_data'] += 1
            elif has_summary:
                duration_vs_sharing[bucket]['summary_only'] += 1
            else:
                duration_vs_sharing[bucket]['no_data'] += 1

    print(f"\nData sharing by consultation duration:")
    for bucket in ['Short (< 8 weeks)', 'Standard (8-11 weeks)', 'Long (12+ weeks)']:
        if bucket in duration_vs_sharing:
            counts = duration_vs_sharing[bucket]
            total_bucket = counts['total']

            if total_bucket > 0:
                full_pct = (counts['full_data'] / total_bucket) * 100

                print(f"\n{bucket}: {total_bucket} consultations")
                print(f"  Full data: {counts['full_data']} ({full_pct:.1f}%)")
                print(f"  Summary only: {counts['summary_only']} ({counts['summary_only']/total_bucket*100:.1f}%)")
                print(f"  No data: {counts['no_data']} ({counts['no_data']/total_bucket*100:.1f}%)")

    print("\n" + "="*80 + "\n")


def main():
    """Main execution"""
    if len(sys.argv) < 2:
        print("Usage: python analyze_temporal.py <json_or_csv_file>")
        print("\nExample:")
        print("  python analyze_temporal.py eu_consultations_2016_2026_*.json")
        sys.exit(1)

    input_file = sys.argv[1]

    if not Path(input_file).exists():
        print(f"Error: File not found: {input_file}")
        sys.exit(1)

    if input_file.endswith('.json'):
        analyze_json(input_file)
    elif input_file.endswith('.csv'):
        analyze_csv(input_file)
    else:
        print("Error: File must be .json or .csv")
        sys.exit(1)


if __name__ == "__main__":
    main()
