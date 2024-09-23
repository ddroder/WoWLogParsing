import sys
import os

path = os.path.abspath(sys.argv[0])
bdir = os.path.dirname(path)
sys.path.append(os.path.join(bdir, ".."))

import wowclp

if __name__ == "__main__":
    import sys

    psr = wowclp.Parser()
    for fname in sys.argv[1:]:
        with open(fname, "r") as f:
            for line in f:
                try:
                    ev = psr.parse_line(line)
                    print(ev)
                    # Add any additional logic you need here
                except Exception as e:
                    print(f"Error parsing line: {e}")
                    print(f"Line content: {line}")
