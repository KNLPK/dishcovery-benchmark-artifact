# Integrity checks
- run 2026-10-15T03-32-12-987Z: 22500 rows, 250 payloads, iterations per cell = [np.int64(30)]
- run 2026-10-15T07-24-40-380Z: 22500 rows, 250 payloads, iterations per cell = [np.int64(30)]
- run 2026-10-15T07-44-09-929Z: 22500 rows, 250 payloads, iterations per cell = [np.int64(30)]
- largest within-payload heap sd across repeats: 0 B (0 = deterministic)
- distinct heap values per payload x format across runs: 1 (1 = identical in every run)
- distinct wire sizes per payload x format across runs: 1
- JSON wire bytes equal canonical byte length: True
- payloads by source x tier: generated/low=50, generated/medium=50, generated/high=50, spoonacular/low=100

# Main table (pooled over accepted runs)
| Tier | Format | KB mean (sd) | ms mean (sd) | MB mean (sd) | Size % | Time % | Alloc % |
|---|---|---|---|---|---|---|---|
| low | JSON | 5.20 (0.61) | 3.29 (0.50) | 0.209 (0.018) |  |  |  |
| low | MessagePack | 4.65 (0.60) | 1.75 (0.30) | 0.165 (0.043) | -10.7 | -46.8 | -21.0 |
| low | Protocol Buffers | 3.40 (0.48) | 1.31 (0.28) | 0.147 (0.043) | -34.6 | -60.2 | -29.6 |
| medium | JSON | 9.91 (0.40) | 6.35 (0.49) | 0.351 (0.010) |  |  |  |
| medium | MessagePack | 8.79 (0.43) | 2.73 (0.17) | 0.241 (0.006) | -11.3 | -57.0 | -31.4 |
| medium | Protocol Buffers | 7.10 (0.38) | 3.40 (0.32) | 0.368 (0.039) | -28.3 | -46.4 | +4.6 |
| high | JSON | 16.82 (1.15) | 10.86 (0.92) | 0.545 (0.037) |  |  |  |
| high | MessagePack | 15.03 (1.10) | 4.34 (0.31) | 0.386 (0.023) | -10.6 | -60.0 | -29.3 |
| high | Protocol Buffers | 12.52 (1.01) | 6.42 (0.70) | 0.708 (0.088) | -25.5 | -40.8 | +29.9 |

- protobuf materialisation overhead, low: +5.2%
- protobuf materialisation overhead, medium: +3.3%
- protobuf materialisation overhead, high: +3.2%

# Between-run stability of mean decode time
- largest between-run CV of a cell mean: 0.39%
- largest between-run spread of a % vs JSON figure: 0.27 percentage points

# Two-way ANOVA: log(metric) ~ format * tier (unit = payload)
- log_wire  C(format)          F(2,741) =      903.2, p = 2.03e-199, partial eta^2 = 0.709
- log_wire  C(tier)            F(2,741) =     8655.5, p = 0.00e+00, partial eta^2 = 0.959
- log_wire  C(format):C(tier)  F(4,741) =       12.8, p = 4.65e-10, partial eta^2 = 0.065
- log_ms    C(format)          F(2,741) =     3152.2, p = 0.00e+00, partial eta^2 = 0.895
- log_ms    C(tier)            F(2,741) =     6184.1, p = 0.00e+00, partial eta^2 = 0.943
- log_ms    C(format):C(tier)  F(4,741) =      184.4, p = 1.32e-109, partial eta^2 = 0.499
- log_heap  C(format)          F(2,741) =      201.0, p = 1.84e-70, partial eta^2 = 0.352
- log_heap  C(tier)            F(2,741) =     2846.5, p = 0.00e+00, partial eta^2 = 0.885
- log_heap  C(format):C(tier)  F(4,741) =      128.3, p = 3.25e-83, partial eta^2 = 0.409

# Mixed model check: log(metric) ~ format * tier + (1 | payload)
- log_ms: likelihood-ratio test of format x tier interaction, chi2(4) = 1191.3, p = 1.22e-256
- log_heap: likelihood-ratio test of format x tier interaction, chi2(4) = 700.9, p = 2.18e-150

# Paired comparison within tier: Protocol Buffers vs MessagePack (per payload)
- low    ms  : protobuf/msgpack = 0.742, t(149) =   -42.1, p = 1.5e-84, dz = -3.43, protobuf lower in 150/150 payloads
- low    heap: protobuf/msgpack = 0.884, t(149) =   -12.7, p = 1.4e-25, dz = -1.04, protobuf lower in 130/150 payloads
- medium ms  : protobuf/msgpack = 1.244, t(49) =    39.9, p = 5.3e-39, dz = +5.64, protobuf lower in 0/50 payloads
- medium heap: protobuf/msgpack = 1.518, t(49) =    31.0, p = 7.8e-34, dz = +4.38, protobuf lower in 0/50 payloads
- high   ms  : protobuf/msgpack = 1.475, t(49) =    66.5, p = 1.1e-49, dz = +9.41, protobuf lower in 0/50 payloads
- high   heap: protobuf/msgpack = 1.826, t(49) =    48.4, p = 5.1e-43, dz = +6.84, protobuf lower in 0/50 payloads

# Covariate: log(protobuf/msgpack) ~ log(JSON bytes)
- ms  : slope = 0.607, R^2 = 0.920, crossover at 8,190 B (95% bootstrap CI 8,054 to 8,327)
- heap: slope = 0.644, R^2 = 0.885, crossover at 6,088 B (95% bootstrap CI 5,940 to 6,233)
- largest Spoonacular payload: 7,108 B

# Heap allocation per byte of JSON input
- low   : JSON 40.3, MessagePack 31.4, Protocol Buffers 27.9
- medium: JSON 35.5, MessagePack 24.4, Protocol Buffers 37.0
- high  : JSON 32.4, MessagePack 23.0, Protocol Buffers 42.0

# Provenance control (low tier): Spoonacular vs generated
- MessagePack      ms  : spoonacular -45.6%, generated -49.2%
- MessagePack      heap: spoonacular -15.6%, generated -32.5%
- MessagePack      wire: spoonacular -9.2%, generated -13.9%
- Protocol Buffers ms  : spoonacular -60.4%, generated -59.8%
- Protocol Buffers heap: spoonacular -27.1%, generated -34.8%
- Protocol Buffers wire: spoonacular -34.8%, generated -34.3%
