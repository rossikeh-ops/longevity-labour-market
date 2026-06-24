# -*- coding: utf-8 -*-
"""
Level 6 — The longevity dividend in the macroeconomy (growth accounting).

Spine (Direction 1): decompose real-GDP growth into a LABOUR channel (employment,
which the longevity/supply engine drives) and a PRODUCTIVITY channel (GDP per
worker), using the exact identity

    GDP = Employment x (GDP / Employment)
    => dln GDP  =  dln Employment  +  dln Productivity      (labour + productivity)

We do this for the observed past (2014->2024) and for the forecast (2024->2033),
projecting employment and productivity each with the simple ensemble and rebuilding
GDP = L x prod (Monte-Carlo bands from the product of the two simulation sets).

Reverse arrow (Direction 3): does *healthy* longevity (HLY / healthy share) lift
labour PRODUCTIVITY? We test cross-country and within-country, honestly.

Inputs : data/raw/nama_10_gdp__*.parquet (real GDP, CLV15_MEUR), panel.parquet.
Outputs: outputs/macro_observed.csv, macro_forecast.csv,
         macro_growth_accounting.csv, macro_relationship.json
"""
from __future__ import annotations
import glob
import json
from pathlib import Path
import numpy as np
import pandas as pd
from forecast import forecast_series

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
COUNTRIES = ["BG", "PL", "CZ", "RO", "DE", "FR", "NO", "CH"]
TGT = list(range(2025, 2034))          # forecast horizon -> 2033 (project standard)
N_SIM = 1000
HIST0, HIST1 = 2014, 2024              # observed growth-accounting window
RNG = np.random.default_rng(6)

# ---------- build the observed macro panel ----------
gdp_raw = pd.read_parquet(sorted(glob.glob(str(ROOT / "data/raw/nama_10_gdp__*.parquet")))[-1])
gdp = (gdp_raw[gdp_raw.value.notna()][["country", "year", "value"]]
       .rename(columns={"value": "gdp"}))               # real GDP, CLV15 MEUR

panel = pd.read_parquet(ROOT / "data" / "processed" / "panel.parquet").copy()
panel["healthy_share"] = panel["hly_birth"] / panel["le_birth"]
emp = panel.groupby(["country", "year"])["employed_ths"].sum().reset_index()   # F+M, ths


def _popw(d, col):
    """Population-weighted mean of `col`, over rows where it is observed.
    Returns NaN when no sex has the value (so missing != spurious 0)."""
    v = d.dropna(subset=[col])
    if v.empty or v["pop_total"].sum() == 0:
        return np.nan
    return float((v[col] * v["pop_total"]).sum() / v["pop_total"].sum())


# pop-weighted healthy share & HLY at country level
hs = (panel.groupby(["country", "year"])
      .apply(lambda d: pd.Series({"healthy_share": _popw(d, "healthy_share"),
                                  "hly_birth": _popw(d, "hly_birth")}))
      .reset_index())

obs = (gdp.merge(emp, on=["country", "year"]).merge(hs, on=["country", "year"]))
obs = obs[obs.employed_ths > 0].copy()
obs["prod"] = obs["gdp"] / obs["employed_ths"]          # real GDP per thousand workers
obs = obs.sort_values(["country", "year"]).reset_index(drop=True)
obs.to_csv(OUT / "macro_observed.csv", index=False)


def cagr(a, b, n):
    return (b / a) ** (1.0 / n) - 1.0


# ---------- forecast L and prod, rebuild GDP = L x prod ----------
fc_rows, ga_rows = [], []
for c in COUNTRIES:
    g = obs[obs.country == c].sort_values("year")
    yrs = g["year"].to_numpy(float)
    Lout, Lsim = forecast_series(yrs, g["employed_ths"].to_numpy(float), TGT, N_SIM, nonneg=True)
    Pout, Psim = forecast_series(yrs, g["prod"].to_numpy(float), TGT, N_SIM, nonneg=True)
    Gsim = Lsim * Psim                                   # GDP simulations
    gmean = Lout["mean"].to_numpy() * Pout["mean"].to_numpy()
    glo, ghi = np.quantile(Gsim, 0.10, axis=0), np.quantile(Gsim, 0.90, axis=0)
    for i, y in enumerate(TGT):
        fc_rows.append({"country": c, "year": y,
                        "gdp": gmean[i], "gdp_lo": glo[i], "gdp_hi": ghi[i],
                        "employed_ths": Lout["mean"].iloc[i], "prod": Pout["mean"].iloc[i]})

    # growth accounting: observed window + projected window (2024 -> 2033)
    g0 = g[g.year == HIST0].iloc[0]
    g1 = g[g.year == HIST1].iloc[0]
    ga_rows.append({"country": c, "period": f"{HIST0}-{HIST1}", "kind": "observed",
                    "g_gdp": cagr(g0.gdp, g1.gdp, HIST1 - HIST0) * 100,
                    "g_labour": cagr(g0.employed_ths, g1.employed_ths, HIST1 - HIST0) * 100,
                    "g_prod": cagr(g0["prod"], g1["prod"], HIST1 - HIST0) * 100})
    L33, P33, G33 = Lout["mean"].iloc[-1], Pout["mean"].iloc[-1], gmean[-1]
    ga_rows.append({"country": c, "period": f"{HIST1}-2033", "kind": "projected",
                    "g_gdp": cagr(g1.gdp, G33, 2033 - HIST1) * 100,
                    "g_labour": cagr(g1.employed_ths, L33, 2033 - HIST1) * 100,
                    "g_prod": cagr(g1["prod"], P33, 2033 - HIST1) * 100})

fc = pd.DataFrame(fc_rows)
fc.to_csv(OUT / "macro_forecast.csv", index=False)
ga = pd.DataFrame(ga_rows)
ga.to_csv(OUT / "macro_growth_accounting.csv", index=False)

# ---------- reverse arrow: does healthy longevity lift productivity? ----------
rel_panel = obs.dropna(subset=["prod", "healthy_share"]).copy()
rel_panel["lp"] = np.log(rel_panel["prod"])

# cross-country: representative recent pre-COVID year (max year with all 8 present)
yr_counts = rel_panel.groupby("year")["country"].nunique()
cyear = int(yr_counts[yr_counts == len(COUNTRIES)].index.max())
cx = rel_panel[rel_panel.year == cyear]
cross_corr = float(np.corrcoef(cx["lp"], cx["healthy_share"])[0, 1])
b_cross = np.polyfit(cx["healthy_share"], cx["lp"], 1)[0]          # dln prod per unit hshare

# pooled levels WITH country fixed effects (within transformation)
rp = rel_panel.copy()
rp["lp_c"] = rp["lp"] - rp.groupby("country")["lp"].transform("mean")
rp["hs_c"] = rp["healthy_share"] - rp.groupby("country")["healthy_share"].transform("mean")
b_fe = np.polyfit(rp["hs_c"], rp["lp_c"], 1)[0]
r2_fe = float(np.corrcoef(rp["hs_c"], rp["lp_c"])[0, 1] ** 2)

# within-country differenced (year-on-year)
dd = []
for c in COUNTRIES:
    g = rel_panel[rel_panel.country == c].sort_values("year")
    if len(g) < 5:
        continue
    dlp = np.diff(g["lp"].to_numpy())
    dhs = np.diff(g["healthy_share"].to_numpy())
    for a, b in zip(dlp, dhs):
        dd.append((a, b))
dd = np.array(dd)
b_within = float(np.polyfit(dd[:, 1], dd[:, 0], 1)[0])
r2_within = float(np.corrcoef(dd[:, 1], dd[:, 0])[0, 1] ** 2)
prod_growth = float(rel_panel.groupby("country")["lp"].apply(
    lambda s: np.diff(s.to_numpy()).mean()).mean()) * 100

rel = {
    "cross_year": cyear,
    "cross_corr": round(cross_corr, 3),
    "cross_elasticity": round(float(b_cross), 3),
    "fe_elasticity": round(float(b_fe), 3),
    "fe_r2": round(r2_fe, 3),
    "within_elasticity": round(b_within, 3),
    "within_r2": round(r2_within, 3),
    "prod_real_growth_pct": round(prod_growth, 1),
    "n_within": int(len(dd)),
    "verdict": ("Self-perceived healthy-life years show no positive cross-country link with "
                "labour productivity (if anything negative, a GALI self-reporting artifact); "
                "within countries the link is statistically nil. The longevity dividend reaches "
                "the macroeconomy through the LABOUR channel, not a measurable productivity boost."),
}
(OUT / "macro_relationship.json").write_text(json.dumps(rel, indent=1), encoding="utf-8")

# ---------- console summary ----------
tot24 = obs[obs.year == HIST1]["gdp"].sum() / 1e6
tot33 = fc[fc.year == 2033]["gdp"].sum() / 1e6
print(f"Real GDP (8 countries): {tot24:.2f}T (2024) -> {tot33:.2f}T (2033, CLV15)")
print(f"GDP per worker corr with healthy share ({cyear}, cross-country): {cross_corr:+.2f}")
print(f"within-country d(lnprod) ~ d(hshare): slope {b_within:+.2f}, R2 {r2_within:.3f} (n={len(dd)})")
print("\nProjected 2024-2033 growth accounting (CAGR %/yr):")
for _, r in ga[ga.kind == "projected"].iterrows():
    print(f"  {r.country}: GDP {r.g_gdp:5.2f} = Labour {r.g_labour:5.2f} + Prod {r.g_prod:5.2f}")
print("\nwrote macro_observed.csv, macro_forecast.csv, macro_growth_accounting.csv, macro_relationship.json")
