"""
Build outputs/map_data.json — per-country metric values for the choropleth map.

Uses the latest available year per (metric, country, sex) from the Level 0 panel.
'T' (total) is sum for stocks (population, person-years) and population-weighted
mean for rates/expectancies (LE, HLY). Vacancy is total-only.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
panel = pd.read_parquet(ROOT / "data" / "processed" / "panel.parquet")
COUNTRIES = {"BG": "Bulgaria", "PL": "Poland", "CZ": "Czechia", "RO": "Romania",
             "DE": "Germany", "FR": "France", "NO": "Norway", "CH": "Switzerland"}
REGIME = {"BG": "Post-socialist EU", "PL": "Post-socialist EU",
          "CZ": "Post-socialist EU", "RO": "Post-socialist EU",
          "DE": "Western EU", "FR": "Western EU",
          "NO": "EFTA", "CH": "EFTA"}


def latest(df, col):
    """Latest year with a non-null value for this column."""
    s = df[df[col].notna()]
    return int(s["year"].max()) if len(s) else None


def by_sex(col, total="sum"):
    """Return {country:{F,M,T}, year, ...} at the latest common-ish year per country."""
    out = {}
    yr_used = {}
    for c in COUNTRIES:
        sub = panel[panel["country"] == c]
        y = latest(sub, col)
        if y is None:
            continue
        row = sub[sub["year"] == y]
        f = row[row["sex"] == "F"][col].mean()
        m = row[row["sex"] == "M"][col].mean()
        vals = {}
        if not np.isnan(f):
            vals["F"] = round(float(f), 2)
        if not np.isnan(m):
            vals["M"] = round(float(m), 2)
        if total == "sum":
            t = np.nansum([f, m])
            vals["T"] = round(float(t), 2) if t else None
        else:  # population-weighted mean
            pr = sub[sub["year"] == y]
            pf = pr[pr["sex"] == "F"]["pop_total"].mean()
            pm = pr[pr["sex"] == "M"]["pop_total"].mean()
            if not (np.isnan(f) or np.isnan(m) or np.isnan(pf) or np.isnan(pm)):
                vals["T"] = round(float((f * pf + m * pm) / (pf + pm)), 2)
        out[c] = vals
        yr_used[c] = y
    return out, yr_used


# Derived: potential labour supply = population x HLY (healthy person-years)
panel = panel.copy()
panel["supply_birth"] = panel["pop_total"] * panel["hly_birth"]
panel["total_le_py"] = panel["pop_total"] * panel["le_birth"]

METRICS = {
    "supply_birth": dict(label="Potential labour supply (healthy person-years)",
                         unit="person-years", total="sum", fmt="millions"),
    "hly_birth": dict(label="Healthy life years at birth", unit="years",
                      total="wmean", fmt="plain"),
    "le_birth": dict(label="Life expectancy at birth", unit="years",
                     total="wmean", fmt="plain"),
    "pop_total": dict(label="Population (1 Jan)", unit="persons",
                      total="sum", fmt="millions"),
    "employed_ths": dict(label="Employment 15-64", unit="thousands",
                         total="sum", fmt="plain"),
    "vacancy_rate": dict(label="Job vacancy rate", unit="%",
                         total="wmean", fmt="plain"),
}

data = {"countries": COUNTRIES, "regime": REGIME, "metrics": {}}
for col, meta in METRICS.items():
    vals, yrs = by_sex(col, total=meta["total"])
    data["metrics"][col] = {**meta, "values": vals, "years": yrs}

out = ROOT / "outputs" / "map_data.json"
out.write_text(json.dumps(data, indent=2))
print("wrote", out)
# quick sanity print
for col in METRICS:
    md = data["metrics"][col]
    sample = {c: md["values"].get(c, {}).get("T") for c in COUNTRIES}
    print(f"{col:14s} ({md['unit']}): {sample}")
