# -*- coding: utf-8 -*-
"""
Head-to-head: does using the REAL Eurostat occupied-posts series (JOBOCC) as the
JVR denominator beat the current employment-calibration (occ_scale x employment)?

Isolates the denominator: both variants reconstruct the vacancy COUNT from the
SAME anchored-Beveridge forecast rate via V = O*r/(1-r); only O differs.
  CALIB : O = occ_scale[country] * total LFS employment  (current model)
  REAL  : O = JOBOCC (number of occupied posts, jvs_q_r21, annualised)

Rolling-origin backtest of the total vacancy count (held-out last 4 years), MAPE
on the subset of (country, year) where JOBOCC is observed. Read-only — prints only.
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

# ---- fetch JOBOCC (occupied posts), annualise quarterly (>=3 quarters) ----
flt = {"geo": C, "nace_r2_1": ["B-T"], "s_adj": ["NSA"], "sizeclas": ["TOTAL"], "indic_em": ["JOBOCC"]}
raw = eurostat.get_data_df("jvs_q_r21", flags=True, filter_pars=flt)
gcol = [c for c in raw.columns if c.endswith("TIME_PERIOD")][0]
raw = raw.rename(columns={gcol: "country"})
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
            occ[(r["country"], yr)] = float(np.mean(vs))   # persons


def _ctotals(c):
    f = panel[(panel.country == c) & (panel.sex == "F")].set_index("year")
    m = panel[(panel.country == c) & (panel.sex == "M")].set_index("year")
    Y, VC, VR, UT, ET, OO = [], [], [], [], [], []
    for y in sorted(set(f.index) & set(m.index)):
        vc, vr = f["vacancy_count"].get(y), f["vacancy_rate"].get(y)
        uF, uM = f["unemp_rate"].get(y), m["unemp_rate"].get(y)
        eF, eM = f["employed_ths"].get(y), m["employed_ths"].get(y)
        if any(pd.isna(z) for z in (vc, vr, uF, uM, eF, eM)):
            continue
        eF, eM = eF * 1000.0, eM * 1000.0
        Y.append(int(y)); VC.append(float(vc)); VR.append(float(vr))
        UT.append((uF * eF + uM * eM) / (eF + eM)); ET.append(eF + eM)
        OO.append(occ.get((c, int(y)), np.nan))
    return tuple(np.array(z, float) for z in (Y, VC, VR, UT, ET, OO))


calib, real, den = [], [], []        # vacancy-count APE (calib / real) and denominator APE
scatter = []                          # calibrated O vs real JOBOCC, per (country, year)
for c in C:
    Y, VC, VR, UT, ET, OO = _ctotals(c)
    n = len(Y)
    if n < 8:
        continue
    occ_k = bev.occ_scale.get(c, bev.occ_gi)
    # full-history scatter of the denominator (calibrated vs real), where JOBOCC observed
    for j in range(n):
        if np.isfinite(OO[j]):
            scatter.append({"c": c, "real": round(OO[j] / 1e6, 3),
                            "calib": round(occ_k * ET[j] / 1e6, 3)})
    for cut in range(n - TEST_H, n):
        fy = Y[cut:]
        if len(fy) == 0:
            continue
        un_pred = _ensemble_mean(Y[:cut], UT[:cut], fy, weighting="backtest")
        h = np.arange(1, len(fy) + 1)
        rate = bev.predict_anchored(un_pred, UT[cut - 1], VR[cut - 1], h, c, damp=0.6)
        rr = np.clip(rate / 100.0, 1e-4, 0.2)
        for j in range(len(fy)):
            a = VC[cut + j]
            o_calib = occ_k * ET[cut + j]
            v_calib = o_calib * rr[j] / (1 - rr[j])
            calib.append(abs(v_calib - a) / abs(a))
            o_real = OO[cut + j]
            if np.isfinite(o_real):
                v_real = o_real * rr[j] / (1 - rr[j])
                real.append(abs(v_real - a) / abs(a))
                den.append(abs(o_calib - o_real) / abs(o_real))   # how off is the calibrated O?


def summ(x):
    x = np.array(x, float)
    return {"n": int(len(x)), "mape": round(float(np.mean(x)) * 100, 1),
            "medape": round(float(np.median(x)) * 100, 1)}


result = {"vacancy_backtest": {"calib": summ(calib), "real": summ(real)},
          "denominator": summ(den), "scatter": scatter}
(OUT / "jobocc_compare.json").write_text(json.dumps(result, indent=1), encoding="utf-8")


def s(d):
    return f"n={d['n']:3d}  MAPE {d['mape']:5.1f}%  medAPE {d['medape']:5.1f}%"


print("Vacancy-COUNT backtest — same forecast rate, denominator swapped:")
print(f"  CALIB (occ_scale x employment) : {s(result['vacancy_backtest']['calib'])}")
print(f"  REAL  (JOBOCC occupied posts)  : {s(result['vacancy_backtest']['real'])}")
print(f"\nDenominator only — calibrated O vs real JOBOCC:  {s(result['denominator'])}")
print(f"\nwrote outputs/jobocc_compare.json ({len(scatter)} scatter points)")
