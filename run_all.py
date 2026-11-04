"""Run the whole project, prove it repeats exactly, and prove the checker works.

What this does, in order:
  1. Runs steps 1 to 5 and fingerprints (SHA-256) every output file.
  2. Runs steps 1 to 5 again and compares the fingerprints. Same input must
     give identical output.
  3. Runs verify.py. It must pass.
  4. PLANTED ERROR: changes one result in outputs/causality.csv, runs verify.py,
     and checks that verify.py FAILS. Then it puts the file back and checks that
     verify.py passes again.

Run from the project folder:

    python run_all.py
"""
import hashlib
import subprocess
import sys
from pathlib import Path

STEPS = ["validity", "seriousness", "expectedness", "causality", "narratives"]
OUTPUTS = ["validity.csv", "seriousness.csv", "expectedness.csv",
           "causality.csv", "narratives.txt"]
PROBLEMS = []


def run(args):
    return subprocess.run([sys.executable] + args, capture_output=True, text=True)


def run_steps():
    for step in STEPS:
        result = run([f"src/{step}.py"])
        if result.returncode != 0:
            print(result.stdout + result.stderr)
            raise SystemExit(f"STOP: src/{step}.py failed")


def fingerprints():
    return {name: hashlib.sha256(Path("outputs", name).read_bytes()).hexdigest()
            for name in OUTPUTS}


def report(label, ok, detail=""):
    print(f"{'PASS' if ok else 'FAIL'}  {label}" + (f"  {detail}" if detail else ""))
    if not ok:
        PROBLEMS.append(label)


# 1 and 2: run twice, compare
run_steps()
first = fingerprints()
run_steps()
second = fingerprints()
same = [n for n in OUTPUTS if first[n] == second[n]]
report("run twice, identical output", len(same) == len(OUTPUTS),
       f"({len(same)} of {len(OUTPUTS)} files identical)")
for name in OUTPUTS:
    print(f"        {name:18} {first[name][:16]}")

# 3: verify must pass
result = run(["verify.py"])
report("verify.py passes on the real outputs", result.returncode == 0)

# 4: planted error
path = Path("outputs/causality.csv")
original = path.read_bytes()   # exact bytes, so the file can be put back unchanged
target, wrong = b"C009,10,definite", b"C009,10,probable"
if target not in original:
    report("planted error", False, f"could not find '{target.decode()}' to change")
else:
    try:
        path.write_bytes(original.replace(target, wrong))
        result = run(["verify.py"])
        caught = result.returncode != 0 and "FAIL  causality.csv" in result.stdout
        report("planted error is caught by verify.py", caught,
               "(changed C009 definite -> probable)")
    finally:
        path.write_bytes(original)
    result = run(["verify.py"])
    report("file restored, verify.py passes again", result.returncode == 0)