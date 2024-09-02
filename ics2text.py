import os
import csv
import argparse
from collections import defaultdict
from icalendar import Calendar

# Default constants
DEFAULT_FOLDER_PATH = 'samples'  # Default folder path if none provided
DEFAULT_KEYWORDS = ['Meeting', 'ClientX', 'Discovery']  # Default keywords for OR query
OUTPUT_TEXT_FILE = 'merged_filtered_events.txt'  # Output text file
OUTPUT_CSV_FILE = 'merged_filtered_events.csv'  # Output CSV file


# Function to extract events based on multiple keywords (OR query)
def extract_events_by_keywords(ics_file_path, keywords):
    matching_events = []

    with open(ics_file_path, 'r', encoding='utf-8') as file:
        # Load the calendar
        calendar = Calendar.from_ical(file.read())

        # Iterate through calendar components
        for component in calendar.walk():
            if component.name == "VEVENT":
                summary = str(component.get('SUMMARY'))
                description = str(component.get('DESCRIPTION'))
                attendees = component.get('ATTENDEE')
                attendees_list = []

                # Ensure attendees are in a list format
                if attendees:
                    if not isinstance(attendees, list):
                        attendees = [attendees]
                    attendees_list = [attendee.to_ical().decode('utf-8').split(':')[1] for attendee in attendees]

                # Check if any keyword is in SUMMARY, DESCRIPTION, or ATTENDEE email list
                matching_keywords = [keyword for keyword in keywords if (
                        keyword.lower() in summary.lower() or
                        keyword.lower() in description.lower() or
                        any(keyword.lower() in attendee.lower() for attendee in attendees_list)
                )]

                if matching_keywords:
                    event_info = {
                        'Event': summary,
                        'Start': component.get('DTSTART').dt.strftime('%Y-%m-%d %H:%M'),
                        'End': component.get('DTEND').dt.strftime('%Y-%m-%d %H:%M'),
                        'Guests': ', '.join(attendees_list),
                        'Location': str(component.get('LOCATION')),
                        'UID': component.get('UID'),  # Unique identifier to check duplicates
                        'SourceFile': ics_file_path,
                        'MatchedKeywords': matching_keywords
                    }
                    matching_events.append(event_info)

    return matching_events


# Function to process all .ics files in a folder
def process_ics_files_in_folder(folder_path, keywords):
    all_matching_events = []

    # List all files in the directory
    for filename in os.listdir(folder_path):
        if filename.endswith('.ics'):
            file_path = os.path.join(folder_path, filename)
            print(f"Processing file: {file_path}")
            events = extract_events_by_keywords(file_path, keywords)
            all_matching_events.extend(events)

    return all_matching_events


# Function to remove duplicates and sort events
def remove_duplicates_and_sort_events(events):
    unique_events = {}
    duplicate_count = 0
    duplicate_details = defaultdict(lambda: defaultdict(int))

    # Check for duplicates based on UID
    for event in events:
        uid = event['UID']
        if uid not in unique_events:
            unique_events[uid] = event
        else:
            duplicate_count += 1
            # Track duplicates by keyword and file
            for keyword in event['MatchedKeywords']:
                duplicate_details[keyword][event['SourceFile']] += 1

    # Sort events chronologically
    sorted_events = sorted(unique_events.values(), key=lambda x: x['Start'])

    return sorted_events, duplicate_count, duplicate_details


# Main function
def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Process .ics files to extract and merge calendar events.')
    parser.add_argument('folder_path', nargs='?', default=DEFAULT_FOLDER_PATH,
                        help='Path to the folder containing .ics files.')
    parser.add_argument('keywords', nargs='*', default=DEFAULT_KEYWORDS,
                        help='Keywords to search for in events (OR query).')

    # Parse the arguments
    args = parser.parse_args()
    folder_path = args.folder_path
    keywords = args.keywords

    # Extract events from all .ics files in the specified folder
    events = process_ics_files_in_folder(folder_path, keywords)

    # Remove duplicates and sort events
    sorted_events, duplicate_count, duplicate_details = remove_duplicates_and_sort_events(events)

    # Calculate keyword counts
    keyword_count = {keyword: 0 for keyword in keywords}
    for event in sorted_events:
        for keyword in event['MatchedKeywords']:
            keyword_count[keyword] += 1

    # Log keyword counts
    for keyword, count in keyword_count.items():
        print(f"Events found for '{keyword}': {count}")

    # Log duplicate counts by keyword and file
    print(f"Overall duplicated events found across .ics files: {duplicate_count}")
    for keyword, file_counts in duplicate_details.items():
        for file, count in file_counts.items():
            print(f"Duplicated events for keyword '{keyword}' in file '{file}': {count}")

    # Log the total number of unique events
    print(f"Total unique events stored in the file: {len(sorted_events)}")

    # Write all filtered events to a single text file
    with open(OUTPUT_TEXT_FILE, 'w', encoding='utf-8') as output_file:
        if sorted_events:
            for event in sorted_events:
                output_file.write(f"Event: {event['Event']}\n")
                output_file.write(f"Start: {event['Start']}\n")
                output_file.write(f"End: {event['End']}\n")
                output_file.write(f"Guests: {event['Guests']}\n")
                output_file.write(f"Location: {event['Location']}\n")
                output_file.write('-' * 40 + '\n')
        else:
            output_file.write("No events found with the specified keywords.\n")

    # Write all filtered events to a CSV file
    with open(OUTPUT_CSV_FILE, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=';')
        csv_writer.writerow(['Start', 'End', 'Guest number', 'Event title or summary', 'Location', 'Guests'])
        for event in sorted_events:
            guest_number = len(event['Guests'].split(', ')) if event['Guests'] else 0
            csv_writer.writerow([
                event['Start'],
                event['End'],
                guest_number,
                event['Event'],
                event['Location'],
                '\n'.join(event['Guests'].split(', '))
            ])

    print(f"Filtered events have been saved to {OUTPUT_TEXT_FILE} and {OUTPUT_CSV_FILE}.")


# Entry point
if __name__ == "__main__":
    main()
