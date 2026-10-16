# Environment

The device and build values below are copied from the `environment` block that
the app writes into every run's `aggregate.json`. That block is identical in
all ten runs in `runs/`, including the 2026-10-12 runs, so every run used the
same build on the same device.

## Device

| | |
|---|---|
| Device | Infinix X6871 (brand Infinix) |
| OS | Android 15, API level 35 |

## Build

| | |
|---|---|
| App | Dishcovery (Android), version 1.0.0 |
| App commit | `bba2d0210145ea0e7df297f023bc457fc0077af6` (2026-10-12, "Exclude expo-image from native autolinking (prebuilt AAR ABI mismatch)") |
| Build | EAS Build, profile `preview`: Android release APK (`:app:assembleRelease`), internal distribution |
| Build type (as recorded) | `release` |
| Execution environment | `bare`, with the JavaScript bundle embedded and precompiled to Hermes bytecode (no dev server) |
| APK SHA-256 | `70d9a95e69ec1904193745f99e14fa08e819be33544fd2c4f6fe407c30f83eaa` |

The APK hash is of `base.apk` pulled from the study phone with `adb pull` on
2026-10-12, after the app was installed at 2026-10-12 20:39:30 (device time,
UTC+7). The phone reported the same install and update time on 2026-10-15 at
09:36 (UTC+7), shortly before that day's runs, so the app was not reinstalled
in between. This is the installed APK, not the file downloaded from EAS. The
two should be the same file, but that was not checked.

## JavaScript runtime

| | |
|---|---|
| Engine | Hermes (`isHermes: true`) |
| React Native | 0.79.2 |
| Hermes version | "for RN 0.79.2" |
| Hermes build | Release |
| Bytecode version | 96 |
| Garbage collector | hades (concurrent) |
| Debugger enabled | false |
| Builtins frozen | false |
| VM experiments | 0 |
| CommonJS modules | None |
| Expo SDK | 53.0.0 (`expo` package 53.0.27) |
| Heap statistic used | `js_totalAllocatedBytes` from `HermesInternal.getInstrumentedStats()` |

## Serialization libraries

| Format | Decode call | Library version |
|---|---|---|
| JSON | `TextDecoder` (UTF-8) then `JSON.parse`, both built into Hermes | (engine) |
| MessagePack | `decode()` from `@msgpack/msgpack` | 3.1.3 |
| Protocol Buffers | `Recipe.decode()` from `protobufjs` static code generated from `dataset/recipe.proto` | 8.8.0 |

"Deserialization time" in the paper is the time of that one call, starting
from the received bytes. For Protocol Buffers the CSV also records
`deserializationWithMaterializationMs`: the decode plus conversion of the
decoded message into a plain JavaScript object.

## All declared app dependencies

As recorded in `environment.libraries.declared` (exact pins from the app's
`package.json`):

| Package | Version |
|---|---|
| @expo/vector-icons | 14.1.0 |
| @msgpack/msgpack | 3.1.3 |
| @react-native-community/datetimepicker | 8.6.0 |
| @react-navigation/bottom-tabs | 7.15.10 |
| @react-navigation/elements | 2.9.15 |
| @react-navigation/native | 7.2.2 |
| @react-navigation/native-stack | 7.14.12 |
| axios | 1.15.2 |
| expo | 53.0.27 |
| expo-blur | 14.1.5 |
| expo-constants | 17.1.8 |
| expo-font | 13.3.2 |
| expo-haptics | 14.1.4 |
| expo-image | 2.1.7 (declared, but excluded from the native build and not used) |
| expo-linking | 7.1.7 |
| expo-router | 5.0.7 |
| expo-sharing | 13.1.5 |
| expo-splash-screen | 0.30.10 |
| expo-status-bar | 2.2.3 |
| expo-symbols | 0.4.5 |
| expo-system-ui | 5.0.11 |
| expo-web-browser | 14.1.6 |
| protobufjs | 8.8.0 |
| react | 19.0.0 |
| react-dom | 19.0.0 |
| react-native | 0.79.2 |
| react-native-gesture-handler | 2.24.0 |
| react-native-paper | 5.15.1 |
| react-native-reanimated | 3.17.5 |
| react-native-safe-area-context | 5.7.0 |
| react-native-screens | 4.10.0 |
| react-native-web | 0.20.0 |
| react-native-webview | 13.13.5 |

## Benchmark configuration

Identical in every run (`config` in `aggregate.json`):

| | |
|---|---|
| Pre-warm | 200 decodes per format, once per run |
| Per-cell warm-up | 10 decodes, discarded |
| Measured iterations | 30 per payload x format |
| Heap counter calibration | an empty measurement bracket allocates 208 B, the same before and after every run; subtracted as a constant |
| Heap determinism | the corrected heap delta was identical on all 30 repeats for every format (checked on payload 9001003 in every run) |

## Analysis environment

`analysis/output/` in this package was produced with:

| | |
|---|---|
| OS | Windows 11 (64-bit) |
| Python | 3.13.16 |
| pandas | 3.0.5 |
| statsmodels | 0.15.0 |
| scipy | 1.18.1 |
| numpy | 2.5.4 |

`requirements.txt` pins those four. The packages they pulled in were: patsy
1.0.3, formulaic 1.2.2, python-dateutil 2.9.0.post0, tzdata 2026.5, packaging
26.3, narwhals 2.27.1, interface_meta 2.0.1, typing_extensions 4.16.0, six
1.17.0 and wrapt 2.5.1. scipy 1.18.1 needs Python 3.12 or newer.

`analysis/warmup/verify_warmup.ts` needs Node.js 22.6 or newer (it was run with
22.17.1) and no packages.
