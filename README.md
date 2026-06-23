# Longevity & the Labour Market — Person-Year Engine

Solution to the [Marchev-Science case "Longevity and the Labour Market"](https://github.com/Marchev-Science/case-longevity-and-labour-market).
It bridges demography and labour economics by converting per-person averages (life
expectancy, healthy life years) into **population totals in human-working-years**, then
forecasts labour **supply**, **demand** and their **balance** to **2035** for 8 countries
(BG, PL, CZ, RO, DE, FR, NO, CH), separately for men and women.

## Headline target
`Balance = Potential Supply − Potential Demand` (in human-working-years), by country × sex × year, where:

```
Supply = healthy working-age people × expected working life
       = (pop_15_64 × HLY/LE) × working_life_yrs
Demand = jobs × required service = (employed + vacancies) × required_service_years
```

## Method (no neural networks)
- **Ensemble forecaster** per series (full history): linear trend + damped Holt +
  random-walk-drift + naive, averaged. Damping + naive anchor stop saturating rates
  (employment, health) from over-extrapolating.
- **Population** from Eurostat projection `proj_23np` (baseline), **calibrated to observed 2024**.
- **Monte-Carlo bands** (1000 sims) combining model disagreement + rolling-origin
  **backtest** out-of-sample error + demographic uncertainty.
- **Scenarios** (e.g. participation plateau) as re-runnable levers.

See `docs/assumptions.md` for every locked decision (common period 2011–2024, calibration,
band methodology, scenarios) and `docs/definitions.md` for the identities.

## Status by level
- **L0 Data foundation** — `src/fetch.py`, `src/clean.py` → balanced panel 2011–2024 ✓
- **L1 Supply** — `src/supply.py`, `src/supply_forecast.py` ✓
- **L2 Demand** — `src/balance_forecast.py`; report `outputs/level2_demand_report.html` ✓
- **L3 Balance** — supply − demand (computed jointly in `balance_forecast.py`) — in progress
- L4 health costs / L5 consumption — planned

## Reproduce
```bash
pip install -r requirements.txt
cd src
python fetch.py --levels 1 2 3 4 5   # pull Eurostat -> data/raw
python fetch_proj.py                 # population projections
python clean.py                      # -> data/processed/panel*.parquet
python supply.py                     # observed working-age supply
python balance_forecast.py           # demand, supply, balance to 2035
python report_level2.py              # -> outputs/level2_demand_report.html
```

## Layout
```
src/        fetch, clean, ensemble forecaster, supply/demand/balance, report
data/       raw/ (Eurostat downloads) + processed/ (panels)
outputs/    forecasts (csv) + interactive HTML report
docs/       definitions, assumptions, missing-data policy
```

## Data sources
Eurostat (`demo_*`, `hlth_hlye`, `lfsa_egan`, `jvs_q_r21`, `proj_23np`, `nama_*`,
`gov_10a_exp`, `nama_10_co3_p3`), MISSOC / OECD *Pensions at a Glance* (retirement
parameters). Eurostat flags (`b/p/e/d`) retained throughout.

## License
MIT
