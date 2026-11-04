"""Step 4: how likely is it that the drug caused the event? (Naranjo scale)

The Naranjo scale asks 10 questions. Each is answered yes / no / unknown and
scores points (yes, no, unknown):
    q1  Previous conclusive reports of this reaction?                  +1, 0, 0
    q2  Did the event appear after the drug was given?                 +2, -1, 0
    q3  Did it improve when the drug was stopped (or antagonist given)? +1, 0, 0
    q4  Did it come back when the drug was given again?                +2, -1, 0
    q5  Other causes that could on their own explain the event?        -1, +2, 0
    q6  Did it come back when a placebo was given?                     -1, +1, 0
    q7  Drug found in blood at toxic concentration?                    +1, 0, 0
    q8  Worse with higher dose / milder with lower dose?               +1, 0, 0
    q9  Similar reaction to the same or similar drug before?           +1, 0, 0
    q10 Confirmed by objective evidence (test, scan, biopsy)?          +1, 0, 0

Total score -> category:
    9 or more = definite    5 to 8 = probable    1 to 4 = possible
    0 or less = doubtful   (the scale's lowest possible score is -4)

The answers are FICTIONAL and stored in data/naranjo.csv. Every valid serious
case must have a row there; the script stops with an error if one is missing.

Reads data/cases.csv and data/naranjo.csv. Writes outputs/causality.csv.
Run from the project folder:

    python src/causality.py
"""
import csv
from pathlib import Path

from validity import check_case
from seriousness import serious_criteria

DATA = Path("data/cases.csv")
ANSWERS = Path("data/naranjo.csv")
OUT = Path("outputs/causality.csv")

# points for (yes, no, unknown)
POINTS = {
    "q1": (1, 0, 0),
    "q2": (2, -1, 0),
    "q3": (1, 0, 0),
    "q4": (2, -1, 0),
    "q5": (-1, 2, 0),
    "q6": (-1, 1, 0),
    "q7": (1, 0, 0),
    "q8": (1, 0, 0),
    "q9": (1, 0, 0),
    "q10": (1, 0, 0),
}
ANSWER_INDEX = {"yes": 0, "no": 1, "unknown": 2}


def score(answers):
    """Add up the Naranjo points for one case. Stops if an answer is not yes/no/unknown."""
    total = 0
    for question, points in POINTS.items():
        answer = answers[question].strip().lower()
        if answer not in ANSWER_INDEX:
            raise ValueError(f"{answers['case_id']} {question}: '{answer}' "
                             "is not yes, no or unknown")
        total += points[ANSWER_INDEX[answer]]
    return total


def category(total):
    if total >= 9:
        return "definite"
    if total >= 5:
        return "probable"
    if total >= 1:
        return "possible"
    return "doubtful"


def main():
    with open(DATA, newline="") as fh:
        cases = list(csv.DictReader(fh))
    with open(ANSWERS, newline="") as fh:
        answers = {r["case_id"]: r for r in csv.DictReader(fh)}

    needed = [c["case_id"] for c in cases if not check_case(c) and serious_criteria(c)]
    missing = [cid for cid in needed if cid not in answers]
    if missing:
        raise SystemExit(f"STOP: no Naranjo answers for: {', '.join(missing)}")

    results = []
    for cid in needed:
        total = score(answers[cid])
        results.append({"case_id": cid, "naranjo_score": total, "causality": category(total)})

    OUT.parent.mkdir(exist_ok=True)
    with open(OUT, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["case_id", "naranjo_score", "causality"])
        writer.writeheader()
        writer.writerows(results)

    print(f"{len(results)} serious valid cases scored\n")
    for r in results:
        print(f"{r['case_id']}  score {r['naranjo_score']:>2}  {r['causality']}")
    print(f"\nWrote {OUT}")


if __name__ == "__main__":
    main()