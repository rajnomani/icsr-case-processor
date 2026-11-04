"""Step 3: is the event expected, according to the drug's label?

Each valid case is compared with data/label.csv, a small FICTIONAL list of
the side effects already listed for each fictional drug.

An event is EXPECTED if the case's event text (event_verbatim) contains one of
the keywords listed for that drug. Otherwise it is UNEXPECTED.
A SERIOUS + UNEXPECTED case is the highest priority in pharmacovigilance.

Reads data/cases.csv and data/label.csv. Writes outputs/expectedness.csv.
Run from the project folder:

    python src/expectedness.py
"""
import csv
from pathlib import Path

from validity import check_case
from seriousness import serious_criteria

DATA = Path("data/cases.csv")
LABEL = Path("data/label.csv")
OUT = Path("outputs/expectedness.csv")


def load_label():
    """Return a list of (drug, listed_term, [keywords]) from label.csv."""
    with open(LABEL, newline="") as fh:
        return [(r["drug"].strip(), r["listed_term"].strip(),
                 [k.strip().lower() for k in r["keywords"].split(";") if k.strip()])
                for r in csv.DictReader(fh)]


def find_listed_term(row, label):
    """Return the label term this case's event matches, or '' if none."""
    text = row["event_verbatim"].lower()
    for drug, term, keywords in label:
        if drug == row["suspect_drug"].strip() and any(k in text for k in keywords):
            return term
    return ""


def main():
    label = load_label()
    with open(DATA, newline="") as fh:
        rows = list(csv.DictReader(fh))

    results = []
    for row in rows:
        if check_case(row):
            results.append({"case_id": row["case_id"], "valid": "no", "serious": "",
                            "expected": "not assessed", "listed_term": "", "priority": ""})
            continue
        serious = "yes" if serious_criteria(row) else "no"
        term = find_listed_term(row, label)
        expected = "yes" if term else "no"
        priority = "HIGH" if (serious == "yes" and expected == "no") else ""
        results.append({"case_id": row["case_id"], "valid": "yes", "serious": serious,
                        "expected": expected, "listed_term": term, "priority": priority})

    OUT.parent.mkdir(exist_ok=True)
    with open(OUT, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["case_id", "valid", "serious", "expected",
                                                "listed_term", "priority"])
        writer.writeheader()
        writer.writerows(results)

    valid = [r for r in results if r["valid"] == "yes"]
    high = [r for r in valid if r["priority"] == "HIGH"]
    print(f"{len(valid)} valid cases: "
          f"{sum(r['expected'] == 'yes' for r in valid)} expected, "
          f"{sum(r['expected'] == 'no' for r in valid)} unexpected")
    print(f"{len(high)} are serious AND unexpected (highest priority)\n")
    for r in high:
        print(f"HIGH  {r['case_id']}")
    print(f"\nWrote {OUT}")


if __name__ == "__main__":
    main()