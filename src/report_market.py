# -*- coding: utf-8 -*-
"""
Build outputs/market.html — "The labour market": Supply, Demand and Balance
(Levels 1–3) collected on ONE page with a sub-tab switcher. Earthy, bilingual.
Each tab loads its level page in a same-origin, auto-sized iframe (the embedded
nav/toggle hide themselves), so it reads as one continuous canvas.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from i18n import lang_css, lang_toggle, T  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "outputs"

SECTIONS = [
    ("level1.html", "Supply", "Предлагане", "healthy working-age people × expected working life", "здрави хора в трудоспособна възраст × очакван трудов живот"),
    ("level2.html", "Demand", "Търсене", "jobs (employed + vacancies) × required service", "работни места (заети + свободни) × изискван стаж"),
    ("level3.html", "Balance", "Баланс", "supply − demand — the East-surplus / West-shortage divide", "предлагане − търсене — разделението излишък-Изток / недостиг-Запад"),
]
TABS = "".join(
    f'<button class="tab{" on" if i == 0 else ""}" data-src="{src}">'
    f'<span lang="en">{en}</span><span lang="bg">{bg}</span></button>'
    for i, (src, en, bg, _, _) in enumerate(SECTIONS))
SUBS = "".join(
    f'<p class="sub subx" data-for="{src}"{"" if i == 0 else " hidden"}>{T(den, dbg)}</p>'
    for i, (src, en, bg, den, dbg) in enumerate(SECTIONS))

CSS = """
:root{--bg:#FAFAF9;--card:#FFFFFF;--ink:#292524;--mut:#78716C;--line:#E7E5E4;--acc:#166534;}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font:16px/1.6 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;padding:32px 22px}
.wrap{max-width:1000px;margin:0 auto}
.home{color:var(--mut);text-decoration:none;font-size:13px}.home:hover{color:var(--acc)}
h1{font-size:27px;margin:8px 0 4px}.sub{color:var(--mut);max-width:760px;margin:0 0 10px}
.tabs{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0 6px;position:sticky;top:0;
background:rgba(250,250,249,.92);backdrop-filter:blur(6px);padding:8px 0;z-index:50}
.tab{border:1px solid var(--line);background:#fff;color:var(--ink);border-radius:20px;
padding:9px 20px;font:700 15px/1 inherit;cursor:pointer}
.tab:hover{border-color:var(--acc)}
.tab.on{background:var(--acc);color:#fff;border-color:var(--acc)}
iframe.embed{width:100%;height:900px;border:1px solid var(--line);border-radius:14px;background:#fff;display:block;margin-top:6px}
.foot{color:var(--mut);font-size:13px;margin-top:24px;border-top:1px solid var(--line);padding-top:14px}a{color:var(--acc)}
"""

JS = """<script>
(function(){
  var F=document.getElementById('mframe');
  function fit(){try{var h=F.contentDocument.body.scrollHeight;if(h>140)F.style.height=h+'px';}catch(e){}}
  function prep(){try{var t=F.contentDocument.getElementById('langtoggle');if(t)t.style.display='none';}catch(e){}fit();}
  F.addEventListener('load',function(){prep();[300,800,1600].forEach(function(d){setTimeout(fit,d);});});
  window.addEventListener('resize',fit);
  function go(src){ // setting iframe.src does not re-navigate an already-loaded frame; use location.replace
    try{ if(F.contentWindow && F.contentWindow.location){ F.contentWindow.location.replace(src); return; } }catch(e){}
    F.src=src;
  }
  document.querySelectorAll('.tab').forEach(function(b){b.addEventListener('click',function(){
    document.querySelectorAll('.tab').forEach(function(x){x.classList.remove('on');}); b.classList.add('on');
    document.querySelectorAll('.subx').forEach(function(p){p.hidden = p.getAttribute('data-for')!==b.dataset.src;});
    go(b.dataset.src);
  });});
  var tg=document.getElementById('langtoggle');
  if(tg)tg.addEventListener('click',function(){setTimeout(function(){try{F.contentWindow.location.reload();}catch(e){}},50);});
})();
</script>"""

HTML = (f'<!doctype html><html lang="bg" data-lang="bg"><head><meta charset="utf-8">'
        f'<meta name="viewport" content="width=device-width, initial-scale=1">'
        f'<title>The labour market — supply, demand &amp; balance</title>'
        f'<style>{CSS}{lang_css()}</style></head><body>{lang_toggle()}<div class="wrap">'
        f'<a class="home" href="../index.html">{T("← Overview", "← Обзор")}</a>'
        f'<h1>{T("The labour market", "Пазарът на труда")}</h1>'
        f'<p class="sub">{T("Supply, demand and their balance — in human-working-years, to 2033.", "Предлагане, търсене и техният баланс — в човеко-работни години, до 2033 г.")}</p>'
        f'<div class="tabs">{TABS}</div>{SUBS}'
        f'<iframe id="mframe" class="embed" src="{SECTIONS[0][0]}" loading="lazy" title="Market"></iframe>'
        f'<p class="foot"><a href="../index.html">{T("← back to overview", "← обратно към обзора")}</a> · src/report_market.py</p>'
        f'</div>{JS}</body></html>')

(OUT / "market.html").write_text(HTML, encoding="utf-8")
print("wrote outputs/market.html  (Supply / Demand / Balance tabs)")
