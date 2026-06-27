# -*- coding: utf-8 -*-
"""
inject_nav.py — stamp a shared, Amazon-style top navigation bar onto EVERY page.

The site's pages come from ~20 generators with different structure, so rather than
edit each one we post-process the built HTML: insert one self-contained nav block
(its own CSS + JS, no dependencies) right after <body>. Idempotent (re-running
replaces the old block), path-aware (root vs outputs/ pages), and the nav hides
itself when loaded inside an iframe, so embedded widgets don't get a double bar.

Run AFTER (re)generating pages:  python src/inject_nav.py
"""
from __future__ import annotations
import re
from pathlib import Path

ROOTDIR = Path(__file__).resolve().parents[1]
OUTDIR = ROOTDIR / "outputs"

# links row — in the PRESENTATION running order (the 10-stop talk track), file, en, bg
LINKS = [
    ("introduction.html", "Introduction", "Въведение"),       # 1
    ("level1.html", "Supply", "Предлагане"),                   # 2
    ("level2.html", "Demand", "Търсене"),                      # 3
    ("level3.html", "Balance", "Баланс"),                      # 4
    ("level4.html", "Open horizons", "Хоризонти"),             # 5
    ("implications.html", "Implications", "Последици"),        # 6
    ("methodology_report.html", "Methodology", "Методология"), # 7
    ("playground.html", "Playground", "Лаборатория"),          # 8
    ("critique.html", "Trust", "Доверие"),                     # 9
    ("whatif.html", "What-if", "Какво-ако"),                   # 10
    ("script.html", "Run-sheet", "Сценарий"),                  # the spoken script
]
# fuller list for the search index (LINKS + pages not on the menu row)
SEARCH = LINKS + [
    ("level5.html", "Dividend (L5)", "Дивидент (Н5)"),
    ("level6.html", "Macroeconomy (L6)", "Макроикономика (Н6)"),
    ("model_validation_report.html", "Model trust", "Доверие в модела"),
    ("kpis.html", "KPIs", "КПИ"),
    ("flexibility.html", "Flexibility", "Гъвкавост"),
]

CSS = """
<style id="pn-css">
html[data-lang='en'] .pn-wrap [lang='bg']{display:none!important}
html[data-lang='bg'] .pn-wrap [lang='en']{display:none!important}
.pn-wrap *{box-sizing:border-box}
.pn-wrap{position:fixed;top:0;left:0;right:0;z-index:4000;font:14px/1.3 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif}
.pn-r1{display:flex;align-items:center;gap:12px;background:#26221f;color:#fff;padding:8px 14px}
.pn-r2{display:flex;align-items:center;gap:4px;background:#332e29;color:#e7e5e4;padding:5px 12px;overflow-x:auto;white-space:nowrap}
.pn-logo{display:flex;align-items:center;gap:8px;text-decoration:none;flex:none}
.pn-logo img{height:30px;display:block}
.pn-logo b{color:#fff;font-weight:800;font-size:19px;letter-spacing:.5px}
.pn-scope{display:none;align-items:center;gap:5px;color:#d6d3d1;font-size:12px;flex:none}
.pn-scope b{color:#fff;font-weight:700}
@media(min-width:760px){.pn-scope{display:flex}}
.pn-search{flex:1;display:flex;min-width:120px;max-width:760px;margin:0 6px;position:relative}
.pn-search select{border:none;background:#e7e5e4;color:#292524;border-radius:8px 0 0 8px;padding:0 8px;font:inherit;cursor:pointer}
.pn-search input{flex:1;border:none;padding:9px 12px;font:inherit;min-width:60px;border-radius:8px 0 0 8px}
.pn-search button{border:none;background:#D97706;color:#26221f;padding:0 16px;border-radius:0 8px 8px 0;cursor:pointer;font-size:17px}
.pn-search button:hover{background:#ea8a16}
.pn-sug{position:absolute;top:42px;left:0;right:0;background:#fff;color:#292524;border:1px solid #E7E5E4;border-radius:10px;
box-shadow:0 8px 24px rgba(0,0,0,.18);overflow:hidden;display:none;z-index:5}
.pn-sug a{display:block;padding:9px 14px;text-decoration:none;color:#292524;font-size:14px}
.pn-sug a:hover,.pn-sug a.on{background:#F0F5F1;color:#166534}
.pn-lang{flex:none;background:transparent;border:1px solid #57534e;color:#fff;border-radius:18px;padding:6px 13px;
cursor:pointer;font:700 13px/1 inherit}.pn-lang:hover{border-color:#D97706}
.pn-link{color:#e7e5e4;text-decoration:none;padding:5px 9px;border-radius:7px;font-size:13.5px;font-weight:600;flex:none}
.pn-link:hover{background:#4b443d;color:#fff}
.pn-burger{flex:none;color:#fff;font-weight:700;display:flex;align-items:center;gap:6px;padding:5px 8px}
.langtoggle{display:none!important}
</style>"""

JS = """
<script>
(function(){
  if(window.top!==window.self){var n=document.getElementById('pn');if(n)n.remove();return;}/* hide inside iframes */
  var root=document.documentElement;
  var L=localStorage.getItem('site-lang')||'bg';root.dataset.lang=L;
  var PAGES=__PAGES__;
  var box=document.getElementById('pn');
  var inp=document.getElementById('pn-q'), sug=document.getElementById('pn-sug'), lang=document.getElementById('pn-lang');
  function isBg(){return root.dataset.lang==='bg';}
  function setLang(){lang.textContent=isBg()?'EN':'БГ';inp.placeholder=isBg()?'Търсене в анализа…':'Search the analysis…';}
  lang.addEventListener('click',function(){var nx=isBg()?'en':'bg';root.dataset.lang=nx;localStorage.setItem('site-lang',nx);setLang();render(inp.value);});
  function matches(q){q=(q||'').toLowerCase().trim();return PAGES.filter(function(p){return !q||(isBg()?p.bg:p.en).toLowerCase().indexOf(q)>=0;});}
  function render(q){var m=matches(q);if(!q||!m.length){sug.style.display='none';return;}
    sug.innerHTML=m.slice(0,8).map(function(p,i){return '<a href="'+p.u+'"'+(i===0?' class="on"':'')+'>'+(isBg()?p.bg:p.en)+'</a>';}).join('');
    sug.style.display='block';}
  inp.addEventListener('input',function(){render(inp.value);});
  inp.addEventListener('focus',function(){render(inp.value);});
  inp.addEventListener('keydown',function(e){if(e.key==='Enter'){var m=matches(inp.value);if(m.length){location.href=m[0].u;}}});
  document.addEventListener('click',function(e){if(!box.contains(e.target))sug.style.display='none';});
  function offset(){document.body.style.paddingTop=(box.offsetHeight+10)+'px';}
  setLang();offset();window.addEventListener('resize',offset);setTimeout(offset,300);
})();
</script>"""


def nav_block(root_pre, out_pre):
    home = root_pre + "index.html"
    pages = ",".join(
        '{u:"%s",en:"%s",bg:"%s"}' % (out_pre + f, en.replace("&amp;", "&"), bg)
        for f, en, bg in SEARCH)
    links = "".join(
        '<a class="pn-link" href="%s"><span lang="en">%s</span><span lang="bg">%s</span></a>'
        % (out_pre + f, en, bg) for f, en, bg in LINKS)
    html = f"""<!--PN-START-->{CSS}
<div class="pn-wrap" id="pn">
 <div class="pn-r1">
  <a class="pn-logo" href="{home}"><img src="{out_pre}logo_primus_mark.svg" alt="Primus"><b>PRIMUS</b></a>
  <span class="pn-scope">📍 <b>8</b>&nbsp;<span lang="en">countries</span><span lang="bg">държави</span>&nbsp;·&nbsp;→ 2033</span>
  <div class="pn-search">
   <input id="pn-q" type="text" autocomplete="off" placeholder="Search…">
   <button id="pn-go" aria-label="search" onclick="var q=document.getElementById('pn-q');q.dispatchEvent(new KeyboardEvent('keydown',{{key:'Enter'}}));">🔍</button>
   <div class="pn-sug" id="pn-sug"></div>
  </div>
  <button class="pn-lang" id="pn-lang" aria-label="switch language">БГ</button>
 </div>
 <div class="pn-r2">
  <a class="pn-link" href="{home}"><span lang="en">Home</span><span lang="bg">Начало</span></a>
  {links}
 </div>
</div>
{JS.replace("__PAGES__", "[" + pages + "]")}
<!--PN-END-->"""
    return html


PN_RE = re.compile(r"<!--PN-START-->.*?<!--PN-END-->\s*", re.DOTALL)
BODY_RE = re.compile(r"(<body[^>]*>)", re.IGNORECASE)


def stamp(path: Path, root_pre: str, out_pre: str):
    html = path.read_text(encoding="utf-8")
    html = PN_RE.sub("", html)                       # remove any previous nav (idempotent)
    block = nav_block(root_pre, out_pre)
    if not BODY_RE.search(html):
        return False
    html = BODY_RE.sub(lambda m: m.group(1) + "\n" + block, html, count=1)
    path.write_text(html, encoding="utf-8")
    return True


n = 0
if stamp(ROOTDIR / "index.html", "", "outputs/"):
    n += 1
for p in sorted(OUTDIR.glob("*.html")):
    if stamp(p, "../", ""):
        n += 1
print(f"injected Primus nav into {n} pages")
