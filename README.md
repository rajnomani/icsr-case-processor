# icsr-case-processor

A small, fully checkable model of the first steps of handling an adverse event report (an ICSR, Individual Case Safety Report) in pharmacovigilance.

It takes 30 **fictional** cases and, using written rules from public sources, works out for each case:

1. Is it a **valid** report?
2. Is it **serious**?
3. Is the event **expected** (already on the drug's label)?
4. How likely is it that the drug **caused** the event (Naranjo score)?
5. A short **narrative**, written from a fixed template.

> All data is fictional: the cases, the two drugs (CRX-440 and LMV-120), the label and the causality answers are invented. This is a learning and portfolio project, not a medical or regulatory tool. See [docs/limits.md](docs/limits.md).

## Results on the 30 fictional cases

| Step | Result |
|---|---|
| Valid | 25 valid, 5 not valid (C007, C012, C018, C021, C025; each has one deliberately missing item) |
| Serious | 13 of the 25 valid cases |
| Expected | 12 expected, 13 unexpected |
| Serious and unexpected (priority HIGH) | 11 |
| Naranjo causality (13 serious cases) | 2 definite, 5 probable, 4 possible, 2 doubtful |

## The rules

| Step | Rule | Source |
|---|---|---|
| Valid | An identifiable reporter (type and country), an identifiable patient (initials, age or sex), a suspect drug and a suspected event are all present | EMA GVP Module VI, section VI.B.2 |
| Serious | At least one of: death, life threatening, hospitalised, disability, congenital anomaly, other important medical event | FDA IND safety reporting, 21 CFR 312.32 |
| Expected | A keyword for the event appears in the label list for that drug (`data/label.csv`) | this project's invented label |
| Causality | Ten Naranjo questions scored; 9 or more definite, 5 to 8 probable, 1 to 4 possible, 0 or less doubtful | Naranjo et al., 1981 |

## How it is checked

- `verify.py` recomputes validity, seriousness, expectedness and Naranjo scores with **SQL** (SQLite) and compares them with the output of the five scripts. It uses none of the code in `src/`.
- `run_all.py` runs the whole project **twice** and compares SHA-256 fingerprints of every output file, runs `verify.py`, then plants an error on purpose and confirms that `verify.py` fails, then restores the file.
- [docs/worked_examples.md](docs/worked_examples.md) works five cases through the rules by hand.

The checks show that two separate implementations of the same written rules agree. They do not show that the rules are clinically right.

## How to run it

You need Python 3. There is nothing to install: only Python's built-in tools are used.

```
git clone https://github.com/rajnomani/icsr-case-processor.git
cd icsr-case-processor
python3 run_all.py
```

You should see four PASS lines and `ALL CHECKS PASSED`.

To run one step at a time (from the project folder):

```
python3 src/validity.py
python3 src/seriousness.py
python3 src/expectedness.py
python3 src/causality.py
python3 src/narratives.py
python3 verify.py
```

## What is in the folders

```
data/       the 30 fictional cases, the invented label, the Naranjo answers
src/        one script per step
outputs/    the result files each step writes
docs/       worked examples and limits
verify.py   independent SQL check
run_all.py  runs everything twice, verifies, plants an error
```

## Limits

Short version: fictional data, keyword matching instead of MedDRA coding, no reporting deadlines, no duplicate detection, no follow-up versions. The full list is in [docs/limits.md](docs/limits.md).

## Author and licence

Raj Akil Nomani, MBBS. MIT licence (see `LICENSE`).