# -*- coding: utf-8 -*-
"""
Level 4 — Cost of unhealthy years.

Robust output: the POOR-HEALTH BURDEN in person-years = Population × (LE − HLY),
by country × sex × year, observed and forecast to 2033 (Monte-Carlo bands), via the
same ensemble as Levels 1–3 (forecast population and per-person poor-health years,
then multiply).

Descriptive relationship (NOT causal): we test whether that burden drives the
NACE-Q "Human health & social work" sector's value added. The honest finding —
cross-country the two scale together (a size artefact), but WITHIN a country over
time the link is statistically negligible (the sector tracks GDP, not the burden).

Outputs: outputs/cost_observed.csv, cost_forecast.csv, cost_relationship.json
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
COUNTRIES = ["BG", "PL", "CZ", "RO", "DE", "FR", "NO", "CH"]
TGT = list(range(2025, 2034))
N = 1000
M = 1e6

panel["poor_pp"] = panel["le_birth"] - panel["hly_birth"]          # poor-health years / person
panel["poor_py"] = panel["pop_total"] * panel["poor_pp"]           # poor-health person-years


def q(a):
    return a.mean(axis=0), np.quantile(a, 0.10, axis=0), np.quantile(a, 0.90, axis=0)


# ---------- observed burden (country × sex × year) ----------
obs = panel.dropna(subset=["poor_pp", "pop_total"])[
    ["country", "sex", "year", "pop_total", "le_birth", "hly_birth", "poor_pp", "poor_py"]].copy()
obs = obs[obs.country.isin(COUNTRIES)].sort_values(["country", "sex", "year"])
obs.to_csv(OUT / "cost_observed.csv", index=False)

# ---------- forecast burden to 2033 (pop × poor-years/person), MC ----------
frows = []
for c in COUNTRIES:
    poor_tot = np.zeros((N, len(TGT)))
    for s in ("F", "M"):
        yp, vp = history(panel, c, s, "pop_total")
        _, pop_s = forecast_series(yp, vp, TGT, N, nonneg=True)
        yh, vh = history(panel, c, s, "poor_pp")
        _, pp_s = forecast_series(yh, vh, TGT, N, nonneg=True)
        poor_tot += pop_s * pp_s
    pm, pl, ph = q(poor_tot)
    # NACE-Q value added: forecast its own trend (sector tracks the economy)
    yq, vq = history(panel, c, "F", "nace_q_va")          # sex=T value, broadcast
    qf, _ = forecast_series(yq, vq, TGT, N, nonneg=True, log=True)
    for i, yr in enumerate(TGT):
        frows.append({"country": c, "year": yr,
                      "poor_py": pm[i], "poor_lo": pl[i], "poor_hi": ph[i],
                      "nace_q_va": float(qf["mean"].iloc[i]),
                      "nace_q_lo": float(qf["lo"].iloc[i]), "nace_q_hi": float(qf["hi"].iloc[i])})
pd.DataFrame(frows).to_csv(OUT / "cost_forecast.csv", index=False)

# ---------- descriptive relationship: burden vs NACE-Q value added ----------
agg = (panel.groupby(["country", "year"])
       .agg(poor=("poor_py", "sum"), qva=("nace_q_va", "first"),
            govh=("gov_health_exp", "first"), govs=("gov_social_exp", "first")).reset_index())
d = agg.dropna(subset=["poor", "qva"])
d = d[(d.poor > 0) & (d.qva > 0)].sort_values(["country", "year"])

# (a) cross-sectional / levels with country FE (size artefact)
cs = sorted(d.country.unique())
yL = np.log(d["qva"].to_numpy(float))
xL = np.log(d["poor"].to_numpy(float))
D = np.array([[1.0 if cc == c else 0.0 for c in cs] for cc in d["country"]])
beta_lvl = np.linalg.lstsq(np.column_stack([xL, D]), yL, rcond=None)[0][0]
r2_lvl = 1 - ((yL - np.column_stack([xL, D]) @ np.linalg.lstsq(np.column_stack([xL, D]), yL, rcond=None)[0]) ** 2).sum() / ((yL - yL.mean()) ** 2).sum()

# (b) within-country first differences (the honest short-run link)
dx, dy = [], []
for c, g in d.groupby("country"):
    g = g.sort_values("year")
    dx += list(np.diff(np.log(g["poor"].to_numpy(float))))
    dy += list(np.diff(np.log(g["qva"].to_numpy(float))))
dx, dy = np.array(dx), np.array(dy)
beta_d, b0 = np.polyfit(dx, dy, 1)
r2_d = 1 - ((dy - (b0 + beta_d * dx)) ** 2).sum() / ((dy - dy.mean()) ** 2).sum()
corr_d = float(np.corrcoef(dx, dy)[0, 1])

rel = {
    "elasticity_levels_fe": round(float(beta_lvl), 3), "r2_levels_fe": round(float(r2_lvl), 3),
    "elasticity_within_diff": round(float(beta_d), 3), "r2_within_diff": round(float(r2_d), 3),
    "corr_within_diff": round(corr_d, 3),
    "q_real_growth_pct": round(float(dy.mean()) * 100, 1),
    "burden_growth_pct": round(float(dx.mean()) * 100, 2),
    "n_levels": int(len(d)), "n_diff": int(len(dx)),
}
(OUT / "cost_relationship.json").write_text(json.dumps(rel, indent=1), encoding="utf-8")

# headline totals
b24 = obs[obs.year == 2024].groupby("country")["poor_py"].sum().sum() / M
f = pd.read_csv(OUT / "cost_forecast.csv")
b33 = f[f.year == 2033]["poor_py"].sum() / M
print(f"poor-health burden: 2024 {b24:,.0f}M -> 2033 {b33:,.0f}M person-years ({(b33/b24-1)*100:+.1f}%)")
print(f"NACE-Q link: cross-FE elasticity {rel['elasticity_levels_fe']} (R2 {rel['r2_levels_fe']}); "
      f"within-diff elasticity {rel['elasticity_within_diff']} (R2 {rel['r2_within_diff']}, corr {rel['corr_within_diff']}) "
      f"— sector grows {rel['q_real_growth_pct']}%/yr regardless of the burden")
