# -*- coding: utf-8 -*-
"""
Level 5 — Healthy retirement dividend.

Headline (per person): HEALTHY YEARS AFTER RETIREMENT = HLY − statutory retirement
age, by country × sex × year — positive where people stay healthy past retirement,
negative where health declines first. Aggregate stock for consumption:
  dividend person-years = Population × max(0, HLY − retirement age).

Both observed and forecast to 2033 (forecast HLY and population; retirement age held
at its statutory value). Then a DESCRIPTIVE test of whether the dividend drives
leisure/education/culture consumption (COICOP CP09 + CP10 + CP11). Honest finding:
cross-country it co-moves (size), within-country the link is ~0 (consumption tracks income).

Outputs: outputs/dividend_observed.csv, dividend_forecast.csv, dividend_relationship.json
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from forecast import forecast_series, history

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
panel = pd.read_parquet(ROOT / "data" / "processed" / "panel.parquet").copy()
rp = pd.read_csv(ROOT / "data" / "retirement_params.csv")
COUNTRIES = ["BG", "PL", "CZ", "RO", "DE", "FR", "NO", "CH"]
TGT = list(range(2025, 2034))
N = 1000
M = 1e6
COICOP = ["coicop_recreation", "coicop_education", "coicop_hotels_rest"]

ret = {(r.country, r.sex): r.statutory_retirement_age for r in rp.itertuples()}
panel["retage"] = panel.apply(lambda r: ret.get((r.country, r.sex), np.nan), axis=1)
panel["hdiv_pp"] = panel["hly_birth"] - panel["retage"]              # healthy yrs after retirement / person
panel["hdiv_py"] = panel["pop_total"] * panel["hdiv_pp"].clip(lower=0)
panel["leisure"] = panel[COICOP].sum(axis=1)


def q(a):
    return a.mean(axis=0), np.quantile(a, 0.10, axis=0), np.quantile(a, 0.90, axis=0)


# ---------- observed (country × sex × year) ----------
obs = panel.dropna(subset=["hdiv_pp", "pop_total"])[
    ["country", "sex", "year", "pop_total", "hly_birth", "retage", "hdiv_pp", "hdiv_py"]].copy()
obs = obs[obs.country.isin(COUNTRIES)].sort_values(["country", "sex", "year"])
obs.to_csv(OUT / "dividend_observed.csv", index=False)

# ---------- forecast to 2033 ----------
frows = []
for c in COUNTRIES:
    div_tot = np.zeros((N, len(TGT)))
    for s in ("F", "M"):
        yp, vp = history(panel, c, s, "pop_total")
        _, pop_s = forecast_series(yp, vp, TGT, N, nonneg=True)
        yh, vh = history(panel, c, s, "hly_birth")
        _, hly_s = forecast_series(yh, vh, TGT, N, nonneg=True)
        div_tot += pop_s * np.clip(hly_s - ret[(c, s)], 0, None)
    dm, dl, dh = q(div_tot)
    yl, vl = history(panel, c, "F", "leisure")        # leisure = sex=T, broadcast
    lf, _ = forecast_series(yl, vl, TGT, N, nonneg=True, log=True)
    for i, yr in enumerate(TGT):
        frows.append({"country": c, "year": yr,
                      "dividend_py": dm[i], "dividend_lo": dl[i], "dividend_hi": dh[i],
                      "leisure": float(lf["mean"].iloc[i])})
pd.DataFrame(frows).to_csv(OUT / "dividend_forecast.csv", index=False)

# ---------- descriptive relationship: dividend vs leisure/education/culture ----------
agg = (panel.groupby(["country", "year"])
       .agg(dividend=("hdiv_py", "sum"), leis=("leisure", "first")).reset_index())
d = agg.dropna(subset=["dividend", "leis"])
d = d[(d["dividend"] > 0) & (d["leis"] > 0)].sort_values(["country", "year"])

cs = sorted(d.country.unique())
yL = np.log(d["leis"].to_numpy(float))
xL = np.log(d["dividend"].to_numpy(float))
D = np.array([[1.0 if cc == c else 0.0 for c in cs] for cc in d["country"]])
X = np.column_stack([xL, D])
beta_lvl = np.linalg.lstsq(X, yL, rcond=None)[0][0]
yhat = X @ np.linalg.lstsq(X, yL, rcond=None)[0]
r2_lvl = 1 - ((yL - yhat) ** 2).sum() / ((yL - yL.mean()) ** 2).sum()

dx, dy = [], []
for c, g in d.groupby("country"):
    g = g.sort_values("year")
    dx += list(np.diff(np.log(g["dividend"].to_numpy(float))))
    dy += list(np.diff(np.log(g["leis"].to_numpy(float))))
dx, dy = np.array(dx), np.array(dy)
beta_d, b0 = np.polyfit(dx, dy, 1)
r2_d = 1 - ((dy - (b0 + beta_d * dx)) ** 2).sum() / ((dy - dy.mean()) ** 2).sum()

rel = {
    "elasticity_levels_fe": round(float(beta_lvl), 3), "r2_levels_fe": round(float(r2_lvl), 3),
    "elasticity_within_diff": round(float(beta_d), 3), "r2_within_diff": round(float(r2_d), 3),
    "corr_within_diff": round(float(np.corrcoef(dx, dy)[0, 1]), 3),
    "leisure_real_growth_pct": round(float(dy.mean()) * 100, 1),
    "n_levels": int(len(d)), "n_diff": int(len(dx)),
}
(OUT / "dividend_relationship.json").write_text(json.dumps(rel, indent=1), encoding="utf-8")

d24 = obs[obs.year == 2024]
pp = d24.groupby("country")["hdiv_pp"].mean()
div24 = round(obs[obs.year == 2024]["hdiv_py"].sum() / M)
f = pd.read_csv(OUT / "dividend_forecast.csv")
div33 = round(f[f.year == 2033]["dividend_py"].sum() / M)
print(f"healthy years after retirement / person 2024: {pp.idxmax()} {pp.max():+.1f} … {pp.idxmin()} {pp.min():+.1f}")
print(f"dividend person-years (positive): 2024 {div24:,}M -> 2033 {div33:,}M")
print(f"leisure link: cross-FE {rel['elasticity_levels_fe']} (R2 {rel['r2_levels_fe']}); "
      f"within-diff {rel['elasticity_within_diff']} (corr {rel['corr_within_diff']}) "
      f"— consumption grows {rel['leisure_real_growth_pct']}%/yr regardless")
