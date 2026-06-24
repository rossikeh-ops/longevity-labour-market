# -*- coding: utf-8 -*-
"""
Build outputs/demand_story.html — a guided, slide-based narrative of the LABOUR
DEMAND build-up, mirroring the supply story, with interactive Chart.js + a
methodology progress tracker and a present/autoplay mode.

Four slides follow the demand equation  Demand = (employed + vacancies) × service:
  1. Jobs base       — employment + vacancies = number of jobs, to 2033
  2. Vacancies       — the Beveridge curve (vacancies fall as unemployment rises)
  3. Required service— length of service for a full pension, by country & sex
  4. Final demand    — jobs × service = potential demand (person-years) to 2033 + band

Data inlined as JSON; Chart.js from CDN. Self-contained for GitHub Pages.
"""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
NAME = {"ALL": "All 8 countries", "BG": "Bulgaria", "PL": "Poland", "CZ": "Czechia",
        "RO": "Romania", "DE": "Germany", "FR": "France", "NO": "Norway", "CH": "Switzerland"}
GEO = [c for c in NAME if c != "ALL"]


def _geos(c):
    return GEO if c == "ALL" else [c]


so = pd.read_csv(OUT / "supply_observed.csv")
fc = pd.read_csv(OUT / "demand_forecast.csv")
rp = pd.read_csv(ROOT / "data" / "retirement_params.csv")

# ---- jobs (employed + vacancies), millions of people ----
jobs = {}
for c in NAME:
    cs = _geos(c)
    o = so[so.country.isin(cs) & (so.year <= 2024)].groupby("year")["jobs"].sum() / 1e6
    f = fc[fc.country.isin(cs)].groupby("year")["jobs"].sum() / 1e6
    jobs[c] = {"oy": [int(y) for y in o.index], "ov": [round(v, 2) for v in o.values],
               "fy": [int(y) for y in f.index], "fv": [round(v, 2) for v in f.values]}

# ---- Beveridge scatter: (unemployment, vacancy rate) per year ----
bev = {}
for c in NAME:
    cs = _geos(c)
    sub = so[so.country.isin(cs)]
    pts = []
    for y in sorted(sub.year.unique()):
        r = sub[sub.year == y]
        u = (r["unemp_rate"] * r["employed_ths"]).sum() / r["employed_ths"].sum()
        v = r["vacancy_rate"].mean()
        if pd.notna(u) and pd.notna(v):
            pts.append({"x": round(float(u), 2), "y": round(float(v), 2), "year": int(y)})
    bev[c] = pts

# ---- required service length (all 8 countries, by sex) ----
service = {"countries": [NAME[c] for c in GEO], "codes": GEO,
           "M": [float(rp[(rp.country == c) & (rp.sex == "M")]["required_service_years"].iloc[0]) for c in GEO],
           "F": [float(rp[(rp.country == c) & (rp.sex == "F")]["required_service_years"].iloc[0]) for c in GEO]}

# ---- demand forecast (million career person-years) ----
demand = {}
for c in NAME:
    cs = _geos(c)
    o = so[so.country.isin(cs) & (so.year <= 2024)].groupby("year")["demand"].sum() / 1e6
    f = fc[fc.country.isin(cs)].groupby("year").agg(
        m=("demand", "sum"), lo=("demand_lo", "sum"), hi=("demand_hi", "sum")) / 1e6
    demand[c] = {"oy": [int(y) for y in o.index], "ov": [round(v, 1) for v in o.values],
                 "fy": [int(y) for y in f.index], "fm": [round(v, 1) for v in f["m"].values],
                 "lo": [round(v, 1) for v in f["lo"].values], "hi": [round(v, 1) for v in f["hi"].values]}

DATA = {"countries": NAME, "jobs": jobs, "bev": bev, "service": service, "demand": demand}

HTML = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Labour Demand — a guided story</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<style>
:root{--bg:#FAFAF9;--card:#FFFFFF;--ink:#292524;--mut:#78716C;--line:#E7E5E4;--acc:#166534;
--slate:#475569;--mustard:#D97706;--sage:#4ADE80;--terra:#B91C1C;}
*{box-sizing:border-box}html,body{margin:0;height:100%}
body{background:var(--bg);color:var(--ink);font:16px/1.6 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
display:flex;flex-direction:column;min-height:100vh}
header{padding:18px 28px 8px;display:flex;align-items:center;gap:18px;flex-wrap:wrap}
header h1{font-size:19px;margin:0;font-weight:650}
header .who{color:var(--mut);font-size:13px}
.spacer{flex:1}
select{background:var(--card);color:var(--ink);border:1px solid var(--line);border-radius:8px;padding:8px 10px;font-size:14px}
.track{display:flex;align-items:center;gap:0;padding:6px 28px 12px;flex-wrap:wrap}
.step{display:flex;align-items:center;gap:9px;cursor:pointer;color:var(--mut);font-size:13px;font-weight:600}
.step .dot{width:30px;height:30px;border-radius:50%;border:2px solid var(--line);background:var(--card);
display:flex;align-items:center;justify-content:center;font-size:13px;color:var(--mut);transition:.2s}
.step.active .dot,.step.done .dot{border-color:var(--acc);background:var(--acc);color:#fff}
.step.active{color:var(--ink)}
.link{flex:0 0 46px;height:3px;background:var(--line);margin:0 6px;border-radius:2px}
.link.done{background:var(--acc)}
main{flex:1;padding:6px 28px 20px;max-width:1080px;margin:0 auto;width:100%}
.slide{display:none;animation:fade .35s ease}.slide.active{display:block}
@keyframes fade{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
.kick{font-size:12px;letter-spacing:1px;text-transform:uppercase;color:var(--acc);font-weight:700}
.slide h2{font-size:24px;margin:4px 0 6px}
.slide p.lead{color:var(--mut);margin:0 0 14px;max-width:760px}
.panel{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:16px 18px;margin:12px 0}
.chwrap{position:relative;height:430px}
.kpis{display:flex;gap:14px;flex-wrap:wrap;margin-top:8px}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px 16px;min-width:150px}
.kpi .v{font-size:22px;font-weight:700}.kpi .l{color:var(--mut);font-size:12px;margin-top:2px}
.note{color:var(--mut);font-size:13px;background:var(--card);border:1px solid var(--line);
border-radius:10px;padding:12px 14px;margin-top:10px}code{color:var(--acc)}
footer{display:flex;align-items:center;justify-content:space-between;padding:14px 28px 26px;max-width:1080px;margin:0 auto;width:100%}
button.nav{background:var(--acc);color:#fff;border:none;border-radius:10px;padding:10px 20px;font-size:14px;font-weight:600;cursor:pointer}
button.nav:disabled{background:var(--line);color:var(--mut);cursor:default}
button.ghost{background:var(--card);color:var(--ink);border:1px solid var(--line)}
a{color:var(--acc)}
</style></head><body>
<header>
  <h1>Labour Demand — a guided story</h1>
  <span class="who">8 European countries · to 2033</span>
  <span class="spacer"></span>
  <label class="who" for="country">Country&nbsp;</label><select id="country"></select>
</header>
<nav class="track" id="track"></nav>
<main>
  <section class="slide" data-i="0">
    <div class="kick">Step 1 · Jobs</div>
    <h2>The jobs base</h2>
    <p class="lead">Demand starts from the jobs the economy runs: <b>employed people plus open
    vacancies</b>. We forecast each and add them, observed then projected to 2033.</p>
    <div class="panel"><div class="chwrap"><canvas id="jobs"></canvas></div></div>
    <div class="kpis" id="jobsKpis"></div>
    <div class="note">Jobs = employment (<code>lfsa_egan</code>) + job vacancies (<code>jvs_q_r21</code>).</div>
  </section>
  <section class="slide" data-i="1">
    <div class="kick">Step 2 · Vacancies</div>
    <h2>Vacancies &amp; the Beveridge curve</h2>
    <p class="lead">Vacancies are shock-driven, but they obey one rule: they <b>fall as unemployment
    rises</b> (the Beveridge curve). We forecast vacancies through this relationship. Each point is a year.</p>
    <div class="panel"><div class="chwrap"><canvas id="bev"></canvas></div></div>
    <div class="kpis" id="bevKpis"></div>
    <div class="note">Job vacancy rate vs unemployment rate, per year (<code>jvs_q_r21</code>, <code>une_rt_a</code>).
    The downward cloud is the Beveridge curve the vacancy model anchors to.</div>
  </section>
  <section class="slide" data-i="2">
    <div class="kick">Step 3 · Required service</div>
    <h2>Required length of service</h2>
    <p class="lead">Each job demands a full career to earn a pension. The <b>required years of service</b>
    differ sharply by country and sex — the multiplier that turns jobs into career person-years.</p>
    <div class="panel"><div class="chwrap"><canvas id="service"></canvas></div></div>
    <div class="kpis" id="svcKpis"></div>
    <div class="note">Required contributory years for a full pension, by sex (MISSOC / OECD Pensions at a Glance).
    France uses a points system (effective ≈ 43y). Shown for all 8 countries.</div>
  </section>
  <section class="slide" data-i="3">
    <div class="kick">Step 4 · Total demand</div>
    <h2>Potential labour demand</h2>
    <p class="lead">Jobs × required service = potential demand for labour in <b>human-working-years</b>,
    observed then forecast to 2033 with an 80% uncertainty band.</p>
    <div class="panel"><div class="chwrap"><canvas id="demand"></canvas></div></div>
    <div class="kpis" id="demKpis"></div>
    <div class="note">Demand = (employed + vacancies) × required length of service. Broadly flat to 2033,
    tilted by the East's shrinking workforce vs the West holding steady.</div>
  </section>
</main>
<footer>
  <button class="nav ghost" id="prev">‹ Back</button>
  <div style="display:flex;align-items:center;gap:14px">
    <button class="nav ghost" id="play">▶ Present</button>
    <span class="who" id="counter"></span></div>
  <button class="nav" id="next">Next ›</button>
</footer>
<script>const DATA = __DATA__;</script>
<script>
const STEPS=[["Jobs","Employed + vacancies"],["Vacancies","Beveridge curve"],
  ["Service","Years per career"],["Total demand","Forecast 2033"]];
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
function lineOF(id,d,unit,title){
  destroy(id);const labels=d.oy.concat(d.fy);
  const obs=d.ov.concat(Array(d.fy.length).fill(null));
  const fcast=Array(d.oy.length-1).fill(null).concat([d.ov[d.ov.length-1]]).concat(d.fm||d.fv);
  const sets=[{label:'Observed',data:obs,borderColor:C.slate,backgroundColor:C.slate,tension:.25,pointRadius:0,borderWidth:2.5},
    {label:'Forecast',data:fcast,borderColor:C.acc,backgroundColor:C.acc,borderDash:[5,3],tension:.25,pointRadius:0,borderWidth:2.5}];
  if(d.lo){const pad=(a)=>Array(d.oy.length).fill(null).concat(a);
    sets.unshift({label:'_hi',data:pad(d.hi),borderColor:'transparent',backgroundColor:'rgba(22,101,52,.10)',pointRadius:0,fill:false});
    sets.unshift({label:'80% band',data:pad(d.lo),borderColor:'transparent',backgroundColor:'rgba(22,101,52,.10)',pointRadius:0,fill:'+1'});}
  charts[id]=new Chart(document.getElementById(id),{type:'line',data:{labels,datasets:sets},
    options:{responsive:true,maintainAspectRatio:false,interaction:{mode:'index',intersect:false},
      scales:{y:{...axis(unit)},x:axis()},
      plugins:{title:{display:true,text:title,color:C.ink,font:{size:15}},
        legend:{position:'bottom',labels:{filter:i=>!i.text.startsWith('_')}},
        tooltip:{filter:i=>!i.dataset.label.startsWith('_'),callbacks:{label:c=>`${c.dataset.label}: ${c.raw} ${unit.includes('person')?'M PY':'M'}`}}}}});
}
function drawJobs(){const d=DATA.jobs[state.country];
  lineOF('jobs',d,'jobs (millions of people)',`Number of jobs — ${DATA.countries[state.country]}`);
  document.getElementById('jobsKpis').innerHTML=kpi(d.ov[d.ov.length-1]+'M','Jobs 2024')+
    kpi(d.fv[d.fv.length-1]+'M','Jobs 2033')+kpi(((d.fv[d.fv.length-1]/d.ov[d.ov.length-1]-1)*100).toFixed(1)+'%','Change to 2033');}
function drawBev(){destroy('bev');const pts=DATA.bev[state.country];
  charts.bev=new Chart(document.getElementById('bev'),{type:'scatter',
    data:{datasets:[{label:'Year',data:pts,backgroundColor:C.mustard,borderColor:C.acc,pointRadius:5,pointHoverRadius:7}]},
    options:{responsive:true,maintainAspectRatio:false,
      scales:{x:{...axis('unemployment rate %'),ticks:{callback:v=>v+'%'}},y:{...axis('vacancy rate %'),ticks:{callback:v=>v+'%'}}},
      plugins:{title:{display:true,text:`Beveridge curve — ${DATA.countries[state.country]}`,color:C.ink,font:{size:15}},legend:{display:false},
        tooltip:{callbacks:{label:c=>`${c.raw.year}: unemp ${c.raw.x}% · vacancy ${c.raw.y}%`}}}}});
  const xs=pts.map(p=>p.x),ys=pts.map(p=>p.y);
  document.getElementById('bevKpis').innerHTML=kpi(Math.min(...xs)+'–'+Math.max(...xs)+'%','Unemployment range')+
    kpi(Math.min(...ys)+'–'+Math.max(...ys)+'%','Vacancy-rate range');}
function drawService(){destroy('service');const s=DATA.service;
  charts.service=new Chart(document.getElementById('service'),{type:'bar',
    data:{labels:s.countries,datasets:[{label:'Men',data:s.M,backgroundColor:C.slate,borderRadius:3},
      {label:'Women',data:s.F,backgroundColor:C.mustard,borderRadius:3}]},
    options:{responsive:true,maintainAspectRatio:false,
      scales:{y:{...axis('required years of service'),beginAtZero:true},x:{grid:{display:false}}},
      plugins:{title:{display:true,text:'Required length of service for a full pension',color:C.ink,font:{size:15}},
        legend:{position:'bottom'},tooltip:{callbacks:{label:c=>`${c.dataset.label}: ${c.raw} years`}}}}});
  const mi=Math.min(...s.M,...s.F),ma=Math.max(...s.M,...s.F);
  document.getElementById('svcKpis').innerHTML=kpi(ma+'y','Longest required career')+kpi(mi+'y','Shortest')+
    kpi((s.M.reduce((a,b)=>a+b,0)/s.M.length).toFixed(0)+'y','Men, 8-country avg');}
function drawDemand(){const d=DATA.demand[state.country];
  lineOF('demand',d,'demand (million person-years)',`Potential labour demand — ${DATA.countries[state.country]}`);
  document.getElementById('demKpis').innerHTML=kpi(d.ov[d.ov.length-1]+'M','Demand 2024 (M PY)')+
    kpi(d.fm[d.fm.length-1]+'M','Demand 2033 (M PY)')+kpi(((d.fm[d.fm.length-1]/d.ov[d.ov.length-1]-1)*100).toFixed(1)+'%','Change to 2033');}
function renderAll(){
  if(state.slide===0)drawJobs();else if(state.slide===1)drawBev();
  else if(state.slide===2)drawService();else if(state.slide===3)drawDemand();}
let timer=null;
function setPlay(on){const b=document.getElementById('play');
  if(on){b.textContent='⏸ Pause';b.classList.remove('ghost');timer=setInterval(()=>go(state.slide>=3?0:state.slide+1),7000);}
  else{b.textContent='▶ Present';b.classList.add('ghost');clearInterval(timer);timer=null;}}
document.getElementById('play').onclick=()=>setPlay(!timer);
go(0);
</script>
</body></html>"""

html = HTML.replace("__DATA__", json.dumps(DATA))
(OUT / "demand_story.html").write_text(html, encoding="utf-8")
print(f"wrote outputs/demand_story.html ({len(html):,} bytes)")
