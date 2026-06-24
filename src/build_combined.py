# -*- coding: utf-8 -*-
"""
Merge each level's guided presentation and full report into ONE page.

Every story (Chart.js deck) and report (static SVG) is already a self-contained
HTML document with its own theme vars, D3/Chart.js and global key handlers, so we
merge them the robust way: a single per-level page with a tab switcher over two
ISOLATED iframes (no CSS/JS collisions, both fully interactive). Deep-linkable via
#story / #report.

Writes outputs/level{1..6}.html
"""
from __future__ import annotations
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "outputs"

# (n, title, tagline, story_file_or_None, report_file)
LEVELS = [
    (1, "Labour supply", "Healthy working-age people × working life — the longevity dividend in person-years.",
     "supply_story.html", "level1_supply_report.html"),
    (2, "Labour demand", "(Employed + vacancies) × required service — the career-years jobs require.",
     "demand_story.html", "level2_demand_report.html"),
    (3, "Labour-market balance", "Supply − demand in human-working-years — the East-surplus / West-shortage divide.",
     "balance_story.html", "level3_balance_report.html"),
    (4, "Cost of unhealthy years", "Poor-health person-years (Pop × (LE − HLY)) and whether they drive health-sector cost.",
     "cost_story.html", "level4_cost_report.html"),
    (5, "Healthy retirement dividend", "Healthy years after retirement (HLY − retirement age) and whether they fund leisure.",
     "dividend_story.html", "level5_dividend_report.html"),
    (6, "Longevity in the macroeconomy", "Growth accounting: real GDP to 2033 split into labour and productivity channels.",
     None, "level6_macro_report.html"),
]

PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Level {n} — {title}</title>
<style>
:root{{--bg:#FAFAF9;--card:#FFFFFF;--ink:#292524;--mut:#78716C;--line:#E7E5E4;--acc:#166534;}}
*{{box-sizing:border-box}}html,body{{margin:0;height:100%}}
body{{display:flex;flex-direction:column;height:100vh;background:var(--bg);color:var(--ink);
font:15px/1.5 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif}}
header{{flex:0 0 auto;padding:12px 22px;border-bottom:1px solid var(--line);background:var(--card);
display:flex;align-items:center;gap:18px;flex-wrap:wrap}}
.home{{color:var(--mut);text-decoration:none;font-size:13px;white-space:nowrap}}.home:hover{{color:var(--acc)}}
.tt{{display:flex;flex-direction:column;min-width:0}}
.tt h1{{font-size:16px;margin:0;font-weight:650}}.tt .sub{{color:var(--mut);font-size:12px;
overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:60ch}}
.spacer{{flex:1}}
.tabs{{display:inline-flex;background:var(--bg);border:1px solid var(--line);border-radius:10px;padding:3px;gap:2px}}
.tab{{appearance:none;border:none;background:transparent;color:var(--mut);font-size:13.5px;font-weight:600;
padding:7px 15px;border-radius:8px;cursor:pointer;display:flex;align-items:center;gap:7px}}
.tab.active{{background:var(--acc);color:#fff}}
.tab:not(.active):hover{{color:var(--ink)}}
.pop{{color:var(--mut);text-decoration:none;font-size:12.5px;white-space:nowrap}}.pop:hover{{color:var(--acc)}}
iframe{{flex:1 1 auto;width:100%;border:none;background:var(--bg)}}
</style></head><body>
<header>
  <a class="home" href="../index.html">← Overview</a>
  <div class="tt"><h1>Level {n} — {title}</h1><span class="sub">{tagline}</span></div>
  <span class="spacer"></span>
  <div class="tabs">{tabs}</div>
  <a class="pop" id="pop" href="{default}" target="_blank" rel="noopener">open ↗</a>
</header>
<iframe id="view" src="{default}" title="Level {n} content"></iframe>
<script>
const VIEW=document.getElementById('view'),POP=document.getElementById('pop'),TABS=[...document.querySelectorAll('.tab')];
function show(key){{
  const t=TABS.find(x=>x.dataset.key===key)||TABS[0];
  TABS.forEach(x=>x.classList.toggle('active',x===t));
  const src=t.dataset.src;
  if(VIEW.getAttribute('src')!==src){{VIEW.src=src;}}
  POP.href=src;
  if(location.hash.slice(1)!==t.dataset.key) history.replaceState(null,'','#'+t.dataset.key);
}}
TABS.forEach(t=>t.onclick=()=>show(t.dataset.key));
show(location.hash.slice(1)||TABS[0].dataset.key);
</script>
</body></html>"""


def build():
    for n, title, tagline, story, report in LEVELS:
        tabs = []
        if story:
            tabs.append(f'<button class="tab" data-key="story" data-src="{story}">▶ Guided story</button>')
        tabs.append(f'<button class="tab" data-key="report" data-src="{report}">📄 Full report</button>')
        default = story or report
        html = PAGE.format(n=n, title=title, tagline=tagline,
                           tabs="".join(tabs), default=default)
        (OUT / f"level{n}.html").write_text(html, encoding="utf-8")
        print(f"wrote outputs/level{n}.html  ({'story+report' if story else 'report only'})")


if __name__ == "__main__":
    build()
