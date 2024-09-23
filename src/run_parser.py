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
    output_file = "parsed_logs.csv"  # Specify the output CSV file name

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
    ]

    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for fname in sys.argv[1:]:
            with open(fname, "r") as f:
                for line in f:
                    try:
                        ev = psr.parse_line(line)
                        writer.writerow(ev)
                    except Exception as e:
                        print(f"Error parsing line: {e}")
                        print(f"Line content: {line}")
