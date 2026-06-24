# -*- coding: utf-8 -*-
"""
Build outputs/whatif.html — an interactive "what-if" scenario explorer.

One question, three dials:  do they live longer in good health (ΔHLY), do they
retire later (ΔRet), do more of them work (ΔParticipation)?  — and four answers,
recomputed live in the browser from the 2033 base via the Level 1/4/5 identities:

  WORK    who keeps working      = Σ_sex supply × (healthy share · working life · participation)   [L1]
  RETIRE  who retires            = Σ_sex pop × max(0, LE − retirement age)
  CARE    who needs healthcare   = Σ_sex pop × max(0, LE − HLY)                                     [L4]
  CULTURE concert halls/courses  = Σ_sex pop × max(0, HLY − retirement age)                          [L5]

Central-path scenario (each driver at its central forecast). Self-contained, earthy.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
BASE = json.loads((OUT / "whatif_base.json").read_text(encoding="utf-8"))

HTML = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>What-if — longer, healthier lives & the economy</title>
<style>
:root{--bg:#FAFAF9;--card:#FFFFFF;--ink:#292524;--mut:#78716C;--line:#E7E5E4;--acc:#166534;
--up:#15803D;--down:#B91C1C;--slate:#475569;--mustard:#D97706;--sage:#4ADE80;--terra:#B91C1C;}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font:15px/1.55 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;padding:30px 22px}
.wrap{max-width:1060px;margin:0 auto}
h1{font-size:25px;margin:0 0 4px}
.lead{color:var(--mut);margin:0 0 6px;max-width:820px}
.ask{font-style:italic;color:var(--acc);margin:6px 0 18px;max-width:820px}
.home{color:var(--mut);text-decoration:none;font-size:13px}.home:hover{color:var(--acc)}
.panel{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px 20px;margin:14px 0}
.row{display:flex;gap:18px;flex-wrap:wrap;align-items:flex-end}
.fctl label{display:block;font-size:12px;color:var(--mut);margin-bottom:5px;font-weight:600}
select{background:var(--bg);color:var(--ink);border:1px solid var(--line);border-radius:9px;padding:8px 11px;font-size:14px}
.sliders{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin-top:6px}
.sl h4{margin:0 0 2px;font-size:14px}.sl .d{color:var(--mut);font-size:12px;margin-bottom:8px;min-height:30px}
.sl .val{font-weight:700;color:var(--acc);font-size:15px}
input[type=range]{width:100%;accent-color:var(--acc);margin:6px 0 2px}
.scale{display:flex;justify-content:space-between;color:var(--mut);font-size:11px}
.presets{display:flex;gap:8px;flex-wrap:wrap;margin-top:14px}
.preset{border:1px solid var(--line);background:var(--bg);border-radius:20px;padding:7px 14px;font-size:13px;
font-weight:600;cursor:pointer;color:var(--ink)}.preset:hover{border-color:var(--acc)}
.preset.reset{margin-left:auto}
.story{background:#F0FDF4;border:1px solid #166534;border-left:5px solid #166534;border-radius:12px;
padding:14px 18px;margin:16px 0;font-size:15.5px;line-height:1.5}
.story b{color:#166534}.story .dn{color:var(--down)}
.cards{display:grid;grid-template-columns:repeat(2,1fr);gap:16px}
.oc{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px 18px;border-top:4px solid var(--c)}
.oc .ic{font-size:22px}.oc h3{margin:6px 0 2px;font-size:15px}.oc .q{color:var(--mut);font-size:12.5px;margin:0 0 10px}
.oc .v{font-size:28px;font-weight:750;line-height:1}.oc .u{color:var(--mut);font-size:12px;margin-top:3px}
.oc .chg{font-size:14px;font-weight:700;margin-top:8px}
.bar{height:12px;background:var(--bg);border:1px solid var(--line);border-radius:7px;overflow:hidden;margin-top:12px;display:flex}
.bar .seg{height:100%}
.note{color:var(--mut);font-size:13px;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px;margin-top:16px}
.note b{color:var(--ink)}code{background:#F5F5F4;border:1px solid #E7E5E4;border-radius:5px;padding:1px 5px;color:#475569;font-size:12.5px}
.legend{display:flex;gap:16px;color:var(--mut);font-size:12px;margin:4px 2px 0;flex-wrap:wrap}
.sw{display:inline-block;width:11px;height:11px;border-radius:2px;margin-right:5px;vertical-align:-1px}
@media(max-width:720px){.sliders{grid-template-columns:1fr}.cards{grid-template-columns:1fr}}
</style></head><body><div class="wrap">
<a class="home" href="../index.html">← Overview</a>
<h1>What-if — do longer, healthier lives reshape the economy?</h1>
<p class="lead">Three dials, four answers. Everything recomputes live from the 2033 base using the
same identities as Levels 1, 4 and 5 — a transparent, central-path scenario sandbox.</p>
<p class="ask">“Do they live longer in good health? And what does that mean for our economy — who keeps working,
who retires, who needs healthcare, and who fills the concert halls and the adult-education courses?”</p>

<div class="panel">
  <div class="row">
    <div class="fctl"><label for="country">Country</label>
      <select id="country"></select></div>
    <div style="flex:1"></div>
  </div>
  <div class="sliders">
    <div class="sl"><h4>🫀 Healthy life years</h4>
      <div class="d">Do they live longer <i>in good health</i>? Shift healthy-life expectancy (HLY).</div>
      <div class="val"><span id="vH">+0.0</span> years HLY</div>
      <input type="range" id="sH" min="-3" max="6" step="0.5" value="0">
      <div class="scale"><span>−3</span><span>base</span><span>+6</span></div></div>
    <div class="sl"><h4>🧓 Retirement age</h4>
      <div class="d">Do they retire later? Shift the statutory retirement age.</div>
      <div class="val"><span id="vR">+0.0</span> years</div>
      <input type="range" id="sR" min="-2" max="6" step="0.5" value="0">
      <div class="scale"><span>−2</span><span>base</span><span>+6</span></div></div>
    <div class="sl"><h4>💪 Participation</h4>
      <div class="d">Do more of them work? Shift the employment rate of healthy working-age people.</div>
      <div class="val"><span id="vP">+0</span> pp</div>
      <input type="range" id="sP" min="-5" max="12" step="1" value="0">
      <div class="scale"><span>−5</span><span>base</span><span>+12</span></div></div>
  </div>
  <div class="presets">
    <button class="preset" data-h="3" data-r="0" data-p="0">Healthy ageing (+3 HLY)</button>
    <button class="preset" data-h="0" data-r="3" data-p="5">Work longer (+3 ret, +5pp)</button>
    <button class="preset" data-h="3" data-r="2" data-p="5">Both at once</button>
    <button class="preset reset" data-h="0" data-r="0" data-p="0">Reset</button>
  </div>
</div>

<div class="story" id="story"></div>

<div class="cards">
  <div class="oc" style="--c:var(--slate)"><div class="ic">👷</div>
    <h3>Who keeps working</h3><p class="q">Labour supply — human-working-years</p>
    <div class="v" id="wWork">—</div><div class="u">million human-working-years</div>
    <div class="chg" id="cWork"></div></div>
  <div class="oc" style="--c:var(--mustard)"><div class="ic">🏖️</div>
    <h3>Who retires</h3><p class="q">Years lived beyond the retirement age</p>
    <div class="v" id="wRet">—</div><div class="u">million retirement person-years</div>
    <div class="chg" id="cRet"></div>
    <div class="legend"><span><span class="sw" style="background:var(--up)"></span>healthy</span>
      <span><span class="sw" style="background:var(--down)"></span>in poor health (needs care)</span></div>
    <div class="bar" id="barRet"></div></div>
  <div class="oc" style="--c:var(--terra)"><div class="ic">🏥</div>
    <h3>Who needs healthcare</h3><p class="q">Poor-health person-years (LE − HLY)</p>
    <div class="v" id="wCare">—</div><div class="u">million poor-health person-years · lower is better</div>
    <div class="chg" id="cCare"></div></div>
  <div class="oc" style="--c:var(--acc)"><div class="ic">🎭</div>
    <h3>Who fills concert halls &amp; courses</h3><p class="q">Healthy years after retirement</p>
    <div class="v" id="wCult">—</div><div class="u">million healthy-retirement person-years</div>
    <div class="chg" id="cCult"></div></div>
</div>

<div class="note"><b>How it works.</b> Values are a <b>central-path scenario</b> for 2033, recomputed from the
forecast base by these identities (all per sex, then summed): <code>work = supply × (HLY/LE · working-life · participation)</code>,
<code>retire = pop × max(0, LE − retirement age)</code>, <code>care = pop × (LE − HLY)</code>,
<code>concert/courses = pop × max(0, HLY − retirement age)</code>. Raising HLY lifts the workforce and the healthy-retiree pool
while cutting the care burden — at the central path several countries start near <b>zero</b> healthy years after retirement
(self-perceived HLY below the retirement age), so the dial reveals how much health gain it takes to change that.</div>
<div class="note"><b>Honest caveats.</b> HLY is <b>self-perceived</b> (Eurostat GALI) — read shifts, not absolute levels.
This is a deterministic central path (Level 5's headline dividend is the probability-weighted mean, which is higher because
the healthy-retirement clip is convex). Participation and working-life responses are first-order — illustrative, not a labour-market model.</div>
<p class="lead" style="margin-top:22px;font-size:12px"><a href="../index.html">← Overview</a> ·
Generated from outputs/whatif_base.json · src/whatif_data.py, report_whatif.py</p>
</div>
<script>const BASE = __BASE__;</script>
<script>
const C={up:'#15803D',down:'#B91C1C',mut:'#78716C'};
const M=1e6, fmt=v=>Math.round(v/M).toLocaleString();
const ceq=document.getElementById('country');
const ALL={name:'All 8 countries'};
const codes=Object.keys(BASE.countries);
[['ALL','All 8 countries'],...codes.map(c=>[c,BASE.countries[c].name])].forEach(([k,n])=>{
  const o=document.createElement('option');o.value=k;o.textContent=n;ceq.appendChild(o);});
let state={c:'ALL',h:0,r:0,p:0};
const clip=(v,a,b)=>Math.max(a,Math.min(b,v));

function segsFor(c){return c==='ALL'?codes.flatMap(k=>BASE.countries[k].seg):BASE.countries[c].seg;}

function compute(c,dH,dR,dP){
  let work=0,retire=0,care=0,cult=0;
  for(const g of segsFor(c)){
    const hly2=g.hly+dH, ret2=g.ret+dR, le=g.le;
    const hs0=Math.min(1,g.hly/le), hs2=Math.min(1,hly2/le);
    const wlf=(g.wl+dR)/g.wl, pf=clip(g.part+dP/100,0,1)/g.part;
    work += g.work0*(hs2/hs0)*wlf*pf;
    retire += g.pop*Math.max(0,le-ret2);
    care   += g.pop*Math.max(0,le-hly2);
    cult   += g.pop*Math.max(0,hly2-ret2);
  }
  return {work,retire,care,cult};
}

function chg(el,now,base,goodUp){
  const d=base?((now/base-1)*100):0, abs=(now-base)/M;
  const good=goodUp?d>=0:d<=0;
  const col=Math.abs(d)<0.05?C.mut:(good?C.up:C.down);
  el.style.color=col;
  const s=(d>=0?'+':'')+d.toFixed(1)+'%';
  const a=(abs>=0?'+':'')+Math.round(abs).toLocaleString()+'M';
  el.textContent=Math.abs(d)<0.05?'no change vs base':`${s}  (${a} vs base)`;
}

function render(){
  document.getElementById('vH').textContent=(state.h>=0?'+':'')+state.h.toFixed(1);
  document.getElementById('vR').textContent=(state.r>=0?'+':'')+state.r.toFixed(1);
  document.getElementById('vP').textContent=(state.p>=0?'+':'')+state.p;
  const now=compute(state.c,state.h,state.r,state.p);
  const base=compute(state.c,0,0,0);
  document.getElementById('wWork').textContent=fmt(now.work);
  document.getElementById('wRet').textContent=fmt(now.retire);
  document.getElementById('wCare').textContent=fmt(now.care);
  document.getElementById('wCult').textContent=fmt(now.cult);
  chg(document.getElementById('cWork'),now.work,base.work,true);
  chg(document.getElementById('cRet'),now.retire,base.retire,true);
  chg(document.getElementById('cCare'),now.care,base.care,false);
  chg(document.getElementById('cCult'),now.cult,base.cult,true);
  // retirement split: healthy (cult) vs poor-health (retire - cult)
  const healthy=Math.min(now.cult,now.retire), poor=Math.max(0,now.retire-now.cult);
  const tot=healthy+poor||1;
  document.getElementById('barRet').innerHTML=
    `<div class="seg" style="width:${healthy/tot*100}%;background:${C.up}"></div>`+
    `<div class="seg" style="width:${poor/tot*100}%;background:${C.down}"></div>`;
  narrate(now,base);
}

function narrate(now,base){
  const nm=state.c==='ALL'?'the 8 countries':BASE.countries[state.c].name;
  if(state.h===0&&state.r===0&&state.p===0){
    document.getElementById('story').innerHTML=
      `<b>Base case (2033) for ${nm}.</b> Move the dials: ask whether people live longer in good health,
       retire later, or work more — and watch who works, who retires, who needs care, and who fills the
       concert halls respond together.`;return;}
  const pc=(n,b)=>((n/b-1)*100);
  const w=pc(now.work,base.work), ca=pc(now.care,base.care), cu=pc(now.cult,base.cult);
  const bits=[];
  if(state.h)bits.push(`<b>+${state.h}</b> healthy year${state.h==1?'':'s'}`);
  if(state.r)bits.push(`retiring <b>${state.r>0?state.r+' yr later':Math.abs(state.r)+' yr earlier'}</b>`);
  if(state.p)bits.push(`participation <b>${state.p>0?'+':''}${state.p}pp</b>`);
  const careTxt = ca<=-0.05?`the care burden falls <b class="dn">${ca.toFixed(1)}%</b>`
                : ca>=0.05?`the care burden rises <span class="dn">+${ca.toFixed(1)}%</span>`:`the care burden is flat`;
  document.getElementById('story').innerHTML=
    `For ${nm}: ${bits.join(', ')} → the workforce ${w>=0?'grows':'shrinks'} <b>${w>=0?'+':''}${w.toFixed(1)}%</b>,
     ${careTxt}, and the <b>active healthy-retiree</b> pool (concert halls &amp; courses)
     ${cu>=0?'grows':'shrinks'} <b>${cu>=0?'+':''}${cu.toFixed(1)}%</b>.`;
}

ceq.onchange=()=>{state.c=ceq.value;render();};
const sH=document.getElementById('sH'),sR=document.getElementById('sR'),sP=document.getElementById('sP');
sH.oninput=()=>{state.h=+sH.value;render();};
sR.oninput=()=>{state.r=+sR.value;render();};
sP.oninput=()=>{state.p=+sP.value;render();};
document.querySelectorAll('.preset').forEach(b=>b.onclick=()=>{
  state.h=+b.dataset.h;state.r=+b.dataset.r;state.p=+b.dataset.p;
  sH.value=state.h;sR.value=state.r;sP.value=state.p;render();});
render();
</script>
</body></html>"""

(OUT / "whatif.html").write_text(HTML.replace("__BASE__", json.dumps(BASE)), encoding="utf-8")
print(f"wrote outputs/whatif.html ({len(json.dumps(BASE))} bytes data, {len(BASE['countries'])} countries)")
