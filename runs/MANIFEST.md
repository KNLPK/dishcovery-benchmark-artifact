# dishcovery-raw: manifest

All files were exported from the Dishcovery app (release APK, build after the expo-image fix,
Infinix X6871, Android 15). The files have been renamed by the runId / profile start time recorded inside them.
Their contents are unchanged.

## Runs

| runId | Status | CSV | Note |
|---|---|---|---|
| 2026-10-15T03-32-12-987Z | final | yes | began 620 s after the per-cell profile and about 6 min after excluded run 03-22; starting sentinel matches other runs within 0.5% |
| 2026-10-15T07-24-40-380Z | final | yes | began 6 s after a short cold profile (msgpack-first); about 3.6 h after the previous run |
| 2026-10-15T07-44-09-929Z | final | yes | began 6 s after a short cold profile (protobuf-first); 16 min after the previous run |
| 2026-10-15T02-54-12-419Z | replication | aggregate only | clean; began 5 s after a cold profile |
| 2026-10-15T03-08-03-075Z | replication | aggregate only | clean; began 30 s after a cold profile |
| 2026-10-12T14-08-51-679Z | replication (other day) | aggregate only | clean |
| 2026-10-12T13-54-39-691Z | replication (other day) | aggregate only | clean; began 25 s after a cold profile |
| 2026-10-15T02-39-22-117Z | excluded | aggregate only | one protobuf high-tier decode stalled about 40 s (cell mean 35.4 ms, sd 1,101 ms) |
| 2026-10-15T03-22-13-583Z | excluded | aggregate only | repeated timing spikes in the medium tier (JSON sd 4.3 ms vs about 0.4) |
| 2026-10-12T14-33-08-203Z | excluded | aggregate only | sentinel drift +28%, above the 5% limit |

Replication runs are not pooled with the final runs because only three runs were planned. Their status
is not caused by the cold-profile proximity, which the final runs share.

### Cooldown rule
The 10-minute cooldown applies between benchmark runs. A cold profile is about 450 decodes of one
payload and lasts about 25 s, so it is not treated as a run. The app's cooldown field counts profiles as
activity and therefore flags several runs as "inside cooldown"; their start-of-run sentinels
(JSON 6.09 to 6.15 ms) show no carry-over.

## Warm-up profiles
- 2026-10-15 morning: json-first 02:39, msgpack-first 02:54, protobuf-first 03:07. These are the
  profiles used for verification: engine requirement robust 20 / strict 140, against a prewarm of 200.
- 2026-10-15 afternoon: msgpack-first 07:11, protobuf-first 07:44 (supplementary).
- 2026-10-12: json-first, msgpack-first, protobuf-first (supplementary).
- Per-cell profile 2026-10-15 ~03:22Z: screenshots only. The app recorded it, but no export is available.
  Requirement 10 equals the configured value of 10; residual bias at W=10 is 0.14 / -0.03 / 0.21%,
  within the 0.5% limit.
- Known app issue: each run reads only the most recent cold profile, so every aggregate reports
  warmupSufficiency "unverified". The verification above is computed from the profile files.

## Analysis
analysis/analyze.py reads the three final CSVs. analysis/output/ is the reference output; a
fresh run must reproduce report.md exactly.
