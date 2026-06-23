# -*- coding: utf-8 -*-
"""
Fixed train/test split validation: train on Eurostat history <= 2019, forecast the
held-out 2020-2024, compare to observed. Harder than rolling-origin (5-year horizon
spanning the COVID shock). Reports accuracy (1-MAPE) per driver and per level output.
Writes outputs/split_validation.json + console summary.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from forecast import _ensemble_mean, history

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
M = 1e6
COUNTRIES = ["BG", "PL", "CZ", "RO", "DE", "FR", "NO", "CH"]
TGT = [2020, 2021, 2022, 2023, 2024]
TRAIN_END = 2019

panel = pd.read_parquet(ROOT / "data" / "processed" / "panel.parquet").copy()
panel["healthy_share"] = panel.hly_birth / panel.le_birth
panel["emp_rate"] = panel.employed_ths * 1000 / panel.pop_15_64
ret = pd.read_csv(ROOT / "data" / "retirement_params.csv")
svc = {(r.country, r.sex): r.required_service_years for r in ret.itertuples()}
sobs = pd.read_csv(OUT / "supply_observed.csv")


def fc(c, s, col):
    y, v = history(panel, c, s, col)
    m = y <= TRAIN_END
    return _ensemble_mean(y[m], v[m], TGT)


def obs_comp(c, s, col, year):
    r = panel[(panel.country == c) & (panel.sex == s) & (panel.year == year)]
    return float(r[col].iloc[0]) if len(r) and pd.notna(r[col].iloc[0]) else np.nan


# ---- driver-level accuracy on the 2020-2024 holdout ----
DRV = {"le_birth": "Life expectancy", "healthy_share": "Healthy share (HLY/LE)",
       "emp_rate": "Employment rate", "working_life_yrs": "Working-life duration",
       "vacancy_count": "Job vacancies"}
drv_acc = {}
for col, lab in DRV.items():
    errs = []
    for c in COUNTRIES:
        for s in (["F", "M"] if col != "vacancy_count" else ["F"]):
            pred = fc(c, s, col)
            for i, y in enumerate(TGT):
                a = obs_comp(c, s, col, y)
                if not np.isnan(a) and a != 0:
                    errs.append(abs(pred[i] - a) / abs(a))
    drv_acc[col] = {"label": lab, "accuracy": round(1 - float(np.mean(errs)), 3),
                    "mape": round(float(np.mean(errs)) * 100, 1)}

# ---- composed level outputs on the holdout (8-country totals per year) ----
Sp = np.zeros(len(TGT)); Dp = np.zeros(len(TGT))
for c in COUNTRIES:
    supF = fc(c, "F", "pop_15_64") * fc(c, "F", "healthy_share") * fc(c, "F", "working_life_yrs")
    supM = fc(c, "M", "pop_15_64") * fc(c, "M", "healthy_share") * fc(c, "M", "working_life_yrs")
    empF = fc(c, "F", "emp_rate") * fc(c, "F", "pop_15_64")
    empM = fc(c, "M", "emp_rate") * fc(c, "M", "pop_15_64")
    vac = fc(c, "F", "vacancy_count")
    den = np.where(empF + empM == 0, 1, empF + empM)
    demF = (empF + vac * empF / den) * svc[(c, "F")]
    demM = (empM + vac * empM / den) * svc[(c, "M")]
    Sp += supF + supM
    Dp += demF + demM
Bp = Sp - Dp

oc = sobs[sobs.year.isin(TGT)].groupby("year").agg(
    S=("supply_realized", "sum"), D=("demand", "sum"), B=("balance_realized", "sum"))
So = np.array([oc.loc[y, "S"] for y in TGT])
Do = np.array([oc.loc[y, "D"] for y in TGT])
Bo = np.array([oc.loc[y, "B"] for y in TGT])

sup_mape = float(np.mean(np.abs(Sp - So) / So))
dem_mape = float(np.mean(np.abs(Dp - Do) / Do))
bal_mae = float(np.mean(np.abs(Bp - Bo)) / M)
bal_base = float(np.mean(np.abs(Bo)) / M)

level = {
    "supply_acc": round(1 - sup_mape, 3), "supply_mape": round(sup_mape * 100, 1),
    "demand_acc": round(1 - dem_mape, 3), "demand_mape": round(dem_mape * 100, 1),
    "balance_mae_m": round(bal_mae), "balance_base_m": round(bal_base),
    "balance_rel": round(bal_mae / bal_base * 100),
}
years = {str(y): {"supply_pred": round(Sp[i] / M), "supply_obs": round(So[i] / M),
                  "demand_pred": round(Dp[i] / M), "demand_obs": round(Do[i] / M),
                  "balance_pred": round(Bp[i] / M), "balance_obs": round(Bo[i] / M)}
         for i, y in enumerate(TGT)}
result = {"train_end": TRAIN_END, "test": TGT, "drivers": drv_acc, "level": level, "years": years}
(OUT / "split_validation.json").write_text(json.dumps(result, indent=1), encoding="utf-8")

print(f"=== Fixed split: train <= {TRAIN_END}, test {TGT[0]}-{TGT[-1]} (incl. COVID) ===")
print("\nDriver accuracy (1-MAPE) on holdout:")
for col, d in drv_acc.items():
    print(f"  {d['label']:24s} acc {d['accuracy']:.3f}  (MAPE {d['mape']}%)")
print("\nComposed level accuracy on holdout:")
print(f"  Supply : acc {level['supply_acc']:.3f}  (MAPE {level['supply_mape']}%)")
print(f"  Demand : acc {level['demand_acc']:.3f}  (MAPE {level['demand_mape']}%)")
print(f"  Balance: MAE +-{level['balance_mae_m']}M  (~{level['balance_rel']}% of |{level['balance_base_m']}M|)")
print("\nTotals by year (million person-years): pred vs obs")
print(f"  {'year':5s}{'supplyP':>9}{'supplyO':>9}{'demandP':>9}{'demandO':>9}{'balP':>7}{'balO':>7}")
for y in TGT:
    d = years[str(y)]
    print(f"  {y:<5d}{d['supply_pred']:>9}{d['supply_obs']:>9}{d['demand_pred']:>9}"
          f"{d['demand_obs']:>9}{d['balance_pred']:>7}{d['balance_obs']:>7}")
