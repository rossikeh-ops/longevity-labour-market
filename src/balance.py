"""
Quick sanity check — OBSERVED person-year balance, 2011-2024 common window.

Mechanical identities only (no forecasting):
  Supply_{c,s,t} = pop_total x HLY_birth              (healthy person-years; case headline)
  jobs           = employed + vacancies (vacancies sex-apportioned by employment share)
  Demand_{c,s,t} = jobs x required_service_years      (person-years)
  Balance        = Supply - Demand                    (human-working-years)

Also reports a working-age-relevant supply variant for context:
  Supply_WA      = pop_total x HLY_65 fraction is NOT used here; instead we flag that
  the headline identity is an UPPER BOUND (counts every healthy year of the whole
  population). Level 1 refines supply to a working-age basis.

Outputs: outputs/observed_balance.csv  + console summary.
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
OUT = ROOT / "outputs"; OUT.mkdir(exist_ok=True)

p = pd.read_parquet(PROC / "panel_common.parquet")
ret = pd.read_csv(ROOT / "data" / "retirement_params.csv")

df = p.merge(ret[["country", "sex", "required_service_years"]], on=["country", "sex"])

# --- sex-apportion the total vacancy count by each sex's employment share ---
emp_tot = (df.groupby(["country", "year"])["employed_ths"].transform("sum"))
df["emp_share"] = df["employed_ths"] / emp_tot
df["vacancies_sex"] = df["vacancy_count"] * df["emp_share"]

# --- jobs (persons) = employed (ths->persons) + apportioned vacancies ---
df["jobs"] = df["employed_ths"] * 1000.0 + df["vacancies_sex"]

# --- person-year stocks ---
df["supply_py"] = df["pop_total"] * df["hly_birth"]            # healthy person-years
df["demand_py"] = df["jobs"] * df["required_service_years"]    # person-years
df["balance_py"] = df["supply_py"] - df["demand_py"]
df["supply_per_demand"] = df["supply_py"] / df["demand_py"]

cols = ["country", "sex", "year", "pop_total", "hly_birth", "employed_ths",
        "vacancies_sex", "jobs", "required_service_years",
        "supply_py", "demand_py", "balance_py", "supply_per_demand"]
df[cols].to_csv(OUT / "observed_balance.csv", index=False)

M = 1e6
print("=== OBSERVED person-year balance, 2024 (millions of person-years) ===")
snap = df[df.year == 2024].copy()
tbl = snap.assign(supply=snap.supply_py/M, demand=snap.demand_py/M,
                  balance=snap.balance_py/M, ratio=snap.supply_per_demand)
piv = tbl.pivot_table(index="country", columns="sex",
                      values=["supply", "demand", "balance"], aggfunc="first")
print(piv.round(1).to_string())

print("\n=== Totals across 8 countries, 2024 (million person-years) ===")
g = snap.groupby("sex").agg(supply=("supply_py", "sum"), demand=("demand_py", "sum"),
                            balance=("balance_py", "sum"))
g = (g / M).round(0)
g["supply/demand"] = (snap.groupby("sex").supply_py.sum() /
                      snap.groupby("sex").demand_py.sum()).round(2)
print(g.to_string())

print("\n=== Balance trend 2011 vs 2024 (million person-years, both sexes) ===")
tr = df.groupby("year").agg(supply=("supply_py", "sum"), demand=("demand_py", "sum"),
                            balance=("balance_py", "sum"))
tr = (tr / M)
print(tr.loc[[2011, 2017, 2024]].round(0).to_string())
print(f"\nrows written: {len(df)}  ->  outputs/observed_balance.csv")
print("NOTE: headline supply = pop x HLY-at-birth is an UPPER BOUND (counts all "
      "healthy years of the whole population, incl. children/retirees). Level 1 "
      "refines supply to a working-age basis.")
