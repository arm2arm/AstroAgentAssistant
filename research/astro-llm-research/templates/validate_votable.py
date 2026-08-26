templates/validate_votable.py: a small validation script example

#!/usr/bin/env python3
"""
Simple VOTable validator using astropy and pyvo. Intended as a template to be copied
into a skill's scripts/ directory and adapted to a repository's CI.
"""

import sys
from astropy.io.votable import parse_single_table


def validate_votable(path):
    try:
        table = parse_single_table(path)
        # Basic checks: columns, units
        for col in table.table.columns:
            if col.unit is None:
                print(f"WARNING: Column {col.name} has no unit")
        print("VOTable parsed OK")
        return 0
    except Exception as e:
        print("ERROR parsing VOTable:", e)
        return 2


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: validate_votable.py <votable.xml>")
        sys.exit(2)
    sys.exit(validate_votable(sys.argv[1]))
