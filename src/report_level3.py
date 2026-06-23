"""
Level 3 — Balance report (the headline). Static SVG, no client-side JS.
Balance = potential supply - potential demand, in human-working-years, by country,
observed 2011-2024 + forecast to 2035. Reads outputs/{supply_observed,balance_forecast}.csv
-> outputs/level3_balance_report.html
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
bf = pd.read_csv(OUT / "balance_forecast.csv")

countries = list((bf[bf.year == 2035].groupby("country").balance.sum() / M)
                 .sort_values().index)        # most deficit -> most surplus
series = {}
for c in countries:
    o = (obs[obs.country == c].groupby("year")["balance_realized"].sum() / M)
    o = o[o.index <= 2024]
    f = bf[bf.country == c].groupby("year").agg(
        b=("balance", "sum"), lo=("balance_lo", "sum"), hi=("balance_hi", "sum")) / M
    series[c] = {
        "name": NAME[c], "region": REGION[c],
        "oy": [int(y) for y in o.index], "ov": [round(v, 1) for v in o.values],
        "fy": [int(y) for y in f.index],
        "fm": [round(v, 1) for v in f["b"].values],
        "lo": [round(v, 1) for v in f["lo"].values],
        "hi": [round(v, 1) for v in f["hi"].values],
        "b2024": round(float(o.loc[2024])),
        "b2035": round(float(f["b"].loc[2035])),
    }

tot24 = round(float(obs[obs.year == 2024]["balance_realized"].sum() / M))
tot35 = round(float(bf[bf.year == 2035]["balance"].sum() / M))
deficit35 = round(sum(series[c]["b2035"] for c in countries if series[c]["b2035"] < 0))
surplus35 = round(sum(series[c]["b2035"] for c in countries if series[c]["b2035"] > 0))

# ---- static diverging bar (2035 balance by country) ----
# Layout: fixed left gutter for names, centred zero axis, value labels at bar ends.
W1, rh = 960, 34
NAMEX, PLOTL, PLOTR = 14, 150, W1 - 100   # name col | plot region [150 .. 860]
cx = (PLOTL + PLOTR) / 2                   # zero axis
half = (PLOTR - PLOTL) / 2
maxabs = max(abs(series[c]["b2035"]) for c in countries)
nrows = len(countries)
bars = []
for i, c in enumerate(countries):
    s = series[c]; v = s["b2035"]
    yc = i * rh + rh / 2 + 4                # row vertical centre (baseline)
    w = abs(v) / maxabs * half
    col = "#34d399" if v >= 0 else "#f87171"
    x = cx if v >= 0 else cx - w
    lab_x = (cx + w + 8) if v >= 0 else (cx - w - 8)
    anchor = "start" if v >= 0 else "end"
    bars.append(
        f'<text x="{NAMEX}" y="{yc:.1f}" fill="#e8edf7" font-size="13" dominant-baseline="middle">{s["name"]}</text>'
        f'<rect x="{x:.1f}" y="{i*rh+9}" width="{w:.1f}" height="16" rx="3" fill="{col}" opacity="0.85"/>'
        f'<text x="{lab_x:.1f}" y="{yc:.1f}" fill="{col}" font-size="12" '
        f'text-anchor="{anchor}" dominant-baseline="middle">{"+" if v>0 else ""}{v}M</text>')
bars.append(f'<line x1="{cx}" y1="4" x2="{cx}" y2="{nrows*rh+2}" stroke="#94a3b8" stroke-width="1"/>')
bars.append(f'<text x="{cx+8}" y="{nrows*rh+20}" fill="#34d399" font-size="11">surplus →</text>')
bars.append(f'<text x="{cx-8}" y="{nrows*rh+20}" fill="#f87171" font-size="11" text-anchor="end">← shortage</text>')
diverge_svg = (f'<svg viewBox="0 0 {W1} {nrows*rh+28}" width="100%" '
               f'xmlns="http://www.w3.org/2000/svg">{"".join(bars)}</svg>')


# ---- per-country balance trajectory (observed + forecast + band + zero line) ----
W, H, PLm, PRm, PTm, PBm = 470, 200, 46, 12, 12, 26


def traj_svg(s):
    oy, ov, fy, fm, lo, hi = s["oy"], s["ov"], s["fy"], s["fm"], s["lo"], s["hi"]
    allv = ov + hi + lo + [0]
    x0, x1 = min(oy + fy), max(oy + fy)
    y0, y1 = min(allv), max(allv)
    pad = (y1 - y0) * 0.08 or 1
    y0 -= pad; y1 += pad
    X = lambda v: PLm + (v - x0) / (x1 - x0) * (W - PLm - PRm)
    Y = lambda v: H - PBm - (v - y0) / (y1 - y0) * (H - PTm - PBm)
    g = []
    for yr in range(x0, x1 + 1, 4):
        g.append(f'<text x="{X(yr):.1f}" y="{H-9}" fill="#94a3b8" font-size="10" text-anchor="middle">{yr}</text>')
    yz = Y(0)
    g.append(f'<line x1="{PLm}" y1="{yz:.1f}" x2="{W-PRm}" y2="{yz:.1f}" stroke="#94a3b8" stroke-width="1" stroke-dasharray="3 2" opacity="0.7"/>')
    g.append(f'<text x="{PLm-6}" y="{yz+3:.1f}" fill="#94a3b8" font-size="10" text-anchor="end">0</text>')
    band = " ".join(f"{X(x):.1f},{Y(hi[i]):.1f}" for i, x in enumerate(fy)) + " " + \
           " ".join(f"{X(x):.1f},{Y(lo[i]):.1f}" for i, x in reversed(list(enumerate(fy))))
    obsp = " ".join(f"{X(x):.1f},{Y(ov[i]):.1f}" for i, x in enumerate(oy))
    fcp = " ".join(f"{X(x):.1f},{Y(fm[i]):.1f}" for i, x in enumerate(fy))
    joinp = f"{X(oy[-1]):.1f},{Y(ov[-1]):.1f} {X(fy[0]):.1f},{Y(fm[0]):.1f}"
    cls = "neg" if s["b2035"] < 0 else "pos"
    sign = "+" if s["b2035"] > 0 else ""
    return (f'<div class="chart"><div class="hd"><div><span class="t">{s["name"]}</span> '
            f'<span class="r">{s["region"]}</span></div>'
            f'<span class="pill {cls}">{sign}{s["b2035"]}M by 2035</span></div>'
            f'<svg viewBox="0 0 {W} {H}" width="100%" xmlns="http://www.w3.org/2000/svg">{"".join(g)}'
            f'<polygon points="{band}" fill="rgba(251,191,36,0.16)"/>'
            f'<polyline points="{obsp}" fill="none" stroke="#7dd3fc" stroke-width="2"/>'
            f'<polyline points="{joinp}" fill="none" stroke="#fbbf24" stroke-width="1.5" stroke-dasharray="2 2"/>'
            f'<polyline points="{fcp}" fill="none" stroke="#fbbf24" stroke-width="2"/>'
            f'</svg></div>')


charts_html = "".join(traj_svg(series[c]) for c in countries)
rows_html = "".join(
    f'<tr><td>{series[c]["name"]}</td><td style="color:#94a3b8">{series[c]["region"]}</td>'
    f'<td>{series[c]["b2024"]:+}</td><td>{series[c]["b2035"]:+}</td>'
    f'<td style="color:#94a3b8">{round(series[c]["lo"][-1]):+} … {round(series[c]["hi"][-1]):+}</td>'
    f'<td style="text-align:right"><span class="pill {"neg" if series[c]["b2035"]<0 else "pos"}">'
    f'{"shortage" if series[c]["b2035"]<0 else "surplus"}</span></td></tr>' for c in countries)

CSS = """
:root{--bg:#0f1420;--card:#171e2e;--ink:#e8edf7;--mut:#94a3b8;--line:#2a3445;
--obs:#7dd3fc;--fc:#fbbf24;--band:rgba(251,191,36,.16);--up:#34d399;--down:#f87171;}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font:15px/1.55 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;padding:32px}
.wrap{max-width:1080px;margin:0 auto}
h1{font-size:26px;margin:0 0 4px}h2{font-size:18px;margin:34px 0 12px;
border-bottom:1px solid var(--line);padding-bottom:6px}
.sub{color:var(--mut);margin:0 0 8px}
.hero{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--up);
border-radius:12px;padding:18px 20px;margin:20px 0}
.kpis{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:20px 0}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px}
.kpi .v{font-size:23px;font-weight:700}.kpi .l{color:var(--mut);font-size:12px;margin-top:4px}
.panel{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px}
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
<title>Level 3 — Labour-Market Balance to 2035</title><style>{CSS}</style></head><body><div class="wrap">
<h1>Level 3 — Labour-Market Balance to 2035</h1>
<p class="sub">The headline: <b>balance = potential supply − potential demand</b>, in
<b>human-working-years</b>, by country · observed 2011–2024, forecast to 2035 · 8 countries.</p>
<div class="hero">Europe is in a <b>slight overall surplus</b> ({tot24:+}M → {tot35:+}M human-working-years to 2035),
but the aggregate hides a sharp <b>East–West divide</b>: the West runs a <b style="color:var(--down)">labour
shortage of {deficit35:+}M</b> while the East holds a <b style="color:var(--up)">surplus of {surplus35:+}M</b>.
Poland's reserve alone roughly offsets Germany's, France's and Switzerland's shortages combined — the
demographic basis of West-bound migration.</div>
<div class="kpis">
<div class="kpi"><div class="v">{tot35:+,}M</div><div class="l">Net balance 2035 (human-working-years)</div></div>
<div class="kpi"><div class="v" style="color:var(--down)">{deficit35:+,}M</div><div class="l">West/EFTA shortage (DE, FR, CH, NO)</div></div>
<div class="kpi"><div class="v" style="color:var(--up)">{surplus35:+,}M</div><div class="l">East surplus (PL, RO, CZ, BG)</div></div>
</div>
<h2>Balance by country, 2035</h2>
<div class="panel">{diverge_svg}</div>
<h2>Balance trajectories, 2011 → 2035</h2>
<div class="lgd"><span><span class="sw" style="background:var(--obs)"></span>Observed 2011–2024</span>
<span><span class="sw" style="background:var(--fc)"></span>Forecast 2025–2035</span>
<span><span class="sw" style="background:var(--band)"></span>80% band</span>
<span><span class="sw" style="background:var(--mut)"></span>zero line (balance)</span></div>
<div class="grid">{charts_html}</div>
<h2>Table</h2>
<table><thead><tr><th>Country</th><th>Region</th><th>2024</th><th>2035</th>
<th>80% band (2035)</th><th>Status</th></tr></thead><tbody>{rows_html}</tbody></table>
<div class="note"><b>How to read it.</b> Balance is in <b>millions of career person-years</b>.
Positive = healthy working-age supply exceeds the labour the economy's jobs require (slack);
negative = demand exceeds supply (shortage). Supply = health-adjusted working-age people × expected
working life; demand = (employed + vacancies) × required service. Bands include out-of-sample model
error (decision D5). The <b>participation-plateau</b> downside (D6) widens Western shortages further.</div>
<h2>Caveats</h2>
<div class="note">• Supply is a <b>potential ceiling</b> — it abstracts from skills mismatch and frictions;
read shortages/surpluses as structural capacity, not literal vacancies.<br>
• <b>Germany &amp; France</b> shortages depend on participation continuing to rise; under the plateau scenario they deepen.<br>
• <b>France</b> vacancies carry Eurostat flag <code>d</code>; population from <code>proj_23np</code> calibrated to 2024 (D4).<br>
• Drivers validated by rolling-origin backtest (see the model-trust report).</div>
<p class="sub" style="margin-top:24px;font-size:12px">Generated from outputs/balance_forecast.csv · src/balance_forecast.py</p>
</div></body></html>"""

(OUT / "level3_balance_report.html").write_text(HTML, encoding="utf-8")
print(f"wrote outputs/level3_balance_report.html  net {tot35:+}M, "
      f"West {deficit35:+}M, East {surplus35:+}M")
