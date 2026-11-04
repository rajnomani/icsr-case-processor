"""Independent check of the whole pipeline.

This script does NOT use any of the code in src/. It loads the same input
files into a small SQL database (SQLite, built into Python), recomputes
validity, seriousness, expectedness and Naranjo scores with SQL, and compares
the answers with the output files that the five steps wrote.

Run steps 1 to 5 first, then, from the project folder:

    python verify.py
"""
import csv
import re
import sqlite3
from pathlib import Path

RESULTS = []


def read(path):
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def check(name, problems, n):
    """Record one check. 'problems' is a list of text lines describing mismatches."""
    status = "PASS" if not problems else "FAIL"
    RESULTS.append(status)
    print(f"{status}  {name}  ({n} compared)")
    for p in problems[:5]:
        print(f"        {p}")


# ---- load inputs into SQLite ------------------------------------------------
db = sqlite3.connect(":memory:")
cases = read("data/cases.csv")
cols = list(cases[0].keys())
db.execute(f"CREATE TABLE cases ({', '.join(c + ' TEXT' for c in cols)})")
db.executemany(f"INSERT INTO cases VALUES ({','.join('?' * len(cols))})",
               [[r[c] for c in cols] for r in cases])

db.execute("CREATE TABLE kw (drug TEXT, term TEXT, keyword TEXT, ord INTEGER)")
for i, r in enumerate(read("data/label.csv")):
    for k in r["keywords"].split(";"):
        db.execute("INSERT INTO kw VALUES (?,?,?,?)",
                   (r["drug"].strip(), r["listed_term"].strip(), k.strip().lower(), i))

db.execute("CREATE TABLE pts (q TEXT, a TEXT, p INTEGER)")
table = {"q1": (1, 0, 0), "q2": (2, -1, 0), "q3": (1, 0, 0), "q4": (2, -1, 0),
         "q5": (-1, 2, 0), "q6": (-1, 1, 0), "q7": (1, 0, 0), "q8": (1, 0, 0),
         "q9": (1, 0, 0), "q10": (1, 0, 0)}
for q, (y, n, u) in table.items():
    db.executemany("INSERT INTO pts VALUES (?,?,?)", [(q, "yes", y), (q, "no", n), (q, "unknown", u)])

nar = read("data/naranjo.csv")
db.execute("CREATE TABLE nar (case_id TEXT, q TEXT, a TEXT)")
for r in nar:
    for q in table:
        db.execute("INSERT INTO nar VALUES (?,?,?)", (r["case_id"], q, r[q].strip().lower()))

# ---- recompute with SQL -----------------------------------------------------
SQL_VALID = """
  SELECT case_id,
    CASE WHEN trim(reporter_type)<>'' AND trim(reporter_country)<>''
          AND (trim(patient_initials)<>'' OR trim(patient_age)<>'' OR trim(patient_sex)<>'')
          AND trim(suspect_drug)<>'' AND trim(event_verbatim)<>''
         THEN 'yes' ELSE 'no' END AS valid,
    (death='1')+(life_threatening='1')+(hospitalised='1')+(disability='1')
      +(congenital_anomaly='1')+(other_important='1') AS n_criteria
  FROM cases"""
valid = {r[0]: (r[1], r[2]) for r in db.execute(SQL_VALID)}

expected = {}
for cid, term in db.execute("""
    SELECT c.case_id,
      (SELECT k.term FROM kw k WHERE k.drug = trim(c.suspect_drug)
         AND instr(lower(c.event_verbatim), k.keyword) > 0
       ORDER BY k.ord LIMIT 1)
    FROM cases c"""):
    expected[cid] = term or ""

naranjo = {}
for cid, total in db.execute("""
    SELECT n.case_id, SUM(p.p) FROM nar n JOIN pts p ON p.q = n.q AND p.a = n.a
    GROUP BY n.case_id"""):
    naranjo[cid] = total


def cat(t):
    return "definite" if t >= 9 else "probable" if t >= 5 else "possible" if t >= 1 else "doubtful"


valid_ids = [c for c, (v, _) in valid.items() if v == "yes"]
serious_ids = [c for c in valid_ids if valid[c][1] > 0]
high_ids = [c for c in serious_ids if not expected[c]]

# ---- compare with the output files ------------------------------------------
# 1 validity
probs = []
rows = read("outputs/validity.csv")
for r in rows:
    if r["valid"] != valid[r["case_id"]][0]:
        probs.append(f"{r['case_id']}: file says valid={r['valid']}, SQL says {valid[r['case_id']][0]}")
if len(rows) != len(cases):
    probs.append(f"file has {len(rows)} rows, expected {len(cases)}")
check("validity.csv", probs, len(rows))

# 2 seriousness
probs = []
rows = read("outputs/seriousness.csv")
for r in rows:
    v, n = valid[r["case_id"]]
    want = "not assessed" if v == "no" else ("yes" if n > 0 else "no")
    got_n = len([x for x in r["criteria"].split(";") if x.strip()])
    if r["serious"] != want:
        probs.append(f"{r['case_id']}: file says serious={r['serious']}, SQL says {want}")
    elif v == "yes" and got_n != n:
        probs.append(f"{r['case_id']}: file lists {got_n} criteria, SQL counts {n}")
check("seriousness.csv", probs, len(rows))

# 3 expectedness
probs = []
rows = read("outputs/expectedness.csv")
for r in rows:
    if valid[r["case_id"]][0] == "no":
        if r["expected"] != "not assessed":
            probs.append(f"{r['case_id']}: invalid case should be 'not assessed'")
        continue
    want_exp = "yes" if expected[r["case_id"]] else "no"
    want_pri = "HIGH" if r["case_id"] in high_ids else ""
    if r["expected"] != want_exp or r["listed_term"] != expected[r["case_id"]]:
        probs.append(f"{r['case_id']}: file expected={r['expected']}/{r['listed_term']}, "
                     f"SQL says {want_exp}/{expected[r['case_id']]}")
    if r["priority"] != want_pri:
        probs.append(f"{r['case_id']}: file priority='{r['priority']}', SQL says '{want_pri}'")
check("expectedness.csv", probs, len(rows))

# 4 causality
probs = []
rows = read("outputs/causality.csv")
if sorted(r["case_id"] for r in rows) != sorted(serious_ids):
    probs.append("the cases scored are not the same as the valid serious cases")
for r in rows:
    t = naranjo.get(r["case_id"])
    if t is None or int(r["naranjo_score"]) != t or r["causality"] != cat(t):
        probs.append(f"{r['case_id']}: file says {r['naranjo_score']}/{r['causality']}, "
                     f"SQL says {t}/{cat(t) if t is not None else '?'}")
check("causality.csv", probs, len(rows))

# 5 narratives
probs = []
text = Path("outputs/narratives.txt").read_text()
paras = [p for p in text.split("\n\n") if p.strip()]
by_id = {}
for p in paras:
    m = re.match(r"Case (C\d+),", p)
    by_id.setdefault(m.group(1) if m else "?", []).append(p)
if sorted(by_id) != sorted(valid_ids) or any(len(v) != 1 for v in by_id.values()):
    probs.append("narratives are not exactly one per valid case")
for cid in valid_ids:
    p = by_id.get(cid, [""])[0]
    if cid in serious_ids:
        want = f"Causality (Naranjo): {cat(naranjo[cid])} (score {naranjo[cid]})."
        if want not in p:
            probs.append(f"{cid}: narrative lacks '{want}'")
    if bool(expected[cid]) != ("(expected)" in p and "(unexpected)" not in p):
        probs.append(f"{cid}: narrative expectedness disagrees with SQL")
    if ("PRIORITY: HIGH" in p) != (cid in high_ids):
        probs.append(f"{cid}: narrative priority disagrees with SQL")
check("narratives.txt", probs, len(valid_ids))

# ---- summary ----------------------------------------------------------------
failed = RESULTS.count("FAIL")
print(f"\n{len(RESULTS) - failed} of {len(RESULTS)} CHECKS PASSED" if not failed
      else f"\n{failed} of {len(RESULTS)} CHECKS FAILED")
raise SystemExit(1 if failed else 0)