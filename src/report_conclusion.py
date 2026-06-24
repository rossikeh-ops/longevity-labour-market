# -*- coding: utf-8 -*-
"""
Build outputs/conclusion.html — the synthesis / "so what" page: the headline
answer, key findings, the three policy levers infographic, honest limitations,
and links into the detailed reports and guided stories. Earthy theme, static.
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
M = 1e6
WEST = ["DE", "FR", "CH", "NO"]
EAST = ["PL", "RO", "CZ", "BG"]
NAME = {"BG": "Bulgaria", "PL": "Poland", "CZ": "Czechia", "RO": "Romania",
        "DE": "Germany", "FR": "France", "NO": "Norway", "CH": "Switzerland"}

bf = pd.read_csv(OUT / "balance_forecast.csv")
so = pd.read_csv(OUT / "supply_observed.csv")
sf = pd.read_csv(OUT / "supply_forecast.csv")
df = pd.read_csv(OUT / "demand_forecast.csv")

b35 = bf[bf.year == 2035]
net = round(b35["balance"].sum() / M)
west_def = round(b35[b35.country.isin(WEST)]["balance"].sum() / M)
east_sur = round(b35[b35.country.isin(EAST)]["balance"].sum() / M)
by = (b35.groupby("country")["balance"].sum() / M)
worst, best = by.idxmin(), by.idxmax()
sup24 = round(so[so.year == 2024]["supply_realized"].sum() / M)
sup35 = round(sf[sf.year == 2035]["supply_realized"].sum() / M)
dem24 = round(so[so.year == 2024]["demand"].sum() / M)
dem35 = round(df[df.year == 2035]["demand"].sum() / M)
sup_chg = round((sup35 / sup24 - 1) * 100, 1)
dem_chg = round((dem35 / dem24 - 1) * 100, 1)

INFOGRAPHIC = """
<svg viewBox="0 0 960 384" width="100%" style="display:block;margin:6px 0 10px;font-family:inherit" xmlns="http://www.w3.org/2000/svg">
  <path d="M480,184 V342" fill="none" stroke="#475569" stroke-width="2.5"/>
  <path d="M334,236 H442 Q464,236 464,258 V342" fill="none" stroke="#15803D" stroke-width="2.5"/>
  <path d="M626,236 H518 Q496,236 496,258 V342" fill="none" stroke="#D97706" stroke-width="2.5"/>
  <circle cx="480" cy="342" r="4" fill="#292524"/>
  <text x="480" y="368" text-anchor="middle" font-size="13" fill="#78716C">Balanced labour market · 2035</text>
  <circle cx="480" cy="150" r="33" fill="#FFFFFF" stroke="#475569" stroke-width="2.5"/>
  <g transform="translate(480,150)" stroke="#475569" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round">
    <line x1="0" y1="-17" x2="0" y2="-12"/><circle cx="0" cy="-18" r="1.7" fill="#475569" stroke="none"/>
    <rect x="-10" y="-12" width="20" height="16" rx="3"/>
    <circle cx="-4" cy="-4" r="1.7" fill="#475569" stroke="none"/><circle cx="4" cy="-4" r="1.7" fill="#475569" stroke="none"/>
    <line x1="-10" y1="4" x2="-14" y2="9"/><line x1="10" y1="4" x2="14" y2="9"/>
  </g>
  <text x="480" y="52" text-anchor="middle" font-size="16" font-weight="700" fill="#475569">Decrease Labour Demand</text>
  <text x="480" y="73" text-anchor="middle" font-size="13" fill="#78716C">Invest in automation &amp; technology to</text>
  <text x="480" y="89" text-anchor="middle" font-size="13" fill="#78716C">reduce the need for human labour.</text>
  <circle cx="300" cy="236" r="33" fill="#FFFFFF" stroke="#15803D" stroke-width="2.5"/>
  <g transform="translate(300,236)" stroke="#15803D" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="-7" cy="-5" r="3.4"/><path d="M-13,8 a6 6 0 0 1 12 0"/>
    <circle cx="7" cy="-5" r="3.4"/><path d="M1,8 a6 6 0 0 1 12 0"/>
  </g>
  <text x="256" y="220" text-anchor="end" font-size="16" font-weight="700" fill="#15803D">Increase Labour Supply</text>
  <text x="256" y="241" text-anchor="end" font-size="13" fill="#78716C">Encourage participation, retention</text>
  <text x="256" y="257" text-anchor="end" font-size="13" fill="#78716C">&amp; migration to boost the workforce.</text>
  <circle cx="660" cy="236" r="33" fill="#FFFFFF" stroke="#D97706" stroke-width="2.5"/>
  <g transform="translate(660,236)" stroke="#D97706" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round">
    <path d="M-13,-3 L0,-9 L13,-3 L0,3 Z"/><path d="M0,3 V11"/><path d="M8,-0.5 V7 a8 3 0 0 1 -16 0 V-0.5"/>
  </g>
  <text x="704" y="220" text-anchor="start" font-size="16" font-weight="700" fill="#D97706">Maintain Balance</text>
  <text x="704" y="241" text-anchor="start" font-size="13" fill="#78716C">Focus on education &amp; training to</text>
  <text x="704" y="257" text-anchor="start" font-size="13" fill="#78716C">align skills with market needs.</text>
</svg>"""

CSS = """
:root{--bg:#FAFAF9;--card:#FFFFFF;--ink:#292524;--mut:#78716C;--line:#E7E5E4;--acc:#166534;
--up:#15803D;--down:#B91C1C;--slate:#475569;--mustard:#D97706;}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font:16px/1.6 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;padding:36px 24px}
.wrap{max-width:980px;margin:0 auto}
h1{font-size:28px;margin:0 0 6px}h2{font-size:20px;margin:34px 0 12px;border-bottom:1px solid var(--line);padding-bottom:6px}
.sub{color:var(--mut);margin:0 0 8px;max-width:780px}
.hero{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--acc);
border-radius:14px;padding:20px 22px;margin:18px 0;font-size:17px}
.kpis{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:18px 0}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px}
.kpi .v{font-size:23px;font-weight:700}.kpi .l{color:var(--mut);font-size:12px;margin-top:4px}
.cards{display:grid;grid-template-columns:repeat(2,1fr);gap:16px}
.find{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px 18px}
.find h3{margin:0 0 4px;font-size:16px}.find p{margin:0;color:var(--mut);font-size:14px}
.find .t{font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:.6px}
.lever{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-top:10px}
.lv{background:var(--card);border:1px solid var(--line);border-top:3px solid var(--c);border-radius:12px;padding:14px 16px}
.lv h3{margin:0 0 4px;font-size:15px;color:var(--c)}.lv p{margin:0;color:var(--mut);font-size:13.5px}
.note{color:var(--mut);font-size:14px;background:var(--card);border:1px solid var(--line);
border-radius:10px;padding:15px;margin-top:12px}.note b{color:var(--ink)}
a{color:var(--acc)}.links{display:flex;gap:12px;flex-wrap:wrap;margin-top:10px}
.links a{background:var(--card);border:1px solid var(--line);border-radius:20px;padding:8px 15px;
text-decoration:none;font-size:14px;font-weight:600}.links a:hover{border-color:var(--acc)}
.foot{color:var(--mut);font-size:13px;margin-top:30px}code{color:var(--acc)}
"""

netcol = "var(--up)" if net >= 0 else "var(--down)"
HTML = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Conclusion — balancing longevity &amp; the labour market by 2035</title>
<style>{CSS}</style></head><body><div class="wrap">
<h1>Conclusion — can Europe balance its labour market by 2035?</h1>
<p class="sub">The synthesis: what the person-year engine projects for 8 countries, and the levers that
close the gap. Supply = healthy working-age people × working life; demand = jobs × required service;
balance = the difference, in human-working-years.</p>

<div class="hero"><b>Short answer: roughly, in aggregate — but not where it's needed.</b> Total supply and
demand both stay near {sup35:,}M and {dem35:,}M human-working-years to 2035 (a net balance of
<b style="color:{netcol}">{net:+,}M</b>). That near-equilibrium hides a sharp <b>East–West divide</b>:
the West/EFTA runs a shortage of <b style="color:var(--down)">{west_def:+,}M</b> while the East holds a
surplus of <b style="color:var(--up)">{east_sur:+,}M</b>. The balancing problem is <b>geographic</b>, not
a Europe-wide shortfall.</div>

<div class="kpis">
<div class="kpi"><div class="v" style="color:{netcol}">{net:+,}M</div><div class="l">Net balance 2035 (human-working-years)</div></div>
<div class="kpi"><div class="v" style="color:var(--down)">{west_def:+,}M</div><div class="l">West/EFTA shortage — deepest in {NAME[worst]}</div></div>
<div class="kpi"><div class="v" style="color:var(--up)">{east_sur:+,}M</div><div class="l">East surplus — largest in {NAME[best]}</div></div>
</div>

<h2>What the forecasts say</h2>
<div class="cards">
<div class="find"><div class="t" style="color:var(--acc)">The headline</div>
<h3>A balanced total, an unbalanced map</h3>
<p>Net supply ≈ demand for the 8 countries combined, but {NAME[best]}'s reserve roughly offsets
{NAME[worst]}'s, France's and Switzerland's shortfalls — the demographic basis of West-bound migration.</p></div>
<div class="find"><div class="t" style="color:var(--acc)">Supply</div>
<h3>The longevity dividend holds the line</h3>
<p>Working-age populations shrink, yet supply is near-flat ({sup24:,}→{sup35:,}M, {sup_chg:+.1f}%): healthier,
longer working lives and rising participation offset the loss. It is the supply lever already in motion.</p></div>
<div class="find"><div class="t" style="color:var(--acc)">Demand</div>
<h3>Broadly flat, ageing-tilted</h3>
<p>Jobs × required service stays close to {dem24:,}→{dem35:,}M ({dem_chg:+.1f}%). Demand doesn't run away;
the imbalance comes from where the working-age people are, not from an explosion in labour needs.</p></div>
<div class="find"><div class="t" style="color:var(--acc)">Honesty</div>
<h3>The balance is a direction, not a point</h3>
<p>It is a small difference of two large forecasts, so its relative error is amplified. Read it as a
<b>structural East-surplus / West-shortage signal with wide bands</b> — validated by a leakage-safe backtest.</p></div>
</div>

<h2>Three levers to close the gap</h2>
<p class="sub">The same arithmetic that creates the imbalance points to what moves it. Each lever maps to a term
in the supply–demand identity.</p>
{INFOGRAPHIC}
<div class="lever">
<div class="lv" style="--c:var(--up)"><h3>Increase supply</h3><p>Raise participation (esp. women &amp; older
workers), retain healthy 55–70s, and use net migration — the fastest dials, and where the East's surplus sits.</p></div>
<div class="lv" style="--c:var(--slate)"><h3>Ease demand</h3><p>Automation and productivity lower the human
hours each job needs — the slow, structural lever that reduces required labour rather than adding workers.</p></div>
<div class="lv" style="--c:var(--mustard)"><h3>Maintain balance</h3><p>Education, training and retirement-age /
service-length policy align skills and careers with need — and convert a geographic surplus into usable supply.</p></div>
</div>

<h2>Honest limitations</h2>
<div class="note">
• Forecasts run to <b>2035</b> — a policy baseline, shorter than a full pension/ageing horizon.<br>
• <b>Supply is a potential ceiling</b> (net of health and working-life length, before skills mismatch and frictions).<br>
• <b>Healthy-life years</b> (HLY) and <b>vacancies</b> are the weak drivers — both near-random-walk; modelled honestly at their accuracy ceiling.<br>
• Population is Eurostat's own projection (<code>proj_23np</code>), calibrated to 2024; migration is the biggest swing factor.<br>
• Levels 4–5 (health-cost and retirement-dividend) are descriptive relationships, not causal mechanisms.</div>

<h2>Go deeper</h2>
<div class="links">
<a href="supply_story.html">🎞️ Supply story</a>
<a href="demand_story.html">🎬 Demand story</a>
<a href="level3_balance_report.html">⚖️ Balance report</a>
<a href="level1_supply_report.html">📈 Supply</a>
<a href="level2_demand_report.html">📊 Demand</a>
<a href="model_validation_report.html">🔍 Model trust</a>
<a href="methodology_report.html">🧭 Methodology</a>
</div>
<p class="foot"><a href="../index.html">← Back to overview</a> · Generated from outputs/balance_forecast.csv · src/report_conclusion.py</p>
</div></body></html>"""

(OUT / "conclusion.html").write_text(HTML, encoding="utf-8")
print(f"wrote outputs/conclusion.html  net {net:+}M (West {west_def:+}M, East {east_sur:+}M)")
