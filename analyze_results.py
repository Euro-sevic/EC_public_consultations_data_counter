"""
Analyze and summarize scraped consultation data
"""

import json
import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path


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
    """Generate analysis summary"""

    print("\n" + "="*80)
    print("EU PUBLIC CONSULTATIONS 2025 - ANALYSIS SUMMARY")
    print("="*80 + "\n")

    # Basic statistics
    total = len(data)
    print(f"Total consultations: {total}")

    # Scrape status
    statuses = Counter(record.get('scrape_status', 'unknown') for record in data)
    print(f"\nScrape Status:")
    for status, count in statuses.items():
        percentage = (count / total) * 100
        print(f"  {status}: {count} ({percentage:.1f}%)")

    # Topics
    topics = Counter(record.get('topic', 'Unknown') for record in data if record.get('topic'))
    print(f"\nTop Topics ({len(topics)} unique):")
    for topic, count in topics.most_common(10):
        print(f"  {topic}: {count}")

    # Feedback statistics
    feedback_counts = []
    for record in data:
        feedback = record.get('total_feedback')
        if feedback:
            try:
                feedback_counts.append(int(feedback))
            except (ValueError, TypeError):
                pass

    if feedback_counts:
        print(f"\nFeedback Statistics:")
        print(f"  Total responses across all consultations: {sum(feedback_counts):,}")
        print(f"  Average per consultation: {sum(feedback_counts) / len(feedback_counts):.0f}")
        print(f"  Median: {sorted(feedback_counts)[len(feedback_counts)//2]:,}")
        print(f"  Min: {min(feedback_counts):,}")
        print(f"  Max: {max(feedback_counts):,}")

    # Data availability
    def count_true(field):
        count = 0
        for record in data:
            value = record.get(field)
            if isinstance(value, bool):
                if value:
                    count += 1
            elif isinstance(value, str):
                if value.lower() == 'true':
                    count += 1
        return count

    summary_count = count_true('has_summary_report')
    contributions_count = count_true('has_contributions_zip')
    documents_count = count_true('has_documents_annexed')

    print(f"\nData Availability:")
    print(f"  Summary reports: {summary_count}/{total} ({(summary_count/total)*100:.1f}%)")
    print(f"  Contributions ZIP: {contributions_count}/{total} ({(contributions_count/total)*100:.1f}%)")
    print(f"  Documents annexed: {documents_count}/{total} ({(documents_count/total)*100:.1f}%)")

    # Consultations with full data
    full_data = sum(1 for record in data
                   if (isinstance(record.get('has_summary_report'), bool) and record.get('has_summary_report') or
                       isinstance(record.get('has_summary_report'), str) and record.get('has_summary_report').lower() == 'true')
                   and (isinstance(record.get('has_contributions_zip'), bool) and record.get('has_contributions_zip') or
                        isinstance(record.get('has_contributions_zip'), str) and record.get('has_contributions_zip').lower() == 'true'))

    print(f"\nConsultations with both summary AND contributions: {full_data}/{total} ({(full_data/total)*100:.1f}%)")

    # Consultation periods
    print(f"\nConsultation Duration Analysis:")
    durations = defaultdict(int)
    for record in data:
        period = record.get('consultation_period')
        if period and '-' in period:
            durations['has_period'] += 1
        else:
            durations['missing_period'] += 1

    print(f"  With period data: {durations['has_period']}/{total}")
    print(f"  Missing period: {durations['missing_period']}/{total}")

    # Top consultations by feedback
    print(f"\nTop 10 Consultations by Feedback:")
    sorted_by_feedback = sorted(
        [r for r in data if r.get('total_feedback')],
        key=lambda x: int(x.get('total_feedback', 0)) if x.get('total_feedback') else 0,
        reverse=True
    )[:10]

    for i, record in enumerate(sorted_by_feedback, 1):
        name = record.get('initiative_name', 'Unknown')[:60]
        feedback = record.get('total_feedback', 0)
        print(f"  {i}. {name}... ({feedback:,} responses)")

    # DATA AVAILABILITY PATTERNS
    print(f"\n" + "="*80)
    print("DATA AVAILABILITY PATTERNS ANALYSIS")
    print("="*80)

    # Categorize consultations by data availability
    full_data_records = []
    summary_only_records = []
    no_data_records = []

    for record in data:
        has_contributions = record.get('has_contributions_zip')
        if isinstance(has_contributions, str):
            has_contributions = has_contributions.lower() == 'true'

        has_summary = record.get('has_summary_report')
        if isinstance(has_summary, str):
            has_summary = has_summary.lower() == 'true'

        if has_contributions:
            full_data_records.append(record)
        elif has_summary:
            summary_only_records.append(record)
        else:
            no_data_records.append(record)

    print(f"\nData Sharing Categories:")
    print(f"  Full data (contributions ZIP): {len(full_data_records)} ({len(full_data_records)/total*100:.1f}%)")
    print(f"  Summary report only: {len(summary_only_records)} ({len(summary_only_records)/total*100:.1f}%)")
    print(f"  No data shared: {len(no_data_records)} ({len(no_data_records)/total*100:.1f}%)")

    # Pattern 1: Data sharing by response volume
    print(f"\n1. PATTERN: Data Sharing vs Response Volume")
    print("-" * 80)

    # Group by response volume
    def get_volume_category(feedback):
        if not feedback:
            return "Unknown"
        try:
            fb = int(feedback)
            if fb < 50:
                return "Low (<50)"
            elif fb < 500:
                return "Medium (50-500)"
            else:
                return "High (>500)"
        except:
            return "Unknown"

    volume_patterns = defaultdict(lambda: {'full': 0, 'summary': 0, 'none': 0, 'total': 0})

    for record in data:
        volume = get_volume_category(record.get('total_feedback'))
        volume_patterns[volume]['total'] += 1

        has_contributions = record.get('has_contributions_zip')
        if isinstance(has_contributions, str):
            has_contributions = has_contributions.lower() == 'true'
        has_summary = record.get('has_summary_report')
        if isinstance(has_summary, str):
            has_summary = has_summary.lower() == 'true'

        if has_contributions:
            volume_patterns[volume]['full'] += 1
        elif has_summary:
            volume_patterns[volume]['summary'] += 1
        else:
            volume_patterns[volume]['none'] += 1

    for volume in ["Low (<50)", "Medium (50-500)", "High (>500)", "Unknown"]:
        if volume in volume_patterns:
            v = volume_patterns[volume]
            print(f"\n{volume} responses: {v['total']} consultations")
            if v['total'] > 0:
                print(f"  Full data: {v['full']} ({v['full']/v['total']*100:.1f}%)")
                print(f"  Summary only: {v['summary']} ({v['summary']/v['total']*100:.1f}%)")
                print(f"  No data: {v['none']} ({v['none']/v['total']*100:.1f}%)")

    # Pattern 2: Data sharing by topic
    print(f"\n2. PATTERN: Data Sharing by Topic")
    print("-" * 80)

    topic_patterns = defaultdict(lambda: {'full': 0, 'summary': 0, 'none': 0, 'total': 0})

    for record in data:
        topic = record.get('topic', 'Unknown')
        if not topic or topic == 'None':
            topic = 'Unknown'

        topic_patterns[topic]['total'] += 1

        has_contributions = record.get('has_contributions_zip')
        if isinstance(has_contributions, str):
            has_contributions = has_contributions.lower() == 'true'
        has_summary = record.get('has_summary_report')
        if isinstance(has_summary, str):
            has_summary = has_summary.lower() == 'true'

        if has_contributions:
            topic_patterns[topic]['full'] += 1
        elif has_summary:
            topic_patterns[topic]['summary'] += 1
        else:
            topic_patterns[topic]['none'] += 1

    # Sort by total consultations
    sorted_topics = sorted(topic_patterns.items(), key=lambda x: x[1]['total'], reverse=True)

    print(f"\nTop topics by consultation count:")
    for topic, counts in sorted_topics[:10]:
        print(f"\n{topic}: {counts['total']} consultations")
        if counts['total'] > 0:
            print(f"  Full data: {counts['full']} ({counts['full']/counts['total']*100:.0f}%)")
            print(f"  Summary only: {counts['summary']} ({counts['summary']/counts['total']*100:.0f}%)")
            print(f"  No data: {counts['none']} ({counts['none']/counts['total']*100:.0f}%)")

    # Pattern 3: Consultation period timing
    print(f"\n3. PATTERN: Data Sharing by Consultation Timing")
    print("-" * 80)

    def extract_start_month(period):
        if not period:
            return None
        try:
            # Extract first date
            parts = period.split('-')[0].strip()
            # Parse "24 July 2025" format
            month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                          'July', 'August', 'September', 'October', 'November', 'December']
            for month in month_names:
                if month in parts:
                    return month
        except:
            pass
        return None

    month_patterns = defaultdict(lambda: {'full': 0, 'summary': 0, 'none': 0, 'total': 0})

    for record in data:
        month = extract_start_month(record.get('consultation_period'))
        if not month:
            month = 'Unknown'

        month_patterns[month]['total'] += 1

        has_contributions = record.get('has_contributions_zip')
        if isinstance(has_contributions, str):
            has_contributions = has_contributions.lower() == 'true'
        has_summary = record.get('has_summary_report')
        if isinstance(has_summary, str):
            has_summary = has_summary.lower() == 'true'

        if has_contributions:
            month_patterns[month]['full'] += 1
        elif has_summary:
            month_patterns[month]['summary'] += 1
        else:
            month_patterns[month]['none'] += 1

    month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December', 'Unknown']

    print(f"\nBy consultation start month:")
    for month in month_order:
        if month in month_patterns and month_patterns[month]['total'] > 0:
            counts = month_patterns[month]
            print(f"\n{month}: {counts['total']} consultations")
            print(f"  Full data: {counts['full']} ({counts['full']/counts['total']*100:.0f}%)")
            print(f"  Summary only: {counts['summary']} ({counts['summary']/counts['total']*100:.0f}%)")
            print(f"  No data: {counts['none']} ({counts['none']/counts['total']*100:.0f}%)")

    print("\n" + "="*80 + "\n")


def main():
    """Main execution"""
    if len(sys.argv) < 2:
        print("Usage: python analyze_results.py <json_or_csv_file>")
        print("\nExample:")
        print("  python analyze_results.py eu_consultations_2025_20240113_123456.json")
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
