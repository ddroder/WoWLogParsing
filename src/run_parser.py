import sys
import os
import csv

# Adjust the import path if necessary
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(parent_dir)

from parser import Parser

if __name__ == "__main__":
    psr = Parser()

    # Define the fieldnames for the CSV file
    fieldnames = [
        "timestamp",
        "event",
        "sourceGUID",
        "sourceName",
        "sourceFlags",
        "sourceFlags2",
        "destGUID",
        "destName",
        "destFlags",
        "destFlags2",
        "spellId",
        "spellName",
        "spellSchool",
        "amount",
        "overhealing",
        "absorbed",
        "critical",
        "auraType",
        "failedType",
        "powerType",
        "absorbAmount",
        "absorberGUID",
        "absorberName",
        "absorberFlags",
        "absorberFlags2",
        "absorberSpellId",
        "absorberSpellName",
        "absorberSpellSchool",
        "sourceClass",
        "destClass",
    ]

    for fname in sys.argv[1:]:
        # Extract the base filename
        base_name = os.path.basename(
            fname
        )  # e.g., 'log_b33c73864838a74ffc72663c445bff04.txt'

        # Check if the filename matches the expected format
        if base_name.startswith("log_") and base_name.endswith(".txt"):
            # Extract the game ID
            game_id = base_name[len("log_") : -len(".txt")]
            # Construct the output filename
            output_file = (
                f"/Users/ddroder/code/wow-log-ml/data/parsed_log_{game_id}.csv"
            )
        else:
            print(
                f"Filename '{base_name}' does not match expected format 'log_<game_id>.txt'"
            )
            continue  # Skip this file

        # Open the output CSV file for writing
        with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            # Open the input log file for reading
            with open(fname, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        ev = psr.parse_line(line)
                        writer.writerow(ev)
                    except Exception as e:
                        print(f"Error parsing line in file '{fname}': {e}")
                        print(f"Line content: {line.strip()}")
