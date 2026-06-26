# -*- coding: utf-8 -*-
"""
Head-to-head: does a REGRESSION TREE (or gradient boosting) beat a LINEAR model
at the descriptive Level 4 / Level 5 relationships?

  Level 4 — does the poor-health burden  [pop x (LE - HLY)]  drive HEALTH spending?
  Level 5 — does the healthy-retirement dividend  [pop x max(0, HLY - retire)]
            drive LEISURE / EDUCATION / CULTURE spending?

Because levels are dominated by country size and confounded across countries
(GALI non-comparability), the honest test is WITHIN-country: year-on-year growth
rates, validated leave-ONE-COUNTRY-out (a relationship that generalises to a
held-out country, not memorised levels). We report out-of-sample R^2 and RMSE for
a linear model, a shallow tree, and gradient boosting. Read-only; writes JSON.
"""
from __future__ import annotations
import json
import warnings
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import LeaveOneGroupOut

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
panel = pd.read_parquet(ROOT / "data" / "processed" / "panel.parquet").copy()

# ---- country-year aggregates -------------------------------------------------
panel["burden_py"] = panel["pop_total"] * (panel["le_birth"] - panel["hly_birth"])
cy = panel.groupby(["country", "year"]).agg(
    burden=("burden_py", "sum"),
    pop=("pop_total", "sum"),
    pop65=("pop_65p", "sum"),
    emp=("employed_ths", "sum"),
    gdp=("nace_q_va", "mean"),
    health=("gov_health_exp", "mean"),
    edu=("coicop_education", "mean"),
    rec=("coicop_recreation", "mean"),
    hot=("coicop_hotels_rest", "mean"),
).reset_index()
# dividend (person-years) summed over sex, merged in
dv = pd.read_csv(OUT / "dividend_observed.csv").groupby(["country", "year"])["hdiv_py"].sum().reset_index()
cy = cy.merge(dv.rename(columns={"hdiv_py": "dividend"}), on=["country", "year"], how="left")
cy["leisure"] = cy[["edu", "rec", "hot"]].sum(axis=1, min_count=1)
cy = cy.sort_values(["country", "year"])


def growth(df, cols):
    """Within-country year-on-year % change (drops the size/level confound)."""
    g = df.copy()
    for c in cols:
        g["g_" + c] = g.groupby("country")[c].pct_change()
    return g


MODELS = {
    "linear": LinearRegression(),
    "tree_d3": DecisionTreeRegressor(max_depth=3, min_samples_leaf=8, random_state=0),
    "gboost": GradientBoostingRegressor(n_estimators=300, max_depth=2,
                                        learning_rate=0.03, subsample=0.8, random_state=0),
}


def run(df, feats, target, label):
    cols = feats + [target]
    d = growth(df, cols).replace([np.inf, -np.inf], np.nan).dropna(subset=["g_" + c for c in cols])
    X = d[["g_" + f for f in feats]].values
    y = d["g_" + target].values
    groups = d["country"].values
    logo = LeaveOneGroupOut()
    out = {"n": int(len(y)), "countries": int(len(set(groups))), "feats": feats, "target": target}
    var = float(np.var(y))
    for name, mdl in MODELS.items():
        preds = np.zeros_like(y)
        for tr, te in logo.split(X, y, groups):
            preds[te] = mdl.fit(X[tr], y[tr]).predict(X[te])
        sse = float(np.sum((y - preds) ** 2))
        r2 = 1 - sse / (var * len(y))                       # out-of-sample R^2
        rmse = float(np.sqrt(sse / len(y)))
        out[name] = {"r2_oos": round(r2, 3), "rmse": round(rmse, 4)}
    # does the burden/dividend feature add anything? linear with vs without it
    key = feats[0]
    d2 = d
    Xc = d2[["g_" + f for f in feats[1:]]].values
    pc = np.zeros_like(y)
    for tr, te in logo.split(Xc, y, groups):
        pc[te] = LinearRegression().fit(Xc[tr], y[tr]).predict(Xc[te])
    out["linear_no_" + key] = {"r2_oos": round(1 - np.sum((y - pc) ** 2) / (var * len(y)), 3)}
    out["label"] = label
    return out


L4 = run(cy, ["burden", "gdp", "pop65", "pop"], "health",
         "Level 4 — poor-health burden -> health spending")
L5 = run(cy, ["dividend", "gdp", "pop", "emp"], "leisure",
         "Level 5 — healthy-retirement dividend -> leisure/education/culture spending")
res = {"level4": L4, "level5": L5, "cv": "leave-one-country-out", "framing": "within-country YoY growth"}
(OUT / "tree_compare.json").write_text(json.dumps(res, indent=1), encoding="utf-8")


def show(o):
    print(f"\n=== {o['label']} ===")
    print(f"  n={o['n']} rows, {o['countries']} countries, leave-one-country-out CV")
    print(f"  {'model':12s} {'OOS R^2':>9} {'RMSE':>9}")
    for m in ("linear", "tree_d3", "gboost"):
        print(f"  {m:12s} {o[m]['r2_oos']:>9} {o[m]['rmse']:>9}")
    k = o["feats"][0]
    print(f"  linear WITHOUT {k}: OOS R^2 = {o['linear_no_'+k]['r2_oos']}  "
          f"(vs linear WITH = {o['linear']['r2_oos']})")


show(L4)
show(L5)
print("\nwrote outputs/tree_compare.json")
