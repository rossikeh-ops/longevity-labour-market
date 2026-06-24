# -*- coding: utf-8 -*-
"""
Build outputs/whatif_base.json — the 2033 base inputs for the interactive
"what-if" scenario explorer. Everything downstream is recomputed in the browser
from these inputs via the SAME identities used in Levels 1/4/5, kept PER SEX so
the convex max(0,·) clips match the published levels:

  WORK   (who keeps working)     = healthy working-age people × working life   [L1]
  RETIRE (who retires)           = Pop × max(0, LE − retirement age)            (retirement person-years)
  CARE   (who needs healthcare)  = Pop × (LE − HLY)                             [L4 poor-health burden]
  CULTURE(concert halls/courses) = Pop × max(0, HLY − retirement age)           [L5 healthy-retirement dividend]

A single lever — "do they live longer in good health?" (ΔHLY) — pushes CARE down
and CULTURE up at once; retirement age and participation are the policy dials.

Per-country population is scaled by one factor so CARE reproduces the published
Level-4 burden; the same factor then makes CULTURE match Level-5 (verified below).
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from forecast import _ensemble_mean, history

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
COUNTRIES = ["BG", "PL", "CZ", "RO", "DE", "FR", "NO", "CH"]
NAME = {"BG": "Bulgaria", "PL": "Poland", "CZ": "Czechia", "RO": "Romania",
        "DE": "Germany", "FR": "France", "NO": "Norway", "CH": "Switzerland"}
REGION = {"BG": "East·EU", "PL": "East·EU", "CZ": "East·EU", "RO": "East·EU",
          "DE": "West·EU", "FR": "West·EU", "NO": "EFTA", "CH": "EFTA"}
Y = 2033

panel = pd.read_parquet(ROOT / "data" / "processed" / "panel.parquet").copy()
panel["emp_rate"] = panel["employed_ths"] * 1000.0 / panel["pop_15_64"]
rp = pd.read_csv(ROOT / "data" / "retirement_params.csv")
RET = {(r.country, r.sex): float(r.statutory_retirement_age) for r in rp.itertuples()}

supA = pd.read_csv(OUT / "supply_forecast.csv")
sup33 = supA[supA.year == Y].set_index(["country", "sex"])["supply_realized"]
cost33 = pd.read_csv(OUT / "cost_forecast.csv").query("year == @Y").set_index("country")["poor_py"]
div33 = pd.read_csv(OUT / "dividend_forecast.csv").query("year == @Y").set_index("country")["dividend_py"]


def f33(c, s, col):
    y, v = history(panel, c, s, col)
    return float(_ensemble_mean(y, v, [Y], weighting="backtest")[0])


base, check = {}, []
for c in COUNTRIES:
    segs = []
    for s in ("F", "M"):
        d = {k: f33(c, s, k) for k in ("pop_total", "pop_15_64", "le_birth", "hly_birth",
                                       "working_life_yrs", "emp_rate")}
        segs.append({"sex": s, "pop": d["pop_total"], "pwa": d["pop_15_64"],
                     "le": d["le_birth"], "hly": d["hly_birth"], "ret": RET[(c, s)],
                     "wl": d["working_life_yrs"], "part": d["emp_rate"],
                     "work0": float(sup33[(c, s)])})
    # scale pop so CARE = Σ pop·(LE−HLY) reproduces the published Level-4 burden
    care_raw = sum(g["pop"] * (g["le"] - g["hly"]) for g in segs)
    k = float(cost33[c]) / care_raw
    for g in segs:
        g["pop"] *= k
        g["pwa"] *= k

    care0 = sum(g["pop"] * (g["le"] - g["hly"]) for g in segs)
    culture0 = sum(g["pop"] * max(0.0, g["hly"] - g["ret"]) for g in segs)
    retire0 = sum(g["pop"] * max(0.0, g["le"] - g["ret"]) for g in segs)
    work0 = sum(g["work0"] for g in segs)
    P = sum(g["pop"] for g in segs)

    base[c] = {
        "name": NAME[c], "region": REGION[c],
        "P": round(P), "LE": round(sum(g["le"] * g["pop"] for g in segs) / P, 1),
        "HLY": round(sum(g["hly"] * g["pop"] for g in segs) / P, 1),
        "ret": round(sum(g["ret"] * g["pop"] for g in segs) / P, 1),
        "work0": round(work0), "care0": round(care0),
        "culture0": round(culture0), "retire0": round(retire0),
        "seg": [{kk: (round(vv, 4) if isinstance(vv, float) else vv) for kk, vv in g.items()} for g in segs],
    }
    check.append((c, culture0, float(div33[c])))

(OUT / "whatif_base.json").write_text(json.dumps({"year": Y, "countries": base}, indent=1), encoding="utf-8")

print(f"{'c':3} {'P(M)':>7} {'work(M)':>8} {'care(M)':>8} {'cult(calc)':>11} {'cult(pub)':>10} {'Δ%':>6}")
for c, cc, cp in check:
    b = base[c]
    dp = (cc / cp - 1) * 100 if cp else 0
    print(f"{c:3} {b['P']/1e6:7.2f} {b['work0']/1e6:8.1f} {b['care0']/1e6:8.1f} "
          f"{cc/1e6:11.1f} {cp/1e6:10.1f} {dp:6.1f}")
print("\nwrote outputs/whatif_base.json")
