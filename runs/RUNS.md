# Runs

Every benchmark run made on the study device with the final build, and what
happened to it. The paper's numbers come only from the three runs marked
**final**. All times are UTC. A run takes about three and a half minutes:
200 pre-warm decodes per format, then 250 payloads x 3 formats x (10 warm-up +
30 measured) decodes.

The runId is the run's start time and is also the name of its folder. Status
was assigned by matching the runId stored inside each file, not the file name.

## Table

Drift is the change in mean decode time of a fixed sentinel payload (150
decodes per format) between the start and the end of the run, listed as
JSON / MessagePack / Protocol Buffers. The limit is 5%. "Start sentinel" is the
JSON mean of the opening sentinel, which is the check for carry-over from
whatever ran before.

| runId | Status | Date | Start | End | Sentinel drift % (J / M / P) | Start sentinel JSON ms | Gap to previous run | Gap to previous profile | CSV |
|---|---|---|---|---|---|---|---|---|---|
| 2026-10-12T13-54-39-691Z | replication | 2026-10-12 | 13:54:39 | 13:57:36 | -0.21 / -0.29 / -0.44 | 6.137 | none that day | 25 s (json-first cold) | no |
| 2026-10-12T14-08-51-679Z | replication | 2026-10-12 | 14:08:51 | 14:11:47 | +0.84 / +0.62 / +0.36 | 6.074 | 675 s (after 13-54-39) | 640 s (msgpack-first cold) | no |
| 2026-10-12T14-33-08-203Z | excluded | 2026-10-12 | 14:33:08 | 14:37:35 | +28.36 / +28.23 / +28.79 | 6.165 | 1,280 s (after 14-08-51) | 1,146 s (protobuf-first cold) | no |
| 2026-10-15T02-39-22-117Z | excluded | 2026-10-15 | 02:39:22 | 02:43:54 | -0.41 / -0.75 / +0.02 | 6.155 | 60.0 h (after 14-33-08) | 21 s (json-first cold) | no |
| 2026-10-15T02-54-12-419Z | replication | 2026-10-15 | 02:54:12 | 02:57:30 | +0.19 / -0.59 / -1.09 | 6.282 | 618 s (after 02-39-22) | 5 s (msgpack-first cold) | no |
| 2026-10-15T03-08-03-075Z | replication | 2026-10-15 | 03:08:03 | 03:11:10 | +1.14 / +1.00 / +1.53 | 6.094 | 633 s (after 02-54-12) | 30 s (protobuf-first cold) | no |
| 2026-10-15T03-22-13-583Z | excluded | 2026-10-15 | 03:22:13 | 03:25:55 | +0.22 / +0.49 / +0.20 | 6.111 | 663 s (after 03-08-03) | 20 s (per-cell, see note 3) | no |
| 2026-10-15T03-32-12-987Z | **final** | 2026-10-15 | 03:32:12 | 03:35:36 | +0.11 / +0.67 / +0.30 | 6.120 | **377 s** (after 03-22-13, see note 1) | 620 s (per-cell, see note 3) | yes |
| 2026-10-15T07-24-40-380Z | **final** | 2026-10-15 | 07:24:40 | 07:27:46 | +0.49 / +1.12 / +1.11 | 6.140 | 3.8 h (after 03-32-12) | 6 s (msgpack-first cold, see note 2) | yes |
| 2026-10-15T07-44-09-929Z | **final** | 2026-10-15 | 07:44:09 | 07:47:07 | +0.21 / +0.10 / +0.46 | 6.116 | 984 s (after 07-24-40) | 6 s (protobuf-first cold) | yes |

Gaps are measured from the end of the previous run, or the end of the previous
profile, to the start of this run. A cold profile's stored `startedAt` is
written when the profile finishes, so it is used as the profile's end time.

## Status rules

**final.** Three runs from one day, as planned. Only these are pooled, and only
their CSVs are read by `analysis/analyze.py`.

**replication.** Clean runs on the same build that were not pooled. Only three
runs were planned, so the extra clean runs are kept as a check, not added to
the pool. Two of them are from 2026-10-12. The plan pooled three runs from one
day, so runs from another day are replication runs whatever their quality.
That, not the short gap after a cold profile, is why 2026-10-12T13-54-39-691Z
is not final: the final runs have the same kind of gap.

**excluded.** Runs with a measured problem. Each folder has a `REASON.md`.

| runId | Reason |
|---|---|
| 2026-10-15T02-39-22-117Z | One Protocol Buffers decode in the high tier stalled for about 40 s. That cell's mean is 35.38 ms with sd 1,101.77 ms, against about 6.4 ms (sd about 0.7) in every other run. An OS-level interruption, not a property of the format. |
| 2026-10-15T03-22-13-583Z | Repeated timing spikes in the medium tier: JSON sd 4.30 ms against 0.37 to 0.65 ms in the clean runs, with MessagePack and Protocol Buffers affected the same way. |
| 2026-10-12T14-33-08-203Z | Sentinel drift of about +28% in all three formats, far above the 5% limit. |

## Cooldown

The protocol puts at least 10 minutes between benchmark runs. A cold profile is
not treated as a run: it is about 450 decodes of one payload and lasts about
25 s. The app's own cooldown check does count profiles as activity, so it marks
several runs "inside cooldown". Their start sentinels (JSON 6.07 to 6.28 ms
across all ten runs, 6.116 to 6.140 ms for the three final runs) show no
carry-over from the profile that preceded them.

Notes on individual gaps:

1. **2026-10-15T03-32-12-987Z started 377 s after the excluded run
   2026-10-15T03-22-13-583Z finished**, which is less than the 10 minutes the
   protocol sets between runs. The app's cooldown record for this run names the
   per-cell profile (ended 03:21:53, 620 s earlier) as the previous activity and
   does not mention the 03:22 run, so the app did not flag it. Its start
   sentinel (JSON 6.120 ms) and drift (+0.11 / +0.67 / +0.30%) are in line with
   the other clean runs. This is recorded here as it happened. It was not
   adjusted.
2. The cold profile that ended 6 s before 2026-10-15T07-24-40-380Z
   (msgpack-first, ended 07:24:34.782) is known only from the run's cooldown
   record. Its file was not exported. The msgpack-first profile in
   `profiles/` from that afternoon is an earlier one (ended 07:11:27), 793 s
   before the run.
3. The per-cell profile's end time (03:21:53.369) comes from the cooldown
   records of the 03:22 and 03:32 runs. No export of that profile exists; see
   below.

## Files per run

- final: `run_<runId>.csv` (22,500 rows each) and `aggregate.json`.
- replication and excluded: `aggregate.json` only. The raw CSV was not
  exported for these runs. They are not used in any computation, so nothing in
  the paper depends on the missing CSVs.

All CSV and JSON files are byte-identical to the files exported from the app
(see `CHECKSUMS.sha256`). `MANIFEST.md` is the note written when the files
were exported. Where it differs from this file on a timing detail, the values
here were computed from the files themselves.

## Warm-up profiles (`profiles/`)

| File | Lead | Ended (UTC) | Used for |
|---|---|---|---|
| cold_json-first_2026-10-15T02-39-01Z.json | json | 2026-10-15 02:39:01 | paper's warm-up verification |
| cold_msgpack-first_2026-10-15T02-54-07Z.json | msgpack | 2026-10-15 02:54:07 | paper's warm-up verification |
| cold_protobuf-first_2026-10-15T03-07-33Z.json | protobuf | 2026-10-15 03:07:33 | paper's warm-up verification |
| per-cell_2026-10-15/ (2 screenshots) | per-cell | about 03:21:53 | paper's per-cell warm-up check |
| cold_msgpack-first_2026-10-15T07-11-27Z.json | msgpack | 2026-10-15 07:11:27 | supplementary |
| cold_protobuf-first_2026-10-15T07-44-03Z.json | protobuf | 2026-10-15 07:44:03 | supplementary |
| cold_json-first_2026-10-12T13-54-14Z.json | json | 2026-10-12 13:54:14 | supplementary |
| cold_msgpack-first_2026-10-12T13-58-11Z.json | msgpack | 2026-10-12 13:58:11 | supplementary |
| cold_protobuf-first_2026-10-12T14-14-02Z.json | protobuf | 2026-10-12 14:14:02 | supplementary |

Each cold profile decodes one high-tier payload 150 times per format, in three
orderings (one per leading format, each from a freshly launched app), and finds
when the timing settles. `analysis/warmup/verify_warmup.ts` recombines them:

- 2026-10-15 morning: engine requirement 20 decodes (robust rule), 140 (strict
  rule). The configured pre-warm is 200, which covers both.
- 2026-10-12: 40 (robust), 140 (strict). Also covered by 200.

**Per-cell profile: screenshots only.** The app recorded the per-cell profile
but it was never exported, so the two screenshots in `per-cell_2026-10-15/`
are the only record. They show a measured per-cell requirement of 10, equal to
the configured `warmupIterations` of 10, and a residual bias at W = 10 of
+0.140% (JSON), -0.030% (MessagePack) and +0.208% (Protocol Buffers), all
within the 0.5% limit. These figures cannot be recomputed from data in this
package.

**Known app issue.** Every aggregate reports `warmupSufficiency.verdict` as
"unverified". When each run started, the app read only one cold profile instead
of all three, so it never saw a complete set. The verification above is
computed from the profile files, not taken from that field.
