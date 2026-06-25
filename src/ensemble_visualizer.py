# -*- coding: utf-8 -*-
"""
Build outputs/ensemble_visualizer.html — an interactive "Ensemble Uncertainty
Visualizer". Pure client-side (no data, no neural nets): it generates noisy
observations of a hidden function, then fits an ENSEMBLE of simple polynomial
models, each on a Monte-Carlo-perturbed copy of the data. The faint lines are
the members, the bold line is their average; their spread IS the uncertainty.

Sliders: Ensemble Size (number of members) and Sampling Noise (Monte-Carlo
perturbation). Confidence = how tightly the members agree. Self-contained.
"""
from __future__ import annotations
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "outputs"

HTML = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ensemble Uncertainty Visualizer</title>
<style>
:root{--bg:#0b0f1a;--panel:#111726;--ink:#eef2f8;--mut:#9fb3d1;--line:#1e2940;
--accent:#7ab0ff;--amber:#f59e0b;}
*{box-sizing:border-box}html,body{margin:0}
body{background:#070a12;color:var(--ink);font:15px/1.5 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
display:flex;justify-content:center;padding:26px 16px}
.card{width:100%;max-width:780px;background:linear-gradient(180deg,#0c1120,#0a0e18);
border:1px solid var(--line);border-radius:18px;padding:24px 26px 26px}
h1{font-size:24px;font-weight:700;margin:0 0 4px;letter-spacing:.2px}
.sub{color:var(--mut);font-size:13px;margin:0 0 16px}
.sub b{color:var(--accent)}
.chartwrap{position:relative}
canvas{width:100%;height:360px;display:block}
.stats{display:grid;grid-template-columns:1fr 1fr;gap:8px;border-top:1px solid var(--line);
border-bottom:1px solid var(--line);margin:18px 0;padding:16px 0;text-align:center}
.stats .lab{color:var(--mut);font-size:14px;margin-bottom:6px}
.stats .val{font-size:20px;font-weight:700}
.stats .conf{color:var(--amber)}
.ctrl{display:flex;align-items:center;gap:16px;margin:14px 0}
.ctrl label{color:var(--mut);font-size:14px;min-width:118px}
.ctrl input[type=range]{-webkit-appearance:none;appearance:none;flex:1;height:4px;border-radius:3px;
background:#2a3550;outline:none}
.ctrl input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:20px;height:20px;border-radius:50%;
background:#fff;cursor:pointer;box-shadow:0 1px 4px rgba(0,0,0,.5)}
.ctrl input[type=range]::-moz-range-thumb{width:20px;height:20px;border:none;border-radius:50%;background:#fff;cursor:pointer}
.ctrl .box{min-width:62px;text-align:center;background:#0c1120;border:1px solid var(--line);
border-radius:9px;padding:8px 6px;font-variant-numeric:tabular-nums;font-weight:600}
button.gen{width:100%;margin-top:14px;background:#1b2336;color:var(--ink);border:1px solid var(--line);
border-radius:14px;padding:15px;font-size:15px;font-weight:600;cursor:pointer;transition:background .15s}
button.gen:hover{background:#243049}
.foot{color:var(--mut);font-size:12px;margin-top:14px;text-align:center}.foot a{color:var(--accent)}
</style></head><body>
<div class="card">
  <h1>Ensemble Uncertainty Visualizer</h1>
  <p class="sub">No neural nets — a <b>simple ensemble + Monte-Carlo</b>. Each faint line is one simple model
  fitted to a noise-perturbed copy of the data; the bold line is their average. Where they fan apart, we're
  uncertain. This is exactly how the forecasts in this project get their bands.</p>
  <div class="chartwrap"><canvas id="cv"></canvas></div>
  <div class="stats">
    <div><div class="lab">Models</div><div class="val" id="mval">21</div></div>
    <div><div class="lab">Confidence</div><div class="val conf" id="cval">—</div></div>
  </div>
  <div class="ctrl"><label>Ensemble Size</label>
    <input type="range" id="size" min="2" max="80" step="1" value="21">
    <span class="box" id="sizeBox">21</span></div>
  <div class="ctrl"><label>Sampling Noise</label>
    <input type="range" id="noise" min="0" max="0.5" step="0.01" value="0.15">
    <span class="box" id="noiseBox">0.15</span></div>
  <button class="gen" id="gen">Generate Ensemble</button>
  <p class="foot">Illustrative · <a href="methodology_report.html">how the model actually works →</a></p>
</div>
<script>
const cv=document.getElementById('cv'),ctx=cv.getContext('2d');
const sizeS=document.getElementById('size'),noiseS=document.getElementById('noise');
const sizeBox=document.getElementById('sizeBox'),noiseBox=document.getElementById('noiseBox');
const mval=document.getElementById('mval'),cval=document.getElementById('cval');
const DEG=6, NX=24, GRID=150, MAXM=80, XMAX=10, YMIN=-2, YMAX=2;
let data=[], Z=[];

function gaussian(){let u=0,v=0;while(u===0)u=Math.random();while(v===0)v=Math.random();
  return Math.sqrt(-2*Math.log(u))*Math.cos(2*Math.PI*v);}

function genData(){
  data=[];
  for(let i=0;i<NX;i++){const x=i/(NX-1)*XMAX; const f=Math.cos(x*0.85); data.push({x,y:f+gaussian()*0.18});}
  Z=Array.from({length:MAXM},()=>data.map(()=>gaussian()));   // fixed MC draws -> smooth slider response
}

function solve(A,b){const n=b.length;
  for(let c=0;c<n;c++){let p=c;for(let r=c+1;r<n;r++)if(Math.abs(A[r][c])>Math.abs(A[p][c]))p=r;
    [A[c],A[p]]=[A[p],A[c]];[b[c],b[p]]=[b[p],b[c]];const piv=A[c][c]||1e-9;
    for(let r=0;r<n;r++){if(r===c)continue;const f=A[r][c]/piv;
      for(let k=c;k<n;k++)A[r][k]-=f*A[c][k];b[r]-=f*b[c];}}
  return b.map((v,i)=>v/(A[i][i]||1e-9));}

function polyfit(ys){const n=DEG+1;const A=Array.from({length:n},()=>new Array(n).fill(0));const bb=new Array(n).fill(0);
  for(let i=0;i<data.length;i++){const t=(data[i].x-5)/5;const pw=[];let p=1;
    for(let j=0;j<2*DEG+1;j++){pw.push(p);p*=t;}
    for(let r=0;r<n;r++){for(let c=0;c<n;c++)A[r][c]+=pw[r+c];bb[r]+=pw[r]*ys[i];}}
  return solve(A,bb);}
function polyval(co,x){const t=(x-5)/5;let p=1,s=0;for(let j=0;j<co.length;j++){s+=co[j]*p;p*=t;}return s;}

function render(){
  const size=+sizeS.value, noise=+noiseS.value;
  sizeBox.textContent=size; noiseBox.textContent=noise.toFixed(2); mval.textContent=size;
  const W=cv.clientWidth,H=cv.clientHeight,dpr=window.devicePixelRatio||1;
  cv.width=W*dpr;cv.height=H*dpr;ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,W,H);
  const ML=52,MR=16,MT=40,MB=34;
  const X=x=>ML+x/XMAX*(W-ML-MR), Y=y=>MT+(YMAX-y)/(YMAX-YMIN)*(H-MT-MB);
  // grid + axes
  ctx.strokeStyle='rgba(255,255,255,.07)';ctx.fillStyle='#7e90ad';ctx.font='11px sans-serif';ctx.lineWidth=1;
  for(let g=YMIN;g<=YMAX+1e-9;g+=0.5){const yy=Y(g);ctx.beginPath();ctx.moveTo(ML,yy);ctx.lineTo(W-MR,yy);ctx.stroke();
    ctx.textAlign='right';ctx.fillText(g.toFixed(1),ML-8,yy+3);}
  ctx.textAlign='center';for(let g=0;g<=XMAX;g++){ctx.fillText(g,X(g),H-MB+16);}
  ctx.textAlign='left';ctx.fillStyle='#9fb3d1';ctx.fillText('Model Output (Y) ↑',ML,MT-18);
  ctx.textAlign='right';ctx.fillText('Input Range (X) →',W-MR,H-6);
  // ensemble members
  const gx=[];for(let g=0;g<GRID;g++)gx.push(g/(GRID-1)*XMAX);
  const curves=[];
  for(let m=0;m<size;m++){const yp=data.map((d,i)=>d.y+Z[m][i]*noise*3);
    const co=polyfit(yp);curves.push(gx.map(x=>polyval(co,x)));}
  ctx.lineWidth=1;ctx.strokeStyle='rgba(150,180,235,'+Math.max(.04,Math.min(.22,3/size))+')';
  for(let m=0;m<size;m++){ctx.beginPath();for(let g=0;g<GRID;g++){const px=X(gx[g]),py=Y(curves[m][g]);
    g?ctx.lineTo(px,py):ctx.moveTo(px,py);}ctx.stroke();}
  // average + spread
  const avg=[],std=[];
  for(let g=0;g<GRID;g++){let s=0;for(let m=0;m<size;m++)s+=curves[m][g];const mu=s/size;
    let v=0;for(let m=0;m<size;m++)v+=(curves[m][g]-mu)**2;avg.push(mu);std.push(Math.sqrt(v/size));}
  ctx.save();ctx.strokeStyle='#7ab0ff';ctx.lineWidth=3;ctx.shadowColor='#7ab0ff';ctx.shadowBlur=10;
  ctx.beginPath();for(let g=0;g<GRID;g++){const px=X(gx[g]),py=Y(Math.max(YMIN,Math.min(YMAX,avg[g])));
    g?ctx.lineTo(px,py):ctx.moveTo(px,py);}ctx.stroke();ctx.restore();
  ctx.fillStyle='#7ab0ff';ctx.font='600 13px sans-serif';ctx.textAlign='center';ctx.fillText('Ensemble Average',W/2,MT+8);
  // data points
  ctx.fillStyle='rgba(255,255,255,.92)';
  for(const d of data){ctx.beginPath();ctx.arc(X(d.x),Y(Math.max(YMIN,Math.min(YMAX,d.y))),3,0,7);ctx.fill();}
  // confidence
  const meanStd=std.reduce((a,b)=>a+b,0)/GRID;
  const conf=100*(1-Math.min(0.96,meanStd/1.1));
  cval.textContent=conf.toFixed(1)+'%';
}
sizeS.oninput=render; noiseS.oninput=render;
document.getElementById('gen').onclick=()=>{genData();render();};
window.addEventListener('resize',render);
genData();render();
</script>
</body></html>"""

(OUT / "ensemble_visualizer.html").write_text(HTML, encoding="utf-8")
print("wrote outputs/ensemble_visualizer.html")
