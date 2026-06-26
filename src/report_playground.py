# -*- coding: utf-8 -*-
"""
Build outputs/playground.html — "Model playground": the two interactive method
widgets (ensemble uncertainty + flexibility / bias-variance) on ONE page, so the
talk has a single hands-on stop. Earthy, bilingual. Embeds the existing widgets
via same-origin, auto-sized iframes — their CSS/JS stay isolated and never drift,
and the page scrolls as one continuous canvas (no nested scrollbars).
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from i18n import lang_css, lang_toggle, T  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "outputs"

SECTIONS = [
    ("band", "ensemble_visualizer.html", "Ensemble uncertainty", "Несигурност на ансамбъла",
     "Drag the <b>ensemble size</b> and <b>sampling noise</b> — watch a cloud of simple models form the uncertainty band.",
     "Променете <b>размера на ансамбъла</b> и <b>шума</b> — вижте как облак от прости модели формира лентата на несигурност."),
    ("flex", "flexibility.html", "Flexibility &amp; bias–variance", "Гъвкавост и отклонение–дисперсия",
     "Drag one slider from <b>underfit → optimal → overfit</b> on a real Healthy-Life-Years series — the cross-validated optimum is computed live.",
     "Плъзнете един слайдер от <b>недонапасване → оптимум → пренапасване</b> върху реален ред за ЗГЖ — крос-валидираният оптимум се изчислява на живо."),
]
NAV = "".join(f'<a href="#{i}">{T(en, bg)}</a>' for i, _, en, bg, _, _ in SECTIONS)
SECS = "".join(
    f'<section id="{i}"><h2>{T(en, bg)}</h2><p class="sub">{T(den, dbg)}</p>'
    f'<iframe class="embed" src="{src}" loading="lazy" title="{en}"></iframe></section>'
    for i, src, en, bg, den, dbg in SECTIONS)

CSS = """
:root{--bg:#FAFAF9;--card:#FFFFFF;--ink:#292524;--mut:#78716C;--line:#E7E5E4;--acc:#166534;}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font:16px/1.6 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;padding:32px 22px}
.wrap{max-width:1000px;margin:0 auto}
.home{color:var(--mut);text-decoration:none;font-size:13px}.home:hover{color:var(--acc)}
h1{font-size:27px;margin:8px 0 4px}h2{font-size:20px;margin:6px 0 4px}
.sub{color:var(--mut);max-width:760px;margin:0 0 10px}
.jump{position:sticky;top:0;background:rgba(250,250,249,.92);backdrop-filter:blur(6px);
border-bottom:1px solid var(--line);padding:9px 0;margin:10px 0 8px;display:flex;gap:8px;z-index:50}
.jump a{font-size:13px;font-weight:700;color:var(--acc);text-decoration:none;border:1px solid var(--line);
border-radius:18px;padding:6px 13px;background:#fff}.jump a:hover{border-color:var(--acc)}
section{margin:22px 0 8px}
iframe.embed{width:100%;height:820px;border:1px solid var(--line);border-radius:14px;background:#fff;display:block}
.foot{color:var(--mut);font-size:13px;margin-top:24px;border-top:1px solid var(--line);padding-top:14px}a{color:var(--acc)}
"""

JS = """<script>
(function(){
  function frames(){return Array.prototype.slice.call(document.querySelectorAll('iframe.embed'));}
  function fit(f){try{var h=f.contentDocument.body.scrollHeight;if(h>140)f.style.height=h+'px';}catch(e){}}
  function prep(f){try{var t=f.contentDocument.getElementById('langtoggle');if(t)t.style.display='none';}catch(e){}fit(f);}
  function hook(f){f.addEventListener('load',function(){prep(f);[300,800,1600].forEach(function(d){setTimeout(function(){fit(f);},d);});});}
  document.addEventListener('DOMContentLoaded',function(){frames().forEach(hook);});
  window.addEventListener('load',function(){frames().forEach(prep);});
  window.addEventListener('resize',function(){frames().forEach(fit);});
  var tg=document.getElementById('langtoggle');
  if(tg)tg.addEventListener('click',function(){setTimeout(function(){frames().forEach(function(f){try{f.contentWindow.location.reload();}catch(e){}});},50);});
})();
</script>"""

HTML = (f'<!doctype html><html lang="bg" data-lang="bg"><head><meta charset="utf-8">'
        f'<meta name="viewport" content="width=device-width, initial-scale=1">'
        f'<title>Model playground — longevity &amp; the labour market</title>'
        f'<style>{CSS}{lang_css()}</style></head><body>{lang_toggle()}<div class="wrap">'
        f'<a class="home" href="../index.html">{T("← Overview", "← Обзор")}</a>'
        f'<h1>{T("Model playground", "Лаборатория на модела")}</h1>'
        f'<p class="sub">{T("Two interactive toys for the method — uncertainty and flexibility — on one page. Drag, and the model responds live.", "Две интерактивни играчки за метода — несигурност и гъвкавост — на една страница. Плъзгайте и моделът реагира на живо.")}</p>'
        f'<div class="jump">{NAV}</div>{SECS}'
        f'<p class="foot"><a href="../index.html">{T("← back to overview", "← обратно към обзора")}</a> · src/report_playground.py</p>'
        f'</div>{JS}</body></html>')

(OUT / "playground.html").write_text(HTML, encoding="utf-8")
print("wrote outputs/playground.html  (2 embedded widgets)")
