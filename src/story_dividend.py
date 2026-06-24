# -*- coding: utf-8 -*-
"""
Build outputs/dividend_story.html — a guided, slide-based narrative of LEVEL 5
(healthy retirement dividend), with interactive Chart.js + tracker + present mode.

Four slides:
  1. Is retirement healthy?  — healthy years after retirement (HLY − retire age), by country
  2. The dividend            — Pop × max(0, HLY − retire), person-years, to 2033
  3. Does it fund leisure?   — cross-country: dividend vs leisure/education consumption
  4. The honest answer       — within-country year-on-year: no link (tracks income)
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


obs = pd.read_csv(OUT / "dividend_observed.csv")
fc = pd.read_csv(OUT / "dividend_forecast.csv")
rel = json.loads((OUT / "dividend_relationship.json").read_text(encoding="utf-8"))
panel = pd.read_parquet(ROOT / "data" / "processed" / "panel.parquet")

# healthy-retirement years per person (2024, pop-weighted), all 8 (fixed cross-country bar)
o24 = obs[obs.year == 2024]
pp = {}
for c in GEO:
    r = o24[o24.country == c]
    pp[c] = round(float((r["hdiv_pp"] * r["pop_total"]).sum() / r["pop_total"].sum()), 1)
order = sorted(GEO, key=lambda c: pp[c])
hrbar = {"names": [NAME[c] for c in order], "val": [pp[c] for c in order]}

# dividend person-years (M), observed + forecast
dividend = {}
for c in NAME:
    cs = _geos(c)
    o = obs[obs.country.isin(cs) & (obs.year <= 2024)].groupby("year")["hdiv_py"].sum() / M
    f = fc[fc.country.isin(cs)].groupby("year").agg(
        m=("dividend_py", "sum"), lo=("dividend_lo", "sum"), hi=("dividend_hi", "sum")) / M
    dividend[c] = {"oy": [int(y) for y in o.index], "ov": [round(v, 1) for v in o.values],
                   "fy": [int(y) for y in f.index], "fm": [round(v, 1) for v in f["m"].values],
                   "lo": [round(v, 1) for v in f["lo"].values], "hi": [round(v, 1) for v in f["hi"].values]}

# cross-country scatter: each country at its latest year with a positive dividend AND
# leisure/education/culture (COICOP CP09+10+11) observed — dividend PY vs spending (€bn)
panel = panel.copy()
panel["leisure"] = panel[["coicop_recreation", "coicop_education", "coicop_hotels_rest"]].sum(axis=1, min_count=1)
lz = panel.dropna(subset=["leisure"]).groupby(["country", "year"])["leisure"].first().reset_index()
divc = (obs.groupby(["country", "year"])["hdiv_py"].sum() / M).reset_index()
mrg = divc.merge(lz, on=["country", "year"])
mrg = mrg[mrg["hdiv_py"] > 0]
scatter = []
for c in GEO:
    g = mrg[mrg.country == c]
    if len(g):
        r = g.loc[g["year"].idxmax()]
        scatter.append({"c": c, "name": NAME[c], "year": int(r["year"]),
                        "div": round(float(r["hdiv_py"]), 1), "leis": round(float(r["leisure"]) / 1000, 1)})

# within-country differenced cloud
rp = pd.read_csv(ROOT / "data" / "retirement_params.csv")
ret = {(r.country, r.sex): r.statutory_retirement_age for r in rp.itertuples()}
panel["retage"] = panel.apply(lambda r: ret.get((r.country, r.sex), np.nan), axis=1)
panel["hdiv_py"] = panel["pop_total"] * (panel["hly_birth"] - panel["retage"]).clip(lower=0)
agg = panel.groupby(["country", "year"]).agg(d=("hdiv_py", "sum"), l=("leisure", "first")).reset_index().dropna()
agg = agg[(agg["d"] > 0) & (agg["l"] > 0)]
diff = []
for c, g in agg.groupby("country"):
    g = g.sort_values("year")
    dl = np.diff(np.log(g["d"].to_numpy(float))) * 100
    dy = np.diff(np.log(g["l"].to_numpy(float))) * 100
    for a, b in zip(dl, dy):
        diff.append({"x": round(float(a), 2), "y": round(float(b), 2)})

DATA = {"countries": NAME, "hrbar": hrbar, "dividend": dividend, "scatter": scatter, "diff": diff, "rel": rel}

HTML = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Healthy Retirement Dividend — a guided story</title>
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
  <h1>Healthy Retirement Dividend — a guided story</h1>
  <span class="who">8 European countries · to 2033</span><span class="spacer"></span>
  <label class="who" for="country">Country&nbsp;</label><select id="country"></select>
</header>
<nav class="track" id="track"></nav>
<main>
  <section class="slide" data-i="0">
    <div class="kick">Step 1 · After retirement</div><h2>Is retirement actually healthy?</h2>
    <p class="lead"><b>Healthy years after retirement = HLY − statutory retirement age.</b> Green = healthy years
    to enjoy; red = self-reported health declines <i>before</i> the retirement age is even reached.</p>
    <div class="panel"><div class="chwrap"><canvas id="hrbar"></canvas></div></div>
    <div class="kpis" id="hrKpis"></div>
    <div class="note">HLY is self-perceived (Eurostat GALI) — Switzerland's −6.6y reflects low self-reported health, not short lives.</div></section>
  <section class="slide" data-i="1">
    <div class="kick">Step 2 · The dividend</div><h2>The healthy-retirement dividend</h2>
    <p class="lead"><b>Dividend = Population × the positive healthy years after retirement.</b> It grows as
    healthy-life years rise and push more of the population across the retirement threshold.</p>
    <div class="panel"><div class="chwrap"><canvas id="dividend"></canvas></div></div>
    <div class="kpis" id="dKpis"></div></section>
  <section class="slide" data-i="2">
    <div class="kick">Step 3 · Consumption?</div><h2>Does it fund leisure, education &amp; culture?</h2>
    <p class="lead">Across countries, the dividend and <b>COICOP CP09/10/11</b> spending co-move — but that's
    largely <b>country size</b>. Each point is a country.</p>
    <div class="panel"><div class="chwrap"><canvas id="scatter"></canvas></div></div>
    <div class="kpis" id="sKpis"></div></section>
  <section class="slide" data-i="3">
    <div class="kick">Step 4 · Honest answer</div><h2>Within a country, no link</h2>
    <p class="lead">Year-on-year, changes in the dividend explain none of the change in leisure/education
    consumption — it tracks household income, not the demographic dividend.</p>
    <div class="panel"><div class="chwrap"><canvas id="diff"></canvas></div></div>
    <div class="kpis" id="aKpis"></div>
    <div class="note">Descriptive, no causal claim. The dividend is a meaningful demographic quantity but not a usable predictor of consumption.</div></section>
</main>
<footer>
  <button class="nav ghost" id="prev">‹ Back</button>
  <div style="display:flex;align-items:center;gap:14px"><button class="nav ghost" id="play">▶ Present</button>
  <span class="who" id="counter"></span></div>
  <button class="nav" id="next">Next ›</button>
</footer>
<script>const DATA = __DATA__;</script>
<script>
const STEPS=[["After retirement","Healthy years"],["The dividend","Person-years"],["Consumption?","Cross-country"],["Honest answer","Within-country"]];
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
const axis=(t)=>({title:{display:!!t,text:t,color:C.mut},grid:{color:C.line}});
function kpi(v,l){return `<div class="kpi"><div class="v">${v}</div><div class="l">${l}</div></div>`;}
function drawHR(){destroy('hrbar');const h=DATA.hrbar;
  charts.hrbar=new Chart(document.getElementById('hrbar'),{type:'bar',data:{labels:h.names,
    datasets:[{label:'Healthy years after retirement',data:h.val,
      backgroundColor:h.val.map(v=>v>=0?C.sage:C.terra),borderColor:h.val.map(v=>v>=0?C.acc:C.terra),borderWidth:1.2,borderRadius:3}]},
    options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,
      scales:{x:{...axis('healthy years after retirement (HLY − retire age)')},y:{grid:{display:false}}},
      plugins:{title:{display:true,text:'Healthy years after retirement, by country (2024)',color:C.ink,font:{size:15}},legend:{display:false},
        tooltip:{callbacks:{label:c=>`${c.raw>=0?'+':''}${c.raw} yrs ${c.raw>=0?'healthy retirement':'(health declines first)'}`}}}}});
  document.getElementById('hrKpis').innerHTML=kpi('+'+h.val[h.val.length-1]+'y',h.names[h.names.length-1]+' (healthiest)')+kpi(h.val[0]+'y',h.names[0]+' (declines first)');}
function drawDividend(){destroy('dividend');const d=DATA.dividend[state.country];const labels=d.oy.concat(d.fy);
  const obs=d.ov.concat(Array(d.fy.length).fill(null));
  const fcast=Array(d.oy.length-1).fill(null).concat([d.ov[d.ov.length-1]]).concat(d.fm);
  const pad=a=>Array(d.oy.length).fill(null).concat(a);
  charts.dividend=new Chart(document.getElementById('dividend'),{type:'line',data:{labels,datasets:[
    {label:'80% band',data:pad(d.lo),borderColor:'transparent',backgroundColor:'rgba(22,101,52,.10)',pointRadius:0,fill:'+1'},
    {label:'_hi',data:pad(d.hi),borderColor:'transparent',backgroundColor:'rgba(22,101,52,.10)',pointRadius:0,fill:false},
    {label:'Observed',data:obs,borderColor:C.slate,backgroundColor:C.slate,tension:.25,pointRadius:0,borderWidth:2.5},
    {label:'Forecast',data:fcast,borderColor:C.acc,backgroundColor:C.acc,borderDash:[5,3],tension:.25,pointRadius:0,borderWidth:2.5}]},
    options:{responsive:true,maintainAspectRatio:false,interaction:{mode:'index',intersect:false},
      scales:{y:{...axis('dividend (million person-years)')},x:axis()},
      plugins:{title:{display:true,text:`Healthy-retirement dividend — ${DATA.countries[state.country]}`,color:C.ink,font:{size:15}},
        legend:{position:'bottom',labels:{filter:i=>!i.text.startsWith('_')}},
        tooltip:{filter:i=>!i.dataset.label.startsWith('_'),callbacks:{label:c=>`${c.dataset.label}: ${c.raw} M PY`}}}}});
  const chg=d.ov[d.ov.length-1]>0?((d.fm[d.fm.length-1]/d.ov[d.ov.length-1]-1)*100).toFixed(0)+'%':'—';
  document.getElementById('dKpis').innerHTML=kpi(d.ov[d.ov.length-1]+'M','Dividend 2024')+kpi(d.fm[d.fm.length-1]+'M','Dividend 2033')+kpi(chg,'Change');}
function drawScatter(){destroy('scatter');const s=DATA.scatter;
  charts.scatter=new Chart(document.getElementById('scatter'),{type:'scatter',
    data:{datasets:[{label:'Country',data:s.map(p=>({x:p.div,y:p.leis,name:p.name,year:p.year})),backgroundColor:C.mustard,borderColor:C.acc,pointRadius:7,pointHoverRadius:9}]},
    options:{responsive:true,maintainAspectRatio:false,
      scales:{x:{...axis('healthy-retirement dividend (million person-years)'),type:'logarithmic'},y:{...axis('leisure/education/culture (€bn)'),type:'logarithmic'}},
      plugins:{title:{display:true,text:'Cross-country: dividend vs leisure/education consumption (latest positive-dividend year)',color:C.ink,font:{size:14}},legend:{display:false},
        tooltip:{callbacks:{label:c=>`${c.raw.name} (${c.raw.year}): ${c.raw.x}M PY · €${c.raw.y}bn`}}}}});
  document.getElementById('sKpis').innerHTML=kpi(DATA.rel.elasticity_levels_fe,'Cross-country elasticity (FE)')+kpi('R² '+DATA.rel.r2_levels_fe,'…but mostly country size');}
function drawDiff(){destroy('diff');
  charts.diff=new Chart(document.getElementById('diff'),{type:'scatter',
    data:{datasets:[{label:'Year-on-year',data:DATA.diff,backgroundColor:'rgba(71,85,105,.55)',borderColor:C.slate,pointRadius:4}]},
    options:{responsive:true,maintainAspectRatio:false,
      scales:{x:{...axis('Δ dividend (% / yr)')},y:{...axis('Δ leisure/education consumption (% / yr)')}},
      plugins:{title:{display:true,text:'Within-country, year-on-year — no relationship',color:C.ink,font:{size:15}},legend:{display:false},
        tooltip:{callbacks:{label:c=>`Δdividend ${c.raw.x}% · Δleisure ${c.raw.y}%`}}}}});
  document.getElementById('aKpis').innerHTML=kpi(DATA.rel.elasticity_within_diff,'Within elasticity (≈ 0)')+kpi('R² '+DATA.rel.r2_within_diff,'no explanatory power')+kpi(DATA.rel.leisure_real_growth_pct+'%/yr','Consumption grows with income');}
function renderAll(){if(state.slide===0)drawHR();else if(state.slide===1)drawDividend();else if(state.slide===2)drawScatter();else drawDiff();}
let timer=null;
function setPlay(on){const b=document.getElementById('play');
  if(on){b.textContent='⏸ Pause';b.classList.remove('ghost');timer=setInterval(()=>go(state.slide>=3?0:state.slide+1),7000);}
  else{b.textContent='▶ Present';b.classList.add('ghost');clearInterval(timer);timer=null;}}
document.getElementById('play').onclick=()=>setPlay(!timer);
go(0);
</script>
</body></html>"""

(OUT / "dividend_story.html").write_text(HTML.replace("__DATA__", json.dumps(DATA)), encoding="utf-8")
print(f"wrote outputs/dividend_story.html ({len(json.dumps(DATA))} bytes data)")
