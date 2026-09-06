# -*- coding: utf-8 -*-
"""
Build outputs/model.html — "The model": how it works (methodology), the interactive
playground, and trust & critique, collected on ONE page with a sub-tab switcher
(same pattern as the Market page). Earthy, bilingual; each tab loads its page in a
same-origin, auto-sized iframe (the embedded nav/toggle hide themselves).
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from i18n import lang_css, lang_toggle, T  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "outputs"

SECTIONS = [
    ("methodology_report.html", "How it works", "Как работи",
     "the 5-model ensemble engine — deliberately no neural networks",
     "ансамбловият двигател от 5 модела — умишлено без невронни мрежи"),
    ("playground.html", "Playground", "Лаборатория",
     "drag the ensemble band and the flexibility / bias–variance tradeoff, live",
     "плъзгайте лентата на ансамбъла и компромиса гъвкавост / дисперсия, на живо"),
    ("critique.html", "Trust &amp; critique", "Доверие и критика",
     "rolling-origin validation, bootstrap CIs, CRPS, and the honest self-audit",
     "валидация с плъзгащ произход, бутстрап интервали, CRPS и честен самоодит"),
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
iframe.embed{width:100%;height:1000px;border:1px solid var(--line);border-radius:14px;background:#fff;display:block;margin-top:6px}
.foot{color:var(--mut);font-size:13px;margin-top:24px;border-top:1px solid var(--line);padding-top:14px}a{color:var(--acc)}
"""

JS = """<script>
(function(){
  var F=document.getElementById('mframe');
  function fit(){try{var h=F.contentDocument.body.scrollHeight;if(h>140)F.style.height=h+'px';}catch(e){}}
  function prep(){try{var t=F.contentDocument.getElementById('langtoggle');if(t)t.style.display='none';}catch(e){}fit();}
  F.addEventListener('load',function(){prep();[300,800,1600].forEach(function(d){setTimeout(fit,d);});});
  window.addEventListener('resize',fit);
  document.querySelectorAll('.tab').forEach(function(b){b.addEventListener('click',function(){
    document.querySelectorAll('.tab').forEach(function(x){x.classList.remove('on');}); b.classList.add('on');
    document.querySelectorAll('.subx').forEach(function(p){p.hidden = p.getAttribute('data-for')!==b.dataset.src;});
    F.src=b.dataset.src;
  });});
  var tg=document.getElementById('langtoggle');
  if(tg)tg.addEventListener('click',function(){setTimeout(function(){try{F.contentWindow.location.reload();}catch(e){}},50);});
})();
</script>"""

HTML = (f'<!doctype html><html lang="bg" data-lang="bg"><head><meta charset="utf-8">'
        f'<meta name="viewport" content="width=device-width, initial-scale=1">'
        f'<title>The model — how it works, why to trust it</title>'
        f'<style>{CSS}{lang_css()}</style></head><body>{lang_toggle()}<div class="wrap">'
        f'<a class="home" href="../index.html">{T("← Overview", "← Обзор")}</a>'
        f'<h1>{T("The model", "Моделът")}</h1>'
        f'<p class="sub">{T("How it works, made interactive, and put on trial — the method behind the numbers.", "Как работи, направено интерактивно и подложено на изпит — методът зад числата.")}</p>'
        f'<div class="tabs">{TABS}</div>{SUBS}'
        f'<iframe id="mframe" class="embed" src="{SECTIONS[0][0]}" loading="lazy" title="The model"></iframe>'
        f'<p class="foot"><a href="../index.html">{T("← back to overview", "← обратно към обзора")}</a> · src/report_model.py</p>'
        f'</div>{JS}</body></html>')

(OUT / "model.html").write_text(HTML, encoding="utf-8")
print("wrote outputs/model.html  (How it works / Playground / Trust & critique tabs)")
