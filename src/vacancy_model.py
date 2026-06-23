"""
vacancy_model.py — pooled Beveridge-curve model for the job vacancy rate.

The job-vacancy series is short and shock-driven, so extrapolating it directly is
noisy. Instead we exploit the Beveridge relationship — vacancies fall when
unemployment rises — fitting ONE pooled panel regression over the FULL history of
all 8 countries × sex, then forecasting the vacancy rate from a forecast of
unemployment:

    vacancy_rate  ~  a_country  +  b · unemp_rate           (b < 0, shared slope)

Country fixed effects (a_country) are essential: Eastern-European labour markets
are structurally low-vacancy at any unemployment level, so a single shared
intercept over-predicts them. The slope b (the Beveridge elasticity) is pooled.

fit_beveridge(panel) -> Beveridge ; .predict(unemp_rate, country) -> vacancy_rate.
"""
from __future__ import annotations
import numpy as np


class Beveridge:
    def __init__(self, slope, intercepts, gi, lo, hi, r2, n, occ_scale):
        self.slope = float(slope)            # shared Beveridge slope (negative)
        self.intercepts = dict(intercepts)   # country -> intercept (fixed effect)
        self.gi = float(gi)                  # mean intercept (fallback)
        self.lo, self.hi = float(lo), float(hi)
        self.r2, self.n = float(r2), int(n)
        # occupied-posts base as a share of total LFS employment, per country —
        # the JVR denominator is B-T occupied posts, smaller than total employment.
        self.occ_scale = dict(occ_scale)
        self.occ_gi = float(np.median(list(occ_scale.values()))) if occ_scale else 1.0

    def predict(self, unemp_rate, country=None):
        """Vacancy rate (%) from unemployment rate (%) for a given country."""
        a = self.intercepts.get(country, self.gi) if country is not None else self.gi
        r = a + self.slope * np.asarray(unemp_rate, dtype=float)
        return np.clip(r, self.lo, self.hi)

    def reconstruct_count(self, rate_pct, total_employment, country=None):
        """Vacancy COUNT from a vacancy rate (%) and total employment, via the JVR
        identity V = O·r/(1-r), with occupied posts O calibrated per country."""
        r = np.clip(np.asarray(rate_pct, float) / 100.0, 1e-4, 0.2)
        k = self.occ_scale.get(country, self.occ_gi) if country is not None else self.occ_gi
        occ = k * np.asarray(total_employment, float)
        return occ * r / (1.0 - r)

    def __repr__(self):
        return (f"Beveridge(slope={self.slope:+.4f}, country-FE, "
                f"R²={self.r2:.2f}, n={self.n})")


def fit_beveridge(panel) -> Beveridge:
    """Pooled panel OLS: vacancy_rate ~ shared slope on unemp_rate + country
    intercepts, over all (country, sex, year) rows with both observed."""
    d = panel[["country", "unemp_rate", "vacancy_rate"]].dropna()
    countries = sorted(d["country"].unique())
    u = d["unemp_rate"].to_numpy(float)
    y = d["vacancy_rate"].to_numpy(float)
    # design: [unemp | one-hot country intercepts]  (no global intercept)
    dummies = np.array([[1.0 if cc == c else 0.0 for c in countries]
                        for cc in d["country"]])
    X = np.column_stack([u, dummies])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    slope = beta[0]
    intercepts = {c: float(beta[1 + i]) for i, c in enumerate(countries)}
    yhat = X @ beta
    ss_res = float(np.sum((y - yhat) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2)) or 1e-9
    r2 = 1.0 - ss_res / ss_tot
    lo = max(0.05, float(y.min()) * 0.5)
    hi = float(y.max()) * 1.5

    # Calibrate occupied-posts base per country: from the JVR identity the implied
    # occupied posts are O = V·(1/r - 1); express as a share of total LFS employment.
    occ_scale = {}
    tot_emp = (panel[panel.sex == "F"].set_index(["country", "year"])["employed_ths"]
               .add(panel[panel.sex == "M"].set_index(["country", "year"])["employed_ths"],
                    fill_value=np.nan) * 1000.0)
    cd = panel[panel.sex == "F"].set_index(["country", "year"])
    for c in countries:
        ratios = []
        for (cc, yr), row in cd.iterrows():
            if cc != c:
                continue
            vc, vr = row.get("vacancy_count"), row.get("vacancy_rate")
            te = tot_emp.get((cc, yr))
            if any(v is None or np.isnan(v) for v in (vc, vr, te)) or vr <= 0 or te <= 0:
                continue
            occ_implied = vc * (100.0 / vr - 1.0)        # JVR identity
            ratios.append(occ_implied / te)
        if ratios:
            occ_scale[c] = float(np.median(ratios))
    return Beveridge(slope, intercepts, float(np.mean(list(intercepts.values()))),
                     lo, hi, r2, len(y), occ_scale)
