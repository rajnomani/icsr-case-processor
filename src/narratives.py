"""Step 5: write a short narrative for each valid case, from a fixed template.

Uses the results of steps 1 to 4. Every sentence comes from a fixed template
filled with the case's own data. Nothing is invented and nothing is guessed:
where a detail is missing the narrative says "unknown".

Reads data/cases.csv, data/label.csv and data/naranjo.csv.
Writes outputs/narratives.txt. Run from the project folder:

    python src/narratives.py
"""
import csv
from pathlib import Path

from validity import check_case
from seriousness import serious_criteria
from expectedness import load_label, find_listed_term
from causality import score, category

DATA = Path("data/cases.csv")
ANSWERS = Path("data/naranjo.csv")
OUT = Path("outputs/narratives.txt")

SEX = {"F": "female", "M": "male"}


def describe_patient(row):
    age = row["patient_age"].strip()
    sex = SEX.get(row["patient_sex"].strip().upper(), "")
    if age == "0":
        who = "an infant" + (f" ({sex})" if sex else "")
    elif age and sex:
        an = "an" if age.startswith("8") or age in ("11", "18") else "a"
        who = f"{an} {age}-year-old {sex} patient"
    elif age:
        who = f"a patient aged {age} (sex unknown)"
    elif sex:
        who = f"a {sex} patient (age unknown)"
    else:
        who = "a patient (age and sex unknown)"
    return who[0].upper() + who[1:]


def write_narrative(row, label, answers):
    drug = row["suspect_drug"].strip()
    reporter = row["reporter_type"].strip()
    article = "an" if reporter[0] in "aeiou" else "a"
    criteria = serious_criteria(row)
    term = find_listed_term(row, label)

    parts = [
        f"Case {row['case_id']}, received {row['receipt_date']}.",
        f"{describe_patient(row)} was reported by {article} {reporter} in "
        f"{row['reporter_country'].strip()}.",
        f"The suspect drug was {drug}.",
        f'The reported event was: "{row["event_verbatim"].strip()}".',
    ]
    if criteria:
        parts.append(f"The event was serious ({', '.join(criteria)}).")
    else:
        parts.append("The event was non-serious.")

    if term:
        parts.append(f'The event is listed on the label for {drug} as "{term}" (expected).')
    else:
        parts.append(f"The event is not listed on the label for {drug} (unexpected).")

    if criteria:
        total = score(answers[row["case_id"]])
        parts.append(f"Causality (Naranjo): {category(total)} (score {total}).")
    else:
        parts.append("Causality was not assessed (non-serious case).")

    if criteria and not term:
        parts.append("PRIORITY: HIGH (serious and unexpected).")
    return " ".join(parts)


def main():
    label = load_label()
    with open(DATA, newline="") as fh:
        cases = list(csv.DictReader(fh))
    with open(ANSWERS, newline="") as fh:
        answers = {r["case_id"]: r for r in csv.DictReader(fh)}

    narratives = [write_narrative(c, label, answers)
                  for c in cases if not check_case(c)]

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text("\n\n".join(narratives) + "\n")

    print(f"{len(narratives)} narratives written to {OUT}\n")
    for text in narratives[:2]:
        print(text + "\n")


if __name__ == "__main__":
    main()