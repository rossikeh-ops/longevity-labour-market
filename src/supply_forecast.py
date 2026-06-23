"""
Level 1 — forecast working-age potential SUPPLY to 2035, with Monte-Carlo bands.

Per (country, sex), combined per Monte-Carlo draw:

  potential_workers = pop_15_64 x healthy_share        (healthy_share = HLY_birth/LE_birth)
  supply_realized   = potential_workers x working_life_yrs

POPULATION uses Eurostat's own projection proj_23np (baseline BSL) instead of naive
extrapolation, because trend models wrongly grow the ageing West (DE etc.); the
migration variants (HMIGR/LMIGR) define the population uncertainty band.
healthy_share (HLY/LE ratio, bounded 0-1) and working_life_yrs are forecast on their
FULL history via the simple ensemble (decision D2). Retirement age held at baseline.

Outputs: outputs/supply_forecast.csv (per country-sex-year: mean/lo/hi)
         console: 8-country total supply 2024 -> 2035 with 80% band.
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd
from forecast import forecast_series, history, RNG

ROOT = Path(__file__).resolve().parents[1]
panel = pd.read_parquet(ROOT / "data" / "processed" / "panel.parquet")
OUT = ROOT / "outputs"; OUT.mkdir(exist_ok=True)
COUNTRIES = ["BG", "PL", "CZ", "RO", "DE", "FR", "NO", "CH"]
TGT = list(range(2025, 2036))
N = 1000

# add healthy_share to history source
panel = panel.copy()
panel["healthy_share"] = panel["hly_birth"] / panel["le_birth"]

# population projections (proj_23np): baseline + migration band
proj = pd.read_csv(ROOT / "data" / "processed" / "proj_pop_wa.csv")
proj_w = proj.pivot_table(index=["country", "sex", "year"], columns="scenario",
                          values="pop_15_64_proj").reset_index()


_obs24 = panel[panel.year == 2024].set_index(["country", "sex"])["pop_15_64"].to_dict()


def pop_proj_sims(c, s):
    """pop_15_64 draws from proj_23np, calibrated to observed 2024 (removes the
    proj-vs-observed level seam, large for BG post-census). mean=BSL, band~[LMIGR,HMIGR]."""
    sub = proj_w[(proj_w.country == c) & (proj_w.sex == s)].set_index("year").sort_index()
    cal = _obs24[(c, s)] / sub.loc[2024, "BSL"]
    sub = sub.reindex(TGT)
    bsl = sub["BSL"].to_numpy(float) * cal
    h = np.arange(1, len(TGT) + 1)
    mig = np.abs((sub["HMIGR"] - sub["LMIGR"]).to_numpy(float)) * cal / (2 * 1.2816)
    demog = bsl * 0.004 * h            # +fertility/mortality/model error (~0.4%/yr)
    sigma = np.sqrt(mig ** 2 + demog ** 2)
    return np.clip(RNG.normal(bsl, sigma, size=(N, len(TGT))), 0, None)


rows = []
total_sims = np.zeros((N, len(TGT)))
for c in COUNTRIES:
    for s in ["F", "M"]:
        yh, vh = history(panel, c, s, "healthy_share")
        yw, vw = history(panel, c, s, "working_life_yrs")
        pop_sims = pop_proj_sims(c, s)
        _, share_sims = forecast_series(yh, vh, TGT, N, bounds=(0.0, 1.0))
        _, wl_sims = forecast_series(yw, vw, TGT, N, nonneg=True)
        supply_sims = pop_sims * share_sims * wl_sims     # career person-years
        total_sims += supply_sims
        mean = supply_sims.mean(axis=0)
        lo = np.quantile(supply_sims, 0.10, axis=0)
        hi = np.quantile(supply_sims, 0.90, axis=0)
        for i, yr in enumerate(TGT):
            rows.append({"country": c, "sex": s, "year": yr,
                         "supply_realized": mean[i], "lo": lo[i], "hi": hi[i]})

fc = pd.DataFrame(rows)
fc.to_csv(OUT / "supply_forecast.csv", index=False)

M = 1e6
# observed 2024 total for reference
obs = pd.read_csv(OUT / "supply_observed.csv")
obs24 = obs[obs.year == 2024]["supply_realized"].sum() / M

print("=== Total realized working-age SUPPLY, 8 countries x M/F (million career PY) ===")
print(f"  2024 (observed): {obs24:,.0f}")
tmean = total_sims.mean(axis=0) / M
tlo = np.quantile(total_sims, 0.10, axis=0) / M
thi = np.quantile(total_sims, 0.90, axis=0) / M
for i, yr in enumerate(TGT):
    if yr in (2025, 2030, 2035):
        print(f"  {yr} (forecast): {tmean[i]:,.0f}   [80% band {tlo[i]:,.0f} - {thi[i]:,.0f}]")

print("\n=== Per-country supply: 2024 obs -> 2035 forecast (million career PY, both sexes) ===")
g35 = fc[fc.year == 2035].groupby("country")["supply_realized"].sum() / M
g24 = obs[obs.year == 2024].groupby("country")["supply_realized"].sum() / M
comp = pd.DataFrame({"2024": g24.round(0), "2035": g35.round(0)})
comp["chg_%"] = ((comp["2035"]/comp["2024"] - 1) * 100).round(1)
print(comp.sort_values("chg_%").to_string())
print(f"\nrows -> outputs/supply_forecast.csv ({len(fc)})")
