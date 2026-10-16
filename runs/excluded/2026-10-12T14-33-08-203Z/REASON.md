# 2026-10-12T14-33-08-203Z (excluded)

Sentinel drift above the 5% limit: +28.36% (JSON), +28.23% (MessagePack),
+28.79% (Protocol Buffers) between the start and end sentinels. The device was
uniformly slower at the end of the run than at the start (the cause was not
measured), so the run is not comparable with the others. Its cell means are
higher across the board, for example medium-tier JSON 8.07 ms against about
6.35 ms in the clean runs.

Files: `aggregate.json` only. Raw CSV not exported. This run is not used in any
computation.

See ../../RUNS.md for timing, drift and the gap to the previous run and profile.
