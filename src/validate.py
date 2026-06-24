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
from vacancy_model import fit_beveridge

ROOT = Path(__file__).resolve().parents[1]
panel = pd.read_parquet(ROOT / "data" / "processed" / "panel.parquet").copy()
panel["healthy_share"] = panel["hly_birth"] / panel["le_birth"]
panel["emp_rate"] = panel["employed_ths"] * 1000.0 / panel["pop_15_64"]
bev = fit_beveridge(panel)                    # pooled Beveridge: vacancy_rate ~ unemp_rate
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
# Job vacancies are a near-random-walk (5-agent study): the trend ensemble members
# over-extrapolate and lose to naive. Forecast this driver with the mean-reverting
# members only (naive + AR1), which tie the naive ceiling — matching the anchored
# model Level 3 actually uses.
DRIVER_MEMBERS = {"vacancy_count": ("naive", "ar1")}


def backtest_series(years, vals, **fkw):
    """Rolling origin. Returns lists of (actual, pred, in_band) and naive preds.
    fkw forwarded to forecast_series (e.g. log/members for the vacancy series)."""
    n = len(vals)
    rows = []
    if n < 8:
        return rows
    for cut in range(n - TEST_H, n):       # origins: n-4 .. n-1
        ytr, vtr = years[:cut], vals[:cut]
        fy = years[cut:]
        if len(fy) == 0:
            continue
        out, sims = forecast_series(ytr, vtr, fy, N_SIM, **fkw)
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


def rmse(rows, key):
    return float(np.sqrt(np.mean([(r["actual"] - r[key]) ** 2 for r in rows])))


def bias_pct(rows):           # signed: + means model over-forecasts
    e = [(r["pred"] - r["actual"]) / r["actual"] for r in rows if r["actual"] != 0]
    return float(np.mean(e)) * 100 if e else np.nan


metrics = {}
for col, label in IND.items():
    allrows = []
    per_country = {}
    for c in COUNTRIES:
        crows = []
        _mem = DRIVER_MEMBERS.get(col)
        for s in ["F", "M"]:
            y, v = history(panel, c, s, col)
            crows += backtest_series(y, v, **({"members": _mem} if _mem else {}))
        if crows:
            per_country[c] = round((1 - mape(crows, "pred")), 3)   # accuracy 0-1
        allrows += crows
    if not allrows:
        continue
    cov = float(np.mean([r["lo"] <= r["actual"] <= r["hi"] for r in allrows]))
    me, mn = mape(allrows, "pred"), mape(allrows, "naive")
    by_h = {}
    for h in sorted({r["h"] for r in allrows}):
        hr = [r for r in allrows if r["h"] == h]
        by_h[int(h)] = round(mape(hr, "pred") * 100, 1)
    metrics[col] = {
        "label": label, "n": len(allrows),
        "accuracy": round(1 - me, 3),                    # 0-1, e.g. 0.97
        "mape_ens": round(me * 100, 2), "mape_naive": round(mn * 100, 2),
        "rmse": round(rmse(allrows, "pred"), 3),
        "bias_pct": round(bias_pct(allrows), 1),
        "skill": round(1 - me / mn, 3) if mn else None,
        "coverage80": round(cov, 3),
        "mape_by_h": by_h,
        "per_country_acc": per_country,
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

# ---- accuracy of the COMPOSED level outputs (Supply / Demand / Balance) ----
# Backtest the assembled quantities, not just the input drivers. Supply is a product
# (errors combine); Balance is a difference of two large numbers (relative error amplified).
ret = pd.read_csv(ROOT / "data" / "retirement_params.csv")
svc = {(r.country, r.sex): r.required_service_years for r in ret.itertuples()}
retage_d = {(r.country, r.sex): r.statutory_retirement_age for r in ret.itertuples()}
sobs = pd.read_csv(OUT / "supply_observed.csv")
eS, eD, eB, baseB, eC, eV = [], [], [], [], [], []
bsS, bsD, bsC, bsV = [], [], [], []   # signed relative error (bias)
hS, hD, hB, hC, hV = {}, {}, {}, {}, {}   # error by horizon
for c in COUNTRIES:
    oc = sobs[sobs.country == c].groupby("year").agg(
        S=("supply_realized", "sum"), D=("demand", "sum"), B=("balance_realized", "sum"))
    # Level 4 — observed poor-health burden = pop x (LE - HLY), summed over sex
    _pc = panel[panel.country == c].assign(
        burden=lambda d: d.pop_total * (d.le_birth - d.hly_birth))
    ocC = _pc.dropna(subset=["burden"]).groupby("year")["burden"].sum()
    # Level 5 — healthy-retirement dividend = pop x max(0, HLY - retire age)
    _pv = _pc.assign(div=lambda d: d.pop_total * np.clip(
        d.hly_birth - d.apply(lambda r: retage_d.get((c, r["sex"]), np.nan), axis=1), 0, None))
    ocV = _pv.dropna(subset=["div"]).groupby("year")["div"].sum()
    for origin in [2020, 2021, 2022, 2023]:
        tgt = [y for y in range(origin + 1, 2025)]
        if not tgt:
            continue
        def fcm(s, col):                       # train on <= origin only (no leakage)
            y, v = history(panel, c, s, col)
            msk = y <= origin
            return _ensemble_mean(y[msk], v[msk], tgt, weighting="backtest")
        supF = fcm("F", "pop_15_64") * fcm("F", "healthy_share") * fcm("F", "working_life_yrs")
        supM = fcm("M", "pop_15_64") * fcm("M", "healthy_share") * fcm("M", "working_life_yrs")
        empF = fcm("F", "emp_rate") * fcm("F", "pop_15_64")
        empM = fcm("M", "emp_rate") * fcm("M", "pop_15_64")
        den = np.where(empF + empM == 0, 1, empF + empM)
        # vacancies anchored at the last observed rate <= origin (matches balance_forecast.py)
        _vt = panel[(panel.country == c) & panel.vacancy_rate.notna() & (panel.year <= origin)]
        lvr = float(_vt.sort_values("year")["vacancy_rate"].iloc[-1]) if len(_vt) else 1.0
        vac = bev.reconstruct_count(np.full(empF.shape, lvr), empF + empM, c)
        demF = (empF + vac * empF / den) * svc[(c, "F")]
        demM = (empM + vac * empM / den) * svc[(c, "M")]
        Sp, Dp = supF + supM, demF + demM
        Bp = Sp - Dp
        # Level 4 — poor-health burden = pop x (LE - HLY), from history-only drivers
        Cp = (fcm("F", "pop_total") * (fcm("F", "le_birth") - fcm("F", "hly_birth"))
              + fcm("M", "pop_total") * (fcm("M", "le_birth") - fcm("M", "hly_birth")))
        # Level 5 — healthy-retirement dividend (history-only)
        Vp = (fcm("F", "pop_total") * np.clip(fcm("F", "hly_birth") - retage_d[(c, "F")], 0, None)
              + fcm("M", "pop_total") * np.clip(fcm("M", "hly_birth") - retage_d[(c, "M")], 0, None))
        for i, y in enumerate(tgt):
            if y in oc.index:
                So, Do, Bo = oc.loc[y, "S"], oc.loc[y, "D"], oc.loc[y, "B"]
                h = int(y - origin)
                eS.append(abs(Sp[i] - So) / So); bsS.append((Sp[i] - So) / So)
                eD.append(abs(Dp[i] - Do) / Do); bsD.append((Dp[i] - Do) / Do)
                eB.append(abs(Bp[i] - Bo) / 1e6); baseB.append(abs(Bo) / 1e6)
                hS.setdefault(h, []).append(abs(Sp[i] - So) / So)
                hD.setdefault(h, []).append(abs(Dp[i] - Do) / Do)
                hB.setdefault(h, []).append(abs(Bp[i] - Bo) / 1e6)
                if y in ocC.index and ocC.loc[y] > 0:
                    Co = ocC.loc[y]
                    eC.append(abs(Cp[i] - Co) / Co); bsC.append((Cp[i] - Co) / Co)
                    hC.setdefault(h, []).append(abs(Cp[i] - Co) / Co)
                if y in ocV.index and ocV.loc[y] > 0:
                    Vo = ocV.loc[y]
                    eV.append(abs(Vp[i] - Vo) / Vo); bsV.append((Vp[i] - Vo) / Vo)
                    hV.setdefault(h, []).append(abs(Vp[i] - Vo) / Vo)
mS, mD, mC = float(np.mean(eS)), float(np.mean(eD)), float(np.mean(eC))
mV = float(np.mean(eV)) if eV else float("nan")
level_acc = {
    "supply_acc": round(1 - mS, 3), "demand_acc": round(1 - mD, 3),
    "burden_acc": round(1 - mC, 3), "burden_mape": round(mC * 100, 1),
    "burden_bias": round(float(np.mean(bsC)) * 100, 1),
    "burden_by_h": {h: round(float(np.mean(v)) * 100, 1) for h, v in sorted(hC.items())},
    "dividend_acc": round(1 - mV, 3), "dividend_mape": round(mV * 100, 1),
    "dividend_bias": round(float(np.mean(bsV)) * 100, 1) if bsV else None,
    "dividend_by_h": {h: round(float(np.mean(v)) * 100, 1) for h, v in sorted(hV.items())},
    "supply_mape": round(mS * 100, 1), "demand_mape": round(mD * 100, 1),
    "supply_bias": round(float(np.mean(bsS)) * 100, 1),
    "demand_bias": round(float(np.mean(bsD)) * 100, 1),
    "balance_mae_m": round(float(np.mean(eB))),
    "balance_base_m": round(float(np.mean(baseB))),
    "balance_rel": round(float(np.mean(eB) / np.mean(baseB)) * 100),
    "supply_by_h": {h: round(float(np.mean(v)) * 100, 1) for h, v in sorted(hS.items())},
    "demand_by_h": {h: round(float(np.mean(v)) * 100, 1) for h, v in sorted(hD.items())},
    "balance_by_h": {h: round(float(np.mean(v))) for h, v in sorted(hB.items())},
}

# ---- reverse test: NEW Beveridge vacancy model vs OLD direct ensemble ----
# Per country, rolling-origin backtest of the TOTAL job-vacancy count:
#   OLD: extrapolate vacancy_count directly with the ensemble.
#   NEW: forecast unemployment -> Beveridge vacancy rate -> rebuild count from the
#        JVR identity V = O·r/(1-r), using OBSERVED occupied posts O (isolates the
#        rate model). Reports MAPE / skill-vs-naive / bias for both.
def _ctotals(c):
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

vt_old, vt_new = [], []
for c in COUNTRIES:
    Y, VC, VR, UT, ET = _ctotals(c)
    n = len(Y)
    if n < 8:
        continue
    for cut in range(n - TEST_H, n):
        fy = Y[cut:]
        if len(fy) == 0:
            continue
        old_pred = _ensemble_mean(Y[:cut], VC[:cut], fy, weighting="backtest")
        un_pred = _ensemble_mean(Y[:cut], UT[:cut], fy, weighting="backtest")
        h = np.arange(1, len(fy) + 1)
        rate = bev.predict_anchored(un_pred, UT[cut - 1], VR[cut - 1], h, c, damp=0.6)
        new_pred = bev.reconstruct_count(rate, ET[cut:cut + len(fy)], c)
        naive = VC[cut - 1]
        for j in range(len(fy)):
            a = float(VC[cut + j])
            vt_old.append({"actual": a, "pred": float(old_pred[j]), "naive": naive})
            vt_new.append({"actual": a, "pred": float(new_pred[j]), "naive": naive})

def _summ(rows):
    mn = mape(rows, "naive")
    apes = [abs(r["actual"] - r["pred"]) / abs(r["actual"]) for r in rows if r["actual"] != 0]
    return {"n": len(rows), "mape": round(mape(rows, "pred") * 100, 2),
            "medape": round(float(np.median(apes)) * 100, 2) if apes else None,
            "mape_naive": round(mn * 100, 2),
            "skill": round(1 - mape(rows, "pred") / mn, 3) if mn else None,
            "bias_pct": round(bias_pct(rows), 1)}

vacancy_model_test = {
    "old_direct_ensemble": _summ(vt_old) if vt_old else None,
    "new_beveridge": _summ(vt_new) if vt_new else None,
    "beveridge_fit": {"slope": round(bev.slope, 4), "country_fe": True,
                      "r2": round(bev.r2, 3), "n": bev.n},
}

result = {"metrics": metrics, "show": show, "test_h": TEST_H, "level_acc": level_acc,
          "vacancy_model_test": vacancy_model_test}
(OUT / "validation_metrics.json").write_text(json.dumps(result, indent=1), encoding="utf-8")

vo, vn = vacancy_model_test["old_direct_ensemble"], vacancy_model_test["new_beveridge"]
if vo and vn:
    print("\n=== Reverse test — job vacancies: OLD direct ensemble vs NEW Beveridge ===")
    print(f"Beveridge fit: {bev}")
    print(f"{'model':22s} {'n':>4} {'MAPE':>7} {'naive':>7} {'skill':>7} {'bias%':>7}")
    print(f"{'OLD direct ensemble':22s} {vo['n']:>4} {vo['mape']:>6.1f}% {vo['mape_naive']:>6.1f}% "
          f"{(vo['skill'] or 0):>7.2f} {vo['bias_pct']:>6.1f}%")
    print(f"{'NEW anchored Bev.':22s} {vn['n']:>4} {vn['mape']:>6.1f}% {vn['mape_naive']:>6.1f}% "
          f"{(vn['skill'] or 0):>7.2f} {vn['bias_pct']:>6.1f}%  (medAPE {vn['medape']}%)")

print("=== Backtest accuracy by driver (held out last 4 years, rolling origin) ===")
print(f"{'indicator':26s} {'n':>4} {'MAPE_ens':>9} {'MAPE_naive':>11} {'skill':>7} {'cover80':>8}")
for col, m in metrics.items():
    print(f"{m['label']:26s} {m['n']:>4} {m['mape_ens']:>8.1f}% {m['mape_naive']:>10.1f}% "
          f"{(m['skill'] if m['skill'] is not None else 0):>7.2f} {m['coverage80']*100:>7.0f}%")
print("\nwrote outputs/validation_metrics.json")
