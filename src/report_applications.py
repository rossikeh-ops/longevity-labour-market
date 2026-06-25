# -*- coding: utf-8 -*-
"""
Build outputs/applications.html — "Practical applications: who uses this, and why
it matters". Static, earthy theme. Each application area links to the level that
supports it; grounded in the EU 2024 Ageing Report and the EU Silver Economy study.
"""
from __future__ import annotations
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "outputs"

# (icon, title, who, what, link, link-label)
AREAS = [
    ("🏛️", "Pensions &amp; retirement policy",
     "Finance &amp; labour ministries, pension regulators, the EU Ageing Working Group, OECD.",
     "Healthy years <i>after</i> retirement (HLY − statutory age) against the headline age show how far retirement "
     "ages can credibly rise and what the <b>effective</b>, not nominal, workforce really is. The what-if sandbox "
     "quantifies the trade-off between later retirement, higher participation and healthier ageing.",
     "level5.html", "Level 5 · the dividend"),
    ("🏥", "Health &amp; long-term-care planning",
     "Health ministries, hospital and social-care planners, regional health authorities.",
     "The poor-health burden <b>Pop × (LE − HLY)</b> projects demand for hospitals, carers and social services — "
     "the line that rises in nearly every EU member state through 2070 in the Ageing Report.",
     "level4.html", "Level 4 · cost of unhealthy years"),
    ("🌍", "Labour &amp; migration policy",
     "Labour ministries, EU mobility &amp; cohesion bodies, regional development agencies.",
     "The sharp <b>East-surplus / West-shortage</b> divide is the demographic basis for labour mobility, targeted "
     "immigration, and participation drives among women and older workers.",
     "level3.html", "Level 3 · the balance"),
    ("📈", "Macro &amp; fiscal sustainability",
     "Treasuries, central banks, independent fiscal councils.",
     "The <b>labour-vs-productivity</b> growth split feeds potential-output and tax-base-versus-spending "
     "projections as the working-age population shrinks — the core tension behind age-related public spending, "
     "already ~24% of EU GDP in 2022.",
     "level6.html", "Level 6 · the macroeconomy"),
    ("💼", "Workforce &amp; actuarial planning",
     "Employers in shortage sectors, pension funds, life and long-term-care insurers.",
     "Price longevity and plan recruitment, retention of older workers and automation against the shrinking "
     "labour supply quantified in the supply and demand levels.",
     "level1.html", "Levels 1–2 · supply &amp; demand"),
    ("🎭", "The “silver economy”",
     "Consumer, tourism, education and wellness businesses; investors.",
     "Healthy, active retirees — the Level 5 dividend — are the market: Europe's silver economy is already "
     "estimated at <b>~€3.7 trillion and ~78 million jobs</b> in leisure, tourism, lifelong learning and wellness.",
     "level5.html", "Level 5 · the dividend"),
]

CARDS = "".join(
    f'<a class="card" href="{lk}"><div class="ic">{ic}</div><h3>{t}</h3>'
    f'<p class="who">{who}</p><p>{what}</p>'
    f'<p class="lk">{ll} →</p></a>'
    for ic, t, who, what, lk, ll in AREAS)

CSS = """
:root{--bg:#FAFAF9;--card:#FFFFFF;--ink:#292524;--mut:#78716C;--line:#E7E5E4;--acc:#166534;}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font:16px/1.6 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;padding:36px 24px}
.wrap{max-width:980px;margin:0 auto}
h1{font-size:28px;margin:0 0 6px}h2{font-size:20px;margin:30px 0 12px;border-bottom:1px solid var(--line);padding-bottom:6px}
.home{color:var(--mut);text-decoration:none;font-size:13px}.home:hover{color:var(--acc)}
.sub{color:var(--mut);margin:6px 0 8px;max-width:800px}
.note{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--acc);border-radius:12px;
padding:18px 20px;margin:18px 0;color:var(--ink)}.note b{color:var(--acc)}
.cards{display:grid;grid-template-columns:repeat(2,1fr);gap:16px;margin-top:6px}
a.card{display:block;background:var(--card);border:1px solid var(--line);border-radius:14px;padding:20px;
text-decoration:none;color:inherit;transition:border-color .15s,transform .15s}
a.card:hover{border-color:var(--acc);transform:translateY(-2px)}
a.card .ic{font-size:24px}a.card h3{margin:8px 0 6px;font-size:17px}
a.card .who{margin:0 0 8px;color:var(--ink);font-size:13px;font-weight:600}
a.card p{margin:0;color:var(--mut);font-size:14px}
a.card .lk{margin-top:12px;color:var(--acc);font-weight:600;font-size:13px}
.foot{color:var(--mut);font-size:13px;margin-top:26px}a{color:var(--acc)}
"""

HTML = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Practical applications — longevity &amp; the labour market</title>
<style>{CSS}</style></head><body><div class="wrap">
<a class="home" href="../index.html">← Overview</a>
<h1>Practical applications — who uses this, and why it matters</h1>
<p class="sub">This analysis is not academic only: each level answers a question a real decision-maker is already
paying to answer. Here is where the person-year engine is used, and why it matters.</p>

<div class="note">Demographic change is slow but decisive. Across the EU, age-related public spending was already
<b>~24% of GDP in 2022</b>, and the old-age dependency ratio (65+ per 100 working-age) is set to climb from
<b>36% to 55% by 2050</b>. Most published projections stop at headcounts and life-expectancy averages — which
can't be weighed against jobs. Turning both into a common unit, <b>human-working-years</b>, lets governments,
planners and businesses see the trade-offs and act while there is still time.</div>

<h2>Where it is used</h2>
<div class="cards">{CARDS}</div>

<p class="foot"><b>Real-world anchors:</b>
<a href="https://economy-finance.ec.europa.eu/publications/2024-ageing-report-economic-and-budgetary-projections-eu-member-states-2022-2070_en">European Commission — 2024 Ageing Report</a> (age-related spending, dependency ratios, pension &amp;
health/long-term-care projections to 2070) ·
<a href="https://digital-strategy.ec.europa.eu/en/library/silver-economy-study-how-stimulate-economy-hundreds-millions-euros-year">European Commission — The Silver Economy study</a> (~€3.7tn, ~78m jobs).</p>
<p class="foot"><a href="../index.html">← Back to overview</a> · src/report_applications.py</p>
</div></body></html>"""

(OUT / "applications.html").write_text(HTML, encoding="utf-8")
print(f"wrote outputs/applications.html ({len(AREAS)} application areas)")
