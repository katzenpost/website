"""Check rule IDs, including references left in older dotted notation."""

import re
import sys
from pathlib import Path


def check(path):
    source = path.read_text(encoding="utf-8")
    definitions = re.findall(r"^\| (R-\d+-\d+) \|", source, re.MULTILINE)
    references = set(re.findall(r"\bR-\d+(?:[.-]\d+)+", source))
    missing = sorted(references - set(definitions))
    duplicates = sorted({rule for rule in definitions if definitions.count(rule) > 1})
    misplaced = []
    section = None
    expected = 0
    for line in source.splitlines():
        heading = re.match(r"### (?:2\.|R-)(\d+)[.\s]", line)
        if heading:
            section = int(heading[1])
            expected = 0
        rule = re.match(r"\| R-(\d+)-(\d+) \|", line)
        if rule:
            expected += 1
            if int(rule[1]) != section or int(rule[2]) != expected:
                misplaced.append(rule[0].strip("| "))
    print(f"{path}: {len(definitions)} rules, missing={missing}, "
          f"duplicates={duplicates}, out_of_order={misplaced}")
    return bool(missing or duplicates or misplaced)


if __name__ == "__main__":
    paths = sys.argv[1:] or ["content/en/docs/specs/dirauth.md"]
    sys.exit(any([check(Path(path)) for path in paths]))
