# Limits: what this project does not do

This is a learning and portfolio project. It shows how the basic steps of handling an adverse event report can be written down as clear, checkable rules. It is **not** a medical, clinical or regulatory tool.

## The data is fictional
- All 30 cases, both drugs (CRX-440 and LMV-120), the drug label and the causality answers are invented.
- No real patient, drug or report is used. Do not put real patient data in this project.

## What each step does not do

**Validity.** It only checks that the four minimum fields are filled in. It does not check that the values make sense (an age of 300 would pass). The rules come from EMA GVP Module VI, section VI.B.2.

**Seriousness.** It uses the six yes/no boxes already filled in on each case. It does not judge seriousness from the text of the report, and it does not apply medical judgement to "other important medical event". The criteria follow the FDA IND safety reporting rules (21 CFR 312.32).

**Expectedness.** It matches keywords in the free text of the event against a tiny invented label.
- It can miss a synonym (for example "feeling sick" for nausea) and can match too loosely.
- Real systems compare coded MedDRA terms against the real reference safety information, such as a product's SmPC or Investigator's Brochure.

**Causality.** The ten Naranjo answers for each case are invented and stored in a file. The script only adds them up.
- It does not read a case and decide the answers.
- Naranjo is one of several methods. WHO-UMC categories are not implemented.
- Sources print the category edges slightly differently. This project uses 9 or more = definite and 0 or less = doubtful.

**Narratives.** They are filled in from a fixed template. They do not include onset dates, doses, treatment, outcome, medical history, other medicines or follow-up information, because the fictional data has none of these.

## What is not included at all
- Reporting deadlines (for example the 15-day rule for serious cases).
- Duplicate detection.
- MedDRA coding.
- Follow-up reports and case versions.
- Any electronic submission format (such as E2B).

## What the checks prove, and what they do not
- `run_all.py` shows that running the project twice gives identical files, and that the checker catches an error planted on purpose.
- `verify.py` recomputes the results with a separate method (SQL) and compares. It proves that two implementations of the **same written rules** agree.
- It does **not** prove that the rules are clinically right. The rules come from the public sources listed above.

## Sources
- EMA, Guideline on good pharmacovigilance practices (GVP), Module VI.
- FDA, IND safety reporting, 21 CFR 312.32.
- Naranjo CA et al., "A method for estimating the probability of adverse drug reactions", Clinical Pharmacology and Therapeutics, 1981.