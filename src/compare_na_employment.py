# -*- coding: utf-8 -*-
"""
Head-to-head: does using NATIONAL-ACCOUNTS domestic-concept employment
(nama_10_a64_e, EMP_DC, THS_PER) as the occupied-posts base beat the current
LFS residence-concept employment (lfsa_egan / employed_ths)?

The JVR denominator is O = occupied posts. We approximate it as occ_scale * E.
This swaps the employment series E (each with its OWN per-country calibration),
keeps the SAME anchored-Beveridge forecast rate, and measures:
  (a) vacancy-COUNT backtest MAPE with each base (rolling-origin, last 4 yrs);
  (b) how well each calibrated base tracks the REAL occupied posts (JOBOCC).
Domestic concept counts jobs in the territory (incl. cross-border commuters) —
expected to matter most for CH, NO, FR. Read-only — prints + small JSON.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
import eurostat
from forecast import _ensemble_mean
from vacancy_model import fit_beveridge

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
C = ["BG", "PL", "CZ", "RO", "DE", "FR", "NO", "CH"]
TEST_H = 4
panel = pd.read_parquet(ROOT / "data" / "processed" / "panel.parquet").copy()
bev = fit_beveridge(panel)


def _annualise_jobocc():
    flt = {"geo": C, "nace_r2_1": ["B-T"], "s_adj": ["NSA"], "sizeclas": ["TOTAL"], "indic_em": ["JOBOCC"]}
    raw = eurostat.get_data_df("jvs_q_r21", flags=True, filter_pars=flt)
    g = [c for c in raw.columns if c.endswith("TIME_PERIOD")][0]
    raw = raw.rename(columns={g: "country"})
    qcols = [c[:-6] for c in raw.columns if c.endswith("_value") and "Q" in c]
    occ = {}
    for _, r in raw.iterrows():
        if r["country"] not in C:
            continue
        by = {}
        for per in qcols:
            v = r.get(per + "_value")
            if pd.notna(v):
                by.setdefault(int(per[:4]), []).append(v)
        for yr, vs in by.items():
            if len(vs) >= 3:
                occ[(r["country"], yr)] = float(np.mean(vs))
    return occ


def _na_emp():
    flt = {"geo": C, "na_item": ["EMP_DC"], "unit": ["THS_PER"], "nace_r2": ["TOTAL"]}
    df = eurostat.get_data_df("nama_10_a64_e", flags=True, filter_pars=flt)
    g = [c for c in df.columns if c.endswith("TIME_PERIOD")][0]
    df = df.rename(columns={g: "country"})
    yrs = [c[:-6] for c in df.columns if c.endswith("_value")]
    out = {}
    for _, r in df.iterrows():
        if r["country"] not in C:
            continue
        for y in yrs:
            v = r.get(y + "_value")
            if pd.notna(v):
                out[(r["country"], int(y[:4]))] = float(v) * 1000.0   # persons
    return out


JOBOCC = _annualise_jobocc()
NAEMP = _na_emp()


def _ctotals(c):
    f = panel[(panel.country == c) & (panel.sex == "F")].set_index("year")
    m = panel[(panel.country == c) & (panel.sex == "M")].set_index("year")
    Y, VC, VR, UT, E_lfs, E_na, OO = [], [], [], [], [], [], []
    for y in sorted(set(f.index) & set(m.index)):
        vc, vr = f["vacancy_count"].get(y), f["vacancy_rate"].get(y)
        uF, uM = f["unemp_rate"].get(y), m["unemp_rate"].get(y)
        eF, eM = f["employed_ths"].get(y), m["employed_ths"].get(y)
        na = NAEMP.get((c, int(y)))
        if any(pd.isna(z) for z in (vc, vr, uF, uM, eF, eM)) or na is None:
            continue
        eF, eM = eF * 1000.0, eM * 1000.0
        Y.append(int(y)); VC.append(float(vc)); VR.append(float(vr))
        UT.append((uF * eF + uM * eM) / (eF + eM))
        E_lfs.append(eF + eM); E_na.append(na); OO.append(JOBOCC.get((c, int(y)), np.nan))
    return tuple(np.array(z, float) for z in (Y, VC, VR, UT, E_lfs, E_na, OO))


def _calib(VC, VR, E):
    """Per-country occupied-posts-to-employment scale: median implied_O / E."""
    ratios = []
    for vc, vr, e in zip(VC, VR, E):
        if vr > 0 and e > 0:
            ratios.append(vc * (100.0 / vr - 1.0) / e)
    return float(np.median(ratios)) if ratios else np.nan


ape = {"lfs": [], "na": []}
den = {"lfs": [], "na": []}                 # vs real JOBOCC
per_country = {}
for c in C:
    Y, VC, VR, UT, E_lfs, E_na, OO = _ctotals(c)
    n = len(Y)
    if n < 8:
        continue
    k_lfs, k_na = _calib(VC, VR, E_lfs), _calib(VC, VR, E_na)
    pc = {"lfs": [], "na": []}
    for cut in range(n - TEST_H, n):
        fy = Y[cut:]
        if len(fy) == 0:
            continue
        un = _ensemble_mean(Y[:cut], UT[:cut], fy, weighting="backtest")
        rate = bev.predict_anchored(un, UT[cut - 1], VR[cut - 1], np.arange(1, len(fy) + 1), c, damp=0.6)
        rr = np.clip(rate / 100.0, 1e-4, 0.2)
        for j in range(len(fy)):
            a = VC[cut + j]
            v_lfs = k_lfs * E_lfs[cut + j] * rr[j] / (1 - rr[j])
            v_na = k_na * E_na[cut + j] * rr[j] / (1 - rr[j])
            ape["lfs"].append(abs(v_lfs - a) / abs(a)); pc["lfs"].append(abs(v_lfs - a) / abs(a))
            ape["na"].append(abs(v_na - a) / abs(a)); pc["na"].append(abs(v_na - a) / abs(a))
            o = OO[cut + j]
            if np.isfinite(o):
                den["lfs"].append(abs(k_lfs * E_lfs[cut + j] - o) / o)
                den["na"].append(abs(k_na * E_na[cut + j] - o) / o)
    per_country[c] = {"lfs": round(float(np.mean(pc["lfs"])) * 100, 1),
                      "na": round(float(np.mean(pc["na"])) * 100, 1)}


def mp(x):
    x = np.array(x, float)
    return {"n": int(len(x)), "mape": round(float(np.mean(x)) * 100, 1), "medape": round(float(np.median(x)) * 100, 1)}


res = {"vacancy_backtest": {"lfs": mp(ape["lfs"]), "na": mp(ape["na"])},
       "denominator_vs_jobocc": {"lfs": mp(den["lfs"]), "na": mp(den["na"])},
       "per_country": per_country}
(OUT / "na_employment_compare.json").write_text(json.dumps(res, indent=1), encoding="utf-8")

print("Employment base for the occupied-posts denominator — LFS (residence) vs NA (domestic):")
print(f"  vacancy-count backtest  LFS {res['vacancy_backtest']['lfs']}")
print(f"                          NA  {res['vacancy_backtest']['na']}")
print(f"  denominator vs real JOBOCC  LFS {res['denominator_vs_jobocc']['lfs']}")
print(f"                              NA  {res['denominator_vs_jobocc']['na']}")
print("\nper-country vacancy-count MAPE (LFS -> NA):")
for c in C:
    if c in per_country:
        d = per_country[c]
        flag = "  <-- cross-border" if c in ("CH", "NO", "FR") else ""
        print(f"  {c}: {d['lfs']:5.1f}% -> {d['na']:5.1f}%{flag}")
