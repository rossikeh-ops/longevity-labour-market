# Missing-Data & Coverage Policy

Eurostat coverage is uneven (short series, methodology breaks, EFTA gaps). This
policy states how every gap is handled so "full coverage" is honest and auditable.
Every filled cell is recorded in `data/imputation_log.csv`; per-series coverage is
in `data/coverage_report.csv`.

## Decision ladder (applied per indicator × country × sex)
1. **Observed** — value present → keep, retain Eurostat flag (`b/p/e`).
2. **Internal gap** (missing year *between* two observed years) → **linear interpolation**
   (`clean.py`), logged. Benign; not extrapolation.
3. **Whole series absent** (EFTA / partial reporting) → **pool-impute or proxy** at the
   level that uses it, documented; or **drop that country from that indicator only**
   (never from the headline supply/demand path).
4. **Forecast (future years)** → handled in modelling (Levels 1–5), never in cleaning.

## Known gaps (from `_manifest.csv` + coverage report)
| Indicator | Gap | Handling |
|---|---|---|
| `vacancy_rate` + `vacancy_count` | Originally FR + CH missing in `jvs_a_rate_r2` (NACE Rev 2) | **Resolved**: switched to **`jvs_q_r21`** (NACE Rev 2.1, quarterly), code **B-T**, size class **TOTAL**, **NSA**, annualised as the mean of ≥3 quarters. Pulls both rate (JVR) and absolute count (JOBVAC, for the jobs identity). Verified coverage: **CH 2003–2025, NO 2010–2025 (both clean, unflagged)**; **FR 2011–2025**. Chosen over the annual array because it fills FR's missing 2020 with real data and supplies counts. |
| ↳ **France caveat** | FR vacancy points all carry Eurostat flag **`d` = definition differs** | Intrinsic to France's vacancy collection (different scope/definition); not correctable. Retained in `panel_long.parquet` flag column; FR demand-side results carry this caveat in the report. NACE scope B-T excludes agriculture (A) — the only cross-country-comparable aggregate. |
| `hly_*` (`hlth_hlye`) | Short (2004–2024), many `b` breaks (2006–2024) | Break-adjust + COVID dummy in Level 1; ratio-to-LE forecasting. |
| `coicop_*`, `nama_10_a64` | Sex = T only (no sex split) | Sex-apportion by NACE-section employment shares (Level 4/5), documented. |

## Break & shock handling (surfaced now, applied in modelling)
- **Breaks** (`b`): flagged per cell; level-shift estimated from overlap, else inherited
  via the HLY/LE ratio or pooled shrinkage.
- **COVID 2020–21**: kept as observed; modelled as a damped dummy — never deleted.

## Coverage gate
The "zero missing cells" assertion on the modelling panel passes only **after** this
report is reviewed and each gap maps to a ladder rule above.
