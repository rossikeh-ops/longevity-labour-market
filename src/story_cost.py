# -*- coding: utf-8 -*-
"""
Build outputs/cost_story.html — a guided, slide-based narrative of LEVEL 4 (cost of
unhealthy years), with interactive Chart.js + progress tracker + present mode.

Four slides:
  1. Living longer    — life expectancy vs healthy life years (the gap)
  2. The burden       — Pop × (LE − HLY), person-years in poor health, to 2033
  3. Does it cost?    — cross-country: burden vs NACE-Q sector (a size artefact)
  4. The honest answer— within-country year-on-year: no link (sector tracks GDP)
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
NAME = {"ALL": "All 8 countries", "BG": "Bulgaria", "PL": "Poland", "CZ": "Czechia",
        "RO": "Romania", "DE": "Germany", "FR": "France", "NO": "Norway", "CH": "Switzerland"}
GEO = [c for c in NAME if c != "ALL"]
M = 1e6


def _geos(c):
    return GEO if c == "ALL" else [c]


co = pd.read_csv(OUT / "cost_observed.csv")
fc = pd.read_csv(OUT / "cost_forecast.csv")
rel = json.loads((OUT / "cost_relationship.json").read_text(encoding="utf-8"))
panel = pd.read_parquet(ROOT / "data" / "processed" / "panel.parquet")

# LE & HLY (pop-weighted over sex / countries)
lehly = {}
for c in NAME:
    sub = co[co.country.isin(_geos(c))]
    yrs = sorted(sub.year.unique())
    le, hly = [], []
    for y in yrs:
        r = sub[sub.year == y]
        w = r["pop_total"].sum()
        le.append(round(float((r["le_birth"] * r["pop_total"]).sum() / w), 1))
        hly.append(round(float((r["hly_birth"] * r["pop_total"]).sum() / w), 1))
    lehly[c] = {"years": [int(y) for y in yrs], "le": le, "hly": hly}

# burden (Pop × (LE−HLY)) observed + forecast, million person-years
burden = {}
for c in NAME:
    cs = _geos(c)
    o = co[co.country.isin(cs) & (co.year <= 2024)].groupby("year")["poor_py"].sum() / M
    f = fc[fc.country.isin(cs)].groupby("year").agg(
        m=("poor_py", "sum"), lo=("poor_lo", "sum"), hi=("poor_hi", "sum")) / M
    burden[c] = {"oy": [int(y) for y in o.index], "ov": [round(v, 1) for v in o.values],
                 "fy": [int(y) for y in f.index], "fm": [round(v, 1) for v in f["m"].values],
                 "lo": [round(v, 1) for v in f["lo"].values], "hi": [round(v, 1) for v in f["hi"].values]}

# cross-country scatter (2024): PER-CAPITA burden vs NACE-Q sector, both per head of population
# (dividing both axes by population removes the country-size artefact that inflates the raw scatter)
scatter = []
for c in GEO:
    poor_py = co[(co.country == c) & (co.year == 2024)]["poor_py"].sum()   # person-years
    pr = panel[(panel.country == c) & (panel.year == 2024)]
    pop = float(pr["pop_total"].sum())
    q_m = float(pr["nace_q_va"].iloc[0])                                   # € millions
    scatter.append({"c": c, "name": NAME[c],
                    "poor": round(poor_py / M),          # kept for reference / KPIs
                    "q": round(q_m / 1000, 1),           # €bn, kept for reference
                    "bpc": round(poor_py / pop, 1),      # poor-health years per person
                    "qpc": round(q_m * 1e6 / pop)})      # NACE-Q value added, € per person

# within-country year-on-year cloud: %Δ burden vs %Δ NACE-Q
panel = panel.copy()
panel["poor_py"] = panel["pop_total"] * (panel["le_birth"] - panel["hly_birth"])
agg = panel.groupby(["country", "year"]).agg(poor=("poor_py", "sum"), q=("nace_q_va", "first")).reset_index()
agg = agg.dropna(subset=["poor", "q"])
agg = agg[(agg.poor > 0) & (agg.q > 0)]
diff_pts = []
for c, g in agg.groupby("country"):
    g = g.sort_values("year")
    dlp = np.diff(np.log(g["poor"].to_numpy(float))) * 100
    dlq = np.diff(np.log(g["q"].to_numpy(float))) * 100
    for a, b in zip(dlp, dlq):
        diff_pts.append({"x": round(float(a), 2), "y": round(float(b), 2)})

DATA = {"countries": NAME, "lehly": lehly, "burden": burden,
        "scatter": scatter, "diff": diff_pts, "rel": rel}

HTML = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cost of Unhealthy Years — a guided story</title>
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
.slide h2{font-size:24px;margin:4px 0 6px}.slide p.lead{color:var(--mut);margin:0 0 14px;max-width:760px}
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
  <h1>Cost of Unhealthy Years — a guided story</h1>
  <span class="who">8 European countries · to 2033</span><span class="spacer"></span>
  <label class="who" for="country">Country&nbsp;</label><select id="country"></select>
</header>
<nav class="track" id="track"></nav>
<main>
  <section class="slide" data-i="0">
    <div class="kick">Step 1 · Longer lives</div><h2>We live longer — but not all of it healthy</h2>
    <p class="lead">Life expectancy keeps rising, but <b>healthy life years</b> (HLY) trail it. The gap between
    the two lines is the years each person is expected to live in poor health.</p>
    <div class="panel"><div class="chwrap"><canvas id="lehly"></canvas></div></div>
    <div class="kpis" id="leKpis"></div>
    <div class="note">HLY is self-perceived (Eurostat GALI survey) — e.g. Switzerland reports low HLY despite top life expectancy.</div></section>
  <section class="slide" data-i="1">
    <div class="kick">Step 2 · The burden</div><h2>The poor-health burden, in person-years</h2>
    <p class="lead"><b>Burden = Population × (LE − HLY)</b> — total person-years lived in poor health. Near-flat
    to 2033: ageing pushes it up, rising healthy-life years pull it down.</p>
    <div class="panel"><div class="chwrap"><canvas id="burden"></canvas></div></div>
    <div class="kpis" id="bKpis"></div></section>
  <section class="slide" data-i="2">
    <div class="kick">Step 3 · Does it cost?</div><h2>Burden vs the health &amp; social-work sector — per capita</h2>
    <p class="lead">The raw totals rise together only because <b>big countries have both</b> a big burden and a big
    sector. So we <b>divide both by population</b>: poor-health <b>years per person</b> against NACE-Q value added
    <b>per person</b>. The size artefact is gone — and the vertical spread is now driven by <b>national income</b>
    (rich Norway and Switzerland spend €6–7k/person; Romania and Bulgaria €280–370), not by the health burden.
    Each point is a country, 2024.</p>
    <div class="panel"><div class="chwrap"><canvas id="scatter"></canvas></div></div>
    <div class="kpis" id="sKpis"></div>
    <div class="note">Per head of population removes scale: e.g. Poland's burden is ~12× Bulgaria's in totals but
    similar per person. The sector's spend per capita tracks GDP, not poor-health years — reinforcing Step 4's
    finding that the demographic burden does not drive the sector's cost.</div></section>
  <section class="slide" data-i="3">
    <div class="kick">Step 4 · The honest answer</div><h2>Within a country, the link vanishes</h2>
    <p class="lead">Plot the <b>year-on-year change</b> in the burden against the change in the sector. The cloud
    is shapeless — the burden does <b>not</b> drive the sector's cost; it tracks the wider economy.</p>
    <div class="panel"><div class="chwrap"><canvas id="diff"></canvas></div></div>
    <div class="kpis" id="dKpis"></div>
    <div class="note">Descriptive, no causal claim. Within-country elasticity ≈ 0 — so we forecast the sector on
    its own ~2.4%/yr trend, not from the demographic burden.</div></section>
</main>
<footer>
  <button class="nav ghost" id="prev">‹ Back</button>
  <div style="display:flex;align-items:center;gap:14px"><button class="nav ghost" id="play">▶ Present</button>
  <span class="who" id="counter"></span></div>
  <button class="nav" id="next">Next ›</button>
</footer>
<script>const DATA = __DATA__;</script>
<script>
const STEPS=[["Longer lives","LE vs HLY"],["The burden","Person-years"],["Does it cost?","Cross-country"],["Honest answer","Within-country"]];
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
document.getElementById('prev').onclick=()=>go(state.slide-1);
document.getElementById('next').onclick=()=>go(state.slide+1);
document.addEventListener('keydown',e=>{if(e.key==='ArrowRight')go(state.slide+1);if(e.key==='ArrowLeft')go(state.slide-1);});
function destroy(id){if(charts[id]){charts[id].destroy();delete charts[id];}}
const axis=(t)=>({title:{display:!!t,text:t,color:C.mut},grid:{color:C.line}});
function kpi(v,l){return `<div class="kpi"><div class="v">${v}</div><div class="l">${l}</div></div>`;}
function drawLEHLY(){destroy('lehly');const d=DATA.lehly[state.country];
  charts.lehly=new Chart(document.getElementById('lehly'),{type:'line',data:{labels:d.years,
    datasets:[{label:'Life expectancy',data:d.le,borderColor:C.slate,backgroundColor:C.slate,tension:.3,pointRadius:0,borderWidth:2.5},
      {label:'Healthy life years',data:d.hly,borderColor:C.acc,backgroundColor:'rgba(22,101,52,.10)',fill:'-1',tension:.3,pointRadius:0,borderWidth:2.5}]},
    options:{responsive:true,maintainAspectRatio:false,interaction:{mode:'index',intersect:false},
      scales:{y:{...axis('years')},x:axis()},
      plugins:{title:{display:true,text:`Life expectancy vs healthy life years — ${DATA.countries[state.country]}`,color:C.ink,font:{size:15}},
        legend:{position:'bottom'},tooltip:{callbacks:{label:c=>`${c.dataset.label}: ${c.raw} yrs`}}}}});
  const le=d.le[d.le.length-1],h=d.hly[d.hly.length-1];
  document.getElementById('leKpis').innerHTML=kpi(le+' yrs','Life expectancy')+kpi(h+' yrs','Healthy life years')+kpi((le-h).toFixed(1)+' yrs','In poor health / person');}
function drawBurden(){destroy('burden');const d=DATA.burden[state.country];const labels=d.oy.concat(d.fy);
  const obs=d.ov.concat(Array(d.fy.length).fill(null));
  const fcast=Array(d.oy.length-1).fill(null).concat([d.ov[d.ov.length-1]]).concat(d.fm);
  const pad=a=>Array(d.oy.length).fill(null).concat(a);
  charts.burden=new Chart(document.getElementById('burden'),{type:'line',data:{labels,datasets:[
    {label:'80% band',data:pad(d.lo),borderColor:'transparent',backgroundColor:'rgba(217,119,6,.13)',pointRadius:0,fill:'+1'},
    {label:'_hi',data:pad(d.hi),borderColor:'transparent',backgroundColor:'rgba(217,119,6,.13)',pointRadius:0,fill:false},
    {label:'Observed',data:obs,borderColor:C.slate,backgroundColor:C.slate,tension:.25,pointRadius:0,borderWidth:2.5},
    {label:'Forecast',data:fcast,borderColor:C.mustard,backgroundColor:C.mustard,borderDash:[5,3],tension:.25,pointRadius:0,borderWidth:2.5}]},
    options:{responsive:true,maintainAspectRatio:false,interaction:{mode:'index',intersect:false},
      scales:{y:{...axis('poor-health person-years (millions)')},x:axis()},
      plugins:{title:{display:true,text:`Poor-health burden — ${DATA.countries[state.country]}`,color:C.ink,font:{size:15}},
        legend:{position:'bottom',labels:{filter:i=>!i.text.startsWith('_')}},
        tooltip:{filter:i=>!i.dataset.label.startsWith('_'),callbacks:{label:c=>`${c.dataset.label}: ${c.raw} M PY`}}}}});
  const chg=((d.fm[d.fm.length-1]/d.ov[d.ov.length-1]-1)*100).toFixed(1);
  document.getElementById('bKpis').innerHTML=kpi(d.ov[d.ov.length-1]+'M','Burden 2024')+kpi(d.fm[d.fm.length-1]+'M','Burden 2033')+kpi((chg>=0?'+':'')+chg+'%','Change');}
function drawScatter(){destroy('scatter');const s=DATA.scatter;
  charts.scatter=new Chart(document.getElementById('scatter'),{type:'scatter',
    data:{datasets:[{label:'Country',data:s.map(p=>({x:p.bpc,y:p.qpc,name:p.name})),backgroundColor:C.mustard,borderColor:C.acc,pointRadius:7,pointHoverRadius:9}]},
    options:{responsive:true,maintainAspectRatio:false,
      scales:{x:{...axis('poor-health years per person, 2024')},y:{...axis('NACE-Q value added, € per person')}},
      plugins:{title:{display:true,text:'Per capita: burden vs health & social-work sector (2024)',color:C.ink,font:{size:15}},legend:{display:false},
        tooltip:{callbacks:{label:c=>`${c.raw.name}: ${c.raw.x} yrs/person · €${c.raw.y.toLocaleString()}/person`}}}}});
  const qs=s.map(p=>p.qpc), qmin=Math.min(...qs), qmax=Math.max(...qs);
  document.getElementById('sKpis').innerHTML=kpi('€'+qmin.toLocaleString()+'–'+qmax.toLocaleString(),'Sector spend per person (RO→NO)')+kpi('per capita','Size artefact removed — spread is national income, not population');}
function drawDiff(){destroy('diff');
  charts.diff=new Chart(document.getElementById('diff'),{type:'scatter',
    data:{datasets:[{label:'Year-on-year',data:DATA.diff,backgroundColor:'rgba(71,85,105,.6)',borderColor:C.slate,pointRadius:4}]},
    options:{responsive:true,maintainAspectRatio:false,
      scales:{x:{...axis('Δ poor-health burden (% / yr)')},y:{...axis('Δ NACE-Q value added (% / yr)')}},
      plugins:{title:{display:true,text:'Within-country, year-on-year — no relationship',color:C.ink,font:{size:15}},legend:{display:false},
        tooltip:{callbacks:{label:c=>`Δburden ${c.raw.x}% · Δsector ${c.raw.y}%`}}}}});
  document.getElementById('dKpis').innerHTML=kpi(DATA.rel.elasticity_within_diff,'Within elasticity (≈ 0)')+kpi('R² '+DATA.rel.r2_within_diff,'no explanatory power')+kpi(DATA.rel.q_real_growth_pct+'%/yr','Sector grows with the economy');}
function renderAll(){if(state.slide===0)drawLEHLY();else if(state.slide===1)drawBurden();else if(state.slide===2)drawScatter();else drawDiff();}
let timer=null;
function setPlay(on){const b=document.getElementById('play');
  if(on){b.textContent='⏸ Pause';b.classList.remove('ghost');timer=setInterval(()=>go(state.slide>=3?0:state.slide+1),7000);}
  else{b.textContent='▶ Present';b.classList.add('ghost');clearInterval(timer);timer=null;}}
document.getElementById('play').onclick=()=>setPlay(!timer);
go(0);
</script>
</body></html>"""

(OUT / "cost_story.html").write_text(HTML.replace("__DATA__", json.dumps(DATA)), encoding="utf-8")
print(f"wrote outputs/cost_story.html ({len(json.dumps(DATA))} bytes data)")
