"""
Build a self-contained HTML model-validation ("can we trust it?") report.
Charts/tables are STATIC markup (SVG generated in Python) — no client-side JS.
Reads outputs/validation_metrics.json (+ panel) -> outputs/model_validation_report.html.
"""
from __future__ import annotations
import sys
from pathlib import Path
import json
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from data_appendix import appendix_css, data_link, data_section  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
val = json.loads((OUT / "validation_metrics.json").read_text(encoding="utf-8"))
metrics, show = val["metrics"], val["show"]

# ---- hover-tooltip glossary: an ⓘ next to every metric explains what it is ----
METRIC_INFO = {
    "Accuracy": "1 − MAPE. 1.000 is a perfect forecast; 0.97 means the prediction is on average 3% off the actual value.",
    "MAPE": "Mean Absolute Percentage Error on held-out years — the average size of the forecast error as a % of the actual value. Lower is better.",
    "RMSE": "Root Mean Squared Error, in the series' own units. Like an average error but penalises large misses more heavily.",
    "Bias": "Mean signed % error. Positive = the model over-forecasts on average, negative = under-forecasts. Near 0 means unbiased.",
    "Skill": "Improvement over a naive last-value guess: 1 − MAPE_model / MAPE_naive. Above 0 beats naive, 0 ties it, below 0 is worse.",
    "Coverage": "Calibration check: the share of held-out actual values that fell inside the model's 80% uncertainty band. Close to 80% means the bands are honest.",
    "Train": "In-sample fit error — the model scored on the very history it was fitted to. Optimistic by construction.",
    "Backtest": "Out-of-sample error — a rolling-origin forecast of held-out future years the model never saw while fitting. The realistic number.",
    "Deviation": "Backtest − Train: the generalisation gap. A small value means the model is not overfitting; a large one means it does much worse on unseen years.",
    "Metric": "The error measure shown in this row — MAPE (% error) or RMSE (error in native units).",
    "medAPE": "The median absolute % error — the typical error, less inflated by a few extreme misses than the mean (MAPE).",
    "naive": "MAPE of a naive last-value forecast (next year = this year) — the baseline every model must beat.",
    "horizon": "How many years ahead the forecast is. Error generally grows the further out you predict.",
    "Balance error": "Average absolute error of the supply − demand balance, in million person-years. The balance is a small difference of two large forecasts, so its relative error is amplified.",
}


def info(key, tip=None):
    """Return an ⓘ icon with a hover tooltip explaining the metric `key`."""
    t = (tip or METRIC_INFO.get(key, "")).replace('"', "'")
    return f'<span class="info" data-tip="{t}">i</span>' if t else ""

p = pd.read_parquet(ROOT / "data" / "processed" / "panel_common.parquet")
v = p[p.year == 2024]
emp = v["employed_ths"].sum() * 1000
vac = v.groupby("country")["vacancy_count"].first().sum()
vac_w = vac / (emp + vac) * 100
jobs_impact = metrics["vacancy_count"]["mape_ens"] * vac_w / 100

VERDICT = {
    "le_birth": ("Trustworthy", "ok", "1.2% error, beats naive, well-calibrated. The model's backbone."),
    "working_life_yrs": ("Trustworthy", "ok", "1.5% error, best skill vs naive (+0.20)."),
    "emp_rate": ("Trustworthy", "ok", "1.8% error, beats naive; drives employment."),
    "healthy_share": ("Use with caution", "warn", "3.13% error, no better than naive — HLY is a self-perceived survey measure (see below)."),
    "vacancy_count": ("At its ceiling", "warn", "24.41% error = the naive random-walk floor; vacancies are shock-driven and only ~1.8% of jobs (see below)."),
}
order = ["le_birth", "working_life_yrs", "emp_rate", "healthy_share", "vacancy_count"]
rows = []
for k in order:
    m = metrics[k]
    lab, cls, why = VERDICT[k]
    rows.append({"label": m["label"], "acc": m["accuracy"], "mape": m["mape_ens"],
                 "rmse": m["rmse"], "bias": m["bias_pct"], "naive": m["mape_naive"],
                 "skill": m["skill"], "cover": round(m["coverage80"] * 100),
                 "verdict": lab, "cls": cls, "why": why})
n_trust = sum(1 for r in rows if r["cls"] == "ok")
COL = {"ok": "#15803D", "warn": "#D97706", "bad": "#B91C1C"}
la = val.get("level_acc", {})
sv_path = OUT / "split_validation.json"
sv = json.loads(sv_path.read_text(encoding="utf-8")) if sv_path.exists() else None

# per-country accuracy: average the 0-1 accuracy across drivers
pc = {}
for k in order:
    for c, a in metrics[k].get("per_country_acc", {}).items():
        pc.setdefault(c, []).append(a)
pc_acc = {c: round(sum(v) / len(v), 3) for c, v in pc.items()}
pc_rows = "".join(
    f'<tr><td>{c}</td><td>{a:.3f}</td></tr>'
    for c, a in sorted(pc_acc.items(), key=lambda x: -x[1]))

# ---- "data behind this report" appendix ----
APPENDIX_CSS = appendix_css()
_drv = pd.DataFrame([{
    "driver": metrics[k]["label"], "accuracy": metrics[k]["accuracy"],
    "train MAPE %": metrics[k]["train_mape"], "backtest MAPE %": metrics[k]["mape_ens"],
    "deviation pp": metrics[k]["dev_mape"], "naive %": metrics[k]["mape_naive"],
    "skill": metrics[k]["skill"], "RMSE": metrics[k]["rmse"],
    "bias %": metrics[k]["bias_pct"], "cover80 %": round(metrics[k]["coverage80"] * 100),
    "n": metrics[k]["n"]} for k in order])
_pc = pd.DataFrame([{"country": c, "accuracy (mean of drivers)": a}
                    for c, a in sorted(pc_acc.items(), key=lambda x: -x[1])])
_lvl = pd.DataFrame([{"level metric": kk, "value": vv} for kk, vv in la.items()
                     if not isinstance(vv, dict)])
DLINK = data_link("Validation data behind this report")
APPENDIX = data_section(
    [("Backtest accuracy by driver (rolling-origin, held-out last 4 years)", _drv),
     ("Forecast accuracy by country (mean across drivers)", _pc),
     ("Composed-level accuracy (supply / demand / balance)", _lvl)],
    note="The metrics behind the charts and verdicts. Source: validation_metrics.json (src/validate.py).",
    filename="model_validation_data")

# reverse test — Beveridge vacancy model vs old direct ensemble
vt = val.get("vacancy_model_test")
vac_test_html = ""
if vt and vt.get("new_beveridge") and vt.get("old_direct_ensemble"):
    o, nw, bf = vt["old_direct_ensemble"], vt["new_beveridge"], vt["beveridge_fit"]

    def _vrow(name, d, hl=False):
        skc = "#15803D" if (d["skill"] or 0) >= 0 else "#B91C1C"
        st = "font-weight:700" if hl else ""
        bsign = "+" if d["bias_pct"] > 0 else ""
        med = f'{d.get("medape","?")}%' if d.get("medape") is not None else "—"
        return (f'<tr style="{st}"><td>{name}</td><td>{d["mape"]}%</td>'
                f'<td style="color:#78716C">{med}</td>'
                f'<td style="color:#78716C">{d["mape_naive"]}%</td>'
                f'<td style="color:{skc};text-align:right">{d["skill"]}</td>'
                f'<td style="color:#78716C">{bsign}{d["bias_pct"]}%</td></tr>')
    vac_test_html = f"""
<h2>Vacancies: how far can prediction go? (5-angle study + reverse test)</h2>
<p class="sub">Job vacancies are the hardest driver. A 5-agent study (seasonal/quarterly models,
Beveridge dynamics, leading-indicator covariates, occupied-posts restructuring, and an adversarial
skeptic) reached one conclusion: the vacancy <b>count is a noisy random walk</b> — its year-to-year
swings are essentially unforecastable, so <b>matching a naive last-value baseline (skill ≈ 0) is the
honest ceiling</b>, not a failure. Covariates and trend/seasonal models all did worse out-of-sample.</p>
<p class="sub">The winning model <b>anchors</b> the vacancy rate at its last observed value (which kills
the level bias of a fitted curve) and adds a <b>damped Beveridge response</b> to unemployment (shared
slope {bf["slope"]}, so vacancies still fall when unemployment rises — keeping it scenario-able).
The count is rebuilt from the vacancy-rate identity.</p>
<table style="max-width:680px"><thead><tr><th>Vacancy model</th><th>MAPE{info("MAPE")}</th>
<th>median APE{info("medAPE")}</th><th>vs naive{info("naive")}</th><th>Skill{info("Skill")}</th>
<th>Bias{info("Bias")}</th></tr></thead><tbody>
{_vrow("OLD — direct trend ensemble", o)}
{_vrow("NEW — anchored Beveridge", nw, hl=True)}
</tbody></table>
<div class="note"><b>Reading.</b> The anchored model <b>halves</b> the earlier pooled-Beveridge error
(was ~40% MAPE) down to <b>{nw["mape"]}%</b> — it now <b>ties the naive random-walk floor</b>
(skill {nw["skill"]:+}) with the lowest bias ({nw["bias_pct"]:+}%), while still responding to
unemployment for scenarios. <b>median APE is {nw["medape"]}%</b> — the honest central tendency
(pooled MAPE is inflated by tiny, hyper-volatile series like CZ). Vacancies are only ~1.8% of jobs,
so this barely moves the balance, but the driver is now at its achievable accuracy ceiling.</div>
"""

# ---------- occupied-posts denominator graph (real JOBOCC vs employment-calibration) ----------
jc_path = OUT / "jobocc_compare.json"
denom_html = ""
if jc_path.exists():
    jc = json.loads(jc_path.read_text(encoding="utf-8"))
    cb, rl, dn = jc["vacancy_backtest"]["calib"], jc["vacancy_backtest"]["real"], jc["denominator"]
    pts = jc["scatter"]
    # left: scatter of calibrated O vs real JOBOCC (million), log-log, with y = x line
    SW, SH = 470, 300
    xs = [p["real"] for p in pts] + [p["calib"] for p in pts]
    lo, hi = min(xs) * 0.9, max(xs) * 1.1
    llo, lhi = np.log10(lo), np.log10(hi)
    SX = lambda v: 58 + (np.log10(v) - llo) / (lhi - llo) * (SW - 84)
    SY = lambda v: SH - 44 - (np.log10(v) - llo) / (lhi - llo) * (SH - 66)
    diag = (f'<line x1="{SX(lo):.1f}" y1="{SY(lo):.1f}" x2="{SX(hi):.1f}" y2="{SY(hi):.1f}" '
            f'stroke="#B91C1C" stroke-width="1.4" stroke-dasharray="4 3"/>')
    dots = "".join(f'<circle cx="{SX(p["real"]):.1f}" cy="{SY(p["calib"]):.1f}" r="3.4" fill="rgba(71,85,105,.5)"/>' for p in pts)
    scat_svg = (f'<svg viewBox="0 0 {SW} {SH}" width="100%" xmlns="http://www.w3.org/2000/svg">{diag}{dots}'
                f'<text x="{SW/2:.0f}" y="{SH-8}" fill="#78716C" font-size="11" text-anchor="middle">real occupied posts — JOBOCC (million) →</text>'
                f'<text x="14" y="{SH/2:.0f}" fill="#78716C" font-size="11" text-anchor="middle" transform="rotate(-90 14 {SH/2:.0f})">calibrated occ_scale × employment (million) →</text>'
                f'<text x="{SX(hi)-6:.0f}" y="{SY(hi)+14:.0f}" fill="#B91C1C" font-size="10" text-anchor="end">y = x</text></svg>')
    # right: vacancy-count backtest MAPE — calibrated vs real denominator
    BW, BH, x0, bh, gap = 470, 300, 196, 50, 46
    barlist = [("occ_scale × employment", cb["mape"], "#15803D"), ("real JOBOCC", rl["mape"], "#B91C1C")]
    mx = max(b[1] for b in barlist) * 1.3
    bsv = [f'<text x="{x0-12}" y="34" text-anchor="end" font-size="11" fill="#78716C">vacancy-count backtest MAPE (n={cb["n"]})</text>']
    for i, (lab, v, col) in enumerate(barlist):
        y = 70 + i * (bh + gap)
        w = v / mx * (BW - x0 - 56)
        bsv.append(f'<text x="{x0-12}" y="{y+bh/2-2:.0f}" text-anchor="end" font-size="12" fill="#292524">{lab}</text>')
        bsv.append(f'<rect x="{x0}" y="{y}" width="{w:.1f}" height="{bh}" rx="5" fill="{col}" opacity="0.88"/>')
        bsv.append(f'<text x="{x0+w+9:.1f}" y="{y+bh/2+5:.0f}" font-size="15" font-weight="700" fill="{col}">{v}%</text>')
    bar_svg = f'<svg viewBox="0 0 {BW} {BH}" width="100%" xmlns="http://www.w3.org/2000/svg">{"".join(bsv)}</svg>'

    # second comparison: LFS (residence) vs NA (domestic-concept) employment base
    na_table_html = ""
    na_path = OUT / "na_employment_compare.json"
    if na_path.exists():
        na = json.loads(na_path.read_text(encoding="utf-8"))
        vL, vN = na["vacancy_backtest"]["lfs"], na["vacancy_backtest"]["na"]
        dL, dN = na["denominator_vs_jobocc"]["lfs"], na["denominator_vs_jobocc"]["na"]
        win = lambda a, b: ("#15803D", "#78716C") if a <= b else ("#78716C", "#15803D")
        c1 = win(vL["mape"], vN["mape"])      # lower vacancy MAPE is better
        c2 = win(dL["mape"], dN["mape"])      # lower JOBOCC gap is better
        na_table_html = f"""
<p class="sub" style="margin-top:22px"><b>A third source — National-Accounts <i>domestic-concept</i> employment</b>
(<code>nama_10_a64_e</code>, EMP_DC, THS_PER): it counts jobs <i>in the territory</i> (incl. cross-border commuters),
so it should be a truer occupied-jobs base than LFS residence-concept employment — especially for CH, NO, FR. Does it help?</p>
<table style="max-width:680px"><thead><tr><th>Occupied-jobs base for the denominator</th>
<th>Vacancy-count backtest MAPE</th><th>Tracks real JOBOCC</th></tr></thead><tbody>
<tr><td>LFS employment — residence concept <b>(current)</b></td>
<td style="color:{c1[0]};font-weight:700">{vL['mape']}%</td>
<td style="color:{c2[0]}">{dL['mape']}%</td></tr>
<tr><td>NA employment — domestic concept</td>
<td style="color:{c1[1]};font-weight:700">{vN['mape']}%</td>
<td style="color:{c2[1]};font-weight:700">{dN['mape']}%</td></tr>
</tbody></table>
<div class="note"><b>Tracks JOBOCC tighter, but forecasts no better.</b> The domestic concept is the truer occupied-jobs
level — it matches the real <code>JOBOCC</code> to <b>{dN['mape']}%</b> vs LFS's {dL['mape']}% (exactly as theory predicts).
But it does <b>not</b> improve the vacancy <i>forecast</i> ({vN['mape']}% vs <b>{vL['mape']}%</b>): the dominant error is the
Beveridge <i>rate</i>, and the annual, revision-prone NA series adds noise the smoother LFS doesn't. Even the cross-border
cases don't pay off — only France improves; CH and NO are slightly worse. <b>So we keep LFS residence-concept employment.</b>
Reproducible in <code>src/compare_na_employment.py</code>.</div>"""

    denom_html = f"""
<h2>Does the real occupied-posts series help? (denominator test)</h2>
<p class="sub">The vacancy count is rebuilt from the forecast rate via the identity
<code>V = O·r/(1−r)</code>, where <b>O = occupied posts</b>. We currently calibrate O as
<code>occ_scale × employment</code>; Eurostat also publishes the real series (<code>JOBOCC</code> in
<code>jvs_q_r21</code>, all 8 countries). Does swapping in the real series help? <b>No.</b></p>
<div class="grid2">
<div class="chart"><div class="t">Calibrated O tracks the real JOBOCC ({dn["mape"]}% MAPE)</div>{scat_svg}
<div class="cap">Each point is a country-year ({dn["n"]} obs). The calibration sits tight on the <b>y = x</b> line —
the employment-based denominator is within <b>{dn["mape"]}%</b> (median {dn["medape"]}%) of the genuine occupied-posts count.</div></div>
<div class="chart"><div class="t">…and reconstructs vacancies no worse</div>{bar_svg}
<div class="cap">Same anchored-Beveridge forecast rate, only the denominator swapped. The smooth calibrated O
gives a <b>lower</b> backtest error ({cb["mape"]}% vs {rl["mape"]}%): the dominant error is the forecast
<i>rate</i>, and raw JOBOCC adds quarterly/annualisation noise without buying accuracy.</div></div>
</div>
<div class="note"><b>Conclusion.</b> The standalone occupied-posts dataset exists and is fully available, but the
employment-calibration is the better engineering choice — it matches the real series to ~{dn["mape"]}% while being
smoother, so it reconstructs vacancies <b>as well or better</b>. We keep the calibration and document the test here.
Reproducible in <code>src/compare_jobocc.py</code>.</div>
{na_table_html}
"""

# fixed train/test split (train <=2019, predict 2020-2024) section
split_html = ""
if sv:
    dr = "".join(f'<tr><td>{d["label"]}</td><td style="font-weight:700">{d["accuracy"]:.3f}</td>'
                 f'<td style="color:#78716C">{d["mape"]}%</td></tr>' for d in sv["drivers"].values())
    lv = sv["level"]
    yr = "".join(
        f'<tr><td>{y}</td><td>{v["supply_pred"]}</td><td style="color:#78716C">{v["supply_obs"]}</td>'
        f'<td>{v["demand_pred"]}</td><td style="color:#78716C">{v["demand_obs"]}</td>'
        f'<td>{v["balance_pred"]:+}</td><td style="color:#78716C">{v["balance_obs"]:+}</td></tr>'
        for y, v in sv["years"].items())
    split_html = f"""
<h2>Hold-out stress test — train ≤2019, predict 2020–2024 (incl. COVID)</h2>
<p class="sub">The strictest test: fit on Eurostat history up to 2019 only, then forecast the
five held-out years (which contain the COVID shock) and compare to what actually happened.</p>
<div class="cards">
<div class="vc" style="border-top:3px solid #15803D"><div class="h">Level 2 — Demand</div>
<div class="v" style="font-size:24px;font-weight:700;color:#15803D">{lv["demand_acc"]}</div>
<div class="d">accuracy · {lv["demand_mape"]}% MAPE · robust across COVID</div></div>
<div class="vc" style="border-top:3px solid #15803D"><div class="h">Level 1 — Supply</div>
<div class="v" style="font-size:24px;font-weight:700;color:#15803D">{lv["supply_acc"]}</div>
<div class="d">accuracy · {lv["supply_mape"]}% MAPE · robust across COVID</div></div>
<div class="vc" style="border-top:3px solid #B91C1C"><div class="h">Level 3 — Balance</div>
<div class="v" style="font-size:24px;font-weight:700;color:#B91C1C">±{lv["balance_mae_m"]}M</div>
<div class="d">~{lv["balance_rel"]}% — not reliably predictable at 5-yr horizon through a shock</div></div>
</div>
<div class="grid2" style="margin-top:14px">
<div class="chart"><div class="t">Driver accuracy on the 2020–2024 hold-out</div>
<table><thead><tr><th>Driver</th><th>Accuracy</th><th>MAPE</th></tr></thead><tbody>{dr}</tbody></table></div>
<div class="chart"><div class="t">Totals: predicted vs observed (M person-years)</div>
<table style="font-size:13px"><thead><tr><th>Year</th><th>Sup·pred</th><th>Sup·obs</th>
<th>Dem·pred</th><th>Dem·obs</th><th>Bal·pred</th><th>Bal·obs</th></tr></thead><tbody>{yr}</tbody></table></div>
</div>
<div class="note"><b>Reading.</b> Supply &amp; demand forecasts stay within ~4–5% even five years out
across COVID — Levels 1–2 are <b>accurate and robust</b>. The balance, a small difference of two large
forecasts, is <b>not</b> precisely predictable at this horizon (observed swung +204→−18→+73 during COVID,
which no model anticipates) — confirming it must be read as <b>structural direction with wide bands</b>,
not a point number. A mild +3–6% over-prediction reflects training only on pre-COVID trend.</div>
"""

# error-by-horizon table (composed levels)
hz = sorted(set(map(int, la.get("supply_by_h", {}).keys())))
_bh = la.get("burden_by_h", {})
hz_rows = "".join(
    f'<tr><td>{h} yr</td><td>{la["supply_by_h"].get(str(h),la["supply_by_h"].get(h,"?"))}%</td>'
    f'<td>{la["demand_by_h"].get(str(h),la["demand_by_h"].get(h,"?"))}%</td>'
    f'<td>{_bh.get(str(h),_bh.get(h,"?"))}%</td>'
    f'<td>±{la["balance_by_h"].get(str(h),la["balance_by_h"].get(h,"?"))}M</td></tr>' for h in hz)

# ---------- static SVG: showcase observed-vs-predicted traces ----------
def trace_svg(s, why=""):
    W, H, PLm, PRm, PTm, PBm = 470, 190, 40, 12, 12, 24
    hy, hv, ty = s["hist_years"], s["hist"], s["test_years"]
    lo, hi, pred = s["lo"], s["hi"], s["pred"]
    allv = hv + lo + hi
    x0, x1 = min(hy), max(hy)
    y0, y1 = min(allv) * 0.985, max(allv) * 1.015
    X = lambda v: PLm + (v - x0) / (x1 - x0) * (W - PLm - PRm)
    Y = lambda v: H - PBm - (v - y0) / (y1 - y0) * (H - PTm - PBm)
    g = []
    for yr in range(x0, x1 + 1, 4):
        g.append(f'<text x="{X(yr):.1f}" y="{H-8}" fill="#78716C" font-size="10" text-anchor="middle">{yr}</text>')
    band = " ".join(f"{X(x):.1f},{Y(hi[i]):.1f}" for i, x in enumerate(ty)) + " " + \
           " ".join(f"{X(x):.1f},{Y(lo[i]):.1f}" for i, x in reversed(list(enumerate(ty))))
    hist = " ".join(f"{X(x):.1f},{Y(hv[i]):.1f}" for i, x in enumerate(hy))
    pp = " ".join(f"{X(x):.1f},{Y(pred[i]):.1f}" for i, x in enumerate(ty))
    dots = "".join(f'<circle cx="{X(x):.1f}" cy="{Y(hv[hy.index(x)]):.1f}" r="3" fill="#475569"/>' for x in ty)
    return (f'<div class="chart"><div class="t">{s["label"]}</div>'
            f'<svg viewBox="0 0 {W} {H}" width="100%" xmlns="http://www.w3.org/2000/svg">{"".join(g)}'
            f'<polygon points="{band}" fill="rgba(217,119,6,0.15)"/>'
            f'<polyline points="{hist}" fill="none" stroke="#475569" stroke-width="1.6" opacity="0.9"/>'
            f'<polyline points="{pp}" fill="none" stroke="#D97706" stroke-width="2"/>'
            f'{dots}</svg>'
            f'<div class="cap">{why}</div></div>')


WHY_TRACE = {
    "le_birth": "Shown as the <b>trustworthy backbone</b> — a smooth driver the model tracks to ~1% error.",
    "healthy_share": "Shown as the <b>hardest smooth driver</b> — self-perceived (GALI), noisy, no better than naive.",
    "emp_rate": "Shown as a <b>fast-converging participation</b> series the damped trend pins well.",
    "working_life_yrs": "Shown as the <b>best-skill driver</b> — a clear rising trend the model captures.",
}
trace_html = "".join(trace_svg(show[k], WHY_TRACE.get(k.split("|")[0], "")) for k in show)

# ---------- static SVG: MAPE horizontal bars ----------
maxM = 30.0
bw, rowh = 700, 34
bars = []
for i, r in enumerate(rows):
    y = i * rowh + 6
    w = min(r["mape"], maxM) / maxM * bw
    nx = 200 + min(r["naive"], maxM) / maxM * bw
    bars.append(f'<text x="0" y="{y+15}" fill="#78716C" font-size="12">{r["label"]}</text>'
                f'<rect x="200" y="{y+4}" width="{w:.1f}" height="18" rx="4" fill="{COL[r["cls"]]}" opacity="0.85"/>'
                f'<line x1="{nx:.1f}" y1="{y+2}" x2="{nx:.1f}" y2="{y+24}" stroke="#292524" stroke-width="1.2" stroke-dasharray="2 2"/>'
                f'<text x="{205+w:.1f}" y="{y+17}" fill="#292524" font-size="12">{r["mape"]}%</text>')
bars.append(f'<text x="200" y="{len(rows)*rowh+8}" fill="#78716C" font-size="11">'
            f'bar = model error · dashed tick = naive baseline · (vacancies capped at 30%)</text>')
mape_svg = (f'<svg viewBox="0 0 1000 {len(rows)*rowh+18}" width="100%" '
            f'xmlns="http://www.w3.org/2000/svg">{"".join(bars)}</svg>')

# ---------- static table + cards ----------
trow = []
for r in rows:
    sk = (f'<span style="color:#15803D">+{r["skill"]}</span>' if r["skill"] > 0
          else f'<span style="color:#B91C1C">{r["skill"]}</span>')
    acol = "#15803D" if r["acc"] >= 0.95 else ("#D97706" if r["acc"] >= 0.85 else "#B91C1C")
    bsign = "+" if r["bias"] > 0 else ""
    trow.append(f'<tr><td>{r["label"]}</td>'
                f'<td style="font-weight:700;color:{acol}">{r["acc"]:.3f}</td>'
                f'<td>{r["mape"]}%</td><td style="color:#78716C">{r["rmse"]:g}</td>'
                f'<td style="color:#78716C">{bsign}{r["bias"]}%</td>'
                f'<td style="text-align:right">{sk}</td><td>{r["cover"]}%</td>'
                f'<td style="text-align:right"><span class="tag {r["cls"]}">{r["verdict"]}</span></td></tr>')
table_html = "".join(trow)

# ---------- per-model Train vs Backtest vs Deviation tables ----------
def _devcol(pp):
    a = abs(pp)
    return "#15803D" if a <= 1 else ("#D97706" if a <= 4 else "#B91C1C")


def _pmtable(k):
    m = metrics[k]
    g = lambda x: f"{x:+g}"
    return (
        f'<div class="pmcard"><div class="pmh">{m["label"]}'
        f'<span class="pmn">n={m["n"]}</span></div>'
        f'<table class="pm"><thead><tr><th>Metric{info("Metric")}</th><th>Train{info("Train")}</th>'
        f'<th>Backtest{info("Backtest")}</th><th>Deviation{info("Deviation")}</th></tr></thead><tbody>'
        f'<tr><td>MAPE</td><td>{m["train_mape"]}%</td><td>{m["mape_ens"]}%</td>'
        f'<td style="color:{_devcol(m["dev_mape"])};font-weight:600">{g(m["dev_mape"])} pp</td></tr>'
        f'<tr><td>RMSE</td><td>{m["train_rmse"]:g}</td><td>{m["rmse"]:g}</td>'
        f'<td style="color:#78716C">{g(round(m["dev_rmse"], 3))}</td></tr>'
        f'</tbody></table></div>')


permodel_html = "".join(_pmtable(k) for k in order)

cards_html = "".join(
    f'<div class="vc" style="border-top:3px solid {COL[r["cls"]]}"><div class="h">{r["label"]}</div>'
    f'<div style="margin:4px 0"><span class="tag {r["cls"]}">{r["verdict"]}</span></div>'
    f'<div class="d">{r["why"]}</div></div>' for r in rows)

CSS = """
:root{--bg:#FAFAF9;--card:#FFFFFF;--ink:#292524;--mut:#78716C;--line:#E7E5E4;
--obs:#475569;--fc:#D97706;--band:rgba(217,119,6,.15);
--ok:#15803D;--warn:#D97706;--bad:#B91C1C;--okbg:rgba(21,128,61,.12);
--warnbg:rgba(217,119,6,.12);--badbg:rgba(185,28,28,.10);}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font:15px/1.55 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;padding:32px}
.wrap{max-width:1040px;margin:0 auto}
h1{font-size:27px;margin:0 0 4px}h2{font-size:18px;margin:36px 0 12px;
border-bottom:1px solid var(--line);padding-bottom:6px}
.sub{color:var(--mut);margin:0 0 8px}
.hero{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--ok);
border-radius:12px;padding:18px 20px;margin:20px 0}.hero b{color:var(--ok)}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:20px 0}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px}
.kpi .v{font-size:23px;font-weight:700}.kpi .l{color:var(--mut);font-size:12px;margin-top:4px}
table{width:100%;border-collapse:collapse;font-size:14px}
th,td{padding:9px 10px;text-align:right;border-bottom:1px solid var(--line)}
th:first-child,td:first-child{text-align:left}th{color:var(--mut);font-weight:600}
.tag{font-size:12px;font-weight:600;padding:2px 9px;border-radius:20px;white-space:nowrap}
.ok{color:var(--ok);background:var(--okbg)}.warn{color:var(--warn);background:var(--warnbg)}
.bad{color:var(--bad);background:var(--badbg)}
.grid2{display:grid;grid-template-columns:repeat(2,1fr);gap:16px}
.chart{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px}
.chart .t{font-weight:600;font-size:14px;margin-bottom:4px}
.chart .cap{color:var(--mut);font-size:12px;margin-top:6px;line-height:1.4}.chart .cap b{color:var(--ink)}
.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
.vc{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:15px}
.vc .h{font-weight:600;margin-bottom:4px}.vc .d{color:var(--mut);font-size:13px}
.note{color:var(--mut);font-size:13.5px;background:var(--card);border:1px solid var(--line);
border-radius:10px;padding:15px;margin-top:10px}.note b{color:var(--ink)}
code{background:#F5F5F4;border:1px solid #E7E5E4;border-radius:5px;padding:1px 6px;
color:#475569;font-size:13px;font-family:ui-monospace,Menlo,Consolas,monospace}
.lgd{display:flex;gap:16px;color:var(--mut);font-size:12px;margin:4px 0 0;flex-wrap:wrap}
.sw{display:inline-block;width:11px;height:11px;border-radius:2px;margin-right:5px;vertical-align:-1px}
.info{display:inline-flex;align-items:center;justify-content:center;width:14px;height:14px;border-radius:50%;
border:1px solid var(--mut);color:var(--mut);font:700 9px/1 Georgia,serif;font-style:italic;cursor:help;
margin-left:5px;position:relative;vertical-align:middle;user-select:none}
.info:hover{border-color:var(--ok);color:var(--ok)}
.info:hover::after{content:attr(data-tip);position:absolute;left:50%;bottom:150%;transform:translateX(-50%);
background:#292524;color:#fff;font:400 12px/1.45 -apple-system,Segoe UI,Roboto,Arial,sans-serif;font-style:normal;
text-align:left;padding:9px 11px;border-radius:8px;width:250px;max-width:60vw;white-space:normal;z-index:60;
box-shadow:0 6px 20px rgba(0,0,0,.22);pointer-events:none}
.info:hover::before{content:'';position:absolute;left:50%;bottom:150%;transform:translateX(-50%) translateY(99%);
border:6px solid transparent;border-top-color:#292524;z-index:60;pointer-events:none}
th .info{border-color:#a8a29e}
.pmgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px}
.pmcard{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px}
.pmh{font-weight:650;font-size:14px;margin-bottom:8px;display:flex;justify-content:space-between;align-items:baseline}
.pmh .pmn{color:var(--mut);font-size:11px;font-weight:400}
table.pm{font-size:13.5px}table.pm th,table.pm td{padding:7px 8px}
"""

HTML = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Can we trust the model?</title><style>{CSS}{APPENDIX_CSS}</style></head><body><div class="wrap">
<h1>Can we trust the model?</h1>
<p class="sub">Honest validation of the longevity–labour forecaster · rolling-origin backtest
(forecast the held-out last 4 years from history only) · 8 countries × sex.</p>
{DLINK}
<div class="hero"><b>Verdict: trustworthy where it matters, honest where it isn't.</b><br>
The structural drivers — life expectancy, working-life duration and employment rate — are
forecast to <b>1–2% error</b> and beat a naive baseline. Healthy-share (HLY) is noisier and
no better than naive. Job vacancies are a <b>near-random-walk</b> (modelled with an anchored,
scenario-able rate at the naive accuracy ceiling) — but make up only <b>{vac_w:.1f}% of jobs</b>, so they move total demand by ~{jobs_impact:.1f}%.
Uncertainty bands cover 84–89% of reality (target 80%) — honest, slightly conservative.</div>
<div class="kpis">
<div class="kpi"><div class="v">{n_trust} / 5</div><div class="l">Drivers forecast well (≤2% error, beat naive)</div></div>
<div class="kpi"><div class="v">1.2–1.8%</div><div class="l">Error on LE, working-life, employment rate</div></div>
<div class="kpi"><div class="v">84–89%</div><div class="l">Band coverage vs 80% target (well-calibrated)</div></div>
<div class="kpi"><div class="v">~{jobs_impact:.1f}%</div><div class="l">Demand impact of the weak vacancy forecast</div></div>
</div>
<h2>Accuracy by driver</h2>
<p class="sub"><b>Accuracy = 1 − MAPE</b> (1.000 = perfect). MAPE = mean abs % error on held-out years;
RMSE in native units; Bias = signed error (+ = over-forecast); Skill = improvement over a naive
last-value forecast; Coverage = share of actuals inside the 80% band.</p>
<table><thead><tr><th>Driver</th><th>Accuracy{info("Accuracy")}</th><th>MAPE{info("MAPE")}</th>
<th>RMSE{info("RMSE")}</th><th>Bias{info("Bias")}</th><th>Skill{info("Skill")}</th>
<th>Cover 80%{info("Coverage")}</th><th>Verdict</th></tr></thead><tbody>{table_html}</tbody></table>
<div style="margin-top:14px">{mape_svg}</div>

<h2>Train vs backtest, by model — the generalisation gap</h2>
<p class="sub">For every driver model: <b>Train</b> = in-sample fit error (the model scored on the history it was
fitted to — optimistic); <b>Backtest</b> = out-of-sample rolling-origin error (held-out future); <b>Deviation</b> =
Backtest − Train, the generalisation gap. A small deviation means the model is <b>not overfitting</b> — it does
almost as well on unseen years as on the training data. MAPE deviation is in percentage points; RMSE in native units.</p>
<div class="pmgrid">{permodel_html}</div>
<div class="note"><b>Reading it.</b> The smooth structural drivers (life expectancy, working-life, employment) have a
<b>small, green deviation</b> — they generalise. <b>Healthy share</b> and especially <b>job vacancies</b> show that even
the in-sample fit is weak and the backtest barely differs: there is no learnable signal to overfit, so the gap is small
but the level is high — a <b>floor</b>, not overfitting. Train uses an equal-weight one-step in-sample ensemble fit;
backtest uses the deployed horizon-aware ensemble.</div>

<h2>What's behind the two weak numbers</h2>
<div class="note"><b>Healthy share (HLY ÷ LE) — 3.13%: it measures <span style="color:var(--warn,#D97706)">self-perceived</span> health.</b>
Healthy Life Years come from Eurostat's <b>GALI</b> question in the EU-SILC survey — people are simply asked whether
they are "limited in activities people usually do, because of a health problem, for at least the past 6 months"
(none / some / severe). HLY is then the Sullivan-method combination of that <b>self-reported</b> answer with the life
table. So healthy share is partly <b>subjective and cultural</b>, not a clinical measurement: e.g. <b>Switzerland reports
low healthy years despite the highest life expectancy</b> — a self-perception artefact, not worse health. That subjectivity
(plus small survey samples and Eurostat methodology breaks, flag <code>b</code>) is most of the 3.13% — there is no learnable
trend in perception, so the model <b>cannot beat a naive last-value guess</b>. We treat it as a bounded ratio with wide bands.</div>

<div class="note"><b>Job vacancies — 24.41%: it's the irreducible random-walk floor, not a model failure.</b>
The number is the mean absolute % error of the <b>total job-vacancy count</b> forecast. Vacancies are <b>shock- and
cycle-driven</b> (hiring freezes, booms, COVID) — year-to-year swings are essentially unforecastable, so <b>24.41% exactly
ties the naive baseline</b> (skill ≈ 0): matching last year's value is the best any honest method can do (a 5-agent study
confirmed seasonal, covariate and trend models all did <i>worse</i>). The level looks alarming but: (1) the median error is
only ~16% — the 24.4% mean is inflated by tiny, hyper-volatile series like Czechia; (2) <b>France's vacancies carry Eurostat
flag <code>d</code></b> (definition differs); and (3) vacancies are just <b>~1.8% of jobs</b>, so this error moves total
labour demand by only ~{jobs_impact:.1f}%. We forecast them through an anchored Beveridge curve, which keeps the link to
unemployment for scenarios while sitting at this accuracy ceiling.</div>

<h2>Accuracy of the composed outputs (Levels 1–5)</h2>
<p class="sub">The drivers above are the inputs. The actual <b>level outputs</b> have their own
accuracy — backtested by assembling each from history-only forecasts and comparing to observed values.
They differ: supply is a <i>product</i> (errors combine), demand is dominated by accurate employment, the
balance is a <i>difference</i> of two large numbers (relative error amplified), and the Level-4 poor-health
burden leans directly on the noisy healthy-life-years measure. The Level-5 retirement dividend is the least
predictable of all — a threshold on the noisy HLY makes it volatile.</p>
<div class="cards" style="grid-template-columns:repeat(auto-fit,minmax(170px,1fr))">
<div class="vc" style="border-top:3px solid #15803D"><div class="h">Level 2 — Demand</div>
<div class="v" style="font-size:24px;font-weight:700;color:#15803D">{la.get("demand_acc","?")}</div>
<div class="d">accuracy · {la.get("demand_mape","?")}% MAPE · bias {"+" if la.get("demand_bias",0)>0 else ""}{la.get("demand_bias","?")}% · employment-driven</div></div>
<div class="vc" style="border-top:3px solid #D97706"><div class="h">Level 1 — Supply</div>
<div class="v" style="font-size:24px;font-weight:700;color:#D97706">{la.get("supply_acc","?")}</div>
<div class="d">accuracy · {la.get("supply_mape","?")}% MAPE · bias {"+" if la.get("supply_bias",0)>0 else ""}{la.get("supply_bias","?")}% · health-share noise</div></div>
<div class="vc" style="border-top:3px solid #D97706"><div class="h">Level 4 — Poor-health burden</div>
<div class="v" style="font-size:24px;font-weight:700;color:#D97706">{la.get("burden_acc","?")}</div>
<div class="d">accuracy · {la.get("burden_mape","?")}% MAPE · bias {"+" if la.get("burden_bias",0)>0 else ""}{la.get("burden_bias","?")}% · inherits HLY (self-perceived) noise</div></div>
<div class="vc" style="border-top:3px solid #B91C1C"><div class="h">Level 5 — Retire dividend</div>
<div class="v" style="font-size:24px;font-weight:700;color:#B91C1C">~{la.get("dividend_mape","?")}% MAPE</div>
<div class="d">threshold-sensitive — clip on noisy HLY makes it volatile &amp; least predictable</div></div>
<div class="vc" style="border-top:3px solid #B91C1C"><div class="h">Level 3 — Balance</div>
<div class="v" style="font-size:24px;font-weight:700;color:#B91C1C">±{la.get("balance_mae_m","?")}M</div>
<div class="d">~{la.get("balance_rel","?")}% rel. · difference of ~4,500M stocks → amplified</div></div>
</div>
<div class="note">Read the balance error in <b>absolute</b> terms: ±{la.get("balance_mae_m","?")}M career
person-years on a typical |balance| of ~{la.get("balance_base_m","?")}M. It is the least accurate
<i>relatively</i> by construction. Backtest origins 2020–2023, all 8 countries.</div>
<div class="note"><b>Level 4 — the cost link is honest, not predictive.</b> The poor-health <i>burden</i>
(pop × (LE − HLY)) backtests at ~{la.get("burden_mape","?")}% — trustworthy as a demographic quantity. But its
tested relationship to the <b>NACE-Q health &amp; social-work sector</b> is statistically negligible
(within-country elasticity ≈ 0, R² ≈ 0), so we do <b>not</b> predict the sector's cost from it — that sector
tracks the economy (~2.4%/yr). Reported descriptively, no causal claim. See the
<a href="level4_cost_report.html">Level 4 report</a>.</div>
<div class="note"><b>Level 5 — read the dividend as direction, not a forecast.</b> The healthy-retirement dividend
(pop × max(0, HLY − retirement age)) backtests at ~{la.get("dividend_mape","?")}% — by far the least accurate
stock, because a <b>threshold on the noisy, self-perceived HLY</b> makes it jump when countries cross the
retirement line. Trust the <i>sign and ranking</i> (who has healthy retirement years vs not), not the level. Its
link to leisure/education/culture consumption is also negligible within-country (elasticity ≈ 0) — consumption
tracks income. See the <a href="level5_dividend_report.html">Level 5 report</a>.</div>
{vac_test_html}
{denom_html}
<h2>Error by forecast horizon</h2>
<p class="sub">How accuracy decays with how far ahead we forecast (1–4 years out), for the composed levels.</p>
<table style="max-width:620px"><thead><tr><th>Years ahead{info("horizon")}</th><th>Supply MAPE{info("MAPE")}</th>
<th>Demand MAPE{info("MAPE")}</th><th>Burden MAPE{info("MAPE")}</th>
<th>Balance error{info("Balance error")}</th></tr></thead><tbody>{hz_rows}</tbody></table>

<h2>Accuracy by country</h2>
<p class="sub">Average forecast accuracy (1 − MAPE) across the five drivers, per country.</p>
<table style="max-width:360px"><thead><tr><th>Country</th><th>Accuracy</th></tr></thead><tbody>{pc_rows}</tbody></table>
{split_html}
<h2>How the forecast tracks reality</h2>
<p class="sub">Each chart forecasts the last 4 years from history only (gold = prediction,
shaded = 80% band) and overlays what actually happened (blue dots). If dots sit in the band, the model is honest.</p>
<div class="lgd"><span><span class="sw" style="background:var(--obs)"></span>Actual (history + held-out)</span>
<span><span class="sw" style="background:var(--fc)"></span>Forecast from history</span>
<span><span class="sw" style="background:var(--band)"></span>80% band</span></div>
<div class="grid2">{trace_html}</div>
<h2>Where to trust it — and where not</h2>
<div class="cards">{cards_html}</div>
<h2>Why the headline still holds</h2>
<div class="note">
• <b>The accurate drivers carry the weight.</b> Supply ≈ population × healthy-share × working-life,
demand ≈ employment × service — all built on the 1–2% drivers. The weak component (vacancies)
is {vac_w:.1f}% of jobs.<br>
• <b>Population isn't extrapolated</b> — it's Eurostat's own projection (proj_23np), calibrated to observed 2024.<br>
• <b>Identities reconcile exactly</b> (Total = average × population); 2024 values verified to the cent by a 5-agent audit.<br>
• <b>Bands are honest</b> — they include real out-of-sample model error (backtest), not just in-sample noise, and cover ~85% of reality.</div>
<h2>Where the model fails to explain the data (honest limitations)</h2>
<div class="note">
• <b>Job vacancies</b> — a <b>noisy random walk</b>: year-to-year swings are essentially
unforecastable, so matching the naive last-value baseline (skill ≈ 0) is the achievable ceiling, not a
defect. A 5-agent study (seasonal/quarterly, Beveridge dynamics, leading-indicator covariates,
occupied-posts restructuring, skeptic) confirmed no covariate or trend model beats it out-of-sample.
Level 3 uses an <b>anchored</b> vacancy rate (last observed value) with a <b>damped Beveridge response</b>
to unemployment — halving the earlier curve's error to the naive floor while staying scenario-able. Only
~1.8% of jobs, so the balance is barely affected.<br>
• <b>Healthy-share / HLY</b> — survey-based (GALI), with methodology breaks; the model can't beat a naive guess. Treated as a bounded ratio, not over-modelled.<br>
• <b>France vacancies</b> carry Eurostat flag <code>d</code> (definition differs) — a data-quality caveat the model can't fix.<br>
• <b>Short horizons of judgement</b> — HLY has ~18 points; forecasts past ~2033 would be speculative.<br>
• <b>Participation-dependent results</b> (DE, FR) — baseline assumes employment rates keep rising; the plateau scenario is the honest downside.<br>
• <b>No causal claims</b> for health-cost / consumption (Levels 4–5) — those are descriptive relationships, not mechanisms.</div>
<h2>Data sources — Eurostat dataset codes</h2>
<div class="note">Drivers validated here come from
<code>hlth_hlye</code> (LE, HLY) · <code>demo_pjangroup</code> (working-age population) ·
<code>lfsi_dwl_a</code> (working-life duration) · <code>lfsa_egan</code> (employment) ·
<code>jvs_q_r21</code> (vacancies). Population forecast benchmarked to <code>proj_23np</code>;
retirement rules from MISSOC / OECD Pensions at a Glance.</div>
{APPENDIX}
<p class="sub" style="margin-top:24px;font-size:12px">Generated from outputs/validation_metrics.json · src/validate.py · rolling-origin backtest, 500 Monte-Carlo sims.</p>
</div></body></html>"""

(OUT / "model_validation_report.html").write_text(HTML, encoding="utf-8")
print(f"wrote outputs/model_validation_report.html  (static SVG, {len(HTML)} bytes, trust {n_trust}/5)")
