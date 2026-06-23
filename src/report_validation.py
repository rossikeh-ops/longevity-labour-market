"""
Build a self-contained HTML model-validation ("can we trust it?") report.
Charts/tables are STATIC markup (SVG generated in Python) — no client-side JS.
Reads outputs/validation_metrics.json (+ panel) -> outputs/model_validation_report.html.
"""
from __future__ import annotations
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
val = json.loads((OUT / "validation_metrics.json").read_text(encoding="utf-8"))
metrics, show = val["metrics"], val["show"]

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
    "healthy_share": ("Use with caution", "warn", "3.1% error, no better than naive — HLY is survey noise + breaks."),
    "vacancy_count": ("Weak — poorly predicted", "bad", "29% error, worse than naive. Volatile & cyclical — but only 2.2% of jobs."),
}
order = ["le_birth", "working_life_yrs", "emp_rate", "healthy_share", "vacancy_count"]
rows = []
for k in order:
    m = metrics[k]
    lab, cls, why = VERDICT[k]
    rows.append({"label": m["label"], "mape": m["mape_ens"], "naive": m["mape_naive"],
                 "skill": m["skill"], "cover": round(m["coverage80"] * 100),
                 "verdict": lab, "cls": cls, "why": why})
n_trust = sum(1 for r in rows if r["cls"] == "ok")
COL = {"ok": "#34d399", "warn": "#fbbf24", "bad": "#f87171"}
la = val.get("level_acc", {})

# ---------- static SVG: showcase observed-vs-predicted traces ----------
def trace_svg(s):
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
        g.append(f'<text x="{X(yr):.1f}" y="{H-8}" fill="#94a3b8" font-size="10" text-anchor="middle">{yr}</text>')
    band = " ".join(f"{X(x):.1f},{Y(hi[i]):.1f}" for i, x in enumerate(ty)) + " " + \
           " ".join(f"{X(x):.1f},{Y(lo[i]):.1f}" for i, x in reversed(list(enumerate(ty))))
    hist = " ".join(f"{X(x):.1f},{Y(hv[i]):.1f}" for i, x in enumerate(hy))
    pp = " ".join(f"{X(x):.1f},{Y(pred[i]):.1f}" for i, x in enumerate(ty))
    dots = "".join(f'<circle cx="{X(x):.1f}" cy="{Y(hv[hy.index(x)]):.1f}" r="3" fill="#7dd3fc"/>' for x in ty)
    return (f'<div class="chart"><div class="t">{s["label"]}</div>'
            f'<svg viewBox="0 0 {W} {H}" width="100%" xmlns="http://www.w3.org/2000/svg">{"".join(g)}'
            f'<polygon points="{band}" fill="rgba(251,191,36,0.16)"/>'
            f'<polyline points="{hist}" fill="none" stroke="#7dd3fc" stroke-width="1.6" opacity="0.9"/>'
            f'<polyline points="{pp}" fill="none" stroke="#fbbf24" stroke-width="2"/>'
            f'{dots}</svg></div>')


trace_html = "".join(trace_svg(show[k]) for k in show)

# ---------- static SVG: MAPE horizontal bars ----------
maxM = 30.0
bw, rowh = 700, 34
bars = []
for i, r in enumerate(rows):
    y = i * rowh + 6
    w = min(r["mape"], maxM) / maxM * bw
    nx = 200 + min(r["naive"], maxM) / maxM * bw
    bars.append(f'<text x="0" y="{y+15}" fill="#94a3b8" font-size="12">{r["label"]}</text>'
                f'<rect x="200" y="{y+4}" width="{w:.1f}" height="18" rx="4" fill="{COL[r["cls"]]}" opacity="0.85"/>'
                f'<line x1="{nx:.1f}" y1="{y+2}" x2="{nx:.1f}" y2="{y+24}" stroke="#e8edf7" stroke-width="1.2" stroke-dasharray="2 2"/>'
                f'<text x="{205+w:.1f}" y="{y+17}" fill="#e8edf7" font-size="12">{r["mape"]}%</text>')
bars.append(f'<text x="200" y="{len(rows)*rowh+8}" fill="#94a3b8" font-size="11">'
            f'bar = model error · dashed tick = naive baseline · (vacancies capped at 30%)</text>')
mape_svg = (f'<svg viewBox="0 0 1000 {len(rows)*rowh+18}" width="100%" '
            f'xmlns="http://www.w3.org/2000/svg">{"".join(bars)}</svg>')

# ---------- static table + cards ----------
trow = []
for r in rows:
    sk = (f'<span style="color:#34d399">+{r["skill"]}</span>' if r["skill"] > 0
          else f'<span style="color:#f87171">{r["skill"]}</span>')
    trow.append(f'<tr><td>{r["label"]}</td><td>{r["mape"]}%</td>'
                f'<td style="color:#94a3b8">{r["naive"]}%</td><td style="text-align:right">{sk}</td>'
                f'<td>{r["cover"]}%</td><td style="text-align:right">'
                f'<span class="tag {r["cls"]}">{r["verdict"]}</span></td></tr>')
table_html = "".join(trow)
cards_html = "".join(
    f'<div class="vc" style="border-top:3px solid {COL[r["cls"]]}"><div class="h">{r["label"]}</div>'
    f'<div style="margin:4px 0"><span class="tag {r["cls"]}">{r["verdict"]}</span></div>'
    f'<div class="d">{r["why"]}</div></div>' for r in rows)

CSS = """
:root{--bg:#0f1420;--card:#171e2e;--ink:#e8edf7;--mut:#94a3b8;--line:#2a3445;
--obs:#7dd3fc;--fc:#fbbf24;--band:rgba(251,191,36,.16);
--ok:#34d399;--warn:#fbbf24;--bad:#f87171;--okbg:rgba(52,211,153,.12);
--warnbg:rgba(251,191,36,.12);--badbg:rgba(248,113,113,.12);}
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
.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
.vc{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:15px}
.vc .h{font-weight:600;margin-bottom:4px}.vc .d{color:var(--mut);font-size:13px}
.note{color:var(--mut);font-size:13.5px;background:var(--card);border:1px solid var(--line);
border-radius:10px;padding:15px;margin-top:10px}.note b{color:var(--ink)}
.lgd{display:flex;gap:16px;color:var(--mut);font-size:12px;margin:4px 0 0;flex-wrap:wrap}
.sw{display:inline-block;width:11px;height:11px;border-radius:2px;margin-right:5px;vertical-align:-1px}
"""

HTML = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Can we trust the model?</title><style>{CSS}</style></head><body><div class="wrap">
<h1>Can we trust the model?</h1>
<p class="sub">Honest validation of the longevity–labour forecaster · rolling-origin backtest
(forecast the held-out last 4 years from history only) · 8 countries × sex.</p>
<div class="hero"><b>Verdict: trustworthy where it matters, honest where it isn't.</b><br>
The structural drivers — life expectancy, working-life duration and employment rate — are
forecast to <b>1–2% error</b> and beat a naive baseline. Healthy-share (HLY) is noisier and
no better than naive. Job vacancies are <b>genuinely poorly predicted (29%)</b> — but make up
only <b>{vac_w:.1f}% of jobs</b>, so they move total demand by ~{jobs_impact:.1f}%.
Uncertainty bands cover 84–89% of reality (target 80%) — honest, slightly conservative.</div>
<div class="kpis">
<div class="kpi"><div class="v">{n_trust} / 5</div><div class="l">Drivers forecast well (≤2% error, beat naive)</div></div>
<div class="kpi"><div class="v">1.2–1.8%</div><div class="l">Error on LE, working-life, employment rate</div></div>
<div class="kpi"><div class="v">84–89%</div><div class="l">Band coverage vs 80% target (well-calibrated)</div></div>
<div class="kpi"><div class="v">~{jobs_impact:.1f}%</div><div class="l">Demand impact of the weak vacancy forecast</div></div>
</div>
<h2>Accuracy by driver</h2>
<p class="sub">MAPE = mean absolute % error on held-out years. Skill = how much better than a
last-value naive forecast (positive is good). Coverage = share of actuals inside the 80% band.</p>
<table><thead><tr><th>Driver</th><th>MAPE (model)</th><th>MAPE (naive)</th>
<th>Skill vs naive</th><th>Coverage 80%</th><th>Verdict</th></tr></thead><tbody>{table_html}</tbody></table>
<div style="margin-top:14px">{mape_svg}</div>
<h2>Accuracy of the composed outputs (Levels 1–3)</h2>
<p class="sub">The drivers above are the inputs. The actual <b>level outputs</b> have their own
accuracy — backtested by assembling supply/demand/balance from history-only forecasts and
comparing to observed values. They differ: supply is a <i>product</i> (errors combine), demand is
dominated by accurate employment, and the balance is a <i>difference</i> of two large numbers (so its
relative error is amplified).</p>
<div class="cards">
<div class="vc" style="border-top:3px solid #34d399"><div class="h">Level 2 — Demand</div>
<div class="kpi" style="border:0;padding:0"><div class="v" style="color:#34d399">{la.get("demand_mape","?")}%</div>
<div class="l">MAPE · most accurate (employment-driven)</div></div></div>
<div class="vc" style="border-top:3px solid #fbbf24"><div class="h">Level 1 — Supply</div>
<div class="kpi" style="border:0;padding:0"><div class="v" style="color:#fbbf24">{la.get("supply_mape","?")}%</div>
<div class="l">MAPE · health-share noise propagates through the product</div></div></div>
<div class="vc" style="border-top:3px solid #fbbf24"><div class="h">Level 3 — Balance</div>
<div class="kpi" style="border:0;padding:0"><div class="v" style="color:#fbbf24">±{la.get("balance_mae_m","?")}M</div>
<div class="l">~{la.get("balance_rel","?")}% rel. · difference of ~4,500M numbers → amplified</div></div></div>
</div>
<div class="note">Read the balance error in <b>absolute</b> terms: ±{la.get("balance_mae_m","?")}M career
person-years on a typical |balance| of ~{la.get("balance_base_m","?")}M. It is the least accurate
<i>relatively</i> by construction — small % moves in the two large stocks (supply, demand) translate
into larger % moves in their difference. Backtest origins 2020–2023, all 8 countries.</div>
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
• <b>Job vacancies (29% error)</b> — cyclical and shock-driven; no simple model predicts them well. Mitigated by their tiny weight.<br>
• <b>Healthy-share / HLY</b> — survey-based (GALI), with methodology breaks; the model can't beat a naive guess. Treated as a bounded ratio, not over-modelled.<br>
• <b>France vacancies</b> carry Eurostat flag <code>d</code> (definition differs) — a data-quality caveat the model can't fix.<br>
• <b>Short horizons of judgement</b> — HLY has ~18 points; forecasts past ~2035 would be speculative.<br>
• <b>Participation-dependent results</b> (DE, FR) — baseline assumes employment rates keep rising; the plateau scenario is the honest downside.<br>
• <b>No causal claims</b> for health-cost / consumption (Levels 4–5) — those are descriptive relationships, not mechanisms.</div>
<p class="sub" style="margin-top:24px;font-size:12px">Generated from outputs/validation_metrics.json · src/validate.py · rolling-origin backtest, 500 Monte-Carlo sims.</p>
</div></body></html>"""

(OUT / "model_validation_report.html").write_text(HTML, encoding="utf-8")
print(f"wrote outputs/model_validation_report.html  (static SVG, {len(HTML)} bytes, trust {n_trust}/5)")
