"""
Levels 2 & 3 — joint Monte-Carlo forecast of DEMAND, SUPPLY and BALANCE to 2035.

One module so supply and demand share the SAME population draws per MC index
(proj_23np) -> the balance = supply - demand keeps the correct correlation
(common population partly cancels), per the statistician review.

Per (country, sex), on FULL history (decision D2):
  SUPPLY  : pop_proj x healthy_share x working_life_yrs
  employment = emp_rate x pop_proj            (emp_rate forecast, bounded)
  vacancies  = vacancy_count (total) sex-apportioned by employment share
  jobs       = employment + vacancies
  DEMAND  : jobs x required_service_years
  BALANCE : supply - demand                   (human-working-years)

Population central = proj_23np BSL; band from migration variants (HMIGR/LMIGR).
Outputs: outputs/demand_forecast.csv, outputs/balance_forecast.csv
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd
from forecast import forecast_series, history, RNG

ROOT = Path(__file__).resolve().parents[1]
panel = pd.read_parquet(ROOT / "data" / "processed" / "panel.parquet").copy()
proj = pd.read_csv(ROOT / "data" / "processed" / "proj_pop_wa.csv")
ret = pd.read_csv(ROOT / "data" / "retirement_params.csv")
OUT = ROOT / "outputs"
COUNTRIES = ["BG", "PL", "CZ", "RO", "DE", "FR", "NO", "CH"]
TGT = list(range(2025, 2036))
N = 1000

panel["healthy_share"] = panel["hly_birth"] / panel["le_birth"]
panel["emp_rate"] = panel["employed_ths"] * 1000.0 / panel["pop_15_64"]
svc = {(r.country, r.sex): r.required_service_years for r in ret.itertuples()}
proj_w = proj.pivot_table(index=["country", "sex", "year"], columns="scenario",
                          values="pop_15_64_proj").reset_index()

# observed working-age population in 2024 (to calibrate the projection level)
_obs24 = (panel[panel.year == 2024].set_index(["country", "sex"])["pop_15_64"].to_dict())


def pop_sims(c, s):
    sub = proj_w[(proj_w.country == c) & (proj_w.sex == s)].set_index("year")
    cal = _obs24[(c, s)] / sub.loc[2024, "BSL"]          # remove proj-vs-observed seam
    sub = sub.reindex(TGT)
    bsl = sub["BSL"].to_numpy(float) * cal
    h = np.arange(1, len(TGT) + 1)
    mig = np.abs((sub["HMIGR"] - sub["LMIGR"]).to_numpy(float)) * cal / (2 * 1.2816)
    demog = bsl * 0.004 * h            # +fertility/mortality/model error (~0.4%/yr)
    sigma = np.sqrt(mig ** 2 + demog ** 2)
    return np.clip(RNG.normal(bsl, sigma, size=(N, len(TGT))), 0, None)


def fc(c, s, col, **kw):
    y, v = history(panel, c, s, col)
    _, sims = forecast_series(y, v, TGT, N, **kw)
    return sims


def last_obs(c, s, col):
    y, v = history(panel, c, s, col)
    return v[-1]


def q(a):
    return a.mean(axis=0), np.quantile(a, 0.10, axis=0), np.quantile(a, 0.90, axis=0)


drows, brows, srows = [], [], []
for c in COUNTRIES:
    pF, pM = pop_sims(c, "F"), pop_sims(c, "M")
    erF = fc(c, "F", "emp_rate", bounds=(0, 0.95))
    erM = fc(c, "M", "emp_rate", bounds=(0, 0.95))
    empF, empM = erF * pF, erM * pM
    vac = fc(c, "F", "vacancy_count", nonneg=True)        # total (broadcast); apportion
    denom = np.where((empF + empM) == 0, 1, empF + empM)
    jobsF = empF + vac * empF / denom
    jobsM = empM + vac * empM / denom
    demF, demM = jobsF * svc[(c, "F")], jobsM * svc[(c, "M")]

    # --- scenario: participation PLATEAU (emp_rate frozen at last observed) ---
    empF_pl, empM_pl = last_obs(c, "F", "emp_rate") * pF, last_obs(c, "M", "emp_rate") * pM
    den_pl = np.where((empF_pl + empM_pl) == 0, 1, empF_pl + empM_pl)
    demF_pl = (empF_pl + vac * empF_pl / den_pl) * svc[(c, "F")]
    demM_pl = (empM_pl + vac * empM_pl / den_pl) * svc[(c, "M")]
    base35 = (demF[:, -1] + demM[:, -1]).mean()
    plat35 = (demF_pl[:, -1] + demM_pl[:, -1]).mean()
    srows.append({"country": c, "demand_2035_baseline": base35,
                  "demand_2035_plateau": plat35})
    supF = pF * fc(c, "F", "healthy_share", bounds=(0, 1)) * fc(c, "F", "working_life_yrs", nonneg=True)
    supM = pM * fc(c, "M", "healthy_share", bounds=(0, 1)) * fc(c, "M", "working_life_yrs", nonneg=True)
    balF, balM = supF - demF, supM - demM
    for s, jobs, dem, sup, bal in [("F", jobsF, demF, supF, balF),
                                   ("M", jobsM, demM, supM, balM)]:
        jm, _, _ = q(jobs); dm, dl, dh = q(dem)
        sm, _, _ = q(sup); bm, bl, bh = q(bal)
        for i, yr in enumerate(TGT):
            drows.append({"country": c, "sex": s, "year": yr, "jobs": jm[i],
                          "demand": dm[i], "demand_lo": dl[i], "demand_hi": dh[i]})
            brows.append({"country": c, "sex": s, "year": yr,
                          "supply": sm[i], "demand": dm[i], "balance": bm[i],
                          "balance_lo": bl[i], "balance_hi": bh[i]})

dfd = pd.DataFrame(drows); dfd.to_csv(OUT / "demand_forecast.csv", index=False)
dfb = pd.DataFrame(brows); dfb.to_csv(OUT / "balance_forecast.csv", index=False)
dfs = pd.DataFrame(srows); dfs.to_csv(OUT / "scenario_participation.csv", index=False)

M = 1e6
obs = pd.read_csv(OUT / "supply_observed.csv")
od = obs[obs.year == 2024].groupby("country")["demand"].sum() / M
print("=== Level 2 DEMAND: 2024 observed -> 2035 forecast (million career PY, both sexes) ===")
d35 = dfd[dfd.year == 2035].groupby("country")["demand"].sum() / M
comp = pd.DataFrame({"2024": od.round(0), "2035": d35.round(0)})
comp["chg_%"] = ((comp["2035"] / comp["2024"] - 1) * 100).round(1)
print(comp.sort_values("chg_%").to_string())
tot = dfd.groupby("year")["demand"].sum() / M
print(f"\n8-country total demand: 2024={od.sum():,.0f}  "
      f"2030={tot[2030]:,.0f}  2035={tot[2035]:,.0f} (million career PY)")

# widened-band check + participation-plateau scenario
w = dfd[dfd.year == 2035].copy()
relw = ((w["demand_hi"] - w["demand_lo"]) / w["demand"] * 100)
print(f"\n2035 demand 80% band width (% of point): "
      f"min {relw.min():.0f}%  median {relw.median():.0f}%  max {relw.max():.0f}%")

print("\n=== Participation-PLATEAU scenario, 2035 demand (million career PY) ===")
dfs["base"] = (dfs.demand_2035_baseline / M).round(0)
dfs["plateau"] = (dfs.demand_2035_plateau / M).round(0)
dfs["gap_%"] = ((dfs.demand_2035_plateau / dfs.demand_2035_baseline - 1) * 100).round(1)
print(dfs[["country", "base", "plateau", "gap_%"]].sort_values("gap_%").to_string(index=False))
print(f"rows -> demand_forecast.csv ({len(dfd)}), balance_forecast.csv ({len(dfb)}), "
      f"scenario_participation.csv ({len(dfs)})")
