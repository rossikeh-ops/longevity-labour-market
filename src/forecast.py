"""
Reusable simple-ensemble forecaster with Monte-Carlo bands. No neural nets.

ensemble point = mean of four transparent models fit on the FULL series history:
  1. linear OLS trend (value ~ year)               -- full trend
  2. DAMPED Holt exponential smoothing             -- trend that flattens out
  3. random-walk-with-drift                        -- full trend
  4. naive (last value held flat)                  -- anchor against over-extrapolation
Damping + the naive anchor stop saturating socio-economic rates (employment rate,
healthy share) from being projected to run away linearly to 2035.
Monte-Carlo: each draw samples one model path + residual noise scaled by sqrt(step),
giving coherent fan uncertainty that mixes model disagreement and noise.

forecast_series(years, values, target_years, n_sim, nonneg, bounds) ->
  DataFrame[year, mean, lo, hi]  and the raw sims array (n_sim x len(target_years)).
"""
from __future__ import annotations
import warnings
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
RNG = np.random.default_rng(42)   # fixed seed -> reproducible bands


def _linear(years, vals, tgt):
    b, a = np.polyfit(years, vals, 1)
    resid = vals - (a + b * years)
    s = resid.std(ddof=1) if len(vals) > 2 else (resid.std() or 1e-6)
    return a + b * np.asarray(tgt), max(s, 1e-6)


def _holt(years, vals, tgt):
    """Damped-trend Holt: extrapolated trend flattens as horizon grows."""
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    try:
        fit = ExponentialSmoothing(np.asarray(vals, float), trend="add",
                                   damped_trend=True).fit()
        return np.asarray(fit.forecast(len(tgt))), None
    except Exception:
        return _linear(years, vals, tgt)[0], None


def _drift(years, vals, tgt):
    last, last_y = vals[-1], years[-1]
    d = np.mean(np.diff(vals)) if len(vals) > 1 else 0.0
    return last + d * (np.asarray(tgt) - last_y), None


def _naive(years, vals, tgt):
    """Last value held flat — anchors the ensemble against over-extrapolation."""
    return np.full(len(tgt), vals[-1]), None


def _paths(years, vals, tgt):
    lin, s = _linear(years, vals, tgt)
    holt, _ = _holt(years, vals, tgt)
    drift, _ = _drift(years, vals, tgt)
    naive, _ = _naive(years, vals, tgt)
    return np.vstack([lin, holt, drift, naive]), s


def _ensemble_mean(years, vals, tgt):
    p, _ = _paths(years, vals, tgt)
    return p.mean(axis=0)


def _backtest_sigma(years, values, tgt):
    """Rolling-origin out-of-sample error by horizon (captures MODEL error/bias,
    not just in-sample residual). Returns sigma aligned to tgt. Beyond the longest
    backtested horizon, the largest observed error is grown by sqrt(h)."""
    n = len(values)
    last_y = years[-1]
    horizons = (np.asarray(tgt) - last_y).astype(int)
    base_s = _linear(years, values, tgt)[1]
    err = {}
    start = max(5, n - 8)                      # up to ~8 rolling origins
    for cut in range(start, n):
        ytr, vtr = years[:cut], values[:cut]
        fy = years[cut:]
        if len(fy) == 0:
            continue
        pred = _ensemble_mean(ytr, vtr, fy)
        for j, y in enumerate(fy):
            h = int(y - ytr[-1])
            err.setdefault(h, []).append(values[cut + j] - pred[j])
    rmse = {h: float(np.sqrt(np.mean(np.square(e)))) for h, e in err.items() if len(e) >= 2}
    max_h = max(rmse) if rmse else 0
    max_rmse = rmse.get(max_h, base_s)
    sig = []
    for h in horizons:
        if h in rmse:
            sig.append(max(rmse[h], base_s * np.sqrt(h) * 0.5))
        elif max_h > 0:                        # extrapolate beyond backtest range
            sig.append(max_rmse * np.sqrt(h / max_h))
        else:
            sig.append(base_s * np.sqrt(h))
    return np.maximum(np.array(sig), 1e-9)


def forecast_series(years, values, target_years, n_sim=1000,
                    nonneg=False, bounds=None):
    years = np.asarray(years, float)
    values = np.asarray(values, float)
    m = ~np.isnan(values)
    years, values = years[m], values[m]
    tgt = np.asarray(target_years, float)

    paths, _ = _paths(years, values, tgt)
    mean = paths.mean(axis=0)

    # Honest band = model DISAGREEMENT (spread across members) (+) empirical
    # out-of-sample MODEL error from the rolling backtest, in quadrature.
    model_spread = paths.std(axis=0)
    bt_sigma = _backtest_sigma(years, values, tgt)
    sigma = np.sqrt(model_spread ** 2 + bt_sigma ** 2)

    sims = np.empty((n_sim, len(tgt)))
    n_paths = paths.shape[0]
    for i in range(n_sim):
        choice = paths[RNG.integers(0, n_paths)]
        sims[i] = choice + RNG.normal(0, sigma)
    if nonneg:
        sims = np.clip(sims, 0, None)
    if bounds:
        sims = np.clip(sims, bounds[0], bounds[1])

    lo = np.quantile(sims, 0.10, axis=0)
    hi = np.quantile(sims, 0.90, axis=0)
    out = pd.DataFrame({"year": tgt.astype(int), "mean": mean, "lo": lo, "hi": hi})
    return out, sims


def history(panel, country, sex, col):
    """Full-history (year, value) for one series, NaN dropped, sorted."""
    s = panel[(panel.country == country) & (panel.sex == sex)][["year", col]].dropna()
    s = s.sort_values("year")
    return s["year"].to_numpy(float), s[col].to_numpy(float)
