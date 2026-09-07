# -*- coding: utf-8 -*-
"""
Build outputs/supply_story.html — a guided, slide-based narrative of the LABOUR
SUPPLY build-up, with interactive Chart.js charts and a methodology progress tracker.

Four slides follow the supply equation:
  1. Demographic baseline   — interactive population pyramid + ageing trend
  2. Participation (LFPR)    — men vs women labour-force participation over time
  3. Migration adjustments   — BSL / high / low migration working-age scenarios
  4. Final supply forecast   — synthesised supply (person-years) to 2033 with bands

Data (demo_pjangroup, supply_observed, proj_pop_wa, supply_forecast) is embedded
inline as JSON so the page is self-contained on GitHub Pages.
"""
from __future__ import annotations
import glob
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
NAME = {"ALL": "All 8 countries", "BG": "Bulgaria", "PL": "Poland", "CZ": "Czechia",
        "RO": "Romania", "DE": "Germany", "FR": "France", "NO": "Norway", "CH": "Switzerland"}
GEO = [c for c in NAME if c != "ALL"]
# pyramid bands, young→old. 5-year up to 70–74, then the 75+ tail split into
# 5-year cohorts (from single-year demo_pjan) up to a 100+ open bucket.
PYR_BANDS = [("15–19", 15, 19), ("20–24", 20, 24), ("25–29", 25, 29), ("30–34", 30, 34),
             ("35–39", 35, 39), ("40–44", 40, 44), ("45–49", 45, 49), ("50–54", 50, 54),
             ("55–59", 55, 59), ("60–64", 60, 64), ("65–69", 65, 69), ("70–74", 70, 74),
             ("75–79", 75, 79), ("80–84", 80, 84), ("85–89", 85, 89), ("90–94", 90, 94),
             ("95–99", 95, 99), ("100+", 100, 200)]
BANDS_LBL = [b[0] for b in PYR_BANDS]
OLD_BANDS = {"Y65-69", "Y70-74", "Y_GE75"}
PYR_YEARS = list(range(2016, 2025))     # single-year age data (demo_pjan) coverage
AGE_YEARS = list(range(2004, 2025))     # 5-year-band data (demo_pjangroup) for the ageing trend

# ---------------- load sources ----------------
pg = sorted(glob.glob(str(ROOT / "data/raw/demo_pjangroup__*.parquet")))[-1]
g = pd.read_parquet(pg)                                    # 5-year bands, 2004+ (ageing trend)
g = g[g.country.isin(GEO)]
# single year of age (demo_pjan) — lets us split the 75+ tail into 5-year cohorts
pjf = sorted(glob.glob(str(ROOT / "data/demo_pjan__custom_*.csv.gz")))[-1]
pj = pd.read_csv(pjf).rename(columns={"geo": "country", "TIME_PERIOD": "year", "OBS_VALUE": "value"})
pj = pj[pj.country.isin(GEO)]


def _agenum(a):
    if isinstance(a, str) and a.startswith("Y") and a[1:].isdigit():
        return int(a[1:])
    return {"Y_LT1": 0, "Y_OPEN": 100}.get(a)          # 100+ collapses onto the open bucket


pj["agenum"] = pj["age"].map(_agenum)
pj = pj.dropna(subset=["agenum"])
pj["agenum"] = pj["agenum"].astype(int)
so = pd.read_csv(OUT / "supply_observed.csv")
so["lfpr"] = (so.employed_ths * 1000 / (1 - so.unemp_rate / 100)) / so.pop_15_64 * 100
pw = pd.read_csv(ROOT / "data/processed/proj_pop_wa.csv")
sf = pd.read_csv(OUT / "supply_forecast.csv")


def _band_count(country, sex, year, lo, hi):
    cs = country if isinstance(country, list) else [country]
    q = pj[pj.country.isin(cs) & (pj.sex == sex) & (pj.year == year)
           & (pj.agenum >= lo) & (pj.agenum <= hi)]
    v = q["value"].sum()
    return round(float(v) / 1000, 1) if pd.notna(v) and v else None


def _geos(c):
    return GEO if c == "ALL" else [c]

# ---------------- pyramid + ageing ----------------
pyramid, ageing = {}, {}
for c in NAME:
    cs = _geos(c)
    d = {"M": {}, "F": {}}
    for s in ("M", "F"):
        for y in PYR_YEARS:
            d[s][str(y)] = [_band_count(cs, s, y, lo, hi) for (_, lo, hi) in PYR_BANDS]
    pyramid[c] = d
    share = []
    for y in AGE_YEARS:
        tot = g[g.country.isin(cs) & (g.year == y) & (g.indicator == "TOTAL")]["value"].sum()
        old = g[g.country.isin(cs) & (g.year == y) & (g.indicator.isin(OLD_BANDS))]["value"].sum()
        share.append(round(old / tot * 100, 1) if tot else None)
    ageing[c] = share

# ---------------- LFPR (participation) ----------------
lfpr = {}
for c in NAME:
    cs = _geos(c)
    sub = so[so.country.isin(cs)]
    yrs = sorted(sub.year.unique())
    out = {"years": [int(y) for y in yrs], "M": [], "F": []}
    for s in ("M", "F"):
        for y in yrs:
            r = sub[(sub.sex == s) & (sub.year == y)]
            # population-weighted participation across countries
            w = (r["lfpr"] * r["pop_15_64"]).sum() / r["pop_15_64"].sum() if len(r) else np.nan
            out[s].append(round(float(w), 1) if pd.notna(w) else None)
    lfpr[c] = out

# ---------------- migration scenarios (working-age pop, millions) ----------------
mig = {}
for c in NAME:
    cs = _geos(c)
    sub = pw[pw.country.isin(cs)]
    yrs = [y for y in sorted(sub.year.unique()) if y <= 2033]   # cap at the 2033 horizon
    out = {"years": [int(y) for y in yrs]}
    for sc in ("BSL", "HMIGR", "LMIGR"):
        out[sc] = [round(float(sub[(sub.year == y) & (sub.scenario == sc)]["pop_15_64_proj"].sum()) / 1e6, 2)
                   for y in yrs]
    mig[c] = out

# ---------------- final supply forecast (million person-years) ----------------
supply = {}
for c in NAME:
    cs = _geos(c)
    o = so[so.country.isin(cs) & (so.year <= 2024)].groupby("year")["supply_realized"].sum() / 1e6
    f = sf[sf.country.isin(cs)].groupby("year").agg(
        m=("supply_realized", "sum"), lo=("lo", "sum"), hi=("hi", "sum")) / 1e6
    supply[c] = {"oy": [int(y) for y in o.index], "ov": [round(v, 1) for v in o.values],
                 "fy": [int(y) for y in f.index], "fm": [round(v, 1) for v in f["m"].values],
                 "lo": [round(v, 1) for v in f["lo"].values], "hi": [round(v, 1) for v in f["hi"].values]}

DATA = {"countries": NAME, "bands": BANDS_LBL, "pyrYears": PYR_YEARS, "ageYears": AGE_YEARS,
        "pyramid": pyramid, "ageing": ageing, "lfpr": lfpr, "migration": mig, "supply": supply}

HTML = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Labour Supply — a guided story</title>
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
select{background:var(--card);color:var(--ink);border:1px solid var(--line);border-radius:8px;
padding:8px 10px;font-size:14px}
/* progress tracker */
.track{display:flex;align-items:center;gap:0;padding:6px 28px 12px;flex-wrap:wrap}
.step{display:flex;align-items:center;gap:9px;cursor:pointer;color:var(--mut);font-size:13px;font-weight:600}
.step .dot{width:30px;height:30px;border-radius:50%;border:2px solid var(--line);background:var(--card);
display:flex;align-items:center;justify-content:center;font-size:13px;color:var(--mut);transition:.2s}
.step.active .dot,.step.done .dot{border-color:var(--acc);background:var(--acc);color:#fff}
.step.active{color:var(--ink)}
.link{flex:0 0 46px;height:3px;background:var(--line);margin:0 6px;border-radius:2px}
.link.done{background:var(--acc)}
/* slides */
main{flex:1;padding:6px 28px 20px;max-width:1080px;margin:0 auto;width:100%}
.slide{display:none;animation:fade .35s ease}
.slide.active{display:block}
@keyframes fade{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
.kick{font-size:12px;letter-spacing:1px;text-transform:uppercase;color:var(--acc);font-weight:700}
.slide h2{font-size:24px;margin:4px 0 6px}
.slide p.lead{color:var(--mut);margin:0 0 14px;max-width:760px}
.panel{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:16px 18px;margin:12px 0}
.grid2{display:grid;grid-template-columns:1.4fr 1fr;gap:16px}
@media(max-width:820px){.grid2{grid-template-columns:1fr}}
.chwrap{position:relative;height:420px}
.chwrap.sm{height:300px}
.ctrls{display:flex;align-items:center;gap:12px;margin:4px 0 0;color:var(--mut);font-size:13px}
.ctrls input[type=range]{flex:1;accent-color:var(--acc)}
.kpis{display:flex;gap:14px;flex-wrap:wrap;margin-top:8px}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px 16px;min-width:150px}
.kpi .v{font-size:22px;font-weight:700}.kpi .l{color:var(--mut);font-size:12px;margin-top:2px}
.note{color:var(--mut);font-size:13px;background:var(--card);border:1px solid var(--line);
border-radius:10px;padding:12px 14px;margin-top:10px}
footer{display:flex;align-items:center;justify-content:space-between;padding:14px 28px 26px;max-width:1080px;
margin:0 auto;width:100%}
button.nav{background:var(--acc);color:#fff;border:none;border-radius:10px;padding:10px 20px;font-size:14px;
font-weight:600;cursor:pointer}
button.nav:disabled{background:var(--line);color:var(--mut);cursor:default}
button.ghost{background:var(--card);color:var(--ink);border:1px solid var(--line)}
a{color:var(--acc)}
</style></head><body>
<header>
  <h1>Labour Supply — a guided story</h1>
  <span class="who">8 European countries · to 2033</span>
  <span class="spacer"></span>
  <label class="who" for="country">Country&nbsp;</label>
  <select id="country"></select>
</header>
<nav class="track" id="track"></nav>
<main>
  <!-- Slide 1 -->
  <section class="slide" data-i="0">
    <div class="kick">Step 1 · Demographics</div>
    <h2>The demographic baseline</h2>
    <p class="lead">Every projection starts from who is alive today. The pyramid shows the working-age and
    older cohorts by sex — with the 75+ tail broken into 5-year cohorts up to 100+ (single-year ages,
    available 2016–2024). Drag the year to watch the bulge move up as Europe ages.</p>
    <div class="grid2">
      <div class="panel"><div class="chwrap"><canvas id="pyramid"></canvas></div>
        <div class="ctrls"><span>Year <b id="pyrYearLbl"></b></span>
          <input type="range" id="pyrYear" min="2016" max="2024" step="1" value="2024"></div></div>
      <div>
        <div class="panel"><div class="chwrap sm"><canvas id="ageing"></canvas></div></div>
        <div class="kpis" id="demoKpis"></div>
      </div>
    </div>
    <div class="note">Population aged 15+ by 5-year band (Eurostat <code>demo_pjangroup</code>). The share aged
    65+ is the ageing signal that erodes the working-age base over time.</div>
  </section>
  <!-- Slide 2 -->
  <section class="slide" data-i="1">
    <div class="kick">Step 2 · Participation</div>
    <h2>Labour-force participation: the closing gap</h2>
    <p class="lead">A shrinking population can still supply more labour if a larger share participates. The
    male–female participation gap has narrowed steadily — the lever the West uses to offset demographics.</p>
    <div class="panel"><div class="chwrap"><canvas id="lfpr"></canvas></div></div>
    <div class="kpis" id="lfprKpis"></div>
    <div class="note">Participation = active (employed + unemployed) ÷ working-age population, by sex
    (Eurostat <code>lfsa_egan</code>, <code>une_rt_a</code>).</div>
  </section>
  <!-- Slide 3 -->
  <section class="slide" data-i="2">
    <div class="kick">Step 3 · Migration</div>
    <h2>Migration adjusts the baseline</h2>
    <p class="lead">Net migration is the biggest swing factor on the working-age population. We carry
    Eurostat's three official variants and forecast within that envelope.</p>
    <div class="panel"><div class="chwrap"><canvas id="mig"></canvas></div></div>
    <div class="kpis" id="migKpis"></div>
    <div class="note">Working-age (15–64) population under baseline, high- and low-migration variants
    (Eurostat projection <code>proj_23np</code>), calibrated to observed 2024.</div>
  </section>
  <!-- Slide 4 -->
  <section class="slide" data-i="3">
    <div class="kick">Step 4 · Total supply</div>
    <h2>The synthesised supply forecast</h2>
    <p class="lead">Demographics × participation × healthy working life, combined into potential labour
    supply in <b>human-working-years</b>, observed then forecast to 2033 with an 80% uncertainty band.</p>
    <div class="panel"><div class="chwrap"><canvas id="supply"></canvas></div></div>
    <div class="kpis" id="supKpis"></div>
    <div class="note">Supply = healthy working-age people × expected working life. The longevity dividend
    (rising healthy-life share + longer careers) offsets the shrinking base.</div>
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
const STEPS=[["Demographics","Pop. & ageing"],["Participation","LFPR by sex"],
  ["Migration","Scenarios"],["Total supply","Forecast 2033"]];
const C={slate:'#475569',mustard:'#D97706',sage:'#4ADE80',terra:'#B91C1C',acc:'#166534',
  ink:'#292524',mut:'#78716C',line:'#E7E5E4'};
Chart.defaults.color=C.mut; Chart.defaults.font.family="-apple-system,Segoe UI,Roboto,Arial,sans-serif";
Chart.defaults.borderColor=C.line;
let state={country:'ALL', slide:0, year:2024}, charts={};

// ---- country selector ----
const sel=document.getElementById('country');
Object.entries(DATA.countries).forEach(([k,v])=>{const o=document.createElement('option');o.value=k;o.textContent=v;sel.appendChild(o);});
sel.value=state.country;
sel.onchange=()=>{state.country=sel.value;renderAll();};

// ---- progress tracker ----
const track=document.getElementById('track');
STEPS.forEach((s,i)=>{
  if(i>0){const l=document.createElement('span');l.className='link';l.dataset.link=i;track.appendChild(l);}
  const el=document.createElement('div');el.className='step';el.dataset.step=i;
  el.innerHTML=`<span class="dot">${i+1}</span><span>${s[0]}</span>`;
  el.onclick=()=>go(i); track.appendChild(el);
});

function go(i){state.slide=Math.max(0,Math.min(3,i));
  document.querySelectorAll('.slide').forEach(s=>s.classList.toggle('active',+s.dataset.i===state.slide));
  document.querySelectorAll('.step').forEach((s,idx)=>{s.classList.toggle('active',idx===state.slide);s.classList.toggle('done',idx<state.slide);});
  document.querySelectorAll('.link').forEach(l=>l.classList.toggle('done',+l.dataset.link<=state.slide));
  document.getElementById('prev').disabled=state.slide===0;
  document.getElementById('next').textContent=state.slide===3?'Finish':'Next ›';
  document.getElementById('counter').textContent=`Step ${state.slide+1} of 4 — ${STEPS[state.slide][1]}`;
  renderAll();
}
document.getElementById('prev').onclick=()=>go(state.slide-1);
document.getElementById('next').onclick=()=>go(state.slide+1);
document.addEventListener('keydown',e=>{if(e.key==='ArrowRight')go(state.slide+1);if(e.key==='ArrowLeft')go(state.slide-1);});

// ---- year slider ----
const yr=document.getElementById('pyrYear');
yr.oninput=()=>{state.year=+yr.value;document.getElementById('pyrYearLbl').textContent=state.year;drawPyramid();};

function destroy(id){if(charts[id]){charts[id].destroy();delete charts[id];}}
const axis=(t)=>({title:{display:!!t,text:t,color:C.mut},grid:{color:C.line}});

function drawPyramid(){
  destroy('pyramid');
  const p=DATA.pyramid[state.country], y=String(state.year);
  const men=(p.M[y]||[]).map(v=>v==null?null:-v), women=p.F[y]||[];
  charts.pyramid=new Chart(document.getElementById('pyramid'),{type:'bar',data:{labels:DATA.bands,
    datasets:[{label:'Men',data:men,backgroundColor:C.slate,borderRadius:2},
              {label:'Women',data:women,backgroundColor:C.mustard,borderRadius:2}]},
    options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,
      scales:{x:{stacked:true,...axis('thousand people'),ticks:{callback:v=>Math.abs(v)}},
              y:{stacked:true,reverse:true,grid:{display:false}}},  // youngest at bottom, oldest at top (standard pyramid)
      plugins:{title:{display:true,text:`Population pyramid — ${DATA.countries[state.country]}, ${state.year}`,color:C.ink,font:{size:15}},
        tooltip:{callbacks:{label:c=>`${c.dataset.label}: ${Math.abs(c.raw).toLocaleString()}k (age ${c.label})`}},
        legend:{position:'bottom'}}}});
}
function drawAgeing(){
  destroy('ageing');
  charts.ageing=new Chart(document.getElementById('ageing'),{type:'line',
    data:{labels:DATA.ageYears,datasets:[{label:'Share aged 65+',data:DATA.ageing[state.country],
      borderColor:C.terra,backgroundColor:'rgba(185,28,28,.12)',fill:true,tension:.3,pointRadius:0}]},
    options:{responsive:true,maintainAspectRatio:false,
      scales:{y:{...axis('% of population'),ticks:{callback:v=>v+'%'}},x:axis()},
      plugins:{title:{display:true,text:'Ageing — share aged 65+',color:C.ink,font:{size:14}},legend:{display:false},
        tooltip:{callbacks:{label:c=>`${c.raw}% aged 65+ in ${c.label}`}}}}});
  const a=DATA.ageing[state.country];
  document.getElementById('demoKpis').innerHTML=
    kpi(a[a.length-1]+'%','Share aged 65+ today')+kpi('+'+(a[a.length-1]-a[0]).toFixed(1)+' pp','Rise since 2004');
}
function drawLFPR(){
  destroy('lfpr');const d=DATA.lfpr[state.country];
  charts.lfpr=new Chart(document.getElementById('lfpr'),{type:'line',data:{labels:d.years,
    datasets:[{label:'Men',data:d.M,borderColor:C.slate,backgroundColor:C.slate,tension:.3,pointRadius:2},
              {label:'Women',data:d.F,borderColor:C.mustard,backgroundColor:C.mustard,tension:.3,pointRadius:2}]},
    options:{responsive:true,maintainAspectRatio:false,interaction:{mode:'index',intersect:false},
      scales:{y:{...axis('participation %'),ticks:{callback:v=>v+'%'}},x:axis()},
      plugins:{title:{display:true,text:`Participation by sex — ${DATA.countries[state.country]}`,color:C.ink,font:{size:15}},
        legend:{position:'bottom'},tooltip:{callbacks:{label:c=>`${c.dataset.label}: ${c.raw}%`}}}}});
  const m=d.M.filter(x=>x!=null),f=d.F.filter(x=>x!=null);
  const gap0=(m[0]-f[0]),gap1=(m[m.length-1]-f[f.length-1]);
  document.getElementById('lfprKpis').innerHTML=
    kpi(f[f.length-1].toFixed(0)+'%','Women participation now')+
    kpi(m[m.length-1].toFixed(0)+'%','Men participation now')+
    kpi(gap1.toFixed(1)+' pp','Gender gap now (was '+gap0.toFixed(0)+')');
}
function drawMig(){
  destroy('mig');const d=DATA.migration[state.country];
  const ds=(k,col,dash)=>({label:k==='BSL'?'Baseline':k==='HMIGR'?'High migration':'Low migration',
    data:d[k],borderColor:col,backgroundColor:col,borderDash:dash||[],tension:.25,pointRadius:0,borderWidth:k==='BSL'?3:2});
  charts.mig=new Chart(document.getElementById('mig'),{type:'line',data:{labels:d.years,
    datasets:[ds('HMIGR',C.sage,[6,4]),ds('BSL',C.acc),ds('LMIGR',C.terra,[6,4])]},
    options:{responsive:true,maintainAspectRatio:false,interaction:{mode:'index',intersect:false},
      scales:{y:{...axis('working-age population (millions)')},x:axis()},
      plugins:{title:{display:true,text:`Working-age population scenarios — ${DATA.countries[state.country]}`,color:C.ink,font:{size:15}},
        legend:{position:'bottom'},tooltip:{callbacks:{label:c=>`${c.dataset.label}: ${c.raw}M`}}}}});
  const last=d.years.length-1, spread=(d.HMIGR[last]-d.LMIGR[last]).toFixed(2);
  document.getElementById('migKpis').innerHTML=
    kpi(d.BSL[last]+'M','Baseline working-age, 2033')+kpi('±'+spread+'M','High–low migration spread by 2033');
}
function drawSupply(){
  destroy('supply');const d=DATA.supply[state.country];
  const labels=d.oy.concat(d.fy);
  const pad=(arr,lead)=>Array(lead).fill(null).concat(arr);
  const obs=d.ov.concat(Array(d.fy.length).fill(null));
  const join=Array(d.oy.length-1).fill(null).concat([d.ov[d.ov.length-1]]).concat(d.fm);
  charts.supply=new Chart(document.getElementById('supply'),{type:'line',data:{labels,
    datasets:[
      {label:'80% band',data:pad(d.lo,d.oy.length),borderColor:'transparent',backgroundColor:'rgba(22,101,52,.10)',pointRadius:0,fill:'+1'},
      {label:'_hi',data:pad(d.hi,d.oy.length),borderColor:'transparent',backgroundColor:'rgba(22,101,52,.10)',pointRadius:0,fill:false},
      {label:'Observed',data:obs,borderColor:C.slate,backgroundColor:C.slate,tension:.25,pointRadius:0,borderWidth:2.5},
      {label:'Forecast',data:join,borderColor:C.acc,backgroundColor:C.acc,borderDash:[5,3],tension:.25,pointRadius:0,borderWidth:2.5}]},
    options:{responsive:true,maintainAspectRatio:false,interaction:{mode:'index',intersect:false},
      scales:{y:{...axis('supply (million person-years)')},x:axis()},
      plugins:{title:{display:true,text:`Potential labour supply — ${DATA.countries[state.country]}`,color:C.ink,font:{size:15}},
        legend:{position:'bottom',labels:{filter:i=>!i.text.startsWith('_')}},
        tooltip:{filter:i=>!i.dataset.label.startsWith('_'),callbacks:{label:c=>`${c.dataset.label}: ${c.raw} M PY`}}}}});
  const chg=((d.fm[d.fm.length-1]/d.ov[d.ov.length-1]-1)*100).toFixed(1);
  document.getElementById('supKpis').innerHTML=
    kpi(d.ov[d.ov.length-1]+'M','Supply 2024 (M PY)')+kpi(d.fm[d.fm.length-1]+'M','Supply 2033 (M PY)')+
    kpi((chg>=0?'+':'')+chg+'%','Change to 2033');
}
function kpi(v,l){return `<div class="kpi"><div class="v">${v}</div><div class="l">${l}</div></div>`;}

function renderAll(){
  document.getElementById('pyrYearLbl').textContent=state.year;
  if(state.slide===0){drawPyramid();drawAgeing();}
  else if(state.slide===1)drawLFPR();
  else if(state.slide===2)drawMig();
  else if(state.slide===3)drawSupply();
}
// ---- present / autoplay mode (loops every 7s) ----
let timer=null;
function setPlay(on){const b=document.getElementById('play');
  if(on){b.textContent='⏸ Pause';b.classList.remove('ghost');
    timer=setInterval(()=>go(state.slide>=3?0:state.slide+1),7000);}
  else{b.textContent='▶ Present';b.classList.add('ghost');clearInterval(timer);timer=null;}}
document.getElementById('play').onclick=()=>setPlay(!timer);
go(0);
</script>
</body></html>"""

html = HTML.replace("__DATA__", json.dumps(DATA))
(OUT / "supply_story.html").write_text(html, encoding="utf-8")
print(f"wrote outputs/supply_story.html ({len(html):,} bytes)")
