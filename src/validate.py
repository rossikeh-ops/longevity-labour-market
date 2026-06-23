"""
Model validation — rolling-origin backtest of the ensemble forecaster.

For each driver series (per country x sex) we hold out the last few years, forecast
them from history only, and compare to actuals. Metrics per indicator:
  MAPE (ensemble)      mean abs % error of the ensemble point forecast
  MAPE (naive)         same for a last-value baseline
  skill                1 - MAPE_ens / MAPE_naive   (>0 means better than naive)
  coverage80           share of held-out actuals inside the 80% band (target 0.80)
Also keeps observed-vs-predicted traces for a few showcase series (for charts).

Writes outputs/validation_metrics.json.
"""
from __future__ import annotations
from pathlib import Path
import json
import numpy as np
import pandas as pd
from forecast import forecast_series, history, _ensemble_mean

ROOT = Path(__file__).resolve().parents[1]
panel = pd.read_parquet(ROOT / "data" / "processed" / "panel.parquet").copy()
panel["healthy_share"] = panel["hly_birth"] / panel["le_birth"]
panel["emp_rate"] = panel["employed_ths"] * 1000.0 / panel["pop_15_64"]
OUT = ROOT / "outputs"
COUNTRIES = ["BG", "PL", "CZ", "RO", "DE", "FR", "NO", "CH"]

IND = {
    "le_birth": "Life expectancy (LE)",
    "healthy_share": "Healthy share (HLY/LE)",
    "emp_rate": "Employment rate",
    "working_life_yrs": "Working-life duration",
    "vacancy_count": "Job vacancies",
}
TEST_H = 4           # hold out up to last 4 years
N_SIM = 500


def backtest_series(years, vals):
    """Rolling origin. Returns lists of (actual, pred, in_band) and naive preds."""
    n = len(vals)
    rows = []
    if n < 8:
        return rows
    for cut in range(n - TEST_H, n):       # origins: n-4 .. n-1
        ytr, vtr = years[:cut], vals[:cut]
        fy = years[cut:]
        if len(fy) == 0:
            continue
        out, sims = forecast_series(ytr, vtr, fy, N_SIM)
        naive = vtr[-1]
        for j, y in enumerate(fy):
            a = vals[cut + j]
            rows.append({
                "h": int(y - ytr[-1]), "actual": float(a),
                "pred": float(out["mean"].iloc[j]),
                "lo": float(out["lo"].iloc[j]), "hi": float(out["hi"].iloc[j]),
                "naive": float(naive)})
    return rows


def mape(rows, key):
    e = [abs(r["actual"] - r[key]) / abs(r["actual"]) for r in rows if r["actual"] != 0]
    return float(np.mean(e)) if e else np.nan


metrics = {}
for col, label in IND.items():
    allrows = []
    per_country = {}
    for c in COUNTRIES:
        crows = []
        for s in ["F", "M"]:
            y, v = history(panel, c, s, col)
            crows += backtest_series(y, v)
        if crows:
            per_country[c] = round(mape(crows, "pred") * 100, 1)
        allrows += crows
    if not allrows:
        continue
    cov = float(np.mean([r["lo"] <= r["actual"] <= r["hi"] for r in allrows]))
    me, mn = mape(allrows, "pred"), mape(allrows, "naive")
    metrics[col] = {
        "label": label, "n": len(allrows),
        "mape_ens": round(me * 100, 2), "mape_naive": round(mn * 100, 2),
        "skill": round(1 - me / mn, 3) if mn else None,
        "coverage80": round(cov, 3),
        "per_country": per_country,
    }

# showcase observed-vs-predicted traces (last-origin forecast vs actual)
show = {}
SHOW = [("le_birth", "DE", "F"), ("healthy_share", "CZ", "F"),
        ("emp_rate", "BG", "M"), ("working_life_yrs", "FR", "F")]
for col, c, s in SHOW:
    y, v = history(panel, c, s, col)
    cut = len(v) - TEST_H
    out, _ = forecast_series(y[:cut], v[:cut], y[cut:], N_SIM)
    show[f"{col}|{c}|{s}"] = {
        "label": f"{IND[col]} — {c} {s}",
        "hist_years": [int(t) for t in y], "hist": [round(float(x), 3) for x in v],
        "test_years": [int(t) for t in y[cut:]],
        "pred": [round(float(x), 3) for x in out["mean"]],
        "lo": [round(float(x), 3) for x in out["lo"]],
        "hi": [round(float(x), 3) for x in out["hi"]],
    }

result = {"metrics": metrics, "show": show, "test_h": TEST_H}
(OUT / "validation_metrics.json").write_text(json.dumps(result, indent=1), encoding="utf-8")

print("=== Backtest accuracy by driver (held out last 4 years, rolling origin) ===")
print(f"{'indicator':26s} {'n':>4} {'MAPE_ens':>9} {'MAPE_naive':>11} {'skill':>7} {'cover80':>8}")
for col, m in metrics.items():
    print(f"{m['label']:26s} {m['n']:>4} {m['mape_ens']:>8.1f}% {m['mape_naive']:>10.1f}% "
          f"{(m['skill'] if m['skill'] is not None else 0):>7.2f} {m['coverage80']*100:>7.0f}%")
print("\nwrote outputs/validation_metrics.json")
