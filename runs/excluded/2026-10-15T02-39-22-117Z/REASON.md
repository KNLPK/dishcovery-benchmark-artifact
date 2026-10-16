# 2026-10-15T02-39-22-117Z (excluded)

One Protocol Buffers decode in the high tier stalled for about 40 s. In
`aggregate.json` the high-tier Protocol Buffers cell has mean 35.38 ms and sd
1,101.77 ms; in every other run that cell is about 6.4 ms with sd about 0.7 ms.
The stall is an OS-level interruption, not a property of the format, but it
makes this run's high-tier figures unusable. Sentinel drift was within limits
(-0.41 / -0.75 / +0.02%).

Files: `aggregate.json` only. Raw CSV not exported. This run is not used in any
computation.

See ../../RUNS.md for timing, drift and the gap to the previous run and profile.
