"""Reproduce every number reported in the paper from the raw run CSVs.

Usage:  python analyze.py [data_dir] [output_dir]
        e.g. python analysis/analyze.py runs/final analysis/output

Input:  one CSV per accepted run, exported by the Dishcovery benchmark runner.
        Columns: runId, payloadId, source, tier, byteLength, format, wireBytes,
        iteration, deserializationMs, heapDeltaBytesRaw, heapDeltaBytesCorrected,
        deserializationWithMaterializationMs, cellStartedAt
Output: integrity report, summary tables (CSV + Markdown) and statistical tests.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats
from statsmodels.stats.anova import anova_lm

FORMATS = ["json", "msgpack", "protobuf"]
TIERS = ["low", "medium", "high"]
LABEL = {"json": "JSON", "msgpack": "MessagePack", "protobuf": "Protocol Buffers"}

data_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "data")
out_dir = Path(sys.argv[2] if len(sys.argv) > 2 else "output")
out_dir.mkdir(parents=True, exist_ok=True)
report = []


def say(line=""):
    print(line)
    report.append(line)


# --------------------------------------------------------------------- load
# CSVs directly in data_dir, or one level down (runs/final/<runId>/run_<runId>.csv)
csv_paths = sorted(data_dir.glob("*.csv")) or sorted(data_dir.glob("*/*.csv"))
frames = [pd.read_csv(p) for p in csv_paths]
df = pd.concat(frames, ignore_index=True)
df["format"] = pd.Categorical(df["format"], FORMATS)
df["tier"] = pd.Categorical(df["tier"], TIERS)
runs = sorted(df["runId"].unique())

# ---------------------------------------------------------------- integrity
say("# Integrity checks")
for r in runs:
    d = df[df.runId == r]
    say(f"- run {r}: {len(d)} rows, {d.payloadId.nunique()} payloads, "
        f"iterations per cell = {sorted(d.groupby(['payloadId', 'format'], observed=True).size().unique())}")
heap_sd = df.groupby(["runId", "payloadId", "format"], observed=True)["heapDeltaBytesCorrected"].std().max()
say(f"- largest within-payload heap sd across repeats: {heap_sd:.0f} B (0 = deterministic)")
heap_runs = df.groupby(["payloadId", "format"], observed=True)["heapDeltaBytesCorrected"].nunique().max()
say(f"- distinct heap values per payload x format across runs: {heap_runs} (1 = identical in every run)")
wire_runs = df.groupby(["payloadId", "format"], observed=True)["wireBytes"].nunique().max()
say(f"- distinct wire sizes per payload x format across runs: {wire_runs}")
json_wire_ok = (df[df.format == "json"].wireBytes == df[df.format == "json"].byteLength).all()
say(f"- JSON wire bytes equal canonical byte length: {json_wire_ok}")
counts = df.drop_duplicates("payloadId").groupby(["source", "tier"], observed=True).size()
say("- payloads by source x tier: " + ", ".join(f"{s}/{t}={n}" for (s, t), n in counts.items()))
say()

# ------------------------------------------------- per-payload observations
# time: mean of 30 repeats x all runs; heap and wire: deterministic per payload
pp = (df.groupby(["payloadId", "source", "tier", "byteLength", "format"], observed=True)
        .agg(ms=("deserializationMs", "mean"),
             ms_mat=("deserializationWithMaterializationMs", "mean"),
             heap=("heapDeltaBytesCorrected", "first"),
             wire=("wireBytes", "first"))
        .reset_index())
pp.to_csv(out_dir / "per_payload.csv", index=False)

# payload sizes file for the artefact (one row per payload, three formats)
sizes = pp.pivot_table(index=["payloadId", "source", "tier"], columns="format",
                       values="wire", observed=True).reset_index()
sizes.columns = ["payloadId", "source", "tier", "json_bytes", "msgpack_bytes", "protobuf_bytes"]
sizes.to_csv(out_dir / "payload_sizes.csv", index=False)

# ------------------------------------------------------------ main table
rows = []
for t in TIERS:
    base = None
    for f in FORMATS:
        raw = df[(df.tier == t) & (df.format == f)]
        p = pp[(pp.tier == t) & (pp.format == f)]
        row = dict(tier=t, format=f, payloads=len(p), decodes=len(raw),
                   kb_mean=p.wire.mean() / 1000, kb_sd=p.wire.std() / 1000,
                   ms_mean=raw.deserializationMs.mean(), ms_sd=raw.deserializationMs.std(),
                   mb_mean=p.heap.mean() / 1e6, mb_sd=p.heap.std() / 1e6)
        if f == "json":
            base = row
        for k in ("kb", "ms", "mb"):
            row[f"{k}_pct_vs_json"] = (None if f == "json"
                                       else 100 * (row[f"{k}_mean"] / base[f"{k}_mean"] - 1))
        if f == "protobuf":
            row["materialisation_pct"] = 100 * (raw.deserializationWithMaterializationMs.mean()
                                                / raw.deserializationMs.mean() - 1)
        rows.append(row)
table = pd.DataFrame(rows)
table.to_csv(out_dir / "table_main.csv", index=False)

say("# Main table (pooled over accepted runs)")
say("| Tier | Format | KB mean (sd) | ms mean (sd) | MB mean (sd) | Size % | Time % | Alloc % |")
say("|---|---|---|---|---|---|---|---|")
fmt = lambda v: "" if v is None or pd.isna(v) else f"{v:+.1f}"
for _, r in table.iterrows():
    say(f"| {r.tier} | {LABEL[r.format]} | {r.kb_mean:.2f} ({r.kb_sd:.2f}) | "
        f"{r.ms_mean:.2f} ({r.ms_sd:.2f}) | {r.mb_mean:.3f} ({r.mb_sd:.3f}) | "
        f"{fmt(r.kb_pct_vs_json)} | {fmt(r.ms_pct_vs_json)} | {fmt(r.mb_pct_vs_json)} |")
say()
for _, r in table[table.format == "protobuf"].iterrows():
    say(f"- protobuf materialisation overhead, {r.tier}: +{r.materialisation_pct:.1f}%")
say()

# ------------------------------------------------------ between-run stability
say("# Between-run stability of mean decode time")
rm = (df.groupby(["runId", "tier", "format"], observed=True)["deserializationMs"].mean()
        .unstack("runId"))
rm["cv_pct"] = 100 * rm.std(axis=1) / rm.mean(axis=1)
rm.to_csv(out_dir / "between_run_means.csv")
say(f"- largest between-run CV of a cell mean: {rm.cv_pct.max():.2f}%")
pct = {}
for r in runs:
    d = df[df.runId == r].groupby(["tier", "format"], observed=True)["deserializationMs"].mean()
    for t in TIERS:
        for f in ("msgpack", "protobuf"):
            pct.setdefault((t, f), []).append(100 * (d[(t, f)] / d[(t, "json")] - 1))
spread = max(max(v) - min(v) for v in pct.values())
say(f"- largest between-run spread of a % vs JSON figure: {spread:.2f} percentage points")
say()

# ---------------------------------------------------------------- statistics
say("# Two-way ANOVA: log(metric) ~ format * tier (unit = payload)")
pp["log_ms"] = np.log(pp.ms)
pp["log_heap"] = np.log(pp.heap)
pp["log_wire"] = np.log(pp.wire)
anova_rows = []
for metric in ("log_wire", "log_ms", "log_heap"):
    m = smf.ols(f"{metric} ~ C(format) * C(tier)", data=pp).fit()
    a = anova_lm(m, typ=2)
    ss_res = a.loc["Residual", "sum_sq"]
    for term in ("C(format)", "C(tier)", "C(format):C(tier)"):
        eta = a.loc[term, "sum_sq"] / (a.loc[term, "sum_sq"] + ss_res)
        anova_rows.append(dict(metric=metric, term=term, df=int(a.loc[term, "df"]),
                               df_resid=int(a.loc["Residual", "df"]),
                               F=a.loc[term, "F"], p=a.loc[term, "PR(>F)"], partial_eta2=eta))
anova = pd.DataFrame(anova_rows)
anova.to_csv(out_dir / "anova.csv", index=False)
for _, r in anova.iterrows():
    say(f"- {r.metric:9s} {r.term:18s} F({r.df},{r.df_resid}) = {r.F:10.1f}, "
        f"p = {r.p:.2e}, partial eta^2 = {r.partial_eta2:.3f}")
say()

# repeated-measures check: random intercept per payload
say("# Mixed model check: log(metric) ~ format * tier + (1 | payload)")
for metric in ("log_ms", "log_heap"):
    mm = smf.mixedlm(f"{metric} ~ C(format) * C(tier)", pp, groups=pp["payloadId"]).fit(reml=False)
    mm0 = smf.mixedlm(f"{metric} ~ C(format) + C(tier)", pp, groups=pp["payloadId"]).fit(reml=False)
    lr = 2 * (mm.llf - mm0.llf)
    say(f"- {metric}: likelihood-ratio test of format x tier interaction, "
        f"chi2(4) = {lr:.1f}, p = {stats.chi2.sf(lr, 4):.2e}")
say()

# paired comparisons MessagePack vs Protocol Buffers within each tier
say("# Paired comparison within tier: Protocol Buffers vs MessagePack (per payload)")
wide = pp.pivot_table(index=["payloadId", "tier", "byteLength", "source"], columns="format",
                      values=["ms", "heap", "wire"], observed=True).reset_index()
pair_rows = []
for t in TIERS:
    w = wide[wide.tier == t]
    for metric in ("ms", "heap"):
        d = np.log(w[(metric, "protobuf")]) - np.log(w[(metric, "msgpack")])
        tt = stats.ttest_1samp(d, 0)
        wil = stats.wilcoxon(d)
        pair_rows.append(dict(tier=t, metric=metric, n=len(d),
                              ratio_protobuf_over_msgpack=float(np.exp(d.mean())),
                              t=tt.statistic, p_t=tt.pvalue, p_wilcoxon=wil.pvalue,
                              cohens_dz=d.mean() / d.std(ddof=1),
                              protobuf_wins=int((d < 0).sum())))
pairs = pd.DataFrame(pair_rows)
pairs.to_csv(out_dir / "paired_protobuf_vs_msgpack.csv", index=False)
for _, r in pairs.iterrows():
    say(f"- {r.tier:6s} {r.metric:4s}: protobuf/msgpack = {r.ratio_protobuf_over_msgpack:.3f}, "
        f"t({r.n - 1}) = {r.t:7.1f}, p = {r.p_t:.1e}, dz = {r.cohens_dz:+.2f}, "
        f"protobuf lower in {r.protobuf_wins}/{r.n} payloads")
say()

# byte length as a continuous covariate, and the crossover point
say("# Covariate: log(protobuf/msgpack) ~ log(JSON bytes)")
cross_rows = []
for metric in ("ms", "heap"):
    y = np.log(wide[(metric, "protobuf")] / wide[(metric, "msgpack")])
    x = np.log(wide["byteLength"])
    fit = stats.linregress(x, y)
    crossover = float(np.exp(-fit.intercept / fit.slope))
    # bootstrap over payloads for an interval on the crossover
    rng = np.random.default_rng(20261015)
    boots = []
    for _ in range(2000):
        i = rng.integers(0, len(x), len(x))
        b = stats.linregress(x.iloc[i], y.iloc[i])
        boots.append(np.exp(-b.intercept / b.slope))
    lo, hi = np.percentile(boots, [2.5, 97.5])
    cross_rows.append(dict(metric=metric, slope=fit.slope, r2=fit.rvalue ** 2, p=fit.pvalue,
                           crossover_bytes=crossover, ci_low=lo, ci_high=hi))
    say(f"- {metric:4s}: slope = {fit.slope:.3f}, R^2 = {fit.rvalue ** 2:.3f}, "
        f"crossover at {crossover:,.0f} B (95% bootstrap CI {lo:,.0f} to {hi:,.0f})")
pd.DataFrame(cross_rows).to_csv(out_dir / "crossover.csv", index=False)
say(f"- largest Spoonacular payload: {wide[wide.source == 'spoonacular'].byteLength.max():,} B")
say()

# allocation per JSON byte
say("# Heap allocation per byte of JSON input")
apb = pp.assign(per_byte=pp.heap / pp.byteLength).groupby(["tier", "format"], observed=True).per_byte.mean()
apb.unstack().to_csv(out_dir / "alloc_per_json_byte.csv")
for t in TIERS:
    say(f"- {t:6s}: " + ", ".join(f"{LABEL[f]} {apb[(t, f)]:.1f}" for f in FORMATS))
say()

# provenance control at the low tier
say("# Provenance control (low tier): Spoonacular vs generated")
low = pp[pp.tier == "low"]
for f in ("msgpack", "protobuf"):
    for metric in ("ms", "heap", "wire"):
        vals = {}
        for s in ("spoonacular", "generated"):
            a = low[(low.source == s) & (low.format == f)].set_index("payloadId")[metric]
            j = low[(low.source == s) & (low.format == "json")].set_index("payloadId")[metric]
            vals[s] = 100 * (a.mean() / j.mean() - 1)
        say(f"- {LABEL[f]:16s} {metric:4s}: spoonacular {vals['spoonacular']:+.1f}%, "
            f"generated {vals['generated']:+.1f}%")

(out_dir / "report.md").write_text("\n".join(report) + "\n")
