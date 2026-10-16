"""Re-fetch the 100 Spoonacular recipes used in the study, by ID.

The raw payloads are not distributed with this package (see dataset/DATASET.md).
This script downloads them again from the Spoonacular API with your own key.

Usage:
    set SPOONACULAR_API_KEY=...        (Windows)
    export SPOONACULAR_API_KEY=...     (macOS / Linux)
    python dataset/spoonacular/refetch.py [output_dir]

It calls GET /recipes/{id}/information?includeNutrition=true for every ID in
recipe_ids.csv (the same request the benchmark proxy made) and writes each
response body unchanged to <output_dir>/<id>.json. The default output_dir is
dataset/spoonacular/raw/, which is not part of the package.

Notes:
- The key is read from the environment only. It is never written to disk or
  printed.
- Each request costs about 1 Spoonacular quota point; 100 recipes need a plan
  with at least that much daily quota.
- Spoonacular content can change after the original capture (2026-09-09), so a
  re-fetched body may not match the bytes used in the study. The study did not
  decode these raw bodies directly: the proxy reduced each one to the fields in
  recipe.proto before encoding, and json_bytes in recipe_ids.csv is the size of
  that reduced JSON, not of the raw response.
"""

import csv
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
URL = "https://api.spoonacular.com/recipes/{id}/information?includeNutrition=true"
DELAY_S = 0.3


def main() -> int:
    key = os.environ.get("SPOONACULAR_API_KEY", "").strip()
    if not key:
        print("SPOONACULAR_API_KEY is not set.", file=sys.stderr)
        return 2

    out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "raw"
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(HERE / "recipe_ids.csv", newline="") as f:
        ids = [row["recipeId"] for row in csv.DictReader(f)]

    failed = []
    for n, recipe_id in enumerate(ids, 1):
        target = out_dir / f"{recipe_id}.json"
        if target.exists():
            print(f"[{n}/{len(ids)}] {recipe_id}: already present, skipped")
            continue
        req = urllib.request.Request(URL.format(id=recipe_id), headers={"x-api-key": key})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                target.write_bytes(resp.read())
            print(f"[{n}/{len(ids)}] {recipe_id}: ok")
        except urllib.error.HTTPError as e:
            failed.append(recipe_id)
            print(f"[{n}/{len(ids)}] {recipe_id}: HTTP {e.code}")
        except urllib.error.URLError as e:
            failed.append(recipe_id)
            print(f"[{n}/{len(ids)}] {recipe_id}: {e.reason}")
        time.sleep(DELAY_S)

    print(f"done: {len(ids) - len(failed)} of {len(ids)} present in {out_dir}")
    if failed:
        print("failed: " + ", ".join(failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
