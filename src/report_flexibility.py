# -*- coding: utf-8 -*-
"""
Build outputs/flexibility.html — an interactive "Model flexibility / bias-variance
tradeoff" widget (bilingual BG|EN, earthy theme).

A slider sweeps polynomial flexibility (degree) on a REAL Healthy-Life-Years
series; the page fits the polynomial by least squares, computes leave-one-out
cross-validated error live, finds the CV-optimal flexibility, and labels the
current setting underfit / optimal / overfit against it. A mini chart shows the
classic train-error-falls / CV-error-U-shape tradeoff. This is the concrete
"why we use simple models, no neural nets" argument from the methodology page.
"""
from __future__ import annotations
import sys
import json
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from i18n import lang_css, lang_toggle, T  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"

# ---- real Healthy-Life-Years series (both sexes, at birth), per country ----
panel = pd.read_parquet(ROOT / "data" / "processed" / "panel.parquet")
g = panel.dropna(subset=["hly_birth"]).groupby(["country", "year"])["hly_birth"].mean().reset_index()
DATA = {}
for c, sub in g.groupby("country"):
    sub = sub.sort_values("year")
    DATA[c] = [[int(y), round(float(v), 1)] for y, v in zip(sub.year, sub.hly_birth)]
DATA_JSON = json.dumps(DATA, separators=(",", ":"))

NAME_EN = {"BG": "Bulgaria", "PL": "Poland", "CZ": "Czechia", "RO": "Romania",
           "DE": "Germany", "FR": "France", "NO": "Norway", "CH": "Switzerland"}
NAME_BG = {"BG": "България", "PL": "Полша", "CZ": "Чехия", "RO": "Румъния",
           "DE": "Германия", "FR": "Франция", "NO": "Норвегия", "CH": "Швейцария"}
ORDER = ["DE", "FR", "CH", "NO", "PL", "CZ", "RO", "BG"]
OPTIONS = "".join(
    f'<option value="{c}" data-en="{NAME_EN[c]}" data-bg="{NAME_BG[c]}"'
    f'{" selected" if c == "CZ" else ""}>{NAME_EN[c]}</option>' for c in ORDER)

CSS = """
:root{--bg:#FAFAF9;--card:#FFFFFF;--ink:#292524;--mut:#78716C;--line:#E7E5E4;
--acc:#166534;--ok:#15803D;--warn:#D97706;--down:#B91C1C;--slate:#475569;}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font:16px/1.6 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;padding:34px 22px}
.wrap{max-width:820px;margin:0 auto}
.home{color:var(--mut);text-decoration:none;font-size:13px}.home:hover{color:var(--acc)}
h1{font-size:26px;margin:8px 0 4px;letter-spacing:-.3px}
.sub{color:var(--mut);max-width:720px;margin:0 0 14px}
.panel{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px 18px 14px;margin:6px 0}
.row{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:8px}
.row label{font-size:13px;font-weight:700;color:var(--mut)}
select{font:inherit;font-size:14px;padding:6px 10px;border:1px solid var(--line);border-radius:8px;background:#fff;color:var(--ink)}
.lgd{display:flex;gap:16px;font-size:12.5px;color:var(--mut);margin:2px 0 6px}
.lgd b{display:inline-block;width:11px;height:11px;border-radius:3px;margin-right:5px;vertical-align:-1px}
svg{display:block;width:100%;height:auto}
.status{border:1px solid var(--line);border-left:4px solid var(--c,var(--mut));border-radius:10px;
padding:12px 15px;margin:12px 0;background:#FBFBFA}
.status .st{font-weight:800;font-size:15px;color:var(--c,var(--ink))}
.status .sd{color:#44403C;font-size:14px;margin-top:3px}
.read{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:10px 0}
.read .b{background:#FBFBFA;border:1px solid var(--line);border-radius:9px;padding:9px 11px}
.read .v{font-size:18px;font-weight:750;font-variant-numeric:tabular-nums}
.read .k{font-size:11.5px;color:var(--mut);margin-top:1px}
.slide{display:flex;align-items:center;gap:14px;margin-top:14px}
.slide label{font-size:14px;font-weight:800;white-space:nowrap}
input[type=range]{flex:1;accent-color:var(--acc);height:4px}
.deg{min-width:52px;height:40px;border:1px solid var(--line);border-radius:20px;display:grid;place-items:center;
font-weight:800;font-size:16px;font-variant-numeric:tabular-nums;background:#fff}
.bvwrap{margin-top:6px}
.note{color:#44403C;font-size:14px;background:var(--card);border:1px solid var(--line);
border-radius:10px;padding:14px 16px;margin-top:14px}.note b{color:var(--ink)}
.foot{color:var(--mut);font-size:13px;margin-top:24px;border-top:1px solid var(--line);padding-top:14px}a{color:var(--acc)}
"""

CHROME = f"""<a class="home" href="../index.html">{T("← Overview", "← Обзор")}</a>
<h1>{T("Model flexibility — the bias–variance tradeoff", "Гъвкавост на модела — компромисът отклонение–дисперсия")}</h1>
<p class="sub">{T(
  "A model that is too <b>rigid</b> misses the real trend (underfit); one that is too <b>flexible</b> bends to chase "
  "noise it can’t predict next year (overfit). Drag the slider on a real Healthy-Life-Years series and watch where it "
  "generalises best — the cross-validated optimum is computed live.",
  "Модел, който е твърде <b>скован</b>, пропуска реалния тренд (недонапасване); такъв, който е твърде <b>гъвкав</b>, "
  "се извива, за да гони шум, който не може да предскаже догодина (пренапасване). Плъзнете слайдера върху реален ред за "
  "Здрави години живот и вижте къде обобщава най-добре — крос-валидираният оптимум се изчислява на живо.")}</p>

<div class="panel">
<div class="row"><label>{T("Country (HLY series):", "Държава (ред ЗГЖ):")}</label>
<select id="country">{OPTIONS}</select></div>
<div class="lgd"><span><b style="background:var(--slate)"></b>{T("Data points", "Данни")}</span>
<span><b id="fitsw" style="background:var(--ok)"></b>{T("Model fit", "Напасване на модела")}</span></div>
<svg id="chart" viewBox="0 0 720 360" role="img"></svg>
</div>

<div class="status" id="status"><div class="st"></div><div class="sd"></div></div>

<div class="read">
<div class="b"><div class="v" id="rTrain">–</div><div class="k">{T("Training error (RMSE)", "Грешка при обучение (RMSE)")}</div></div>
<div class="b"><div class="v" id="rCV">–</div><div class="k">{T("Cross-validated error (LOO)", "Крос-валидирана грешка (LOO)")}</div></div>
<div class="b"><div class="v" id="rStar">–</div><div class="k">{T("Best flexibility (CV-optimal)", "Най-добра гъвкавост (CV-оптимум)")}</div></div>
</div>

<div class="slide"><label>{T("Model flexibility", "Гъвкавост на модела")}</label>
<input type="range" id="flex" min="0" max="12" step="1" value="3"><div class="deg" id="degval">3</div></div>

<div class="panel bvwrap">
<div class="lgd"><span><b style="background:var(--slate)"></b>{T("Training error — always falls", "Грешка при обучение — винаги пада")}</span>
<span><b style="background:var(--acc)"></b>{T("Cross-validated error — U-shaped", "Крос-валидирана грешка — U-форма")}</span></div>
<svg id="bv" viewBox="0 0 720 220" role="img"></svg>
</div>

<div class="note">{T(
  "<b>Why this is the whole argument for simple models.</b> These histories are only ~13–21 years long, so the "
  "cross-validated optimum sits at a <b>modest</b> flexibility — never near the maximum. Try each country: the optimum "
  "shifts, but a wiggly high-degree fit always loses, and a neural network would land far to the right, deep in the "
  "overfit zone. Push the slider past the optimum and the training error keeps falling while the cross-validated error "
  "<b>climbs</b> — the model is memorising noise. That is exactly why the forecaster averages five simple models and "
  "carries honest bands, with no neural nets.",
  "<b>Защо това е целият аргумент за простите модели.</b> Тези истории са едва ~13–21 години, затова крос-валидираният "
  "оптимум е при <b>умерена</b> гъвкавост — никога близо до максимума. Пробвайте всяка държава: оптимумът се мести, но "
  "извиваща се крива от висока степен винаги губи, а невронна мрежа би попаднала далеч вдясно, дълбоко в зоната на "
  "пренапасване. Бутнете слайдера отвъд оптимума и грешката при обучение продължава да пада, докато крос-валидираната "
  "грешка <b>се покачва</b> — моделът запаметява шум. Точно затова прогнозата усреднява пет прости модела и носи честни "
  "ленти, без невронни мрежи.")}</div>

<p class="foot">{T("Ties into the", "Свързано с")} <a href="methodology_report.html">{T("methodology", "методологията")}</a>
({T("the 5-model ensemble &amp; the 3/6/9-year test", "ансамбълът от 5 модела и тестът 3/6/9 години")}) ·
<a href="../index.html">{T("← back to overview", "← обратно към обзора")}</a> · src/report_flexibility.py</p>"""

JS = r"""<script>
const DATA = __DATA__;
const SVGNS = "http://www.w3.org/2000/svg";
const isBg = () => document.documentElement.dataset.lang === 'bg';
const L = (en, bg) => isBg() ? bg : en;
const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();

// ---- least-squares polynomial fit on x scaled to [-1,1] ----
function fitPoly(pts, deg){
  const xs = pts.map(p=>p[0]), ys = pts.map(p=>p[1]);
  const x0 = Math.min(...xs), x1 = Math.max(...xs), mid=(x0+x1)/2, half=((x1-x0)/2)||1;
  const m = deg+1, n = pts.length;
  const ATA = Array.from({length:m},()=>new Array(m).fill(0)), ATy = new Array(m).fill(0);
  for(let i=0;i<n;i++){
    const t=(xs[i]-mid)/half; const row=[]; let p=1;
    for(let j=0;j<m;j++){ row.push(p); p*=t; }
    for(let a=0;a<m;a++){ ATy[a]+=row[a]*ys[i]; for(let b=0;b<m;b++) ATA[a][b]+=row[a]*row[b]; }
  }
  for(let a=0;a<m;a++) ATA[a][a]+=1e-9;            // tiny ridge for numerical stability
  const c = solve(ATA, ATy);
  return x => { const t=(x-mid)/half; let p=1,s=0; for(let j=0;j<m;j++){ s+=c[j]*p; p*=t; } return s; };
}
function solve(M, b){
  const n=b.length, A=M.map((r,i)=>r.concat(b[i]));
  for(let col=0;col<n;col++){
    let piv=col; for(let r=col+1;r<n;r++) if(Math.abs(A[r][col])>Math.abs(A[piv][col])) piv=r;
    [A[col],A[piv]]=[A[piv],A[col]];
    const d=A[col][col]||1e-12;
    for(let r=0;r<n;r++){ if(r===col) continue; const f=A[r][col]/d; for(let k=col;k<=n;k++) A[r][k]-=f*A[col][k]; }
  }
  return A.map((r,i)=>r[n]/(r[i]||1e-12));
}
const rmse = (pts,f)=>Math.sqrt(pts.reduce((s,[x,y])=>s+(f(x)-y)**2,0)/pts.length);
function looCV(pts, deg){
  let s=0;
  for(let i=0;i<pts.length;i++){
    const tr = pts.filter((_,j)=>j!==i);
    if(tr.length < deg+1) return NaN;
    s += (fitPoly(tr,deg)(pts[i][0]) - pts[i][1])**2;
  }
  return Math.sqrt(s/pts.length);
}

let PTS=[], MAXDEG=12, TRAIN=[], CV=[], DSTAR=1;
function prep(country){
  PTS = DATA[country];
  MAXDEG = Math.min(PTS.length-2, 12);
  TRAIN=[]; CV=[];
  for(let d=0; d<=MAXDEG; d++){ TRAIN[d]=rmse(PTS,fitPoly(PTS,d)); CV[d]=looCV(PTS,d); }
  let best=0, bv=Infinity;
  for(let d=0; d<=MAXDEG; d++){ if(isFinite(CV[d]) && CV[d] < bv-1e-9){ bv=CV[d]; best=d; } }
  DSTAR = best;
  const fx=document.getElementById('flex'); fx.max=MAXDEG;
  if(+fx.value>MAXDEG) fx.value=MAXDEG;
}

function el(p,t,a){ const e=document.createElementNS(SVGNS,t); for(const k in a) e.setAttribute(k,a[k]); p.appendChild(e); return e; }
function txt(p,x,y,s,a={}){ const e=el(p,'text',Object.assign({x,y},a)); e.textContent=s; return e; }
function clear(svg){ while(svg.firstChild) svg.removeChild(svg.firstChild); }

function niceRange(){
  const ys=PTS.map(p=>p[1]); let lo=Math.min(...ys), hi=Math.max(...ys);
  lo=Math.floor((lo-1.5)/2)*2; hi=Math.ceil((hi+1.5)/2)*2; return [lo,hi];
}
function drawChart(deg){
  const svg=document.getElementById('chart'); clear(svg);
  const ml=52,mr=22,mt=26,mb=46, W=720-ml-mr, H=360-mt-mb;
  const xs=PTS.map(p=>p[0]), x0=Math.min(...xs), x1=Math.max(...xs);
  const [y0,y1]=niceRange();
  const X=v=>ml+(v-x0)/(x1-x0)*W, Y=v=>mt+(y1-v)/(y1-y0)*H;
  const grid=css('--line'), mut=css('--mut');
  // y grid + labels
  for(let v=y0; v<=y1; v+=5){ el(svg,'line',{x1:ml,y1:Y(v),x2:ml+W,y2:Y(v),stroke:grid,'stroke-width':1});
    txt(svg,ml-8,Y(v)+4,v,{'font-size':12,fill:mut,'text-anchor':'end'}); }
  // x ticks
  const step=Math.max(1,Math.ceil((x1-x0)/7));
  for(let v=x0; v<=x1; v+=step){ txt(svg,X(v),mt+H+20,v,{'font-size':12,fill:mut,'text-anchor':'middle'}); }
  txt(svg,ml,mt-10,L('Healthy Life Years (HLY)','Здрави години живот (ЗГЖ)'),{'font-size':12.5,fill:css('--acc'),'font-weight':700});
  txt(svg,ml+W,mt+H+40,L('Year →','Година →'),{'font-size':12.5,fill:mut,'text-anchor':'end'});
  // fit curve, coloured by regime
  const reg = deg<DSTAR ? 'under' : deg>DSTAR ? 'over' : 'opt';
  const col = reg==='opt'?css('--ok'):reg==='under'?css('--slate'):css('--down');
  document.getElementById('fitsw').style.background=col;
  const f=fitPoly(PTS,deg); let dpath='';
  for(let k=0;k<=160;k++){ const xv=x0+(x1-x0)*k/160; const yv=Math.max(y0,Math.min(y1,f(xv)));
    dpath+=(k?'L':'M')+X(xv).toFixed(1)+' '+Y(yv).toFixed(1)+' '; }
  el(svg,'path',{d:dpath,fill:'none',stroke:col,'stroke-width':2.6,'stroke-linejoin':'round'});
  // data points
  for(const [x,y] of PTS) el(svg,'circle',{cx:X(x),cy:Y(y),r:4.2,fill:'#fff',stroke:css('--slate'),'stroke-width':1.8});
  return reg;
}
function drawBV(deg){
  const svg=document.getElementById('bv'); clear(svg);
  const ml=44,mr=14,mt=16,mb=34, W=720-ml-mr, H=220-mt-mb;
  const all=TRAIN.concat(CV).filter(isFinite); let lo=Math.min(...all), hi=Math.max(...all);
  lo=Math.max(0,lo*0.9); hi=hi*1.06||1;
  const X=d=>ml+(MAXDEG?d/MAXDEG:0)*W, Y=v=>mt+(hi-v)/(hi-lo)*H;
  const grid=css('--line'), mut=css('--mut');
  el(svg,'line',{x1:ml,y1:mt+H,x2:ml+W,y2:mt+H,stroke:grid});
  for(let d=0; d<=MAXDEG; d++) txt(svg,X(d),mt+H+18,d,{'font-size':11,fill:mut,'text-anchor':'middle'});
  txt(svg,ml,mt-4,L('error','грешка'),{'font-size':11.5,fill:mut});
  txt(svg,ml+W,mt+H+30,L('flexibility (degree) →','гъвкавост (степен) →'),{'font-size':11.5,fill:mut,'text-anchor':'end'});
  // current-degree marker + optimum marker
  el(svg,'line',{x1:X(deg),y1:mt,x2:X(deg),y2:mt+H,stroke:css('--ink'),'stroke-width':1,'stroke-dasharray':'3 3',opacity:.5});
  el(svg,'line',{x1:X(DSTAR),y1:mt,x2:X(DSTAR),y2:mt+H,stroke:css('--ok'),'stroke-width':1,opacity:.35});
  const line=(arr,c)=>{ let d=''; for(let i=0;i<=MAXDEG;i++){ if(!isFinite(arr[i]))continue; d+=(d?'L':'M')+X(i).toFixed(1)+' '+Y(arr[i]).toFixed(1)+' '; }
    el(svg,'path',{d,fill:'none',stroke:c,'stroke-width':2.4,'stroke-linejoin':'round'}); };
  line(TRAIN,css('--slate')); line(CV,css('--acc'));
  for(let i=0;i<=MAXDEG;i++){ if(isFinite(CV[i])) el(svg,'circle',{cx:X(i),cy:Y(CV[i]),r:i===DSTAR?4.5:2.6,fill:i===DSTAR?css('--ok'):css('--acc')}); }
}
function setStatus(reg){
  const box=document.getElementById('status');
  const M={ under:['var(--slate)', L('Underfit — too rigid','Недонапасване — твърде скован'),
            L('The model is smoother than the data and misses real structure. Increase flexibility.',
              'Моделът е по-гладък от данните и пропуска реална структура. Увеличете гъвкавостта.')],
     opt:['var(--ok)', L('Optimal balance','Оптимален баланс'),
            L('Captures the trend, ignores the noise — this is where the model generalises best on unseen years.',
              'Улавя тренда, пренебрегва шума — тук моделът обобщава най-добре върху невиждани години.')],
     over:['var(--down)', L('Overfit — too flexible','Пренапасване — твърде гъвкав'),
            L('The curve bends to hit points it will not predict next year. Training error keeps falling, but cross-validated error rises.',
              'Кривата се извива към точки, които няма да предскаже догодина. Грешката при обучение пада, но крос-валидираната се покачва.')] };
  const [c,t,d]=M[reg]; box.style.setProperty('--c',c);
  box.querySelector('.st').textContent=t; box.querySelector('.sd').textContent=d;
}
function fmt(v){ return isFinite(v)? v.toFixed(2):'—'; }
function render(){
  const deg=+document.getElementById('flex').value;
  document.getElementById('degval').textContent=deg;
  const reg=drawChart(deg); drawBV(deg); setStatus(reg);
  document.getElementById('rTrain').textContent=fmt(TRAIN[deg]);
  document.getElementById('rCV').textContent=fmt(CV[deg]);
  document.getElementById('rStar').textContent=L('degree ','степен ')+DSTAR;
}
function applyLangOptions(){
  for(const o of document.getElementById('country').options) o.textContent = isBg()? o.dataset.bg : o.dataset.en;
}
document.getElementById('country').addEventListener('change', e=>{ prep(e.target.value); document.getElementById('flex').value=DSTAR; render(); });
document.getElementById('flex').addEventListener('input', render);
new MutationObserver(()=>{ applyLangOptions(); render(); }).observe(document.documentElement,{attributes:true,attributeFilter:['data-lang']});
prep('CZ'); document.getElementById('flex').value=DSTAR; applyLangOptions(); render();
</script>"""

HTML = (f'<!doctype html><html lang="bg" data-lang="bg"><head><meta charset="utf-8">'
        f'<meta name="viewport" content="width=device-width, initial-scale=1">'
        f'<title>Model flexibility — bias–variance tradeoff</title>'
        f'<style>{CSS}{lang_css()}</style></head><body>{lang_toggle()}'
        f'<div class="wrap">{CHROME}</div>{JS.replace("__DATA__", DATA_JSON)}'
        f'</body></html>')

(OUT / "flexibility.html").write_text(HTML, encoding="utf-8")
print(f"wrote outputs/flexibility.html  ({len(DATA)} HLY series, DE n={len(DATA['DE'])})")
