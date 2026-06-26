# -*- coding: utf-8 -*-
"""
Is POOLING the Beveridge slope across 8 countries justified? Leave-ONE-COUNTRY-out.

The deployed vacancy model fits ONE shared Beveridge slope (vacancies fall when
unemployment rises) over all countries, with country fixed effects. The anchored
forecast uses only that SHARED SLOPE (the level cancels via anchoring), so we can
test transfer directly: for each held-out country, predict its vacancy COUNT with
a slope estimated three ways and see which generalises —

  POOLED : slope fitted on ALL 8 countries (the deployed choice)
  LOCO   : slope fitted on the OTHER 7 (country fully held out) -> pure transfer
  OWN    : slope fitted on the held-out country alone (within-country)
  NAIVE  : last vacancy rate held flat (slope = 0)

Rolling-origin over each country's last TEST_H years; unemployment forecast by the
ensemble; vacancy rate anchored + damped; count rebuilt from observed occupied
posts (isolates the rate model). Writes outputs/beveridge_loco.json.
"""
from __future__ import annotations
import json
import warnings
from pathlib import Path
import numpy as np
import pandas as pd
from forecast import _ensemble_mean
from vacancy_model import fit_beveridge

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
C = ["BG", "PL", "CZ", "RO", "DE", "FR", "NO", "CH"]
TEST_H, DAMP = 5, 0.6
panel = pd.read_parquet(ROOT / "data" / "processed" / "panel.parquet").copy()

bev_pool = fit_beveridge(panel)
slope_pool = bev_pool.slope
slope_loco = {c: fit_beveridge(panel[panel.country != c]).slope for c in C}
slope_own = {c: fit_beveridge(panel[panel.country == c]).slope for c in C}


def ctotals(c):
    f = panel[(panel.country == c) & (panel.sex == "F")].set_index("year")
    m = panel[(panel.country == c) & (panel.sex == "M")].set_index("year")
    Y, VC, VR, UT, ET = [], [], [], [], []
    for y in sorted(set(f.index) & set(m.index)):
        vc, vr = f["vacancy_count"].get(y), f["vacancy_rate"].get(y)
        uF, uM = f["unemp_rate"].get(y), m["unemp_rate"].get(y)
        eF, eM = f["employed_ths"].get(y), m["employed_ths"].get(y)
        if any(pd.isna(z) for z in (vc, vr, uF, uM, eF, eM)):
            continue
        eF, eM = eF * 1000.0, eM * 1000.0
        Y.append(int(y)); VC.append(float(vc)); VR.append(float(vr))
        UT.append((uF * eF + uM * eM) / (eF + eM)); ET.append(eF + eM)
    return tuple(np.array(z, float) for z in (Y, VC, VR, UT, ET))


def anchored_rate(slope, un_pred, last_u, last_vr, h):
    dev = np.asarray(un_pred, float) - float(last_u)
    return np.clip(last_vr + (DAMP ** (np.asarray(h, float) - 1.0)) * slope * dev,
                   bev_pool.lo, bev_pool.hi)


err = {k: [] for k in ("pooled", "loco", "own", "naive")}
for c in C:
    Y, VC, VR, UT, ET = ctotals(c)
    n = len(Y)
    if n < 10:
        continue
    for cut in range(n - TEST_H, n):
        fy = Y[cut:]
        if len(fy) == 0:
            continue
        un = _ensemble_mean(Y[:cut], UT[:cut], fy, weighting="backtest")
        h = np.arange(1, len(fy) + 1)
        slopes = {"pooled": slope_pool, "loco": slope_loco[c], "own": slope_own[c], "naive": 0.0}
        for name, sl in slopes.items():
            rate = anchored_rate(sl, un, UT[cut - 1], VR[cut - 1], h)
            cnt = bev_pool.reconstruct_count(rate, ET[cut:cut + len(fy)], c)
            for j in range(len(fy)):
                a = VC[cut + j]
                if a != 0:
                    err[name].append(abs(cnt[j] - a) / abs(a))


def mape(x):
    return round(float(np.mean(x)) * 100, 1) if x else None


res = {
    "slopes": {"pooled": round(slope_pool, 4),
               "loco_mean": round(float(np.mean(list(slope_loco.values()))), 4),
               "own_mean": round(float(np.mean(list(slope_own.values()))), 4),
               "own_range": [round(min(slope_own.values()), 4), round(max(slope_own.values()), 4)]},
    "mape": {k: mape(v) for k, v in err.items()},
    "skill_vs_naive": {k: (round(1 - np.mean(err[k]) / np.mean(err["naive"]), 3)
                           if err["naive"] and err[k] else None) for k in ("pooled", "loco", "own")},
    "n": len(err["pooled"]), "test_h": TEST_H,
}
(OUT / "beveridge_loco.json").write_text(json.dumps(res, indent=1), encoding="utf-8")

print("=== Beveridge slope: does pooling across countries justify itself? (leave-one-country-out) ===")
print(f"slopes  pooled {res['slopes']['pooled']:+.3f} | LOCO-mean {res['slopes']['loco_mean']:+.3f} | "
      f"own-mean {res['slopes']['own_mean']:+.3f} (range {res['slopes']['own_range']})")
print(f"\n{'slope source':12s} {'MAPE':>7} {'skill vs naive':>15}")
for k in ("pooled", "loco", "own", "naive"):
    sk = res["skill_vs_naive"].get(k)
    print(f"{k:12s} {res['mape'][k]:>6}% {('' if sk is None else f'{sk:+.3f}'):>15}")
print(f"\nn={res['n']} country-horizon evaluations; wrote outputs/beveridge_loco.json")
