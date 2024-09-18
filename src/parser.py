import csv
from scraper import scraper
from combat_config import *

import csv
import pandas as pd
from datetime import datetime
import re


def parse_log_line(line):
    csv_reader = csv.reader([line], delimiter=",", quotechar='"', skipinitialspace=True)
    fields = next(csv_reader)

    # Handle lines without timestamps
    if not re.match(r"\d+/\d+/\d+", fields[0]):
        # This might be position data or another type
        return None

    # Extract timestamp and event
    timestamp_event = fields[0].split("  ")
    if len(timestamp_event) < 2:
        return None
    timestamp_str = timestamp_event[0].strip()
    event = timestamp_event[1].strip()

    # Reconstruct fields list
    fields = [timestamp_str, event] + fields[1:]

    # Get expected fields
    expected_fields = event_fields.get(event, [])

    if not expected_fields:
        # Unknown event type
        return None

    # Map fields to names
    event_data = {}
    for i, field_name in enumerate(expected_fields):
        if i < len(fields):
            event_data[field_name] = fields[i]
        else:
            event_data[field_name] = None  # Optional field

    # Convert timestamp
    try:
        event_data["timestamp"] = datetime.strptime(
            event_data["timestamp"], "%m/%d/%Y %H:%M:%S.%f%z"
        )
    except ValueError:
        # Handle different formats if necessary
        pass

    # Convert numerical fields

    numerical_fields = [
        "sourceFlags",
        "sourceRaidFlags",
        "destFlags",
        "destRaidFlags",
        "spellId",
        "spellSchool",
        "amount",
        "overkill",
        "school",
        "resisted",
        "blocked",
        "absorbed",
        "critical",
        "glancing",
        "crushing",
        "isOffHand",
        "multistrike",
        "stackCount",
        "extraSpellId",
        "extraSpellSchool",
        "posX",
        "posY",
        "posZ",
        "facing",
        # Add any other numeric fields
    ]
    for field in numerical_fields:
        if field in event_data and event_data[field]:
            try:
                event_data[field] = int(event_data[field], 0)
            except ValueError:
                event_data[field] = 0

    return event_data


# Initialize the event_fields dictionary with detailed field mappings for each event type

if __name__ == "__main__":
    scraper = scraper()
    url = "https://wowarenalogs.com/match?id=8ac0be8088ade79236447693b8e86d4d&viewerIsOwner=false&source=search"
    log_data = scraper.get_og_log_file_given_url(url)
    # Parse the log file
    log_entries = []

    for line in log_data.strip().split("\n"):
        line = line.strip()
        parsed_line = parse_log_line(line)
        if parsed_line:
            log_entries.append(parsed_line)
        else:
            # Handle or log lines that couldn't be parsed
            pass

    # Create DataFrame
    df = pd.DataFrame(log_entries)

    # Display the DataFrame
    print(df.head())
    df.to_csv("test.csv")
