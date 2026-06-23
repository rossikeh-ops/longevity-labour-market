# Definitions & Person-Year Identities

All quantities are computed by **country (c)**, **sex (s)**, **year (t)**.

## Source indicators (Eurostat unless noted)
| Panel column | Source | Meaning | Unit |
|---|---|---|---|
| `le_birth`, `le_65` | `hlth_hlye` (`LE_0`,`LE_65`) | Life expectancy at birth / at 65 | years |
| `hly_birth`, `hly_65` | `hlth_hlye` (`HLY_0`,`HLY_65`) | Healthy life years at birth / at 65 (Sullivan/GALI) | years |
| `pop_total` | `demo_pjan` | Population on 1 Jan | persons |
| `employed_ths` | `lfsa_egan` | Employment 15–64 | thousands |
| `vacancy_rate`, `vacancy_count` | `jvs_q_r21` (annualised) | Job vacancy rate / count, B-T TOTAL | % / posts — unbalanced: CH 2003+, …, NO 2010+, FR 2011+ (FR flagged `d`) |
| `working_life_yrs` | `lfsi_dwl_a` | Expected duration of working life | years |
| `unemp_rate` | `une_rt_a` | Unemployment rate 15–74 | % |
| `nace_q_va` | `nama_10_a64` | NACE-Q gross value added | chain-linked €M |
| `gov_health_exp`,`gov_social_exp` | `gov_10a_exp` | COFOG GF07 health / GF10 social | €M |
| `coicop_*` | `nama_10_co3_p3` | Household consumption CP09/10/11 | chain-linked €M |
| retirement age, required service | Excel/MISSOC/OECD | by country × sex | years |

## Person-year identities (mechanical — not behavioural)
```
Total LE        = pop_total × le              (person-years of expected life)
Potential supply= pop_total × HLY             (healthy person-years = labour-supply ceiling)
Total poor-health = pop_total × (le − HLY)    (Level 4 cost driver)
Healthy LE after retirement = pop_total × (HLY − retirement_age)   (Level 5 driver)
Number of jobs  = employed + vacancies
Potential demand= jobs × required_service     (person-years stock comparator)
Balance (TARGET)= supply − demand             (human-working-years)
```
`le − HLY` and the totals above are **accounting identities**, distinguished throughout
from estimated **behavioural relationships** (Levels 4–5 regressions).

## Working-age LE window (decision #1)
The supply tally uses a **working-age remaining-LE window** (ages 15→statutory age,
built from age-specific remaining LE weighted by population structure), not raw
LE-at-birth. LE-at-birth totals are reported only as an explicit upper-bound sensitivity.
