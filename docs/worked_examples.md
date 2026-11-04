# Five cases worked by hand

These five fictional cases from `data/cases.csv` are worked through the rules by hand, without the scripts. The script output for each one matches.

The rules are listed in the README. In short: a case is valid if it has an identifiable reporter, an identifiable patient, a suspect drug and a suspected event. It is serious if any of the six seriousness boxes is 1. It is expected if the event is on the drug's label (`data/label.csv`). Causality is the total of ten Naranjo answers.

## C007: not valid

| Field | Value |
|---|---|
| Reporter type, country | both blank |
| Patient | T.B., 46, F |
| Drug | CRX-440 |
| Event | swollen face and lips |

- Reporter: type and country are both blank, so there is **no identifiable reporter**.
- Patient, drug and event are all present.
- A case needs all four, so it is **not valid**.
- Seriousness, expectedness and causality are not assessed, and no narrative is written.

## C011: death, unexpected, doubtful

| Field | Value |
|---|---|
| Reporter | physician, India |
| Patient | G.T., 80, M |
| Drug | CRX-440 |
| Event | died suddenly at home |
| Seriousness boxes | death = 1 |

- **Valid:** all four criteria are present.
- **Serious:** death = 1.
- **Expected?** The CRX-440 label lists dizziness, nausea, vomiting, headache, diarrhoea and fatigue. "died suddenly at home" matches none of them, so it is **unexpected**.
- Serious and unexpected, so priority is **HIGH**.
- **Naranjo** answers: q1 no (0), q2 unknown (0), q3 unknown (0), q4 unknown (0), q5 yes (-1, another cause is possible), q6 unknown (0), q7 unknown (0), q8 unknown (0), q9 unknown (0), q10 no (0).
- Total: **-1**, which is 0 or less, so **doubtful**.

## C009: the highest score

| Field | Value |
|---|---|
| Reporter | physician, India |
| Patient | D.M., 35, M |
| Drug | CRX-440 |
| Event | anaphylaxis within 10 minutes of dose |
| Seriousness boxes | life threatening = 1, hospitalised = 1 |

- **Valid and serious** (two boxes).
- **Unexpected:** anaphylaxis is not on the CRX-440 label. Priority **HIGH**.
- **Naranjo:** q1 yes (+1), q2 yes (+2), q3 yes (+1), q4 yes (+2), q5 no (+2), q6 unknown (0), q7 unknown (0), q8 unknown (0), q9 yes (+1), q10 yes (+1).
- Total: 1 + 2 + 1 + 2 + 2 + 0 + 0 + 0 + 1 + 1 = **10**, which is 9 or more, so **definite**.

## C030: serious but expected

| Field | Value |
|---|---|
| Reporter | physician, India |
| Patient | R.T., 70, F |
| Drug | LMV-120 |
| Event | pancreatitis |
| Seriousness boxes | hospitalised = 1 |

- **Valid and serious.**
- **Expected:** the LMV-120 label lists pancreatitis. So this case is serious but **not** high priority.
- **Naranjo:** q1 yes (+1), q2 yes (+2), q3 yes (+1), q4 unknown (0), q5 no (+2), q6 to q9 unknown (0), q10 yes (+1).
- Total: **7**, which is 5 to 8, so **probable**.

## C003: the same word, a different answer by drug

| Field | Value |
|---|---|
| Reporter | physician, India |
| Patient | M.P., 41, F |
| Drug | CRX-440 |
| Event | severe skin rash with blisters |
| Seriousness boxes | hospitalised = 1 |

- **Valid and serious.**
- **Unexpected:** "rash" is on the label for LMV-120 but **not** for CRX-440, and this case is on CRX-440. Priority **HIGH**.
- **Naranjo:** q1 no (0), q2 yes (+2), q3 yes (+1), q4 unknown (0), q5 no (+2), q6 to q9 unknown (0), q10 yes (+1).
- Total: **6**, which is 5 to 8, so **probable**.

## What this shows

Each result above was worked out from the rules and the case row, then compared with `outputs/` from the scripts. All five matched. The scripts and the independent checker (`verify.py`) agree with the hand working. This does not show that the rules themselves are clinically right. See the limits page.