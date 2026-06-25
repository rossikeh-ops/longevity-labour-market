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

HTML = r"""<!doctype html><html lang="bg" data-lang="bg"><head><meta charset="utf-8">
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
.jobchips{display:flex;gap:8px;margin-top:12px}
.jc{flex:1;background:var(--bg);border:1px solid var(--line);border-radius:9px;padding:8px 10px;text-align:center}
.jc .jv{font-size:16px;font-weight:700}.jc .jl{color:var(--mut);font-size:10.5px;margin-top:2px}
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
.info{display:inline-flex;align-items:center;justify-content:center;width:14px;height:14px;border-radius:50%;
border:1px solid var(--mut);color:var(--mut);font:700 9px/1 Georgia,serif;font-style:italic;cursor:help;
margin-left:5px;position:relative;vertical-align:middle;user-select:none}
.info:hover{border-color:var(--acc);color:var(--acc)}
.info:hover::after{content:attr(data-tip);position:absolute;left:50%;bottom:150%;transform:translateX(-50%);
background:#292524;color:#fff;font:400 12px/1.45 -apple-system,Segoe UI,Roboto,Arial,sans-serif;font-style:normal;
text-align:left;padding:9px 11px;border-radius:8px;width:250px;max-width:70vw;white-space:normal;z-index:60;
box-shadow:0 6px 20px rgba(0,0,0,.22);pointer-events:none}
.info:hover::before{content:'';position:absolute;left:50%;bottom:150%;transform:translateX(-50%) translateY(99%);
border:6px solid transparent;border-top-color:#292524;z-index:60;pointer-events:none}
.bar{height:12px;background:var(--bg);border:1px solid var(--line);border-radius:7px;overflow:hidden;margin-top:12px;display:flex}
.bar .seg{height:100%}
.note{color:var(--mut);font-size:13px;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px;margin-top:16px}
.note b{color:var(--ink)}code{background:#F5F5F4;border:1px solid #E7E5E4;border-radius:5px;padding:1px 5px;color:#475569;font-size:12.5px}
.legend{display:flex;gap:16px;color:var(--mut);font-size:12px;margin:4px 2px 0;flex-wrap:wrap}
.sw{display:inline-block;width:11px;height:11px;border-radius:2px;margin-right:5px;vertical-align:-1px}
@media(max-width:720px){.sliders{grid-template-columns:1fr}.cards{grid-template-columns:1fr}}
html[data-lang='en'] [lang='bg']{display:none!important}html[data-lang='bg'] [lang='en']{display:none!important}
.langtoggle{position:fixed;top:14px;right:14px;z-index:9999;background:var(--card);border:1px solid var(--line);
border-radius:20px;padding:7px 15px;cursor:pointer;font:700 13px/1 inherit;color:var(--acc);box-shadow:0 2px 10px rgba(0,0,0,.08)}
.langtoggle:hover{border-color:var(--acc)}
</style></head><body>
<button class="langtoggle" id="langtoggle" aria-label="switch language">EN</button>
<div class="wrap">
<a class="home" href="../index.html"><span lang="en">← Overview</span><span lang="bg">← Обзор</span></a>
<h1 lang="en">What-if — do longer, healthier lives reshape the economy?</h1>
<h1 lang="bg">Какво-ако — преобразяват ли по-дългите, по-здрави животи икономиката?</h1>
<p class="lead" lang="en">Three dials, four answers. Everything recomputes live from the 2033 base using the
same identities as Levels 1, 4 and 5 — a transparent, central-path scenario sandbox.</p>
<p class="lead" lang="bg">Три плъзгача, четири отговора. Всичко се преизчислява на живо от базата за 2033 г. по същите
тъждества като Нива 1, 4 и 5 — прозрачен пясъчник на сценарий по централната пътека.</p>
<p class="ask" lang="en">“Do they live longer in good health? And what does that mean for our economy — who keeps working,
who retires, who needs healthcare, and who fills the concert halls and the adult-education courses?”</p>
<p class="ask" lang="bg">„Живеят ли по-дълго в добро здраве? И какво означава това за нашата икономика — кой продължава да работи,
кой се пенсионира, кой има нужда от здравни грижи и кой пълни концертните зали и курсовете за възрастни?“</p>

<div class="panel">
  <div class="row">
    <div class="fctl"><label for="country"><span lang="en">Country</span><span lang="bg">Държава</span></label>
      <select id="country"></select></div>
    <div style="flex:1"></div>
  </div>
  <div class="sliders">
    <div class="sl"><h4><span lang="en">🫀 Healthy life years</span><span lang="bg">🫀 Здрави години живот</span></h4>
      <div class="d" lang="en">Do they live longer <i>in good health</i>? Shift healthy-life expectancy (HLY).</div>
      <div class="d" lang="bg">Живеят ли по-дълго <i>в добро здраве</i>? Променете очакваните здрави години живот (ЗГЖ).</div>
      <div class="val"><span id="vH">+0.0</span> <span lang="en">years HLY</span><span lang="bg">години ЗГЖ</span></div>
      <input type="range" id="sH" min="-3" max="6" step="0.5" value="0">
      <div class="scale"><span>−3</span><span lang="en">base</span><span lang="bg">база</span><span>+6</span></div></div>
    <div class="sl"><h4><span lang="en">🧓 Retirement age</span><span lang="bg">🧓 Пенсионна възраст</span></h4>
      <div class="d" lang="en">Do they retire later? Shift the statutory retirement age.</div>
      <div class="d" lang="bg">Пенсионират ли се по-късно? Променете законовата пенсионна възраст.</div>
      <div class="val"><span id="vR">+0.0</span> <span lang="en">years</span><span lang="bg">години</span></div>
      <input type="range" id="sR" min="-2" max="6" step="0.5" value="0">
      <div class="scale"><span>−2</span><span lang="en">base</span><span lang="bg">база</span><span>+6</span></div></div>
    <div class="sl"><h4><span lang="en">💪 Participation</span><span lang="bg">💪 Участие</span></h4>
      <div class="d" lang="en">Do more of them work? Shift the employment rate of healthy working-age people.</div>
      <div class="d" lang="bg">Работят ли повече от тях? Променете коефициента на заетост на здравите хора в трудоспособна възраст.</div>
      <div class="val"><span id="vP">+0</span> <span lang="en">pp</span><span lang="bg">пр.п.</span></div>
      <input type="range" id="sP" min="-5" max="12" step="1" value="0">
      <div class="scale"><span>−5</span><span lang="en">base</span><span lang="bg">база</span><span>+12</span></div>
      <div class="jobchips">
        <div class="jc"><div class="jv" id="occJobs">—</div><div class="jl"><span lang="en">💼 Occupied jobs</span><span lang="bg">💼 Заети работни места</span></div></div>
        <div class="jc"><div class="jv" id="jobList">—</div><div class="jl"><span lang="en">📋 Job listings (vacancies)</span><span lang="bg">📋 Обяви за работа (свободни)</span></div></div>
      </div></div>
  </div>
  <div class="presets">
    <button class="preset" data-h="3" data-r="0" data-p="0"><span lang="en">Healthy ageing (+3 HLY)</span><span lang="bg">Здраво застаряване (+3 ЗГЖ)</span></button>
    <button class="preset" data-h="0" data-r="3" data-p="5"><span lang="en">Work longer (+3 ret, +5pp)</span><span lang="bg">Работа по-дълго (+3 пенс., +5пр.п.)</span></button>
    <button class="preset" data-h="3" data-r="2" data-p="5"><span lang="en">Both at once</span><span lang="bg">И двете заедно</span></button>
    <button class="preset reset" data-h="0" data-r="0" data-p="0"><span lang="en">Reset</span><span lang="bg">Нулиране</span></button>
  </div>
</div>

<div class="story" id="story"></div>

<div class="cards">
  <div class="oc" style="--c:var(--slate)"><div class="ic">👷</div>
    <h3><span lang="en">Who keeps working</span><span lang="bg">Кой продължава да работи</span><span class="info" lang="en" data-tip="Labour supply in human-working-years = healthy working-age people × working life × participation (Level 1) — the labour the population can actually supply.">i</span><span class="info" lang="bg" data-tip="Предлагане на труд в човеко-работни години = здрави хора в трудоспособна възраст × трудов живот × участие (Ниво 1) — трудът, който населението реално може да осигури.">i</span></h3><p class="q"><span lang="en">Labour supply — human-working-years</span><span lang="bg">Предлагане на труд — човеко-работни години</span></p>
    <div class="v" id="wWork">—</div><div class="u"><span lang="en">million human-working-years</span><span lang="bg">милиона човеко-работни години</span></div>
    <div class="chg" id="cWork"></div></div>
  <div class="oc" style="--c:var(--mustard)"><div class="ic">🏖️</div>
    <h3><span lang="en">Who retires</span><span lang="bg">Кой се пенсионира</span><span class="info" lang="en" data-tip="Population × years lived beyond the statutory retirement age (LE − retirement age) — total person-years spent in retirement. The bar splits them into healthy vs poor-health years.">i</span><span class="info" lang="bg" data-tip="Население × годините, изживени след законовата пенсионна възраст (ОПЖ − пенс. възраст) — общо човеко-години в пенсия. Лентата ги разделя на здрави срещу в лошо здраве.">i</span></h3><p class="q"><span lang="en">Years lived beyond the retirement age</span><span lang="bg">Години, изживени след пенсионната възраст</span></p>
    <div class="v" id="wRet">—</div><div class="u"><span lang="en">million retirement person-years</span><span lang="bg">милиона пенсионни човеко-години</span></div>
    <div class="chg" id="cRet"></div>
    <div class="legend"><span><span class="sw" style="background:var(--up)"></span><span lang="en">healthy</span><span lang="bg">здрави</span></span>
      <span><span class="sw" style="background:var(--down)"></span><span lang="en">in poor health (needs care)</span><span lang="bg">в лошо здраве (нужда от грижи)</span></span></div>
    <div class="bar" id="barRet"></div></div>
  <div class="oc" style="--c:var(--terra)"><div class="ic">🏥</div>
    <h3><span lang="en">Who needs healthcare</span><span lang="bg">Кой има нужда от здравни грижи</span><span class="info" lang="en" data-tip="Population × years lived in poor health (LE − HLY) (Level 4). Lower is better — more healthy life years means less care needed.">i</span><span class="info" lang="bg" data-tip="Население × годините, изживени в лошо здраве (ОПЖ − ЗГЖ) (Ниво 4). По-ниско е по-добре — повече здрави години означава по-малко нужда от грижи.">i</span></h3><p class="q"><span lang="en">Poor-health person-years (LE − HLY)</span><span lang="bg">Човеко-години в лошо здраве (ОПЖ − ЗГЖ)</span></p>
    <div class="v" id="wCare">—</div><div class="u"><span lang="en">million poor-health person-years · lower is better</span><span lang="bg">милиона човеко-години в лошо здраве · по-ниско е по-добре</span></div>
    <div class="chg" id="cCare"></div></div>
  <div class="oc" style="--c:var(--acc)"><div class="ic">🎭</div>
    <h3><span lang="en">Who fills concert halls &amp; courses</span><span lang="bg">Кой пълни концертните зали и курсовете</span><span class="info" lang="en" data-tip="Population × healthy years after retirement (HLY − retirement age, floored at 0) (Level 5) — the active, healthy retirees who fill leisure, education &amp; culture.">i</span><span class="info" lang="bg" data-tip="Население × здравите години след пенсиониране (ЗГЖ − пенс. възраст, ограничено до 0) (Ниво 5) — активните, здрави пенсионери, които пълнят свободното време, образованието и културата.">i</span></h3><p class="q"><span lang="en">Healthy years after retirement</span><span lang="bg">Здрави години след пенсиониране</span></p>
    <div class="v" id="wCult">—</div><div class="u"><span lang="en">million healthy-retirement person-years</span><span lang="bg">милиона човеко-години здраво пенсиониране</span></div>
    <div class="chg" id="cCult"></div></div>
</div>

<div class="note" lang="en"><b>How it works.</b> Values are a <b>central-path scenario</b> for 2033, recomputed from the
forecast base by these identities (all per sex, then summed): <code>work = supply × (HLY/LE · working-life · participation)</code>,
<code>retire = pop × max(0, LE − retirement age)</code>, <code>care = pop × (LE − HLY)</code>,
<code>concert/courses = pop × max(0, HLY − retirement age)</code>. Raising HLY lifts the workforce and the healthy-retiree pool
while cutting the care burden — at the central path several countries start near <b>zero</b> healthy years after retirement
(self-perceived HLY below the retirement age), so the dial reveals how much health gain it takes to change that.</div>
<div class="note" lang="bg"><b>Как работи.</b> Стойностите са <b>сценарий по централната пътека</b> за 2033 г., преизчислени от
прогнозната база по тези тъждества (всички по пол, после сумирани): <code>труд = предлагане × (ЗГЖ/ОПЖ · трудов живот · участие)</code>,
<code>пенсия = насел. × max(0, ОПЖ − пенс. възраст)</code>, <code>грижи = насел. × (ОПЖ − ЗГЖ)</code>,
<code>концерти/курсове = насел. × max(0, ЗГЖ − пенс. възраст)</code>. Повишаването на ЗГЖ увеличава работната сила и пула от
здрави пенсионери, докато намалява тежестта от грижи — по централната пътека няколко държави започват близо до <b>нула</b>
здрави години след пенсиониране (самооценените ЗГЖ под пенсионната възраст), затова плъзгачът разкрива колко здравна печалба е нужна, за да се промени това.</div>
<div class="note" lang="en"><b>Honest caveats.</b> HLY is <b>self-perceived</b> (Eurostat GALI) — read shifts, not absolute levels.
This is a deterministic central path (Level 5's headline dividend is the probability-weighted mean, which is higher because
the healthy-retirement clip is convex). Participation and working-life responses are first-order — illustrative, not a labour-market model.</div>
<div class="note" lang="bg"><b>Честни уговорки.</b> ЗГЖ е <b>самооценено</b> (Eurostat GALI) — четете промените, не абсолютните нива.
Това е детерминистична централна пътека (заглавният дивидент на Ниво 5 е вероятностно претеглената средна, която е по-висока,
защото отрязването при здравото пенсиониране е изпъкнало). Реакциите на участието и трудовия живот са от първи ред — илюстративни, не модел на пазара на труда.</div>
<p class="lead" style="margin-top:22px;font-size:12px"><a href="../index.html"><span lang="en">← Overview</span><span lang="bg">← Обзор</span></a> ·
src/whatif_data.py, report_whatif.py</p>
</div>
<script>const BASE = __BASE__;</script>
<script>
const C={up:'#15803D',down:'#B91C1C',mut:'#78716C'};
const M=1e6, fmt=v=>Math.round(v/M).toLocaleString();
const fmtM=v=>{const m=v/M;return (m>=10?m.toFixed(1):m.toFixed(2))+'M';};
const isBg=()=>document.documentElement.dataset.lang==='bg';
const L=(en,bg)=>isBg()?bg:en;
const ceq=document.getElementById('country');
const codes=Object.keys(BASE.countries);
let allOpt;
[['ALL',null],...codes.map(c=>[c,BASE.countries[c].name])].forEach(([k,n])=>{
  const o=document.createElement('option');o.value=k;o.textContent=n||L('All 8 countries','Всички 8 държави');
  ceq.appendChild(o);if(k==='ALL')allOpt=o;});
(function(){var r=document.documentElement;var Lg=localStorage.getItem('site-lang')||'bg';r.dataset.lang=Lg;
 var b=document.getElementById('langtoggle');function u(){b.textContent=r.dataset.lang==='en'?'БГ':'EN';}
 b.onclick=function(){var n=r.dataset.lang==='en'?'bg':'en';r.dataset.lang=n;localStorage.setItem('site-lang',n);u();
   allOpt.textContent=L('All 8 countries','Всички 8 държави');render();};u();})();
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
  el.textContent=Math.abs(d)<0.05?L('no change vs base','без промяна спрямо базата'):`${s}  (${a} ${L('vs base','спрямо базата')})`;
}

function render(){
  document.getElementById('vH').textContent=(state.h>=0?'+':'')+state.h.toFixed(1);
  document.getElementById('vR').textContent=(state.r>=0?'+':'')+state.r.toFixed(1);
  document.getElementById('vP').textContent=(state.p>=0?'+':'')+state.p;
  // occupied jobs (employed = participation × working-age people) and job listings (vacancies):
  // raising participation fills the open listings, so occupied ↑ and listings ↓.
  const segs=segsFor(state.c);
  const occ0=segs.reduce((a,g)=>a+g.part*g.pwa,0);
  const occ=segs.reduce((a,g)=>a+clip(g.part+state.p/100,0,1)*g.pwa,0);
  const vac0=state.c==='ALL'?codes.reduce((a,k)=>a+BASE.countries[k].vac0,0):BASE.countries[state.c].vac0;
  document.getElementById('occJobs').textContent=fmtM(occ);
  document.getElementById('jobList').textContent=fmtM(Math.max(0,vac0-(occ-occ0)));
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
  const bg=isBg();
  const nm=state.c==='ALL'?(bg?'8-те държави':'the 8 countries'):BASE.countries[state.c].name;
  const el=document.getElementById('story');
  if(state.h===0&&state.r===0&&state.p===0){
    el.innerHTML=bg
      ? `<b>Базов случай (2033) за ${nm}.</b> Движете плъзгачите: попитайте дали хората живеят по-дълго в добро здраве,
         пенсионират ли се по-късно или работят повече — и вижте как „кой работи“, „кой се пенсионира“, „кой има нужда от
         грижи“ и „кой пълни концертните зали“ реагират заедно.`
      : `<b>Base case (2033) for ${nm}.</b> Move the dials: ask whether people live longer in good health,
         retire later, or work more — and watch who works, who retires, who needs care, and who fills the
         concert halls respond together.`;
    return;}
  const pc=(n,b)=>((n/b-1)*100);
  const w=pc(now.work,base.work), ca=pc(now.care,base.care), cu=pc(now.cult,base.cult);
  const bits=[];
  if(bg){
    if(state.h)bits.push(`<b>+${state.h}</b> г. ЗГЖ`);
    if(state.r)bits.push(`пенсиониране <b>${state.r>0?state.r+' г. по-късно':Math.abs(state.r)+' г. по-рано'}</b>`);
    if(state.p)bits.push(`участие <b>${state.p>0?'+':''}${state.p}пр.п.</b>`);
    const careTxt = ca<=-0.05?`тежестта от грижи пада <b class="dn">${ca.toFixed(1)}%</b>`
                  : ca>=0.05?`тежестта от грижи расте <span class="dn">+${ca.toFixed(1)}%</span>`:`тежестта от грижи е без промяна`;
    el.innerHTML=
      `За ${nm}: ${bits.join(', ')} → работната сила ${w>=0?'расте':'намалява'} <b>${w>=0?'+':''}${w.toFixed(1)}%</b>,
       ${careTxt}, а пулът от <b>активни здрави пенсионери</b> (концертни зали и курсове)
       ${cu>=0?'расте':'намалява'} <b>${cu>=0?'+':''}${cu.toFixed(1)}%</b>.`;
  } else {
    if(state.h)bits.push(`<b>+${state.h}</b> healthy year${state.h==1?'':'s'}`);
    if(state.r)bits.push(`retiring <b>${state.r>0?state.r+' yr later':Math.abs(state.r)+' yr earlier'}</b>`);
    if(state.p)bits.push(`participation <b>${state.p>0?'+':''}${state.p}pp</b>`);
    const careTxt = ca<=-0.05?`the care burden falls <b class="dn">${ca.toFixed(1)}%</b>`
                  : ca>=0.05?`the care burden rises <span class="dn">+${ca.toFixed(1)}%</span>`:`the care burden is flat`;
    el.innerHTML=
      `For ${nm}: ${bits.join(', ')} → the workforce ${w>=0?'grows':'shrinks'} <b>${w>=0?'+':''}${w.toFixed(1)}%</b>,
       ${careTxt}, and the <b>active healthy-retiree</b> pool (concert halls &amp; courses)
       ${cu>=0?'grows':'shrinks'} <b>${cu>=0?'+':''}${cu.toFixed(1)}%</b>.`;
  }
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
