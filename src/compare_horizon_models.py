# -*- coding: utf-8 -*-
"""
Does using SEPARATE per-horizon models (a dedicated 3-, 6-, 9-year model) beat the
single horizon-aware ensemble? Rolling-origin backtest, pooled over the smooth
supply drivers, MAPE by horizon for three approaches:

  ENSEMBLE : the deployed horizon-aware ensemble (5 simple models, per-horizon weights)
  DIRECT   : a separate "direct" model per horizon h — OLS of y_(t+h) on y_t, fit on
             its own (y_t, y_(t+h)) pairs, then extrapolated from the last value.
  NAIVE    : last value held flat (the floor).

Writes outputs/horizon_models_compare.json. Read-only otherwise.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from forecast import _ensemble_mean, history

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
C = ["BG", "PL", "CZ", "RO", "DE", "FR", "NO", "CH"]
H = 9
panel = pd.read_parquet(ROOT / "data" / "processed" / "panel.parquet").copy()
panel["healthy_share"] = panel["hly_birth"] / panel["le_birth"]
panel["emp_rate"] = panel["employed_ths"] * 1000.0 / panel["pop_15_64"]
DRV = ["le_birth", "healthy_share", "working_life_yrs", "emp_rate"]

ens = {h: [] for h in range(1, H + 1)}
dire = {h: [] for h in range(1, H + 1)}
naive = {h: [] for h in range(1, H + 1)}
npairs = {h: [] for h in range(1, H + 1)}

for c in C:
    for s in ("F", "M"):
        for col in DRV:
            y, v = history(panel, c, s, col)
            n = len(v)
            if n < 12:
                continue
            for o in range(8, n - 1):                 # origin index (>=8 training pts)
                cut = o + 1
                hmax = min(H, n - 1 - o)
                if hmax < 1:
                    continue
                tgt = np.array([y[o] + h for h in range(1, hmax + 1)], float)
                em = _ensemble_mean(y[:cut], v[:cut], tgt, weighting="backtest")
                for h in range(1, hmax + 1):
                    a = v[o + h]
                    if a == 0:
                        continue
                    ens[h].append(abs(em[h - 1] - a) / abs(a))
                    naive[h].append(abs(v[o] - a) / abs(a))
                    # DIRECT per-horizon model: OLS y_(t+h) ~ y_t on training pairs
                    xs, ys = v[:cut - h], v[h:cut]
                    npairs[h].append(len(xs))
                    if len(xs) >= 4:
                        b1, b0 = np.polyfit(xs, ys, 1)
                        pred = b0 + b1 * v[o]
                    else:
                        pred = v[o]                   # too few pairs -> fall back to naive
                    dire[h].append(abs(pred - a) / abs(a))


def mp(d):
    return {h: (round(float(np.mean(x)) * 100, 1) if x else None) for h, x in d.items()}


res = {
    "horizons": list(range(1, H + 1)),
    "ensemble_mape": mp(ens), "direct_mape": mp(dire), "naive_mape": mp(naive),
    "direct_pairs_med": {h: (int(np.median(x)) if x else None) for h, x in npairs.items()},
    "n_eval": {h: len(x) for h, x in ens.items()},
}
(OUT / "horizon_models_compare.json").write_text(json.dumps(res, indent=1), encoding="utf-8")

print(f"{'h':>2} {'ENSEMBLE':>9} {'DIRECT':>8} {'NAIVE':>7} {'pairs':>6} {'n':>5}")
for h in range(1, H + 1):
    e, d, nv = res["ensemble_mape"][h], res["direct_mape"][h], res["naive_mape"][h]
    print(f"{h:>2} {e:>8}% {d:>7}% {nv:>6}% {res['direct_pairs_med'][h]:>6} {res['n_eval'][h]:>5}")
print("\nwrote outputs/horizon_models_compare.json")
