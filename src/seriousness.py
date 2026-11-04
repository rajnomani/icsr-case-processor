"""Step 2: is each valid case serious?

A case is serious if at least one of these six criteria is marked 1
(FDA IND safety reporting criteria, also used by ICH E2A):
    death, life_threatening, hospitalised, disability,
    congenital_anomaly, other_important (important medical event)

Only valid cases (from step 1) are assessed. A case that is not valid
is not assessed for seriousness here.

Reads data/cases.csv. Writes outputs/seriousness.csv. Run from the project folder:

    python src/seriousness.py
"""
import csv
from pathlib import Path

from validity import check_case

DATA = Path("data/cases.csv")
OUT = Path("outputs/seriousness.csv")

CRITERIA = ["death", "life_threatening", "hospitalised",
            "disability", "congenital_anomaly", "other_important"]


def serious_criteria(row):
    """Return the list of seriousness criteria marked 1 for this case."""
    return [c for c in CRITERIA if row[c].strip() == "1"]


def main():
    with open(DATA, newline="") as fh:
        rows = list(csv.DictReader(fh))

    results = []
    for row in rows:
        if check_case(row):
            results.append({"case_id": row["case_id"], "valid": "no",
                            "serious": "not assessed", "criteria": ""})
            continue
        met = serious_criteria(row)
        results.append({"case_id": row["case_id"], "valid": "yes",
                        "serious": "yes" if met else "no",
                        "criteria": "; ".join(met)})

    OUT.parent.mkdir(exist_ok=True)
    with open(OUT, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["case_id", "valid", "serious", "criteria"])
        writer.writeheader()
        writer.writerows(results)

    valid = [r for r in results if r["valid"] == "yes"]
    serious = [r for r in valid if r["serious"] == "yes"]
    print(f"{len(results)} cases read, {len(valid)} valid, "
          f"{len(serious)} serious, {len(valid) - len(serious)} non-serious\n")
    for r in serious:
        print(f"SERIOUS  {r['case_id']}: {r['criteria']}")
    print(f"\nWrote {OUT}")


if __name__ == "__main__":
    main()