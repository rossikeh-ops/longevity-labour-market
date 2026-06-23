"""
Level 0 — Clean & assemble the analysis panel.

Reads the latest data/raw/<code>__<date>.parquet files, harmonises them into one
tidy long table, fills *internal* gaps (interpolation only — never extrapolation,
which is forecasting), and writes:

  data/processed/panel_long.parquet   tidy long: country, sex, year, indicator, unit, value, flag, imputed
  data/processed/panel.parquet        modelling-wide: one row per (country, sex, year), core indicators as columns
  data/imputation_log.csv             one row per filled cell (country, sex, indicator, year, method)
  data/coverage_report.csv            per (indicator, country, sex): n_obs, year range, flag counts, coverage decision

Leakage note: internal-gap interpolation is benign for the foundation. The
forecast hold-out (last 3-4 years) and break/COVID adjustments are applied in the
modelling step (Level 1) on observed data, so nothing leaks into validation here.
Break (b) and COVID (2020-21) are surfaced as boolean columns for the models.
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"
PROC.mkdir(parents=True, exist_ok=True)
DATA = ROOT / "data"
COUNTRIES = ["BG", "PL", "CZ", "RO", "DE", "FR", "NO", "CH"]

# Locked after the 5-angle "Fat & Dirty" panel (3xA vs 1xB,1xC): the COMBINED
# balance is computed on the maximal fully-observed common window, zero backcast.
# Per-series forecasting still uses each series' full history (set elsewhere).
ANALYSIS_START, ANALYSIS_END = 2011, 2024
# Indicators that must be fully observed (no synthetic data) on the common window.
BALANCE_CORE = ["le_birth", "le_65", "hly_birth", "hly_65", "pop_total",
                "pop_15_64", "pop_65p", "employed_ths", "vacancy_count",
                "vacancy_rate", "working_life_yrs", "unemp_rate"]

# Map raw (dataset, indicator) -> friendly column name in the wide panel.
INDICATOR_MAP = {
    ("hlth_hlye", "LE_0"): "le_birth",
    ("hlth_hlye", "LE_65"): "le_65",
    ("hlth_hlye", "HLY_0"): "hly_birth",
    ("hlth_hlye", "HLY_65"): "hly_65",
    ("demo_mlexpec", "Y15"): "le_15_alt",
    ("demo_pjan", "TOTAL"): "pop_total",
    ("lfsa_egan", "Y15-64"): "employed_ths",
    ("lfsi_dwl_a", "YR"): "working_life_yrs",
    ("une_rt_a", "Y15-74"): "unemp_rate",
    ("jvs_q_r21", "vacancy_rate"): "vacancy_rate",    # sex = T; B-T TOTAL, annualised
    ("jvs_q_r21", "vacancy_count"): "vacancy_count",  # sex = T; absolute vacancies
    ("nama_10_a64", "Q"): "nace_q_va",          # sex = T
    ("gov_10a_exp", "GF07"): "gov_health_exp",  # sex = T
    ("gov_10a_exp", "GF10"): "gov_social_exp",  # sex = T
    ("nama_10_co3_p3", "CP09"): "coicop_recreation",  # sex = T
    ("nama_10_co3_p3", "CP10"): "coicop_education",    # sex = T
    ("nama_10_co3_p3", "CP11"): "coicop_hotels_rest",  # sex = T
}


def load_raw() -> pd.DataFrame:
    """Concatenate the latest version of every raw parquet."""
    files = {}
    for p in RAW.glob("*.parquet"):
        code = p.stem.split("__")[0]
        date = p.stem.split("__")[1]
        if code not in files or date > files[code][1]:
            files[code] = (p, date)
    frames = [pd.read_parquet(p) for p, _ in files.values()]
    df = pd.concat(frames, ignore_index=True)
    df = df[df["country"].isin(COUNTRIES)].copy()
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df["flag"] = df["flag"].fillna("").astype(str)
    return df


def coverage_report(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    obs = df[df["value"].notna()]
    for (ds, ind, c, s), g in obs.groupby(["dataset", "indicator", "country", "sex"]):
        flags = g["flag"].value_counts().to_dict()
        rows.append({
            "dataset": ds, "indicator": ind, "country": c, "sex": s,
            "n_obs": len(g), "year_min": int(g["year"].min()),
            "year_max": int(g["year"].max()),
            "n_break": sum(v for k, v in flags.items() if "b" in k),
            "n_provisional": sum(v for k, v in flags.items() if "p" in k),
            "n_estimated": sum(v for k, v in flags.items() if "e" in k),
        })
    return pd.DataFrame(rows).sort_values(["dataset", "indicator", "country", "sex"])


def interpolate_gaps(df: pd.DataFrame):
    """Linear-interpolate *internal* missing years per series. Returns (df, log)."""
    log = []
    out = []
    for keys, g in df.groupby(["dataset", "indicator", "country", "sex"], sort=False):
        g = g.sort_values("year").copy()
        obs = g[g["value"].notna()]
        if len(obs) >= 2:
            lo, hi = obs["year"].min(), obs["year"].max()
            inner = g[(g["year"] >= lo) & (g["year"] <= hi)].copy()
            before = inner["value"].isna()
            inner["value"] = inner["value"].interpolate(method="linear")
            filled = inner[before & inner["value"].notna()]
            for _, r in filled.iterrows():
                log.append({"dataset": keys[0], "indicator": keys[1],
                            "country": keys[2], "sex": keys[3],
                            "year": int(r["year"]), "method": "linear_interp"})
            g.loc[inner.index, "value"] = inner["value"]
            g["imputed"] = False
            g.loc[filled.index, "imputed"] = True
        else:
            g["imputed"] = False
        out.append(g)
    return pd.concat(out, ignore_index=True), pd.DataFrame(log)


def build_wide(df: pd.DataFrame) -> pd.DataFrame:
    full = df.copy()   # keep ALL rows (age bands) before indicator filtering
    df = df.copy()
    # vacancy dataset ships both annual (AVG_A) and 3-year (AVG_3Y) averages —
    # keep the annual series only.
    df = df[~((df["dataset"] == "jvs_a_rate_r2") & (df["unit"] != "AVG_A"))]
    df["col"] = df.apply(lambda r: INDICATOR_MAP.get((r["dataset"], r["indicator"])), axis=1)
    df = df[df["col"].notna()]
    # Guard: a mapped (col, country, sex, year) must be unique. Duplicates mean an
    # unfiltered hidden dimension (e.g. citizen, wstatus) — would silently collapse
    # to a wrong subcategory under pivot 'first'. Fail loudly instead.
    dup = df.duplicated(subset=["col", "country", "sex", "year"], keep=False)
    if dup.any():
        bad = df.loc[dup, ["dataset", "col", "country", "sex", "year"]].drop_duplicates()
        raise ValueError(f"duplicate keys (unfiltered dimension?):\n{bad.head(20)}")
    # sex-specific indicators
    sexed = df[df["sex"].isin(["F", "M"])]
    wide = sexed.pivot_table(index=["country", "sex", "year"], columns="col",
                             values="value", aggfunc="first").reset_index()
    # working-age (15-64) and 65+ population from demo_pjangroup 5-year bands
    WA = ["Y15-19", "Y20-24", "Y25-29", "Y30-34", "Y35-39", "Y40-44",
          "Y45-49", "Y50-54", "Y55-59", "Y60-64"]
    P65 = ["Y65-69", "Y70-74", "Y_GE75"]
    grp = full[full["dataset"] == "demo_pjangroup"]
    for name, bands in [("pop_15_64", WA), ("pop_65p", P65)]:
        agg = (grp[grp["indicator"].isin(bands)]
               .groupby(["country", "sex", "year"])["value"].sum().reset_index()
               .rename(columns={"value": name}))
        wide = wide.merge(agg, on=["country", "sex", "year"], how="left")

    # T-only indicators (vacancy, NACE, COICOP, gov) -> broadcast to both sexes,
    # to be apportioned within their own level.
    tonly = df[df["sex"] == "T"]
    if not tonly.empty:
        tw = tonly.pivot_table(index=["country", "year"], columns="col",
                               values="value", aggfunc="first").reset_index()
        rows = []
        for s in ["F", "M"]:
            t2 = tw.copy(); t2["sex"] = s; rows.append(t2)
        tw2 = pd.concat(rows, ignore_index=True)
        wide = wide.merge(tw2, on=["country", "year", "sex"], how="outer",
                          suffixes=("", "_t"))
    wide["covid"] = wide["year"].isin([2020, 2021]).astype(int)
    return wide.sort_values(["country", "sex", "year"]).reset_index(drop=True)


def emit_common_panel(wide: pd.DataFrame) -> pd.DataFrame:
    """Slice the locked common window and HARD-ASSERT it is rectangular:
    every (country, sex, year) cell present and every BALANCE_CORE indicator
    fully observed (no NaN) — the 'same period' hard requirement."""
    yrs = list(range(ANALYSIS_START, ANALYSIS_END + 1))
    common = wide[(wide["year"] >= ANALYSIS_START) & (wide["year"] <= ANALYSIS_END)].copy()
    # 1) frame is complete: 8 countries x 2 sexes x 14 years = 224 rows
    expected = len(COUNTRIES) * 2 * len(yrs)
    assert len(common) == expected, f"frame not rectangular: {len(common)} != {expected}"
    # 2) every core indicator fully observed on the window
    miss = {c: int(common[c].isna().sum()) for c in BALANCE_CORE if c in common.columns}
    bad = {k: v for k, v in miss.items() if v > 0}
    assert not bad, f"missing cells in common window for: {bad}"
    common.to_parquet(PROC / "panel_common.parquet", index=False)
    return common


def main():
    df = load_raw()
    cov = coverage_report(df)
    cov.to_csv(DATA / "coverage_report.csv", index=False)

    df2, log = interpolate_gaps(df)
    df2.to_parquet(PROC / "panel_long.parquet", index=False)
    log.to_csv(DATA / "imputation_log.csv", index=False)

    wide = build_wide(df2)
    wide.to_parquet(PROC / "panel.parquet", index=False)
    common = emit_common_panel(wide)

    print(f"raw long rows         : {len(df)}")
    print(f"COMMON window         : {ANALYSIS_START}-{ANALYSIS_END}  "
          f"rows={len(common)} (=8x2x{ANALYSIS_END-ANALYSIS_START+1}), "
          f"core indicators fully observed [OK]")
    print(f"datasets              : {sorted(df['dataset'].unique())}")
    print(f"internal gaps filled  : {len(log)}")
    print(f"panel.parquet shape   : {wide.shape}")
    print(f"panel columns         : {[c for c in wide.columns]}")
    print(f"countries x sex x yrs : {wide['country'].nunique()} x "
          f"{wide['sex'].nunique()} x {wide['year'].nunique()}")
    print("\ncoverage by indicator (n series, min n_obs):")
    summ = cov.groupby("indicator").agg(series=("n_obs", "size"),
                                        min_obs=("n_obs", "min"),
                                        breaks=("n_break", "sum")).reset_index()
    print(summ.to_string(index=False))


if __name__ == "__main__":
    main()
