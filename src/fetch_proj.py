"""
Fetch Eurostat population PROJECTIONS (proj_23np) and build working-age (15-64)
population by country x sex x year for 2024-2035. Baseline scenario (BSL) used for
the central forecast; migration variants (HMIGR/LMIGR) kept for scenario analysis.

Output: data/processed/proj_pop_wa.csv  [country, sex, year, scenario, pop_15_64_proj]
"""
from __future__ import annotations
from pathlib import Path
import datetime as dt
import pandas as pd
import eurostat

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"; RAW.mkdir(parents=True, exist_ok=True)
PROC = ROOT / "data" / "processed"
COUNTRIES = ["BG", "PL", "CZ", "RO", "DE", "FR", "NO", "CH"]
AGES = [f"Y{a}" for a in range(15, 65)]      # single-year ages 15..64
SCEN = ["BSL", "HMIGR", "LMIGR"]
TODAY = dt.date.today().isoformat()

flt = {"geo": COUNTRIES, "projection": SCEN, "sex": ["F", "M"],
       "age": AGES, "unit": ["PER"]}
raw = eurostat.get_data_df("proj_23np", filter_pars=flt)
raw.to_parquet(RAW / f"proj_23np__{TODAY}.parquet", index=False)

geo_col = [c for c in raw.columns if c.endswith("TIME_PERIOD")][0]
ycols = [c for c in raw.columns if c[:4].isdigit() and 2024 <= int(c[:4]) <= 2035]
long = raw.melt(id_vars=["projection", "sex", geo_col],
                value_vars=ycols, var_name="year", value_name="v")
long = long.rename(columns={geo_col: "country"})
long["year"] = long["year"].astype(int)
long["v"] = pd.to_numeric(long["v"], errors="coerce")
wa = (long.groupby(["country", "sex", "year", "projection"])["v"].sum()
      .reset_index().rename(columns={"v": "pop_15_64_proj", "projection": "scenario"}))
wa.to_csv(PROC / "proj_pop_wa.csv", index=False)

print("proj_23np working-age population saved:", wa.shape)
piv = wa[(wa.scenario == "BSL") & (wa.sex == "F")].pivot_table(
    index="country", columns="year", values="pop_15_64_proj")
print("\nBaseline (BSL) female working-age population, millions:")
print((piv[[2024, 2030, 2035]] / 1e6).round(2).to_string())
