"""
Build a self-contained HTML report for Level 2 — Labour Demand.
Charts and tables are emitted as STATIC markup (SVG generated in Python) so they
render in any browser / viewer — no client-side JS, no innerHTML SVG quirks.
Reads outputs/{supply_observed,demand_forecast,scenario_participation}.csv and
writes outputs/level2_demand_report.html.
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
fc = pd.read_csv(OUT / "demand_forecast.csv")
sc = pd.read_csv(OUT / "scenario_participation.csv")

countries = ["DE", "FR", "PL", "RO", "CZ", "CH", "BG", "NO"]
series = {}
for c in countries:
    o = (obs[obs.country == c].groupby("year")["demand"].sum() / M)
    o = o[o.index <= 2024]
    f = fc[fc.country == c].groupby("year").agg(
        mean=("demand", "sum"), lo=("demand_lo", "sum"), hi=("demand_hi", "sum")) / M
    series[c] = {
        "name": NAME[c], "region": REGION[c],
        "oy": [int(y) for y in o.index], "ov": [round(v, 1) for v in o.values],
        "fy": [int(y) for y in f.index],
        "fm": [round(v, 1) for v in f["mean"].values],
        "lo": [round(v, 1) for v in f["lo"].values],
        "hi": [round(v, 1) for v in f["hi"].values],
        "d2024": round(float(o.loc[2024])),
        "d2035": round(float(f["mean"].loc[2035])),
        "chg": round((f["mean"].loc[2035] / o.loc[2024] - 1) * 100, 1),
        "plateau": round(float(sc[sc.country == c]["demand_2035_plateau"].iloc[0] / M)),
    }

tot24 = round(sum(series[c]["d2024"] for c in countries))
tot35 = round(sum(series[c]["d2035"] for c in countries))
totchg = round((tot35 / tot24 - 1) * 100, 1)
jobs24 = round(float(obs[obs.year == 2024]["jobs"].sum() / M), 1)
jobs35 = round(float(fc[fc.year == 2035]["jobs"].sum() / M), 1)
sexF = round(float(fc[fc.year == 2035].query("sex=='F'")["demand"].sum() / M))
sexM = round(float(fc[fc.year == 2035].query("sex=='M'")["demand"].sum() / M))
totcol = "#f87171" if totchg < 0 else "#34d399"

# ---------- static SVG chart (Python-generated) ----------
W, H, PL_, PR, PT, PB = 470, 210, 44, 12, 12, 26


def chart_svg(s):
    oy, ov, fy, fm, lo, hi = s["oy"], s["ov"], s["fy"], s["fm"], s["lo"], s["hi"]
    allv = ov + hi + lo + [s["plateau"]]
    x0, x1 = min(oy + fy), max(oy + fy)
    y0, y1 = min(allv) * 0.97, max(allv) * 1.03
    X = lambda v: PL_ + (v - x0) / (x1 - x0) * (W - PL_ - PR)
    Y = lambda v: H - PB - (v - y0) / (y1 - y0) * (H - PT - PB)
    g = []
    for yr in range(x0, x1 + 1, 4):
        g.append(f'<line x1="{X(yr):.1f}" y1="{PT}" x2="{X(yr):.1f}" y2="{H-PB}" stroke="#2a3445" stroke-width="0.7"/>')
        g.append(f'<text x="{X(yr):.1f}" y="{H-9}" fill="#94a3b8" font-size="10" text-anchor="middle">{yr}</text>')
    for k in range(3):
        v = y0 + (y1 - y0) * k / 2
        g.append(f'<line x1="{PL_}" y1="{Y(v):.1f}" x2="{W-PR}" y2="{Y(v):.1f}" stroke="#2a3445" stroke-width="0.7" opacity="0.5"/>')
        g.append(f'<text x="{PL_-6}" y="{Y(v)+3:.1f}" fill="#94a3b8" font-size="10" text-anchor="end">{round(v)}</text>')
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
            f'<svg viewBox="0 0 {W} {H}" width="100%" xmlns="http://www.w3.org/2000/svg">'
            f'{"".join(g)}'
            f'<polygon points="{band}" fill="rgba(251,191,36,0.16)"/>'
            f'<polyline points="{obsp}" fill="none" stroke="#7dd3fc" stroke-width="2"/>'
            f'<polyline points="{joinp}" fill="none" stroke="#fbbf24" stroke-width="1.5" stroke-dasharray="2 2"/>'
            f'<polyline points="{fcp}" fill="none" stroke="#fbbf24" stroke-width="2"/>'
            f'<circle cx="{X(2035):.1f}" cy="{Y(s["plateau"]):.1f}" r="3.4" fill="none" stroke="#e8edf7" stroke-dasharray="2 1.5"/>'
            f'</svg></div>')


def row_html(s):
    cls = "neg" if s["chg"] < 0 else "pos"
    sign = "+" if s["chg"] > 0 else ""
    return (f'<tr><td>{s["name"]}</td><td style="color:#94a3b8">{s["region"]}</td>'
            f'<td>{s["d2024"]}</td><td>{s["d2035"]}</td>'
            f'<td style="color:#94a3b8">{round(s["lo"][-1])}–{round(s["hi"][-1])}</td>'
            f'<td class="{cls}" style="text-align:right">{sign}{s["chg"]}%</td>'
            f'<td style="color:#94a3b8">{s["plateau"]}</td></tr>')


charts_html = "".join(chart_svg(series[c]) for c in countries)
rows_html = "".join(row_html(series[c]) for c in countries)

CSS = """
:root{--bg:#0f1420;--card:#171e2e;--ink:#e8edf7;--mut:#94a3b8;--line:#2a3445;
--acc:#5b9dff;--obs:#7dd3fc;--fc:#fbbf24;--band:rgba(251,191,36,.16);
--up:#34d399;--down:#f87171;}
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
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:22px 0}
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
border-radius:10px;padding:14px;margin-top:10px}
.lgd{display:flex;gap:16px;color:var(--mut);font-size:12px;margin:6px 0 0;flex-wrap:wrap}
.sw{display:inline-block;width:11px;height:11px;border-radius:2px;margin-right:5px;vertical-align:-1px}
"""

HTML = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Level 2 — Labour Demand to 2035</title><style>{CSS}</style></head><body><div class="wrap">
<h1>Level 2 — Labour Demand to 2035</h1>
<p class="sub">Potential labour demand in <b>career person-years</b> (jobs × required length of service),
8 countries, by sex · model 2011–2024, forecast to 2035 · Eurostat + MISSOC.</p>
<div class="formula"><b>Demand</b> = jobs (employed + vacancies) <b>×</b> required length of service
<span class="u">measured in human-working-years (career person-years)</span></div>
<div class="lgd"><span><span class="sw" style="background:var(--obs)"></span>Observed 2011–2024</span>
<span><span class="sw" style="background:var(--fc)"></span>Forecast 2025–2035</span>
<span><span class="sw" style="background:var(--band)"></span>80% uncertainty band</span>
<span><span class="sw" style="background:#fff;border:1px dashed #888"></span>Participation-plateau 2035</span></div>
<div class="kpis">
<div class="kpi"><div class="v">{tot24:,} → {tot35:,}M</div><div class="l">Total demand, career person-years (2024 → 2035)</div></div>
<div class="kpi"><div class="v" style="color:{totcol}">{totchg:+.1f}%</div><div class="l">Change to 2035 (broadly flat, ageing-tilted)</div></div>
<div class="kpi"><div class="v">{jobs24:.0f} → {jobs35:.0f}M</div><div class="l">Jobs (employed + vacancies), people</div></div>
<div class="kpi"><div class="v">{sexF:,} / {sexM:,}M</div><div class="l">2035 demand by sex (F / M)</div></div>
</div>
<h2>Demand predictions by country</h2><div class="grid">{charts_html}</div>
<h2>Forecast table</h2>
<table><thead><tr><th>Country</th><th>Region</th><th>2024</th><th>2035</th>
<th>80% band</th><th>Δ%</th><th>Plateau 2035</th></tr></thead><tbody>{rows_html}</tbody></table>
<div class="note"><b>How to read it.</b> Demand = (employed + vacancies) × required years of service —
the stock of career-years the economy's jobs require. <b>East (BG/CZ/PL/RO) declines</b> as the
working-age population shrinks; <b>West holds or grows</b>. The <b>plateau</b> column is the downside
where employment rates stop rising — it hits DE, FR and BG hardest. Bands include out-of-sample
model error and demographic uncertainty (decisions D5/D6).</div>
<h2>Caveats</h2>
<div class="note">• <b>France</b> vacancies carry Eurostat flag <code>d</code> (definition differs); its
+growth depends on rising participation (plateau → ~flat).<br>
• <b>Required service</b> held at baseline (France's points system ≈ 43y effective); pension reforms are levers.<br>
• Population from Eurostat <code>proj_23np</code> calibrated to observed 2024 (decision D4).<br>
• 2024 demand reproduces exactly from raw data; verified by a 5-agent audit.</div>
<h2>Data sources — Eurostat dataset codes</h2>
<div class="note"><code>lfsa_egan</code> employment by sex &amp; age ·
<code>jvs_q_r21</code> job vacancies (NACE Rev 2.1, quarterly→annual) ·
<code>demo_pjangroup</code> working-age population (for the employment rate) ·
<code>proj_23np</code> population projections. ·
Required length of service: <b>MISSOC</b> / <b>OECD Pensions at a Glance</b> (not published by Eurostat).</div>
<p class="sub" style="margin-top:24px;font-size:12px">Generated from outputs/demand_forecast.csv · src/balance_forecast.py</p>
</div></body></html>"""

(OUT / "level2_demand_report.html").write_text(HTML, encoding="utf-8")
print(f"wrote outputs/level2_demand_report.html  (static SVG, {len(HTML)} bytes, "
      f"total {tot24:,}->{tot35:,}M {totchg:+.1f}%)")
