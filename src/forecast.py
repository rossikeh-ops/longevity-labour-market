"""
Reusable simple-ensemble forecaster with Monte-Carlo bands. No neural nets.

ensemble point = mean of four transparent models fit on the FULL series history:
  1. linear OLS trend (value ~ year)               -- full trend
  2. DAMPED Holt exponential smoothing             -- trend that flattens out
  3. random-walk-with-drift                        -- full trend
  4. naive (last value held flat)                  -- anchor against over-extrapolation
Damping + the naive anchor stop saturating socio-economic rates (employment rate,
healthy share) from being projected to run away linearly to 2033.
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


def _ar1(years, vals, tgt):
    """Mean-reverting AR(1): decay last value toward the long-run mean. Right for
    cyclical, mean-reverting series (e.g. job vacancies) where trend members over-extrapolate."""
    if len(vals) < 4:
        return _naive(years, vals, tgt)[0], None
    phi, c0 = np.polyfit(vals[:-1], vals[1:], 1)
    phi = min(max(phi, 0.0), 0.98)
    mu = c0 / (1 - phi) if abs(1 - phi) > 1e-6 else float(np.mean(vals))
    last, ly = vals[-1], years[-1]
    return np.array([mu + (last - mu) * phi ** int(t - ly) for t in tgt]), None


_MEMBERS = {"linear": _linear, "holt": _holt, "drift": _drift,
            "naive": _naive, "ar1": _ar1}
# ar1 (mean-reversion toward the long-run mean) is now part of the default set —
# it pulls cyclical / saturating series back instead of letting trend members run away.
DEFAULT_MEMBERS = ("linear", "holt", "drift", "naive", "ar1")


def _paths(years, vals, tgt, members=DEFAULT_MEMBERS):
    s = _linear(years, vals, tgt)[1]          # residual scale base (always)
    rows = [_MEMBERS[m](years, vals, tgt)[0] for m in members]
    return np.vstack(rows), s


def _member_weights(years, vals, tgt, members=DEFAULT_MEMBERS):
    """Weight each member by its rolling-origin backtest accuracy (∝ 1/RMSE),
    shrunk toward equal weights. Lets the better models dominate where one member
    systematically wins (e.g. ar1 on vacancies), without over-committing on short
    series. Falls back to equal weights when history is too short."""
    n = len(vals)
    k = len(members)
    eq = np.ones(k) / k
    if n < 8 or k == 1:
        return eq
    sse = np.zeros(k)
    cnt = np.zeros(k)
    for cut in range(max(5, n - 6), n):       # up to ~6 rolling origins
        ytr, vtr, fy = years[:cut], vals[:cut], years[cut:]
        if len(fy) == 0:
            continue
        act = vals[cut:cut + len(fy)]
        for mi, m in enumerate(members):
            pred = _MEMBERS[m](ytr, vtr, fy)[0]
            sse[mi] += float(np.sum((act - pred) ** 2))
            cnt[mi] += len(fy)
    rmse = np.sqrt(sse / np.maximum(cnt, 1))
    inv = 1.0 / (rmse + 0.25 * rmse.mean() + 1e-9)     # shrink toward equal
    w = inv / inv.sum()
    return 0.7 * w + 0.3 * eq                  # 30% floor on equal weighting


def _ensemble_mean(years, vals, tgt, members=DEFAULT_MEMBERS, weighting="equal"):
    p, _ = _paths(years, vals, tgt, members)
    if weighting == "backtest":
        w = _member_weights(years, vals, tgt, members)
        return (p * w[:, None]).sum(axis=0)
    return p.mean(axis=0)


def _backtest_sigma(years, values, tgt, members=DEFAULT_MEMBERS):
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
        pred = _ensemble_mean(ytr, vtr, fy, members)
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
                    nonneg=False, bounds=None, members=DEFAULT_MEMBERS, log=False,
                    weighting="backtest"):
    """members: which ensemble members to combine (default the 5-model set incl. ar1).
    weighting: 'backtest' weights members by 1/backtest-RMSE (shrunk to equal);
    'equal' is the old simple average. log=True forecasts in log space
    (multiplicative noise; for positive volatile counts) and exponentiates."""
    years = np.asarray(years, float)
    values = np.asarray(values, float)
    m = ~np.isnan(values)
    years, values = years[m], values[m]
    tgt = np.asarray(target_years, float)

    work = np.log(np.clip(values, 1e-9, None)) if log else values
    paths, _ = _paths(years, work, tgt, members)
    if weighting == "backtest":
        w = _member_weights(years, work, tgt, members)
    else:
        w = np.ones(paths.shape[0]) / paths.shape[0]
    mean_w = (paths * w[:, None]).sum(axis=0)

    # Honest band = model DISAGREEMENT (weighted spread across members) (+) empirical
    # out-of-sample MODEL error from the rolling backtest, in quadrature.
    model_spread = np.sqrt((w[:, None] * (paths - mean_w) ** 2).sum(axis=0))
    bt_sigma = _backtest_sigma(years, work, tgt, members)
    sigma = np.sqrt(model_spread ** 2 + bt_sigma ** 2)

    mean = np.exp(mean_w) if log else mean_w
    sims = np.empty((n_sim, len(tgt)))
    n_paths = paths.shape[0]
    for i in range(n_sim):
        choice = paths[RNG.choice(n_paths, p=w)]      # sample members by weight
        sims[i] = choice + RNG.normal(0, sigma)
    if log:
        sims = np.exp(sims)
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
