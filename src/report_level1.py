"""
Level 1 — Labour Supply report. Static SVG, no client-side JS.
Potential supply = health-adjusted working-age people × expected working life,
in human-working-years; observed 2011-2024 + forecast to 2035.
Reads outputs/{supply_observed,supply_forecast}.csv -> outputs/level1_supply_report.html
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
M = 1e6
NAME = {"BG": "Bulgaria", "PL": "Poland", "CZ": "Czechia", "RO": "Romania",
        "DE": "Germany", "FR": "France", "NO": "Norway", "CH": "Switzerland"}
REGION = {"BG": "East·EU", "PL": "East·EU", "CZ": "East·EU", "RO": "East·EU",
          "DE": "West·EU", "FR": "West·EU", "NO": "EFTA", "CH": "EFTA"}

obs = pd.read_csv(OUT / "supply_observed.csv")
sf = pd.read_csv(OUT / "supply_forecast.csv")

countries = list((sf[sf.year == 2035].groupby("country").supply_realized.sum() / M)
                 .pipe(lambda s: (s / (obs[obs.year == 2024].groupby("country").supply_realized.sum() / M) - 1))
                 .sort_values().index)        # biggest decline -> biggest growth
series = {}
for c in countries:
    o = (obs[obs.country == c].groupby("year")["supply_realized"].sum() / M)
    o = o[o.index <= 2024]
    f = sf[sf.country == c].groupby("year").agg(
        m=("supply_realized", "sum"), lo=("lo", "sum"), hi=("hi", "sum")) / M
    series[c] = {
        "name": NAME[c], "region": REGION[c],
        "oy": [int(y) for y in o.index], "ov": [round(v, 1) for v in o.values],
        "fy": [int(y) for y in f.index],
        "fm": [round(v, 1) for v in f["m"].values],
        "lo": [round(v, 1) for v in f["lo"].values],
        "hi": [round(v, 1) for v in f["hi"].values],
        "s2024": round(float(o.loc[2024])),
        "s2035": round(float(f["m"].loc[2035])),
        "chg": round((f["m"].loc[2035] / o.loc[2024] - 1) * 100, 1),
    }

o24 = obs[obs.year == 2024]
tot24 = round(float(o24["supply_realized"].sum() / M))
ceil24 = round(float(o24["supply_ceiling"].sum() / M))
tot35 = round(float(sf[sf.year == 2035]["supply_realized"].sum() / M))
totchg = round((tot35 / tot24 - 1) * 100, 1)
realiz = round(float(o24["realization_ratio"].mean()), 2)
unused = round((1 - tot24 / ceil24) * 100)
totcol = "#f87171" if totchg < 0 else "#34d399"

W, H, PLm, PRm, PTm, PBm = 470, 200, 46, 12, 12, 26


def chart_svg(s):
    oy, ov, fy, fm, lo, hi = s["oy"], s["ov"], s["fy"], s["fm"], s["lo"], s["hi"]
    allv = ov + hi + lo
    x0, x1 = min(oy + fy), max(oy + fy)
    y0, y1 = min(allv) * 0.96, max(allv) * 1.04
    X = lambda v: PLm + (v - x0) / (x1 - x0) * (W - PLm - PRm)
    Y = lambda v: H - PBm - (v - y0) / (y1 - y0) * (H - PTm - PBm)
    g = []
    for yr in range(x0, x1 + 1, 4):
        g.append(f'<text x="{X(yr):.1f}" y="{H-9}" fill="#94a3b8" font-size="10" text-anchor="middle">{yr}</text>')
    for k in range(3):
        v = y0 + (y1 - y0) * k / 2
        g.append(f'<line x1="{PLm}" y1="{Y(v):.1f}" x2="{W-PRm}" y2="{Y(v):.1f}" stroke="#2a3445" stroke-width="0.7" opacity="0.5"/>')
        g.append(f'<text x="{PLm-6}" y="{Y(v)+3:.1f}" fill="#94a3b8" font-size="10" text-anchor="end">{round(v)}</text>')
    band = " ".join(f"{X(x):.1f},{Y(hi[i]):.1f}" for i, x in enumerate(fy)) + " " + \
           " ".join(f"{X(x):.1f},{Y(lo[i]):.1f}" for i, x in reversed(list(enumerate(fy))))
    obsp = " ".join(f"{X(x):.1f},{Y(ov[i]):.1f}" for i, x in enumerate(oy))
    fcp = " ".join(f"{X(x):.1f},{Y(fm[i]):.1f}" for i, x in enumerate(fy))
    joinp = f"{X(oy[-1]):.1f},{Y(ov[-1]):.1f} {X(fy[0]):.1f},{Y(fm[0]):.1f}"
    cls = "neg" if s["chg"] < 0 else "pos"
    sign = "+" if s["chg"] > 0 else ""
    return (f'<div class="chart"><div class="hd"><div><span class="t">{s["name"]}</span> '
            f'<span class="r">{s["region"]}</span></div>'
            f'<span class="pill {cls}">{sign}{s["chg"]}%</span></div>'
            f'<svg viewBox="0 0 {W} {H}" width="100%" xmlns="http://www.w3.org/2000/svg">{"".join(g)}'
            f'<polygon points="{band}" fill="rgba(251,191,36,0.16)"/>'
            f'<polyline points="{obsp}" fill="none" stroke="#7dd3fc" stroke-width="2"/>'
            f'<polyline points="{joinp}" fill="none" stroke="#fbbf24" stroke-width="1.5" stroke-dasharray="2 2"/>'
            f'<polyline points="{fcp}" fill="none" stroke="#fbbf24" stroke-width="2"/>'
            f'</svg></div>')


charts_html = "".join(chart_svg(series[c]) for c in countries)
rows_html = "".join(
    f'<tr><td>{series[c]["name"]}</td><td style="color:#94a3b8">{series[c]["region"]}</td>'
    f'<td>{series[c]["s2024"]}</td><td>{series[c]["s2035"]}</td>'
    f'<td style="color:#94a3b8">{round(series[c]["lo"][-1])}–{round(series[c]["hi"][-1])}</td>'
    f'<td class="{"neg" if series[c]["chg"]<0 else "pos"}" style="text-align:right">'
    f'{"+" if series[c]["chg"]>0 else ""}{series[c]["chg"]}%</td></tr>' for c in countries)

CSS = """
:root{--bg:#0f1420;--card:#171e2e;--ink:#e8edf7;--mut:#94a3b8;--line:#2a3445;
--obs:#7dd3fc;--fc:#fbbf24;--band:rgba(251,191,36,.16);--up:#34d399;--down:#f87171;}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font:15px/1.55 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;padding:32px}
.wrap{max-width:1080px;margin:0 auto}
h1{font-size:26px;margin:0 0 4px}h2{font-size:18px;margin:34px 0 12px;
border-bottom:1px solid var(--line);padding-bottom:6px}
.sub{color:var(--mut);margin:0 0 8px}
.formula{background:#101a2e;border:1px solid #5b9dff;border-left:5px solid #5b9dff;
border-radius:12px;padding:16px 22px;margin:18px 0;font-size:21px;font-weight:600;
text-align:center;line-height:1.45;color:var(--ink)}
.formula b{color:#5b9dff}.formula .u{display:block;font-size:13px;color:var(--mut);font-weight:400;margin-top:5px}
code{background:#0e1830;border:1px solid #2a3445;border-radius:5px;padding:1px 6px;
color:#7dd3fc;font-size:13px;font-family:ui-monospace,Menlo,Consolas,monospace}
.hero{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--up);
border-radius:12px;padding:18px 20px;margin:20px 0}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:20px 0}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px}
.kpi .v{font-size:22px;font-weight:700}.kpi .l{color:var(--mut);font-size:12px;margin-top:4px}
.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:16px}
.chart{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px}
.chart .hd{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:4px}
.chart .t{font-weight:600}.chart .r{color:var(--mut);font-size:11px}
.pill{font-size:12px;font-weight:700;padding:2px 8px;border-radius:20px}
.pos{color:var(--up);background:rgba(52,211,153,.12)}
.neg{color:var(--down);background:rgba(248,113,113,.12)}
table{width:100%;border-collapse:collapse;font-size:14px}
th,td{padding:8px 10px;text-align:right;border-bottom:1px solid var(--line)}
th:first-child,td:first-child{text-align:left}th{color:var(--mut);font-weight:600}
.note{color:var(--mut);font-size:13px;background:var(--card);border:1px solid var(--line);
border-radius:10px;padding:14px;margin-top:10px}.note b{color:var(--ink)}
.lgd{display:flex;gap:16px;color:var(--mut);font-size:12px;margin:6px 0 0;flex-wrap:wrap}
.sw{display:inline-block;width:11px;height:11px;border-radius:2px;margin-right:5px;vertical-align:-1px}
"""

HTML = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Level 1 — Labour Supply to 2035</title><style>{CSS}</style></head><body><div class="wrap">
<h1>Level 1 — Labour Supply to 2035</h1>
<p class="sub">Potential labour supply in <b>human-working-years</b> = health-adjusted working-age
people × expected working life · observed 2011–2024, forecast to 2035 · 8 countries, by sex.</p>
<div class="formula"><b>Supply</b> = health-adjusted working-age people <b>×</b> expected working life
<span class="u">measured in human-working-years (career person-years)</span></div>
<div class="hero">Total supply is <b>essentially flat ({tot24:,}M → {tot35:,}M, {totchg:+.1f}%)</b> to 2035 — a
<b>longevity dividend</b>: working-age populations shrink, but rising healthy-life share and longer
working lives offset the loss. The split is demographic: <b>Romania −13%, Bulgaria −9%</b> (emigration +
ageing) vs <b>Germany, France, Norway +3–5%</b> (participation + health gains outweigh population decline).</div>
<div class="kpis">
<div class="kpi"><div class="v">{tot24:,} → {tot35:,}M</div><div class="l">Realized supply, career person-years (2024→2035)</div></div>
<div class="kpi"><div class="v" style="color:{totcol}">{totchg:+.1f}%</div><div class="l">Change to 2035 (longevity offsets shrinkage)</div></div>
<div class="kpi"><div class="v">{ceil24:,}M</div><div class="l">Ceiling supply if all healthy years worked</div></div>
<div class="kpi"><div class="v">{realiz} · {unused}% idle</div><div class="l">Realization ratio (working-life ÷ max span)</div></div>
</div>
<h2>Supply predictions by country</h2><div class="grid">{charts_html}</div>
<h2>Forecast table</h2>
<table><thead><tr><th>Country</th><th>Region</th><th>2024</th><th>2035</th>
<th>80% band</th><th>Δ%</th></tr></thead><tbody>{rows_html}</tbody></table>
<div class="note"><b>How to read it.</b> Supply = <b>population (15–64) × healthy-life share (HLY/LE) ×
expected working life</b>, in career person-years. It's a <b>potential ceiling</b>, net of health and
typical working-life length, but before skills/frictions. The <b>realization ratio (0.77)</b> means ~{unused}%
of healthy working-age capacity is institutionally idle (later entry, early exit, non-participation) —
the lever the West uses to offset shrinking populations. Population from Eurostat <code>proj_23np</code>
(calibrated to 2024, D4); bands include out-of-sample model error (D5).</div>
<h2>Caveats</h2>
<div class="note">• HLY is survey-based (GALI) with methodology breaks — the model can't beat a naive guess on it
(see the model-trust report); treated as a bounded ratio.<br>
• Forecasts assume the recent rise in working-life duration continues; the <b>participation-plateau</b>
scenario (D6) flattens supply growth in the West.<br>
• Supply feeds the Level 3 balance (supply − demand).</div>
<h2>Data sources — Eurostat dataset codes</h2>
<div class="note"><code>hlth_hlye</code> life expectancy &amp; healthy life years (LE, HLY) ·
<code>demo_pjangroup</code> population by age (working-age 15–64) ·
<code>proj_23np</code> population projections (baseline + migration) ·
<code>lfsi_dwl_a</code> expected duration of working life ·
<code>demo_pjan</code> / <code>demo_mlexpec</code> total population &amp; LE cross-check.</div>
<p class="sub" style="margin-top:24px;font-size:12px">Generated from outputs/supply_forecast.csv · src/supply.py, supply_forecast.py</p>
</div></body></html>"""

(OUT / "level1_supply_report.html").write_text(HTML, encoding="utf-8")
print(f"wrote outputs/level1_supply_report.html  total {tot24:,}->{tot35:,}M {totchg:+.1f}%, realiz {realiz}")
