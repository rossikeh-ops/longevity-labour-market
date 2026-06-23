"""
Build a self-contained HTML report for Level 2 — Labour Demand.
Reads outputs/{supply_observed,demand_forecast,scenario_participation}.csv and
writes outputs/level2_demand_report.html (no external assets; opens in a browser).
"""
from __future__ import annotations
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
M = 1e6
NAME = {"BG": "Bulgaria", "PL": "Poland", "CZ": "Czechia", "RO": "Romania",
        "DE": "Germany", "FR": "France", "NO": "Norway", "CH": "Switzerland"}
REGION = {"BG": "East·EU", "PL": "East·EU", "CZ": "East·EU", "RO": "East·EU",
          "DE": "West·EU", "FR": "West·EU", "NO": "EFTA", "CH": "EFTA"}

obs = pd.read_csv(OUT / "supply_observed.csv")
fc = pd.read_csv(OUT / "demand_forecast.csv")
sc = pd.read_csv(OUT / "scenario_participation.csv")

countries = ["DE", "FR", "PL", "RO", "CZ", "CH", "BG", "NO"]
series = {}
for c in countries:
    o = (obs[obs.country == c].groupby("year")["demand"].sum() / M)
    o = o[o.index <= 2024]
    f = fc[fc.country == c].groupby("year").agg(
        mean=("demand", "sum"), lo=("demand_lo", "sum"), hi=("demand_hi", "sum")) / M
    series[c] = {
        "name": NAME[c], "region": REGION[c],
        "obs_years": [int(y) for y in o.index], "obs": [round(v, 1) for v in o.values],
        "fyears": [int(y) for y in f.index],
        "mean": [round(v, 1) for v in f["mean"].values],
        "lo": [round(v, 1) for v in f["lo"].values],
        "hi": [round(v, 1) for v in f["hi"].values],
        "d2024": round(float(o.loc[2024]), 0),
        "d2035": round(float(f["mean"].loc[2035]), 0),
        "chg": round((f["mean"].loc[2035] / o.loc[2024] - 1) * 100, 1),
        "jobs2035": round(float(fc[(fc.country == c) & (fc.year == 2035)]["jobs"].sum() / M), 1),
        "plateau2035": round(float(sc[sc.country == c]["demand_2035_plateau"].iloc[0] / M), 0),
    }

tot24 = round(sum(series[c]["d2024"] for c in countries))
tot35 = round(sum(series[c]["d2035"] for c in countries))
totchg = round((tot35 / tot24 - 1) * 100, 1)
jobs24 = round(float(obs[obs.year == 2024]["jobs"].sum() / M), 1)
jobs35 = round(sum(series[c]["jobs2035"] for c in countries), 1)
sexF = round(float(fc[fc.year == 2035].query("sex=='F'")["demand"].sum() / M))
sexM = round(float(fc[fc.year == 2035].query("sex=='M'")["demand"].sum() / M))
DATA = json.dumps(series)
totcol = "var(--down)" if totchg < 0 else "var(--up)"

CSS = """
:root{--bg:#0f1420;--card:#171e2e;--ink:#e8edf7;--mut:#94a3b8;--line:#2a3445;
--acc:#5b9dff;--obs:#7dd3fc;--fc:#fbbf24;--band:rgba(251,191,36,.16);
--up:#34d399;--down:#f87171;}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font:15px/1.5 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;padding:32px}
.wrap{max-width:1080px;margin:0 auto}
h1{font-size:26px;margin:0 0 4px}h2{font-size:18px;margin:34px 0 12px;
border-bottom:1px solid var(--line);padding-bottom:6px}
.sub{color:var(--mut);margin:0 0 8px}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:22px 0}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px}
.kpi .v{font-size:22px;font-weight:700}.kpi .l{color:var(--mut);font-size:12px;margin-top:4px}
.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:16px}
.chart{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px}
.chart .hd{display:flex;justify-content:space-between;align-items:baseline}
.chart .t{font-weight:600}.chart .r{color:var(--mut);font-size:11px}
.pill{font-size:12px;font-weight:700;padding:2px 8px;border-radius:20px}
.pos{color:var(--up);background:rgba(52,211,153,.12)}
.neg{color:var(--down);background:rgba(248,113,113,.12)}
table{width:100%;border-collapse:collapse;font-size:14px}
th,td{padding:8px 10px;text-align:right;border-bottom:1px solid var(--line)}
th:first-child,td:first-child{text-align:left}th{color:var(--mut);font-weight:600}
.note{color:var(--mut);font-size:13px;background:var(--card);border:1px solid var(--line);
border-radius:10px;padding:14px;margin-top:10px}
.lgd{display:flex;gap:16px;color:var(--mut);font-size:12px;margin:6px 0 0;flex-wrap:wrap}
.sw{display:inline-block;width:11px;height:11px;border-radius:2px;margin-right:5px;vertical-align:-1px}
"""

HEAD = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Level 2 — Labour Demand to 2035</title><style>{CSS}</style></head><body><div class="wrap">
<h1>Level 2 — Labour Demand to 2035</h1>
<p class="sub">Potential labour demand in <b>career person-years</b> (jobs × required length of service),
8 countries, by sex · model 2011–2024, forecast to 2035 · Eurostat + MISSOC.</p>
<div class="lgd"><span><span class="sw" style="background:var(--obs)"></span>Observed 2011–2024</span>
<span><span class="sw" style="background:var(--fc)"></span>Forecast 2025–2035</span>
<span><span class="sw" style="background:var(--band)"></span>80% uncertainty band</span>
<span><span class="sw" style="background:#fff;border:1px dashed #888"></span>Participation-plateau 2035</span></div>
<div class="kpis">
<div class="kpi"><div class="v">{tot24:,} → {tot35:,}M</div><div class="l">Total demand, career person-years (2024 → 2035)</div></div>
<div class="kpi"><div class="v" style="color:{totcol}">{totchg:+.1f}%</div><div class="l">Change to 2035 (broadly flat, ageing-tilted)</div></div>
<div class="kpi"><div class="v">{jobs24:.0f} → {jobs35:.0f}M</div><div class="l">Jobs (employed + vacancies), people</div></div>
<div class="kpi"><div class="v">{sexF:,} / {sexM:,}M</div><div class="l">2035 demand by sex (F / M)</div></div>
</div>
<h2>Demand predictions by country</h2><div class="grid" id="charts"></div>
<h2>Forecast table</h2>
<table><thead><tr><th>Country</th><th>Region</th><th>2024</th><th>2035</th>
<th>80% band</th><th>Δ%</th><th>Plateau 2035</th></tr></thead><tbody id="tbody"></tbody></table>
<div class="note"><b>How to read it.</b> Demand = (employed + vacancies) × required years of service —
the stock of career-years the economy's jobs require. <b>East (BG/CZ/PL/RO) declines</b> as the
working-age population shrinks; <b>West holds or grows</b>. The <b>plateau</b> column is the downside
where employment rates stop rising — it hits DE, FR and BG hardest. Bands include out-of-sample
model error and demographic uncertainty (decisions D5/D6).</div>
<h2>Caveats</h2>
<div class="note">• <b>France</b> vacancies carry Eurostat flag <code>d</code> (definition differs); its
+growth depends on rising participation (plateau → ~flat).<br>
• <b>Required service</b> held at baseline (France's points system ≈ 43y effective); pension reforms are levers.<br>
• Population from Eurostat <code>proj_23np</code> calibrated to observed 2024 (decision D4).<br>
• 2024 demand reproduces exactly from raw data; verified by a 5-agent audit.</div>
<p class="sub" style="margin-top:24px;font-size:12px">Generated from outputs/demand_forecast.csv · src/balance_forecast.py</p>
</div>
"""

JS = r"""
<script>
const D=__DATA__;
const W=470,H=210,P={l:42,r:12,t:12,b:24};
function chart(c){
 const s=D[c],ow=s.obs_years,ov=s.obs,fy=s.fyears,fm=s.mean,lo=s.lo,hi=s.hi;
 const xs=[...ow,...fy],allv=[...ov,...hi,...lo,s.plateau2035];
 const x0=Math.min(...xs),x1=Math.max(...xs),y1=Math.max(...allv)*1.08;
 const X=v=>P.l+(v-x0)/(x1-x0)*(W-P.l-P.r);
 const Y=v=>H-P.b-(v)/(y1)*(H-P.t-P.b);
 const lp=(xx,yy)=>xx.map((x,i)=>(i?'L':'M')+X(x).toFixed(1)+' '+Y(yy[i]).toFixed(1)).join(' ');
 const band=fy.map((x,i)=>X(x).toFixed(1)+' '+Y(hi[i]).toFixed(1)).join(' L ')
   +' L '+fy.slice().reverse().map((x,i)=>X(x).toFixed(1)+' '+Y(lo[lo.length-1-i]).toFixed(1)).join(' L ');
 let g='';
 for(let yr=x0;yr<=x1;yr+=4){g+=`<line x1=${X(yr)} y1=${P.t} x2=${X(yr)} y2=${H-P.b} stroke="var(--line)"/>`
   +`<text x=${X(yr)} y=${H-8} fill="var(--mut)" font-size=10 text-anchor=middle>${yr}</text>`;}
 for(let k=0;k<=2;k++){const v=y1*k/2;g+=`<line x1=${P.l} y1=${Y(v)} x2=${W-P.r} y2=${Y(v)} stroke="var(--line)" opacity=.5/>`
   +`<text x=${P.l-6} y=${Y(v)+3} fill="var(--mut)" font-size=10 text-anchor=end>${Math.round(v)}</text>`;}
 const join=[ow[ow.length-1],fy[0]],joinv=[ov[ov.length-1],fm[0]];
 const cls=s.chg<0?'neg':'pos';
 return `<div class="chart"><div class="hd"><div><span class="t">${s.name}</span>
   <span class="r"> ${s.region}</span></div><span class="pill ${cls}">${s.chg>0?'+':''}${s.chg}%</span></div>
 <svg viewBox="0 0 ${W} ${H}" width="100%">${g}
 <path d="M ${band} Z" fill="var(--band)"/>
 <path d="${lp(ow,ov)}" fill="none" stroke="var(--obs)" stroke-width="2"/>
 <path d="${lp(join,joinv)}" fill="none" stroke="var(--fc)" stroke-width="1.5" stroke-dasharray="2 2"/>
 <path d="${lp(fy,fm)}" fill="none" stroke="var(--fc)" stroke-width="2"/>
 <circle cx=${X(2035)} cy=${Y(s.plateau2035)} r=3.2 fill="none" stroke="#fff" stroke-dasharray="2 1.5"/>
 </svg></div>`;
}
document.getElementById('charts').innerHTML=Object.keys(D).map(chart).join('');
document.getElementById('tbody').innerHTML=Object.keys(D).map(c=>{const s=D[c];
 const cls=s.chg<0?'neg':'pos';
 return `<tr><td>${s.name}</td><td style="color:var(--mut)">${s.region}</td>
 <td>${s.d2024}</td><td>${s.d2035}</td>
 <td style="color:var(--mut)">${s.lo[s.lo.length-1]}–${s.hi[s.hi.length-1]}</td>
 <td class="${cls}" style="text-align:right">${s.chg>0?'+':''}${s.chg}%</td>
 <td style="color:var(--mut)">${s.plateau2035}</td></tr>`;}).join('');
</script></body></html>"""

html = HEAD + JS.replace("__DATA__", DATA)
(OUT / "level2_demand_report.html").write_text(html, encoding="utf-8")
print("wrote outputs/level2_demand_report.html  ("
      f"total demand {tot24:,}->{tot35:,}M {totchg:+.1f}%, jobs {jobs24:.0f}->{jobs35:.0f}M)")
