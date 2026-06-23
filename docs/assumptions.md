# Key Assumptions & Locked Decisions

## D1 — Common analysis period: **2011–2024** (hard requirement)
The combined person-year balance is computed on a single period shared by **all 8
countries × both sexes**, with **every core indicator fully observed (zero synthetic
data)**. The maximal such window is **2011–2024** (14 years):
- **Start = 2011** — binding constraint is France's job-vacancy series (begins 2011, flag `d`).
- **End = 2024** — binding constraint is Healthy Life Years (latest Eurostat year).

Enforced in `src/clean.py` (`ANALYSIS_START/END`, `emit_common_panel`) which asserts
the slice is rectangular: 8×2×14 = **224 cells**, no missing values in `BALANCE_CORE`.
Output: `data/processed/panel_common.parquet`.

**Chosen via a 5-angle "Fat & Dirty model" review panel** (data-rich + robust-to-messy):
verdict **A (2011–2024 strict) 3 votes** vs B (2008–2024+backcast) 1, C (2004–2024+backcast) 1.
Decisive reasons: (a) only window where all 8 vacancy series are *observed* — the balance
is measured, not synthesized; (b) per-series forecasts use full history anyway, so a longer
*combined* window adds no forecast signal; (c) backcasting demand into 2008–2010 (GFC) would
inject fabricated, non-comparable, validation-contaminating data. 224 observed cells is amply
"fat"; backcasting the load-bearing demand driver is the wrong kind of "dirty".

## D2 — Forecasting uses full per-series history
Each component forecast (LE, HLY/LE ratio, population, employment, vacancies) is fit on
that series' **entire** available history (e.g. LE from 2004, population from 1991) for
accuracy. Only the **combined** historical balance is restricted to the D1 window; forecasts
to 2035 are likewise reported on the common future horizon.

## D4 — Population projection calibrated to observed 2024
`proj_23np` baseline levels can sit above the observed `demo_pjangroup` working-age
population (notably **BG: 2.19M vs 1.98M ~ +10%**, from Bulgaria's 2021 census revision).
We multiply each country×sex projection path (BSL/HMIGR/LMIGR) by
`observed_2024 / proj_BSL_2024` so 2025→2035 continues smoothly from the real 2024
level. Without this, the forecast masked genuine workforce decline (e.g. it wrongly
showed BG demand +6% and DE flat; calibrated values are BG −3%, DE −1.4%).

## D5 — Honest uncertainty bands
Forecast 80% bands combine, in quadrature: (i) cross-model disagreement (spread across
the 4 ensemble members), (ii) **rolling-origin backtest** out-of-sample error by horizon
(captures model misspecification/bias, not just in-sample residual), and (iii) for
population, a demographic term (~0.4%/yr) added to the migration-variant spread. Result:
2035 demand band widths ~12–43% of point (vs ~5–14% before). Central estimates unchanged.

## D6 — Scenario: participation plateau
Baseline assumes employment rates keep rising (ensemble forecast). The **plateau** scenario
freezes emp_rate at the last observed value. 2035 demand impact: BG −7.2%, DE −4.6%,
FR −3.5%, others smaller, RO ~0 (already flat). This is the credible downside for the
West's near-flat demand and is exposed as a lever (outputs/scenario_participation.csv).

## D3 — France vacancy caveat
All French vacancy points carry Eurostat flag `d` (definition differs); retained, flagged,
and surfaced in French demand-side results. Not correctable from the data side.
