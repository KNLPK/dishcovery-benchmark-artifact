# 2026-10-15T03-22-13-583Z (excluded)

Repeated timing spikes in the medium tier. In `aggregate.json` the medium-tier
JSON cell has sd 4.30 ms (mean 6.95 ms) against 0.37 to 0.65 ms (mean about
6.35 ms) in the clean runs, and MessagePack (sd 2.06 ms) and Protocol Buffers
(sd 2.44 ms) are affected the same way. Sentinel drift was within limits
(+0.22 / +0.49 / +0.20%), so the spikes were confined to part of the run.

Files: `aggregate.json` only. Raw CSV not exported. This run is not used in any
computation.

See ../../RUNS.md for timing, drift and the gap to the previous run and profile.
