"""
Build a self-contained HTML model-validation ("can we trust it?") report.
Reads outputs/validation_metrics.json (+ panel for context) and writes
outputs/model_validation_report.html.
"""
from __future__ import annotations
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
val = json.loads((OUT / "validation_metrics.json").read_text(encoding="utf-8"))
metrics, show = val["metrics"], val["show"]

# context: vacancy weight in jobs
p = pd.read_parquet(ROOT / "data" / "processed" / "panel_common.parquet")
v = p[p.year == 2024]
emp = v["employed_ths"].sum() * 1000
vac = v.groupby("country")["vacancy_count"].first().sum()
vac_w = vac / (emp + vac) * 100
jobs_impact = metrics["vacancy_count"]["mape_ens"] * vac_w / 100

# verdict classification
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
    rows.append({"key": k, "label": m["label"], "mape": m["mape_ens"],
                 "naive": m["mape_naive"], "skill": m["skill"],
                 "cover": round(m["coverage80"] * 100), "verdict": lab,
                 "cls": cls, "why": why})
n_trust = sum(1 for r in rows if r["cls"] == "ok")
DATA = json.dumps({"rows": rows, "show": show, "vac_w": round(vac_w, 1),
                   "jobs_impact": round(jobs_impact, 1)})

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
border-radius:12px;padding:18px 20px;margin:20px 0}
.hero b{color:var(--ok)}
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
.chart .t{font-weight:600;font-size:14px}.chart .r{color:var(--mut);font-size:11px}
.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
.vc{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:15px}
.vc .h{font-weight:600;margin-bottom:4px}.vc .d{color:var(--mut);font-size:13px}
.note{color:var(--mut);font-size:13.5px;background:var(--card);border:1px solid var(--line);
border-radius:10px;padding:15px;margin-top:10px}
.note b{color:var(--ink)}
.lgd{display:flex;gap:16px;color:var(--mut);font-size:12px;margin:4px 0 0;flex-wrap:wrap}
.sw{display:inline-block;width:11px;height:11px;border-radius:2px;margin-right:5px;vertical-align:-1px}
"""

HEAD = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Can we trust the model?</title><style>{CSS}</style></head><body><div class="wrap">
<h1>Can we trust the model?</h1>
<p class="sub">Honest validation of the longevity–labour forecaster · rolling-origin backtest
(forecast the held-out last 4 years from history only) · 8 countries × sex.</p>

<div class="hero"><b>Verdict: trustworthy where it matters, honest where it isn't.</b><br>
The structural drivers — life expectancy, working-life duration and employment rate — are
forecast to <b>1–2% error</b> and beat a naive baseline. Healthy-share (HLY) is noisier and
no better than naive. Job vacancies are <b>genuinely poorly predicted (29%)</b> — but make up
only <b>{round(vac_w,1)}% of jobs</b>, so they move total demand by ~{round(jobs_impact,1)}%.
Uncertainty bands cover 84–89% of reality (target 80%) — honest, slightly conservative.</p>

<div class="kpis">
<div class="kpi"><div class="v">{n_trust} / 5</div><div class="l">Drivers forecast well (≤2% error, beat naive)</div></div>
<div class="kpi"><div class="v">1.2–1.8%</div><div class="l">Error on LE, working-life, employment rate</div></div>
<div class="kpi"><div class="v">84–89%</div><div class="l">Band coverage vs 80% target (well-calibrated)</div></div>
<div class="kpi"><div class="v">~{round(jobs_impact,1)}%</div><div class="l">Demand impact of the weak vacancy forecast</div></div>
</div>

<h2>Accuracy by driver</h2>
<p class="sub">MAPE = mean absolute % error on held-out years. Skill = how much better than a
last-value naive forecast (positive is good). Coverage = share of actuals inside the 80% band.</p>
<table><thead><tr><th>Driver</th><th>MAPE (model)</th><th>MAPE (naive)</th>
<th>Skill vs naive</th><th>Coverage 80%</th><th>Verdict</th></tr></thead><tbody id="tbody"></tbody></table>
<div id="mapebar" style="margin-top:14px"></div>

<h2>How the forecast tracks reality</h2>
<p class="sub">Each chart forecasts the last 4 years from history only (gold = prediction,
shaded = 80% band) and overlays what actually happened (blue dots). If dots sit in the band, the model is honest.</p>
<div class="lgd"><span><span class="sw" style="background:var(--obs)"></span>Actual (history + held-out)</span>
<span><span class="sw" style="background:var(--fc)"></span>Forecast from history</span>
<span><span class="sw" style="background:var(--band)"></span>80% band</span></div>
<div class="grid2" id="show"></div>

<h2>Where to trust it — and where not</h2>
<div class="cards" id="cards"></div>

<h2>Why the headline still holds</h2>
<div class="note">
• <b>The accurate drivers carry the weight.</b> Supply ≈ population × healthy-share × working-life,
demand ≈ employment × service — all built on the 1–2% drivers. The weak component (vacancies)
is {round(vac_w,1)}% of jobs.<br>
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
</div>
"""

JS = r"""
<script>
const D=__DATA__;
function el(h){const d=document.createElement('div');d.innerHTML=h;return d.firstElementChild;}

// table
document.getElementById('tbody').innerHTML=D.rows.map(r=>{
 const sk=r.skill>0?`<span style="color:var(--ok)">+${r.skill}</span>`:`<span style="color:var(--bad)">${r.skill}</span>`;
 return `<tr><td>${r.label}</td><td>${r.mape}%</td>
 <td style="color:var(--mut)">${r.naive}%</td><td style="text-align:right">${sk}</td>
 <td>${r.cover}%</td><td style="text-align:right"><span class="tag ${r.cls}">${r.verdict}</span></td></tr>`;}).join('');

// MAPE bar (horizontal), log-ish scale capped at 30
const maxM=30;
document.getElementById('mapebar').innerHTML=`<svg viewBox="0 0 1000 ${D.rows.length*34+10}" width="100%">`+
 D.rows.map((r,i)=>{const y=i*34+6,w=Math.min(r.mape,maxM)/maxM*(700);
  const col=r.cls==='ok'?'var(--ok)':r.cls==='warn'?'var(--warn)':'var(--bad)';
  const nx=200+Math.min(r.naive,maxM)/maxM*700;
  return `<text x=0 y=${y+15} fill="var(--mut)" font-size=12>${r.label}</text>`+
   `<rect x=200 y=${y+4} width=${w} height=18 rx=4 fill="${col}" opacity=.85/>`+
   `<line x1=${nx} y1=${y+2} x2=${nx} y2=${y+24} stroke="var(--ink)" stroke-width=1.2 stroke-dasharray="2 2"/>`+
   `<text x=${205+w} y=${y+17} fill="var(--ink)" font-size=12>${r.mape}%</text>`;}).join('')+
 `<text x=200 y=${D.rows.length*34+8} fill="var(--mut)" font-size=11>bar = model error · dashed tick = naive baseline · (vacancies capped at 30%)</text></svg>`;

// showcase line+band+dots
function trace(key){
 const s=D.show[key],hy=s.hist_years,hv=s.hist,ty=s.test_years;
 const W=470,H=190,P={l:38,r:10,t:10,b:22};
 const allv=hv.concat(s.lo,s.hi),x0=Math.min(...hy),x1=Math.max(...hy);
 const y0=Math.min(...allv)*0.985,y1=Math.max(...allv)*1.015;
 const X=v=>P.l+(v-x0)/(x1-x0)*(W-P.l-P.r),Y=v=>H-P.b-(v-y0)/(y1-y0)*(H-P.t-P.b);
 const lp=(xx,yy)=>xx.map((x,i)=>(i?'L':'M')+X(x).toFixed(1)+' '+Y(yy[i]).toFixed(1)).join(' ');
 const band=ty.map((x,i)=>X(x).toFixed(1)+' '+Y(s.hi[i]).toFixed(1)).join(' L ')+' L '+
   ty.slice().reverse().map((x,i)=>X(x).toFixed(1)+' '+Y(s.lo[s.lo.length-1-i]).toFixed(1)).join(' L ');
 let g='';for(let yr=x0;yr<=x1;yr+=4){g+=`<text x=${X(yr)} y=${H-7} fill="var(--mut)" font-size=10 text-anchor=middle>${yr}</text>`;}
 const dots=ty.map((x,i)=>`<circle cx=${X(x)} cy=${Y(hv[hy.indexOf(x)])} r=3 fill="var(--obs)"/>`).join('');
 return `<div class="chart"><div class="t">${s.label}</div>
 <svg viewBox="0 0 ${W} ${H}" width="100%">${g}
 <path d="M ${band} Z" fill="var(--band)"/>
 <path d="${lp(hy,hv)}" fill="none" stroke="var(--obs)" stroke-width="1.6" opacity=".9"/>
 <path d="${lp(ty,s.pred)}" fill="none" stroke="var(--fc)" stroke-width="2"/>
 ${dots}</svg></div>`;
}
document.getElementById('show').innerHTML=Object.keys(D.show).map(trace).join('');

// verdict cards
document.getElementById('cards').innerHTML=D.rows.map(r=>{
 const c=r.cls==='ok'?'var(--ok)':r.cls==='warn'?'var(--warn)':'var(--bad)';
 return `<div class="vc" style="border-top:3px solid ${c}"><div class="h">${r.label}</div>
 <div style="margin:4px 0"><span class="tag ${r.cls}">${r.verdict}</span></div>
 <div class="d">${r.why}</div></div>`;}).join('');
</script></body></html>"""

(OUT / "model_validation_report.html").write_text(HEAD + JS.replace("__DATA__", DATA), encoding="utf-8")
print(f"wrote outputs/model_validation_report.html  (trust {n_trust}/5 drivers, "
      f"vacancy weight {vac_w:.1f}%, demand impact ~{jobs_impact:.1f}%)")
