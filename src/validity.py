"""Step 1: is each fictional case a valid report?

A case is valid only if it has all four minimum criteria
(EMA GVP Module VI, section VI.B.2):
    1. an identifiable reporter  (here: reporter_type AND reporter_country filled in)
    2. an identifiable patient   (here: at least one of initials, age or sex)
    3. a suspect drug
    4. a suspected adverse event

Reads data/cases.csv. Writes outputs/validity.csv. Run from the project folder:

    python src/validity.py
"""
import csv
from pathlib import Path

DATA = Path("data/cases.csv")
OUT = Path("outputs/validity.csv")


def filled(row, *columns):
    """True if at least one of the columns has text in it."""
    return any(row[c].strip() for c in columns)


def check_case(row):
    """Return the list of reasons why this case is NOT valid (empty list = valid)."""
    reasons = []
    if not (row["reporter_type"].strip() and row["reporter_country"].strip()):
        reasons.append("no identifiable reporter")
    if not filled(row, "patient_initials", "patient_age", "patient_sex"):
        reasons.append("no identifiable patient")
    if not filled(row, "suspect_drug"):
        reasons.append("no suspect drug")
    if not filled(row, "event_verbatim"):
        reasons.append("no suspected adverse event")
    return reasons


def main():
    with open(DATA, newline="") as fh:
        rows = list(csv.DictReader(fh))

    results = []
    for row in rows:
        reasons = check_case(row)
        results.append({"case_id": row["case_id"],
                        "valid": "no" if reasons else "yes",
                        "reasons": "; ".join(reasons)})

    OUT.parent.mkdir(exist_ok=True)
    with open(OUT, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["case_id", "valid", "reasons"])
        writer.writeheader()
        writer.writerows(results)

    valid = sum(r["valid"] == "yes" for r in results)
    print(f"{len(results)} cases read, {valid} valid, {len(results) - valid} not valid\n")
    for r in results:
        if r["valid"] == "no":
            print(f"NOT VALID  {r['case_id']}: {r['reasons']}")
    print(f"\nWrote {OUT}")


if __name__ == "__main__":
    main()