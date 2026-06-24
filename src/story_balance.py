# -*- coding: utf-8 -*-
"""
Build outputs/balance_story.html — a guided, slide-based narrative of the LABOUR
MARKET BALANCE (Level 3), with interactive Chart.js + progress tracker + present mode.

Four slides follow  Balance = Supply − Demand (human-working-years):
  1. Supply   — the healthy workforce, to 2033
  2. Demand   — the career-years jobs require, to 2033
  3. Balance  — subtract them: surplus or shortage, with bands
  4. The divide — 2033 balance by country: East surplus vs West shortage
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
M = 1e6


def _geos(c):
    return GEO if c == "ALL" else [c]


so = pd.read_csv(OUT / "supply_observed.csv")
bf = pd.read_csv(OUT / "balance_forecast.csv")


def _series(c, obs_col, fc_col, band=False):
    cs = _geos(c)
    o = so[so.country.isin(cs) & (so.year <= 2024)].groupby("year")[obs_col].sum() / M
    g = bf[bf.country.isin(cs)].groupby("year")
    fm = g[fc_col].sum() / M
    out = {"oy": [int(y) for y in o.index], "ov": [round(v, 1) for v in o.values],
           "fy": [int(y) for y in fm.index], "fm": [round(v, 1) for v in fm.values]}
    if band:
        out["lo"] = [round(v, 1) for v in (g["balance_lo"].sum().values / M)]
        out["hi"] = [round(v, 1) for v in (g["balance_hi"].sum().values / M)]
    return out


supply = {c: _series(c, "supply_realized", "supply") for c in NAME}
demand = {c: _series(c, "demand", "demand") for c in NAME}
balance = {c: _series(c, "balance_realized", "balance", band=True) for c in NAME}

# divide: 2033 balance by country (both sexes)
b33 = bf[bf.year == 2033].groupby("country")["balance"].sum() / M
divide = {"codes": list(b33.sort_values().index),
          "names": [NAME[c] for c in b33.sort_values().index],
          "val": [round(float(v)) for v in b33.sort_values().values]}

DATA = {"countries": NAME, "supply": supply, "demand": demand, "balance": balance, "divide": divide}

HTML = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Labour-Market Balance — a guided story</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<style>
:root{--bg:#FAFAF9;--card:#FFFFFF;--ink:#292524;--mut:#78716C;--line:#E7E5E4;--acc:#166534;
--slate:#475569;--mustard:#D97706;--sage:#4ADE80;--terra:#B91C1C;}
*{box-sizing:border-box}html,body{margin:0;height:100%}
body{background:var(--bg);color:var(--ink);font:16px/1.6 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
display:flex;flex-direction:column;min-height:100vh}
header{padding:18px 28px 8px;display:flex;align-items:center;gap:18px;flex-wrap:wrap}
header h1{font-size:19px;margin:0;font-weight:650}header .who{color:var(--mut);font-size:13px}
.spacer{flex:1}
select{background:var(--card);color:var(--ink);border:1px solid var(--line);border-radius:8px;padding:8px 10px;font-size:14px}
.track{display:flex;align-items:center;gap:0;padding:6px 28px 12px;flex-wrap:wrap}
.step{display:flex;align-items:center;gap:9px;cursor:pointer;color:var(--mut);font-size:13px;font-weight:600}
.step .dot{width:30px;height:30px;border-radius:50%;border:2px solid var(--line);background:var(--card);
display:flex;align-items:center;justify-content:center;font-size:13px;color:var(--mut);transition:.2s}
.step.active .dot,.step.done .dot{border-color:var(--acc);background:var(--acc);color:#fff}
.step.active{color:var(--ink)}
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
  <h1>Labour-Market Balance — a guided story</h1>
  <span class="who">8 European countries · to 2033</span><span class="spacer"></span>
  <label class="who" for="country">Country&nbsp;</label><select id="country"></select>
</header>
<nav class="track" id="track"></nav>
<main>
  <section class="slide" data-i="0">
    <div class="kick">Step 1 · Supply</div><h2>The healthy workforce</h2>
    <p class="lead">Potential <b>supply</b> = healthy working-age people × expected working life, in
    human-working-years. Near-flat to 2033 — the longevity dividend offsets shrinking populations.</p>
    <div class="panel"><div class="chwrap"><canvas id="supply"></canvas></div></div>
    <div class="kpis" id="supKpis"></div></section>
  <section class="slide" data-i="1">
    <div class="kick">Step 2 · Demand</div><h2>The career-years jobs require</h2>
    <p class="lead">Potential <b>demand</b> = (employed + vacancies) × required length of service. The stock
    of career-years the economy's jobs need to be staffed.</p>
    <div class="panel"><div class="chwrap"><canvas id="demand"></canvas></div></div>
    <div class="kpis" id="demKpis"></div></section>
  <section class="slide" data-i="2">
    <div class="kick">Step 3 · Balance</div><h2>Subtract them: surplus or shortage</h2>
    <p class="lead"><b>Balance = Supply − Demand.</b> Above zero is slack (more healthy workers than jobs
    require); below is a shortage. The band is wide — read direction, not a point.</p>
    <div class="panel"><div class="chwrap"><canvas id="balance"></canvas></div></div>
    <div class="kpis" id="balKpis"></div>
    <div class="note">The balance is a small difference of two ~4,300M stocks, so its band is wide —
    it is a structural signal, not a precise number.</div></section>
  <section class="slide" data-i="3">
    <div class="kick">Step 4 · The divide</div><h2>East surplus, West shortage</h2>
    <p class="lead">The 8-country total is roughly balanced, but it hides a sharp geographic split: the East
    holds a labour reserve while the West/EFTA runs a shortage — the demographic basis of West-bound migration.</p>
    <div class="panel"><div class="chwrap"><canvas id="divide"></canvas></div></div>
    <div class="kpis" id="divKpis"></div></section>
</main>
<footer>
  <button class="nav ghost" id="prev">‹ Back</button>
  <div style="display:flex;align-items:center;gap:14px"><button class="nav ghost" id="play">▶ Present</button>
  <span class="who" id="counter"></span></div>
  <button class="nav" id="next">Next ›</button>
</footer>
<script>const DATA = __DATA__;</script>
<script>
const STEPS=[["Supply","Healthy workforce"],["Demand","Jobs to staff"],["Balance","Surplus / shortage"],["The divide","By country, 2033"]];
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
function lineOF(id,d,unit,title,col){
  destroy(id);const labels=d.oy.concat(d.fy);
  const obs=d.ov.concat(Array(d.fy.length).fill(null));
  const fcast=Array(d.oy.length-1).fill(null).concat([d.ov[d.ov.length-1]]).concat(d.fm);
  const sets=[{label:'Observed',data:obs,borderColor:C.slate,backgroundColor:C.slate,tension:.25,pointRadius:0,borderWidth:2.5},
    {label:'Forecast',data:fcast,borderColor:col||C.acc,backgroundColor:col||C.acc,borderDash:[5,3],tension:.25,pointRadius:0,borderWidth:2.5}];
  if(d.lo){const pad=(a)=>Array(d.oy.length).fill(null).concat(a);
    sets.unshift({label:'_hi',data:pad(d.hi),borderColor:'transparent',backgroundColor:'rgba(22,101,52,.10)',pointRadius:0,fill:false});
    sets.unshift({label:'80% band',data:pad(d.lo),borderColor:'transparent',backgroundColor:'rgba(22,101,52,.10)',pointRadius:0,fill:'+1'});}
  charts[id]=new Chart(document.getElementById(id),{type:'line',data:{labels,datasets:sets},
    options:{responsive:true,maintainAspectRatio:false,interaction:{mode:'index',intersect:false},
      scales:{y:{...axis(unit)},x:axis()},
      plugins:{title:{display:true,text:title,color:C.ink,font:{size:15}},
        legend:{position:'bottom',labels:{filter:i=>!i.text.startsWith('_')}},
        tooltip:{filter:i=>!i.dataset.label.startsWith('_'),callbacks:{label:c=>`${c.dataset.label}: ${c.raw} M`}}}}});
}
function pct(d){return ((d.fm[d.fm.length-1]/d.ov[d.ov.length-1]-1)*100).toFixed(1);}
function drawSupply(){const d=DATA.supply[state.country];lineOF('supply',d,'supply (million human-working-years)',`Potential supply — ${DATA.countries[state.country]}`,C.acc);
  document.getElementById('supKpis').innerHTML=kpi(d.ov[d.ov.length-1]+'M','2024')+kpi(d.fm[d.fm.length-1]+'M','2033')+kpi((pct(d)>=0?'+':'')+pct(d)+'%','Change');}
function drawDemand(){const d=DATA.demand[state.country];lineOF('demand',d,'demand (million career person-years)',`Potential demand — ${DATA.countries[state.country]}`,C.mustard);
  document.getElementById('demKpis').innerHTML=kpi(d.ov[d.ov.length-1]+'M','2024')+kpi(d.fm[d.fm.length-1]+'M','2033')+kpi((pct(d)>=0?'+':'')+pct(d)+'%','Change');}
function drawBalance(){const d=DATA.balance[state.country];lineOF('balance',d,'balance (million human-working-years)',`Balance = supply − demand — ${DATA.countries[state.country]}`,C.acc);
  const b=d.fm[d.fm.length-1];document.getElementById('balKpis').innerHTML=
    kpi((d.ov[d.ov.length-1]>=0?'+':'')+d.ov[d.ov.length-1]+'M','Balance 2024')+
    kpi((b>=0?'+':'')+b+'M','Balance 2033')+kpi((b>=0?'Surplus':'Shortage'),'2033 status');}
function drawDivide(){destroy('divide');const dv=DATA.divide;
  charts.divide=new Chart(document.getElementById('divide'),{type:'bar',
    data:{labels:dv.names,datasets:[{label:'2033 balance (M)',data:dv.val,
      backgroundColor:dv.val.map(v=>v>=0?C.sage:C.terra),borderColor:dv.val.map(v=>v>=0?C.acc:C.terra),borderWidth:1.2,borderRadius:3}]},
    options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,
      scales:{x:{...axis('balance 2033 (million human-working-years)'),grid:{color:C.line}},y:{grid:{display:false}}},
      plugins:{title:{display:true,text:'2033 balance by country — surplus (green) vs shortage (red)',color:C.ink,font:{size:15}},legend:{display:false},
        tooltip:{callbacks:{label:c=>`${c.raw>=0?'+':''}${c.raw}M ${c.raw>=0?'surplus':'shortage'}`}}}}});
  const sur=dv.val.filter(v=>v>0).reduce((a,b)=>a+b,0),sh=dv.val.filter(v=>v<0).reduce((a,b)=>a+b,0);
  document.getElementById('divKpis').innerHTML=kpi('+'+Math.round(sur)+'M','East surplus')+kpi(Math.round(sh)+'M','West/EFTA shortage')+
    kpi((Math.round(sur+sh)>=0?'+':'')+Math.round(sur+sh)+'M','Net');}
function renderAll(){if(state.slide===0)drawSupply();else if(state.slide===1)drawDemand();else if(state.slide===2)drawBalance();else drawDivide();}
let timer=null;
function setPlay(on){const b=document.getElementById('play');
  if(on){b.textContent='⏸ Pause';b.classList.remove('ghost');timer=setInterval(()=>go(state.slide>=3?0:state.slide+1),7000);}
  else{b.textContent='▶ Present';b.classList.add('ghost');clearInterval(timer);timer=null;}}
document.getElementById('play').onclick=()=>setPlay(!timer);
go(0);
</script>
</body></html>"""

(OUT / "balance_story.html").write_text(HTML.replace("__DATA__", json.dumps(DATA)), encoding="utf-8")
print(f"wrote outputs/balance_story.html ({len(json.dumps(DATA))} bytes data)")
