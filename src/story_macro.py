# -*- coding: utf-8 -*-
"""
Build outputs/macro_story.html — a guided, slide-based narrative of LEVEL 6
(longevity in the macroeconomy / growth accounting), Chart.js + tracker + present.

Four slides:
  1. Real GDP to 2033    — GDP = employment × productivity, trajectory + band
  2. Growth accounting   — labour vs productivity contribution, all 8 countries
  3. The reverse arrow   — cross-country: healthy share vs productivity (wrong sign)
  4. The honest answer   — within-country: no link → longevity acts through labour
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
T = 1e6
NAME = {"ALL": "All 8 countries", "BG": "Bulgaria", "PL": "Poland", "CZ": "Czechia",
        "RO": "Romania", "DE": "Germany", "FR": "France", "NO": "Norway", "CH": "Switzerland"}
GEO = [c for c in NAME if c != "ALL"]


def _geos(c):
    return GEO if c == "ALL" else [c]


obs = pd.read_csv(OUT / "macro_observed.csv")
fc = pd.read_csv(OUT / "macro_forecast.csv")
ga = pd.read_csv(OUT / "macro_growth_accounting.csv")
rel = json.loads((OUT / "macro_relationship.json").read_text(encoding="utf-8"))

# ---- GDP trajectory (€ trillion), observed + forecast, per country ----
gdp = {}
for c in NAME:
    cs = _geos(c)
    o = obs[obs.country.isin(cs)].groupby("year")["gdp"].sum() / T
    f = fc[fc.country.isin(cs)].groupby("year").agg(
        m=("gdp", "sum"), lo=("gdp_lo", "sum"), hi=("gdp_hi", "sum")) / T
    gdp[c] = {"oy": [int(y) for y in o.index], "ov": [round(v, 2) for v in o.values],
              "fy": [int(y) for y in f.index], "fm": [round(v, 2) for v in f["m"].values],
              "lo": [round(v, 2) for v in f["lo"].values], "hi": [round(v, 2) for v in f["hi"].values]}

# ---- growth accounting (projected 2024→2033), all 8, ordered by GDP growth ----
gp = ga[ga.kind == "projected"].set_index("country")
order = list(gp.sort_values("g_gdp", ascending=False).index)
decomp = {"codes": order, "names": [NAME[c] for c in order],
          "labour": [round(float(gp.loc[c, "g_labour"]), 2) for c in order],
          "prod": [round(float(gp.loc[c, "g_prod"]), 2) for c in order],
          "gdp": [round(float(gp.loc[c, "g_gdp"]), 2) for c in order]}

# ---- cross-country scatter: healthy share vs productivity (cross_year) ----
cyear = rel["cross_year"]
cx = obs[obs.year == cyear].dropna(subset=["prod", "healthy_share"])
cross = [{"c": r.country, "name": NAME[r.country],
          "hs": round(float(r.healthy_share), 3), "prod": round(float(r.prod), 1)}
         for r in cx.itertuples()]

# ---- within-country differenced cloud (Δ healthy share pp vs Δ ln prod %) ----
diff = []
for c in GEO:
    g = obs[obs.country == c].dropna(subset=["prod", "healthy_share"]).sort_values("year")
    if len(g) < 5:
        continue
    dp = np.diff(np.log(g["prod"].to_numpy(float))) * 100
    dh = np.diff(g["healthy_share"].to_numpy(float)) * 100
    for a, b in zip(dh, dp):
        diff.append({"x": round(float(a), 2), "y": round(float(b), 2)})

DATA = {"countries": NAME, "gdp": gdp, "decomp": decomp, "cross": cross,
        "diff": diff, "rel": rel, "cyear": cyear}

HTML = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Longevity in the Macroeconomy — a guided story</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<style>
:root{--bg:#FAFAF9;--card:#FFFFFF;--ink:#292524;--mut:#78716C;--line:#E7E5E4;--acc:#166534;
--slate:#475569;--mustard:#D97706;--sage:#4ADE80;--terra:#B91C1C;}
*{box-sizing:border-box}html,body{margin:0;height:100%}
body{background:var(--bg);color:var(--ink);font:16px/1.6 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
display:flex;flex-direction:column;min-height:100vh}
header{padding:18px 28px 8px;display:flex;align-items:center;gap:18px;flex-wrap:wrap}
header h1{font-size:19px;margin:0;font-weight:650}header .who{color:var(--mut);font-size:13px}.spacer{flex:1}
select{background:var(--card);color:var(--ink);border:1px solid var(--line);border-radius:8px;padding:8px 10px;font-size:14px}
.track{display:flex;align-items:center;gap:0;padding:6px 28px 12px;flex-wrap:wrap}
.step{display:flex;align-items:center;gap:9px;cursor:pointer;color:var(--mut);font-size:13px;font-weight:600}
.step .dot{width:30px;height:30px;border-radius:50%;border:2px solid var(--line);background:var(--card);
display:flex;align-items:center;justify-content:center;font-size:13px;color:var(--mut);transition:.2s}
.step.active .dot,.step.done .dot{border-color:var(--acc);background:var(--acc);color:#fff}.step.active{color:var(--ink)}
.link{flex:0 0 46px;height:3px;background:var(--line);margin:0 6px;border-radius:2px}.link.done{background:var(--acc)}
main{flex:1;padding:6px 28px 20px;max-width:1080px;margin:0 auto;width:100%}
.slide{display:none;animation:fade .35s ease}.slide.active{display:block}
@keyframes fade{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
.kick{font-size:12px;letter-spacing:1px;text-transform:uppercase;color:var(--acc);font-weight:700}
.slide h2{font-size:24px;margin:4px 0 6px}.slide p.lead{color:var(--mut);margin:0 0 14px;max-width:780px}
.panel{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:16px 18px;margin:12px 0}
.chwrap{position:relative;height:430px}
.kpis{display:flex;gap:14px;flex-wrap:wrap;margin-top:8px}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px 16px;min-width:150px}
.kpi .v{font-size:22px;font-weight:700}.kpi .l{color:var(--mut);font-size:12px;margin-top:2px}
.note{color:var(--mut);font-size:13px;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px;margin-top:10px}code{color:var(--acc)}
footer{display:flex;align-items:center;justify-content:space-between;padding:14px 28px 26px;max-width:1080px;margin:0 auto;width:100%}
button.nav{background:var(--acc);color:#fff;border:none;border-radius:10px;padding:10px 20px;font-size:14px;font-weight:600;cursor:pointer}
button.nav:disabled{background:var(--line);color:var(--mut);cursor:default}button.ghost{background:var(--card);color:var(--ink);border:1px solid var(--line)}
a{color:var(--acc)}
</style></head><body>
<header>
  <h1>Longevity in the Macroeconomy — a guided story</h1>
  <span class="who">8 European countries · to 2033</span><span class="spacer"></span>
  <label class="who" for="country">Country&nbsp;</label><select id="country"></select>
</header>
<nav class="track" id="track"></nav>
<main>
  <section class="slide" data-i="0">
    <div class="kick">Step 1 · The identity</div><h2>Real GDP = employment × productivity</h2>
    <p class="lead">Where does growth come from? Every euro of output is <b>someone working</b> times
    <b>how much each worker produces</b>. We forecast both and rebuild GDP to 2033 with an uncertainty band.</p>
    <div class="panel"><div class="chwrap"><canvas id="gdp"></canvas></div></div>
    <div class="kpis" id="gKpis"></div>
    <div class="note">Real GDP: <code>nama_10_gdp</code> (B1GQ, chain-linked 2015). Productivity = GDP ÷ employment.</div></section>
  <section class="slide" data-i="1">
    <div class="kick">Step 2 · Growth accounting</div><h2>Labour vs productivity, to 2033</h2>
    <p class="lead">Splitting each country's projected growth: the <b>labour</b> channel (employment — where
    longevity acts) and the <b>productivity</b> channel. The East grows on productivity catch-up; the West leans on labour.</p>
    <div class="panel"><div class="chwrap"><canvas id="decomp"></canvas></div></div>
    <div class="kpis" id="dKpis"></div>
    <div class="note">A <b>negative labour</b> segment (Romania) is a demographic drag the productivity channel must offset.</div></section>
  <section class="slide" data-i="2">
    <div class="kick">Step 3 · The reverse arrow</div><h2>Does healthy longevity lift productivity?</h2>
    <p class="lead">If longer <i>healthy</i> lives made workers more productive, healthy share and GDP-per-worker
    would rise together across countries. Each point is a country.</p>
    <div class="panel"><div class="chwrap"><canvas id="cross"></canvas></div></div>
    <div class="kpis" id="cKpis"></div></section>
  <section class="slide" data-i="3">
    <div class="kick">Step 4 · Honest answer</div><h2>Within a country, no link</h2>
    <p class="lead">Year-on-year, changes in healthy share explain none of the change in productivity. The
    longevity dividend reaches GDP through the <b>number of healthy workers</b>, not a per-worker premium.</p>
    <div class="panel"><div class="chwrap"><canvas id="diff"></canvas></div></div>
    <div class="kpis" id="aKpis"></div>
    <div class="note">Descriptive identity decomposition — no causal claim; productivity bundles capital &amp; technology.</div></section>
</main>
<footer>
  <button class="nav ghost" id="prev">‹ Back</button>
  <div style="display:flex;align-items:center;gap:14px"><button class="nav ghost" id="play">▶ Present</button>
  <span class="who" id="counter"></span></div>
  <button class="nav" id="next">Next ›</button>
</footer>
<script>const DATA = __DATA__;</script>
<script>
const STEPS=[["The identity","GDP build-up"],["Growth accounting","Labour vs productivity"],["Reverse arrow","Cross-country"],["Honest answer","Within-country"]];
const C={slate:'#475569',mustard:'#D97706',sage:'#4ADE80',terra:'#B91C1C',acc:'#166534',ink:'#292524',mut:'#78716C',line:'#E7E5E4'};
Chart.defaults.color=C.mut;Chart.defaults.font.family="-apple-system,Segoe UI,Roboto,Arial,sans-serif";Chart.defaults.borderColor=C.line;
let state={country:'ALL',slide:0},charts={};
const sel=document.getElementById('country');
Object.entries(DATA.countries).forEach(([k,v])=>{const o=document.createElement('option');o.value=k;o.textContent=v;sel.appendChild(o);});
sel.value=state.country;sel.onchange=()=>{state.country=sel.value;renderAll();};
const track=document.getElementById('track');
STEPS.forEach((s,i)=>{if(i>0){const l=document.createElement('span');l.className='link';l.dataset.link=i;track.appendChild(l);}
  const el=document.createElement('div');el.className='step';el.dataset.step=i;
  el.innerHTML=`<span class="dot">${i+1}</span><span>${s[0]}</span>`;el.onclick=()=>go(i);track.appendChild(el);});
function go(i){state.slide=Math.max(0,Math.min(3,i));
  document.querySelectorAll('.slide').forEach(s=>s.classList.toggle('active',+s.dataset.i===state.slide));
  document.querySelectorAll('.step').forEach((s,idx)=>{s.classList.toggle('active',idx===state.slide);s.classList.toggle('done',idx<state.slide);});
  document.querySelectorAll('.link').forEach(l=>l.classList.toggle('done',+l.dataset.link<=state.slide));
  document.getElementById('prev').disabled=state.slide===0;
  document.getElementById('next').textContent=state.slide===3?'Finish':'Next ›';
  document.getElementById('counter').textContent=`Step ${state.slide+1} of 4 — ${STEPS[state.slide][1]}`;renderAll();}
document.getElementById('prev').onclick=()=>go(state.slide-1);document.getElementById('next').onclick=()=>go(state.slide+1);
document.addEventListener('keydown',e=>{if(e.key==='ArrowRight')go(state.slide+1);if(e.key==='ArrowLeft')go(state.slide-1);});
function destroy(id){if(charts[id]){charts[id].destroy();delete charts[id];}}
const axis=(t,extra={})=>({title:{display:!!t,text:t,color:C.mut},grid:{color:C.line},...extra});
function kpi(v,l){return `<div class="kpi"><div class="v">${v}</div><div class="l">${l}</div></div>`;}

function drawGDP(){destroy('gdp');const d=DATA.gdp[state.country];const labels=d.oy.concat(d.fy);
  const obs=d.ov.concat(Array(d.fy.length).fill(null));
  const fcast=Array(d.oy.length-1).fill(null).concat([d.ov[d.ov.length-1]]).concat(d.fm);
  const pad=a=>Array(d.oy.length).fill(null).concat(a);
  charts.gdp=new Chart(document.getElementById('gdp'),{type:'line',data:{labels,datasets:[
    {label:'80% band',data:pad(d.lo),borderColor:'transparent',backgroundColor:'rgba(217,119,6,.12)',pointRadius:0,fill:'+1'},
    {label:'_hi',data:pad(d.hi),borderColor:'transparent',backgroundColor:'rgba(217,119,6,.12)',pointRadius:0,fill:false},
    {label:'Observed',data:obs,borderColor:C.slate,backgroundColor:C.slate,tension:.2,pointRadius:0,borderWidth:2.5},
    {label:'Forecast (L × productivity)',data:fcast,borderColor:C.mustard,backgroundColor:C.mustard,borderDash:[5,3],tension:.2,pointRadius:0,borderWidth:2.5}]},
    options:{responsive:true,maintainAspectRatio:false,interaction:{mode:'index',intersect:false},
      scales:{y:{...axis('real GDP (€ trillion, CLV15)')},x:axis()},
      plugins:{title:{display:true,text:`Real GDP — ${DATA.countries[state.country]}`,color:C.ink,font:{size:15}},
        legend:{position:'bottom',labels:{filter:i=>!i.text.startsWith('_')}},
        tooltip:{filter:i=>!i.dataset.label.startsWith('_'),callbacks:{label:c=>`${c.dataset.label}: €${c.raw}T`}}}}});
  const a=d.ov[d.ov.length-1],b=d.fm[d.fm.length-1];
  document.getElementById('gKpis').innerHTML=kpi('€'+a+'T','GDP 2024')+kpi('€'+b+'T','GDP 2033')+
    kpi(((b/a)**(1/9)-1>=0?'+':'')+(((b/a)**(1/9)-1)*100).toFixed(1)+'%/yr','Real growth');}

function drawDecomp(){destroy('decomp');const d=DATA.decomp;
  charts.decomp=new Chart(document.getElementById('decomp'),{type:'bar',data:{labels:d.names,datasets:[
    {label:'Productivity',data:d.prod,backgroundColor:C.acc,stack:'s',borderRadius:2},
    {label:'Labour',data:d.labour,backgroundColor:C.slate,stack:'s',borderRadius:2}]},
    options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,
      scales:{x:{stacked:true,...axis('contribution to projected GDP growth (pp/yr)')},y:{stacked:true,grid:{display:false}}},
      plugins:{title:{display:true,text:'Projected growth split: labour vs productivity (2024–2033)',color:C.ink,font:{size:15}},
        legend:{position:'bottom'},
        tooltip:{callbacks:{label:c=>`${c.dataset.label}: ${c.raw>=0?'+':''}${c.raw} pp/yr`,
          footer:items=>`Total GDP: ${d.gdp[items[0].dataIndex]>=0?'+':''}${d.gdp[items[0].dataIndex]}%/yr`}}}}});
  const i=d.codes.indexOf('RO');
  document.getElementById('dKpis').innerHTML=
    kpi('productivity-led','East (catch-up convergence)')+kpi('labour-tilted','West / EFTA')+
    kpi((i>=0?d.labour[i]:0)+' pp/yr','Romania labour channel (drag)');}

function drawCross(){destroy('cross');const s=DATA.cross;
  charts.cross=new Chart(document.getElementById('cross'),{type:'scatter',
    data:{datasets:[{label:'Country',data:s.map(p=>({x:p.hs,y:p.prod,name:p.name})),
      backgroundColor:C.mustard,borderColor:C.acc,pointRadius:7,pointHoverRadius:9}]},
    options:{responsive:true,maintainAspectRatio:false,
      scales:{x:{...axis(`healthy share (HLY / LE), ${DATA.cyear}`)},y:{...axis('productivity (GDP per worker, €000s)'),type:'logarithmic'}},
      plugins:{title:{display:true,text:'Cross-country: healthier ≠ more productive',color:C.ink,font:{size:15}},legend:{display:false},
        tooltip:{callbacks:{label:c=>`${c.raw.name}: healthy share ${c.raw.x} · €${c.raw.y}k/worker`}}}}});
  document.getElementById('cKpis').innerHTML=kpi(DATA.rel.cross_corr,'Cross-country correlation (wrong sign)')+
    kpi('GALI','self-perceived health, not output');}

function drawDiff(){destroy('diff');
  charts.diff=new Chart(document.getElementById('diff'),{type:'scatter',
    data:{datasets:[{label:'Year-on-year',data:DATA.diff,backgroundColor:'rgba(71,85,105,.5)',borderColor:C.slate,pointRadius:4}]},
    options:{responsive:true,maintainAspectRatio:false,
      scales:{x:{...axis('Δ healthy share (pp / yr)')},y:{...axis('Δ productivity (% / yr)')}},
      plugins:{title:{display:true,text:'Within-country, year-on-year — no relationship',color:C.ink,font:{size:15}},legend:{display:false},
        tooltip:{callbacks:{label:c=>`Δhealthy ${c.raw.x}pp · Δprod ${c.raw.y}%`}}}}});
  document.getElementById('aKpis').innerHTML=kpi(DATA.rel.within_elasticity,'Within slope (≈ 0)')+
    kpi('R² '+DATA.rel.within_r2,'no explanatory power')+kpi(DATA.rel.prod_real_growth_pct+'%/yr','Productivity grows on capital & tech');}

function renderAll(){if(state.slide===0)drawGDP();else if(state.slide===1)drawDecomp();else if(state.slide===2)drawCross();else drawDiff();}
let timer=null;
function setPlay(on){const b=document.getElementById('play');
  if(on){b.textContent='⏸ Pause';b.classList.remove('ghost');timer=setInterval(()=>go(state.slide>=3?0:state.slide+1),7000);}
  else{b.textContent='▶ Present';b.classList.add('ghost');clearInterval(timer);timer=null;}}
document.getElementById('play').onclick=()=>setPlay(!timer);
go(0);
</script>
</body></html>"""

(OUT / "macro_story.html").write_text(HTML.replace("__DATA__", json.dumps(DATA)), encoding="utf-8")
print(f"wrote outputs/macro_story.html ({len(json.dumps(DATA))} bytes data)")
