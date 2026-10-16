"""Check that the analysis reproduces the numbers the paper was written from.

Usage (from the package root, with requirements.txt installed):
    python analysis/verify.py

Runs analysis/analyze.py on the final runs into a temporary folder, then
compares the result with analysis/reference_output/:

- every CSV numerically: same columns, same rows, same text in non-numeric
  cells, and every number equal within a relative tolerance of 1e-9 (enough to
  absorb last-digit floating-point differences between platforms, far tighter
  than anything printed in the paper);
- report.md as text, after normalising line endings.

Prints one line per file and ends with PASS or FAIL. Exit code 0 on PASS.
"""

import math
import subprocess
import sys
import tempfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
REFERENCE = ROOT / "analysis" / "reference_output"
RTOL = 1e-9


def same_number(a, b) -> bool:
    if pd.isna(a) and pd.isna(b):
        return True
    if pd.isna(a) or pd.isna(b):
        return False
    return math.isclose(float(a), float(b), rel_tol=RTOL, abs_tol=0.0)


def compare_csv(new: Path, ref: Path) -> list[str]:
    # Read as text so that numeric and non-numeric cells are both compared
    # exactly as written, then parse numbers cell by cell.
    a = pd.read_csv(new, dtype=str, keep_default_na=False)
    b = pd.read_csv(ref, dtype=str, keep_default_na=False)
    if list(a.columns) != list(b.columns):
        return [f"columns differ: {list(a.columns)} vs {list(b.columns)}"]
    if a.shape != b.shape:
        return [f"shape differs: {a.shape} vs {b.shape}"]
    problems = []
    for col in a.columns:
        for i, (x, y) in enumerate(zip(a[col], b[col])):
            if x == y:
                continue
            try:
                fx, fy = float(x), float(y)
            except ValueError:
                problems.append(f"row {i + 2}, {col}: '{x}' vs '{y}'")
                continue
            if not same_number(fx, fy):
                problems.append(f"row {i + 2}, {col}: {x} vs {y}")
    return problems


def compare_text(new: Path, ref: Path) -> list[str]:
    a = new.read_text(encoding="utf-8").replace("\r\n", "\n").splitlines()
    b = ref.read_text(encoding="utf-8").replace("\r\n", "\n").splitlines()
    if a == b:
        return []
    problems = [f"line {i + 1}: {x!r} vs {y!r}" for i, (x, y) in enumerate(zip(a, b)) if x != y]
    if len(a) != len(b):
        problems.append(f"{len(a)} lines vs {len(b)} in the reference")
    return problems


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        print("Regenerating output from runs/final ...")
        run = subprocess.run(
            [sys.executable, str(ROOT / "analysis" / "analyze.py"), str(ROOT / "runs" / "final"), str(out)],
            capture_output=True,
            text=True,
        )
        if run.returncode != 0:
            print(run.stderr)
            print("FAIL: analyze.py did not finish")
            return 1

        failed = False
        for ref in sorted(REFERENCE.iterdir()):
            new = out / ref.name
            if not new.exists():
                problems = ["not produced"]
            elif ref.suffix == ".csv":
                problems = compare_csv(new, ref)
            else:
                problems = compare_text(new, ref)
            status = "ok" if not problems else "DIFFERS"
            print(f"  {status:8s} {ref.name}")
            for p in problems[:10]:
                print(f"           {p}")
            if len(problems) > 10:
                print(f"           ... and {len(problems) - 10} more")
            failed = failed or bool(problems)

        extra = sorted({p.name for p in out.iterdir()} - {p.name for p in REFERENCE.iterdir()})
        if extra:
            print(f"  note: produced but not in the reference: {', '.join(extra)}")

    print("FAIL" if failed else "PASS")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
