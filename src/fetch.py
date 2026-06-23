"""
Level 0 — Eurostat data fetcher (hardened).

Pulls each dataset code via the `eurostat` API into data/raw/ as:
  - <code>__<YYYY-MM-DD>.parquet        (tidy long: country, sex, year, indicator, unit, value, flag)
And appends one row per dataset to data/raw/_manifest.csv documenting
download date, filters, shape, and country coverage (catches NO/CH gaps early).

Design notes (per plan, 5-angle review):
  * Pre-flight check of parameter values before download (no silent 404s).
  * Retry with exponential backoff; never silently truncate.
  * Flags (b/p/e/:) retained.
  * Units pinned per dataset; fallback logged, never silently downgraded.

Usage:
  python src/fetch.py --levels 1 2 3      # core supply/demand/balance path
  python src/fetch.py --levels 4 5        # cost & consumption datasets
  python src/fetch.py --all
"""
from __future__ import annotations
import argparse, time, sys, datetime as dt
from pathlib import Path
import pandas as pd
import eurostat

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)
MANIFEST = RAW / "_manifest.csv"

COUNTRIES = ["BG", "PL", "CZ", "RO", "DE", "FR", "NO", "CH"]
TODAY = dt.date.today().isoformat()

# Per-dataset spec: filters, the dimension that names the indicator, and the
# preferred unit (validated post-download; fallback logged).
REGISTRY = {
    # ---- Level 1: supply (LE, HLY, population) ----
    "hlth_hlye": dict(level=1, filter={"sex": ["F", "M"],
                       "indic_he": ["LE_0", "LE_65", "HLY_0", "HLY_65"]},
                       indic_dim="indic_he", unit_pref=None),
    "demo_mlexpec": dict(level=1, filter={"sex": ["F", "M"],
                         "age": ["Y_LT1", "Y15", "Y65"]},
                         indic_dim="age", unit_pref="YR"),
    "demo_pjan": dict(level=1, filter={"sex": ["F", "M"], "age": ["TOTAL"]},
                      indic_dim="age", unit_pref="NR"),
    "demo_pjangroup": dict(level=1, filter={"sex": ["F", "M"],
                           "age": ["TOTAL", "Y15-19", "Y20-24", "Y25-29",
                                   "Y30-34", "Y35-39", "Y40-44", "Y45-49",
                                   "Y50-54", "Y55-59", "Y60-64", "Y65-69",
                                   "Y70-74", "Y_GE75"]},
                           indic_dim="age", unit_pref="NR"),
    # ---- Level 2/3: demand & balance ----
    "lfsa_egan": dict(level=2, filter={"sex": ["F", "M"], "age": ["Y15-64"],
                      "unit": ["THS_PER"], "citizen": ["TOTAL"]},
                      indic_dim="age", unit_pref="THS_PER"),
    # Vacancy rate handled by the dedicated fetch_vacancy() below (jvs_a_r21,
    # NACE Rev 2.1, code B-T, size-class fallback) because the older
    # jvs_a_rate_r2 array lacks FR and CH.
    "lfsi_dwl_a": dict(level=2, filter={"sex": ["F", "M"], "unit": ["YR"]},
                       indic_dim="unit", unit_pref="YR"),
    "une_rt_a": dict(level=3, filter={"sex": ["F", "M"], "age": ["Y15-74"],
                     "unit": ["PC_ACT"]}, indic_dim="age", unit_pref="PC_ACT"),
    # ---- Level 4: cost of unhealthy years ----
    "nama_10_a64": dict(level=4, filter={"nace_r2": ["Q"], "na_item": ["B1G"],
                        "unit": ["CLV15_MEUR"]}, indic_dim="nace_r2",
                        unit_pref="CLV15_MEUR"),
    "gov_10a_exp": dict(level=4, filter={"cofog99": ["GF07", "GF10"],
                        "na_item": ["TE"], "sector": ["S13"],
                        "unit": ["MIO_EUR"]}, indic_dim="cofog99",
                        unit_pref="MIO_EUR"),
    # ---- Level 5: consumption (COICOP) ----
    "nama_10_co3_p3": dict(level=5, filter={"coicop": ["CP09", "CP10", "CP11"],
                           "unit": ["CLV15_MEUR"]}, indic_dim="coicop",
                           unit_pref="CLV15_MEUR"),
}


def preflight(code: str, flt: dict) -> dict:
    """Verify requested geo/filter values exist. Returns a coverage report and a
    `clean_filter` containing only values actually available (so the query is
    always valid; dropped values are logged, never silently sent)."""
    pars = eurostat.get_pars(code)
    report = {"code": code, "missing_geo": [], "unavailable_filters": {},
              "clean_filter": {}}
    for dim, vals in flt.items():
        if dim in pars:
            avail = set(eurostat.get_par_values(code, dim))
            ok = [v for v in vals if v in avail]
            miss = [v for v in vals if v not in avail]
            if miss:
                report["unavailable_filters"][dim] = miss
            report["clean_filter"][dim] = ok
        else:
            report["clean_filter"][dim] = vals
    if "geo" in pars:
        avail = set(eurostat.get_par_values(code, "geo"))
        report["missing_geo"] = [c for c in COUNTRIES if c not in avail]
    return report


def fetch_one(code: str, clean_filter: dict, retries: int = 4) -> pd.DataFrame:
    flt = dict(clean_filter)
    flt["geo"] = COUNTRIES
    last = None
    for attempt in range(retries):
        try:
            df = eurostat.get_data_df(code, flags=True, filter_pars=flt)
            if df is None or df.empty:
                raise ValueError("empty response")
            return df
        except Exception as e:  # noqa: BLE001
            last = e
            wait = 2 ** attempt
            print(f"  retry {attempt+1}/{retries} for {code} after {wait}s ({e})")
            time.sleep(wait)
    raise RuntimeError(f"FAILED to fetch {code}: {last}")


def to_long(df: pd.DataFrame, code: str, spec: dict) -> pd.DataFrame:
    """Wide (geo\\TIME_PERIOD + <year>_value/_flag) -> tidy long."""
    geo_col = [c for c in df.columns if c.endswith("TIME_PERIOD")][0]
    df = df.rename(columns={geo_col: "geo"})
    id_dims = [c for c in df.columns if "_value" not in c and "_flag" not in c]
    years = sorted({c.split("_")[0] for c in df.columns if c.endswith("_value")})
    rows = []
    for _, r in df.iterrows():
        base = {d: r[d] for d in id_dims}
        for y in years:
            v = r.get(f"{y}_value")
            f = r.get(f"{y}_flag")
            rows.append({**base, "year": int(y), "value": v, "flag": f})
    out = pd.DataFrame(rows)
    out = out.rename(columns={"geo": "country"})
    out["indicator"] = out[spec["indic_dim"]].astype(str)
    out["dataset"] = code
    if "sex" not in out.columns:
        out["sex"] = "T"  # not sex-disaggregated; apportioned later
    if "unit" not in out.columns:
        out["unit"] = spec.get("unit_pref") or ""
    keep = ["dataset", "country", "sex", "year", "indicator", "unit", "value", "flag"]
    return out[keep]


def fetch_vacancy() -> pd.DataFrame:
    """Whole-economy job vacancies for all 8 countries, annualised from quarterly.

    Source: jvs_q_r21 (NACE Rev 2.1, quarterly), code B-T (business economy — the
    only cross-country-comparable aggregate; A-T excludes FR/CH), size class TOTAL,
    not seasonally adjusted. We pull BOTH the rate (JVR) and the absolute vacancy
    count (JOBVAC), then annualise as the mean of available quarters (>=3 required).

    Why quarterly: relative to the annual jvs_a_r21 array it fills FR's missing 2020,
    extends FR back to 2011, and supplies the absolute count the jobs identity needs.
    Verified coverage: CH 2003+, NO 2010+, FR 2011+ (all FR points carry Eurostat
    flag `d` = definition differs — France's structurally different collection;
    documented in docs/missing-data-policy.md, not correctable).
    """
    flt = {"geo": COUNTRIES, "nace_r2_1": ["B-T"], "s_adj": ["NSA"],
           "sizeclas": ["TOTAL"], "indic_em": ["JVR", "JOBVAC"]}
    raw = eurostat.get_data_df("jvs_q_r21", flags=True, filter_pars=flt)
    geo_col = [c for c in raw.columns if c.endswith("TIME_PERIOD")][0]
    raw = raw.rename(columns={geo_col: "country"})
    qcols = [c[:-6] for c in raw.columns if c.endswith("_value") and "Q" in c]
    ind_name = {"JVR": "vacancy_rate", "JOBVAC": "vacancy_count"}
    rows = []
    for _, r in raw.iterrows():
        if r["country"] not in COUNTRIES:
            continue
        by_year = {}
        for per in qcols:
            yr = int(per[:4]); v = r.get(f"{per}_value"); f = r.get(f"{per}_flag")
            if pd.notna(v):
                by_year.setdefault(yr, {"v": [], "f": []})
                by_year[yr]["v"].append(v)
                if f:
                    by_year[yr]["f"].append(f)
        for yr, d in by_year.items():
            if len(d["v"]) < 3:   # require >=3 quarters for a credible annual mean
                continue
            flag = max(set(d["f"]), key=d["f"].count) if d["f"] else ""
            rows.append({"dataset": "jvs_q_r21", "country": r["country"], "sex": "T",
                         "year": yr, "indicator": ind_name[r["indic_em"]],
                         "unit": "annual_mean(NSA,B-T,TOTAL)",
                         "value": sum(d["v"]) / len(d["v"]), "flag": flag})
    return pd.DataFrame(rows)


def run(levels):
    manifest_rows = []
    if 2 in levels:
        print("[jvs_q_r21] level 2 (vacancy fetch, B-T TOTAL NSA, quarterly->annual) ...")
        try:
            vac = fetch_vacancy()
            out_path = RAW / f"jvs_q_r21__{TODAY}.parquet"
            vac.to_parquet(out_path, index=False)
            rate = vac[vac["indicator"] == "vacancy_rate"]
            present = sorted(rate.loc[rate["value"].notna(), "country"].unique())
            manifest_rows.append({
                "code": "jvs_q_r21", "level": 2, "download_date": TODAY,
                "filter": "nace_r2_1=B-T; sizeclas=TOTAL; s_adj=NSA; indic_em=JVR,JOBVAC",
                "rows": len(vac), "countries_with_data": ",".join(present),
                "missing_geo": "", "units": "annual_mean", "file": out_path.name,
                "status": "ok"})
            print(f"  saved {out_path.name}  rows={len(vac)}  countries={len(present)}/8")
        except Exception as e:  # noqa: BLE001
            print(f"  XX vacancy FAILED: {e}")
    for code, spec in REGISTRY.items():
        if spec["level"] not in levels:
            continue
        print(f"[{code}] level {spec['level']} ...")
        try:
            pf = preflight(code, spec["filter"])
            if pf["missing_geo"]:
                print(f"  ! missing geo coverage: {pf['missing_geo']}")
            if pf["unavailable_filters"]:
                print(f"  ! dropped unavailable filter values: {pf['unavailable_filters']}")
            raw = fetch_one(code, pf["clean_filter"])
            long = to_long(raw, code, spec)
        except Exception as e:  # noqa: BLE001 — one bad dataset must not kill the run
            print(f"  XX FAILED: {e}")
            manifest_rows.append({
                "code": code, "level": spec["level"], "download_date": TODAY,
                "filter": str(spec["filter"]), "rows": 0,
                "countries_with_data": "", "missing_geo": "", "units": "",
                "file": "", "status": f"FAILED: {e}"})
            continue
        units = sorted(long["unit"].dropna().unique())
        pref = spec.get("unit_pref")
        if pref and pref not in units and units:
            print(f"  ! unit fallback: wanted {pref}, got {units}")
        out_path = RAW / f"{code}__{TODAY}.parquet"
        long.to_parquet(out_path, index=False)
        present = sorted(long.loc[long["value"].notna(), "country"].unique())
        manifest_rows.append({
            "code": code, "level": spec["level"], "download_date": TODAY,
            "filter": str(spec["filter"]), "rows": len(long),
            "countries_with_data": ",".join(present),
            "missing_geo": ",".join(pf["missing_geo"]),
            "units": ",".join(units), "file": out_path.name, "status": "ok"})
        print(f"  saved {out_path.name}  rows={len(long)}  countries={len(present)}/8")
    if manifest_rows:
        mdf = pd.DataFrame(manifest_rows)
        if MANIFEST.exists():
            old = pd.read_csv(MANIFEST)
            old = old[~old["code"].isin(mdf["code"])]
            mdf = pd.concat([old, mdf], ignore_index=True)
        mdf.to_csv(MANIFEST, index=False)
        print(f"\nmanifest -> {MANIFEST}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--levels", nargs="*", type=int, default=None)
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    lv = list(range(0, 7)) if a.all or a.levels is None else a.levels
    print(f"Fetching levels {lv} for {COUNTRIES}\n")
    run(set(lv))
