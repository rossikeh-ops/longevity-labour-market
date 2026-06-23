"""
Level 1 — working-age potential labour SUPPLY (observed, 2011-2024).

Fixes the upper-bound caveat of the headline identity (pop x HLY-at-birth, which
counts children/retirees). Supply is recast as a *career person-year stock*,
directly comparable to demand (= jobs x required_service):

  healthy_share        = HLY_birth / LE_birth                 (lifetime healthy fraction)
  potential_workers    = pop_15_64 x healthy_share            (health-adjusted working-age people)
  span_ceiling         = retirement_age - 15                  (max possible working span)
  Supply_ceiling (PY)  = potential_workers x span_ceiling     (upper bound, all work full careers)
  Supply_realized (PY) = potential_workers x working_life_yrs (anchored to expected working life, DWL)
  realization_ratio    = working_life_yrs / span_ceiling      (participation/health gap)

Demand and the two balances are recomputed on the same basis.
Output: outputs/supply_observed.csv + console summary.
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
p = pd.read_parquet(ROOT / "data" / "processed" / "panel_common.parquet")
ret = pd.read_csv(ROOT / "data" / "retirement_params.csv")
OUT = ROOT / "outputs"; OUT.mkdir(exist_ok=True)

df = p.merge(ret[["country", "sex", "statutory_retirement_age",
                  "required_service_years"]], on=["country", "sex"])

# --- supply (career person-years) ---
df["healthy_share"] = df["hly_birth"] / df["le_birth"]
df["potential_workers"] = df["pop_15_64"] * df["healthy_share"]
df["span_ceiling"] = df["statutory_retirement_age"] - 15
df["supply_ceiling"] = df["potential_workers"] * df["span_ceiling"]
df["supply_realized"] = df["potential_workers"] * df["working_life_yrs"]
df["realization_ratio"] = df["working_life_yrs"] / df["span_ceiling"]

# --- demand (career person-years), vacancies sex-apportioned by employment share ---
emp_tot = df.groupby(["country", "year"])["employed_ths"].transform("sum")
df["vacancies_sex"] = df["vacancy_count"] * df["employed_ths"] / emp_tot
df["jobs"] = df["employed_ths"] * 1000.0 + df["vacancies_sex"]
df["demand"] = df["jobs"] * df["required_service_years"]

df["balance_ceiling"] = df["supply_ceiling"] - df["demand"]
df["balance_realized"] = df["supply_realized"] - df["demand"]

df.to_csv(OUT / "supply_observed.csv", index=False)

M = 1e6
snap = df[df.year == 2024].copy()
print("=== Level 1 working-age SUPPLY vs DEMAND, 2024 (million career person-years) ===")
t = snap.assign(workers=snap.potential_workers/M, sup_ceil=snap.supply_ceiling/M,
                sup_real=snap.supply_realized/M, dem=snap.demand/M,
                bal_ceil=snap.balance_ceiling/M, bal_real=snap.balance_realized/M)
view = t.groupby(["country", "sex"]).agg(
    workers_m=("workers", "first"), supply_realized=("sup_real", "first"),
    demand=("dem", "first"), balance_realized=("bal_real", "first"),
    realiz=("realization_ratio", "first")).round(1)
print(view.to_string())

print("\n=== 8-country totals, 2024 (million career person-years) ===")
for label, col in [("supply_ceiling", "supply_ceiling"),
                   ("supply_realized", "supply_realized"),
                   ("demand", "demand"),
                   ("balance_realized", "balance_realized")]:
    print(f"  {label:18s}: {snap[col].sum()/M:,.0f}")
print(f"  realized supply/demand : {snap['supply_realized'].sum()/snap['demand'].sum():.2f}")

print("\n=== Country-sex in REALIZED deficit (balance_realized < 0), 2024 ===")
dfc = snap[snap.balance_realized < 0][["country", "sex", "balance_realized"]]
dfc = dfc.assign(balance_m=(dfc.balance_realized/M).round(1)).drop(columns="balance_realized")
print(dfc.to_string(index=False) if len(dfc) else "  none")
print(f"\nrows -> outputs/supply_observed.csv  ({len(df)})")
