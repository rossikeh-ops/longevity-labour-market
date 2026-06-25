# -*- coding: utf-8 -*-
"""
Download AI-related labour/economy data for the 8 case countries.

Eurostat has no direct "AI occupation" employment series, so we pull the two
closest, relevant signals:
  1. AI ADOPTION  — isoc_eb_ain2: % of enterprises (10+ emp) using AI technologies
                    (any AI, plus machine-learning and natural-language types).
  2. ICT-SPECIALIST JOBS — isoc_sks_itsps: ICT specialists in employment
                    (thousand persons and % of total employment), by sex —
                    the workforce that builds and runs AI.

Saves tidy long CSVs in data/raw/ and prints coverage + latest values.
"""
from __future__ import annotations
import datetime as dt
from pathlib import Path
import pandas as pd
import eurostat

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)
C = ["BG", "PL", "CZ", "RO", "DE", "FR", "NO", "CH"]
TODAY = dt.date.today().isoformat()


def geo_for(code):
    """Only request the case countries that the dataset actually carries."""
    avail = set(eurostat.get_par_values(code, "geo"))
    keep = [c for c in C if c in avail]
    miss = [c for c in C if c not in avail]
    if miss:
        print(f"  ! {code}: no data for {miss}")
    return keep


def to_long(df, idcols):
    geo_col = [c for c in df.columns if c.endswith("TIME_PERIOD")][0]
    df = df.rename(columns={geo_col: "country"})
    years = sorted({c.split("_")[0] for c in df.columns if c.endswith("_value")})
    rows = []
    for _, r in df.iterrows():
        if r["country"] not in C:
            continue
        base = {k: r[k] for k in idcols if k in df.columns}
        for y in years:
            v = r.get(f"{y}_value")
            if pd.notna(v):
                rows.append({**base, "country": r["country"], "year": int(y), "value": float(v)})
    return pd.DataFrame(rows)


# ---------- 1. AI adoption by enterprises ----------
ai = eurostat.get_data_df("isoc_eb_ain2", flags=True, filter_pars={
    "geo": geo_for("isoc_eb_ain2"), "size_emp": ["GE10"], "nace_r2": ["C10-S951_X_K"], "unit": ["PC_ENT"],
    "indic_is": ["E_AI_TANY", "E_AI_TML", "E_AI_TNLG"]})
ai_long = to_long(ai, ["indic_is", "unit"])
AI_LABEL = {"E_AI_TANY": "any AI technology", "E_AI_TML": "machine learning",
            "E_AI_TNLG": "natural-language generation"}
ai_long["indicator"] = ai_long["indic_is"].map(AI_LABEL).fillna(ai_long["indic_is"])
ai_long.to_csv(RAW / f"ai_adoption_enterprises__{TODAY}.csv", index=False)

# ---------- 2. ICT specialists in employment ----------
ict = eurostat.get_data_df("isoc_sks_itsps", flags=True, filter_pars={
    "geo": geo_for("isoc_sks_itsps"), "unit": ["THS_PER", "PC"], "sex": ["M", "F"]})
ict_long = to_long(ict, ["unit", "sex"])
ict_long.to_csv(RAW / f"ict_specialists_employment__{TODAY}.csv", index=False)

# ---------- report ----------
print("=== 1) AI adoption — % of enterprises (10+) using ANY AI, latest year ===")
a = ai_long[(ai_long.indic_is == "E_AI_TANY")]
ly = int(a.year.max())
for c in C:
    s = a[(a.country == c) & (a.year == ly)]["value"]
    print(f"  {c}: {s.iloc[0]:.1f}%" if len(s) else f"  {c}: (no {ly} data)")
print(f"  [latest common year ~{ly}; rows {len(ai_long)}]")

print("\n=== 2) ICT specialists in employment (thousand persons, latest year, F+M) ===")
t = ict_long[ict_long.unit == "THS_PER"].groupby(["country", "year"])["value"].sum().reset_index()
for c in C:
    sub = t[t.country == c]
    if len(sub):
        r = sub.loc[sub.year.idxmax()]
        print(f"  {c}: {r['value']:.0f}k  ({int(r['year'])})")
pc = ict_long[ict_long.unit == "PC"].groupby(["country", "year"])["value"].mean().reset_index()
print("  (also saved as % of employment)")

print(f"\nwrote data/raw/ai_adoption_enterprises__{TODAY}.csv ({len(ai_long)} rows)")
print(f"wrote data/raw/ict_specialists_employment__{TODAY}.csv ({len(ict_long)} rows)")
