/**
 * Recompute the engine warm-up requirement from the stored cold profiles.
 *
 * Usage (Node 22.6 or later, no packages needed):
 *   node --experimental-strip-types analysis/warmup/verify_warmup.ts
 *
 * warmupRules.ts is a byte-identical copy of src/bench/warmupRules.ts from the
 * app at the build commit (see environment.md). It only has type imports, so
 * Node can run it with type stripping and nothing else from the app is needed.
 *
 * For each set of three cold profiles (one per leading format) it prints the
 * robust and strict requirement, the pre-warm that requirement implies at 2x
 * headroom, and whether any ordering is missing or never settled.
 */

import * as fs from 'node:fs';
import * as path from 'node:path';

import { coldEvidenceGaps, combineProfileReports } from './warmupRules.ts';

const PROFILES = path.join(import.meta.dirname, '..', '..', 'runs', 'profiles');
const FORMATS = ['json', 'msgpack', 'protobuf'] as const;
const CONFIGURED = { warmupIterations: 10, prewarmDecodes: 200 };

const SETS: Record<string, string[]> = {
  '2026-10-15 morning (used in the paper)': [
    'cold_json-first_2026-10-15T02-39-01Z.json',
    'cold_msgpack-first_2026-10-15T02-54-07Z.json',
    'cold_protobuf-first_2026-10-15T03-07-33Z.json',
  ],
  '2026-10-12 (supplementary)': [
    'cold_json-first_2026-10-12T13-54-14Z.json',
    'cold_msgpack-first_2026-10-12T13-58-11Z.json',
    'cold_protobuf-first_2026-10-12T14-14-02Z.json',
  ],
};

for (const [name, files] of Object.entries(SETS)) {
  // Each exported file holds exactly one cold profile in reports[0].
  const reports = files.map((f) => JSON.parse(fs.readFileSync(path.join(PROFILES, f), 'utf8')).reports[0]);
  const series = combineProfileReports(reports, FORMATS, CONFIGURED);
  const gaps = coldEvidenceGaps(series);

  console.log(`\n${name}`);
  console.log(`  robust requirement : ${series.coldRequirement} decodes`);
  console.log(`  strict requirement : ${series.coldRequirementStrict} decodes`);
  console.log(`  implied pre-warm   : ${series.recommendedPrewarm} (configured ${CONFIGURED.prewarmDecodes})`);
  console.log(`  evidence gaps      : ${gaps.length === 0 ? 'none' : gaps.join('; ')}`);
  console.log('  format    cold robust/strict   max robust/strict');
  for (const f of series.perFormat) {
    console.log(
      `  ${f.format.padEnd(9)} ${`${f.coldRecommended}/${f.coldStrict}`.padStart(19)}` +
        `${`${f.maxRecommended}/${f.maxStrict}`.padStart(20)}`
    );
  }
}
