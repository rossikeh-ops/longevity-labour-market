# -*- coding: utf-8 -*-
"""
Level 4 — Cost of unhealthy years. Static SVG, earthy theme, data appendix + Excel.
Reads outputs/{cost_observed,cost_forecast}.csv + cost_relationship.json
-> outputs/level4_cost_report.html
"""
from __future__ import annotations
import sys
import json
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from data_appendix import appendix_css, data_link, data_section, info_css, info_icon  # noqa: E402
from map_section import build_map_section  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
M = 1e6
NAME = {"BG": "Bulgaria", "PL": "Poland", "CZ": "Czechia", "RO": "Romania",
        "DE": "Germany", "FR": "France", "NO": "Norway", "CH": "Switzerland"}
REGION = {"BG": "East·EU", "PL": "East·EU", "CZ": "East·EU", "RO": "East·EU",
          "DE": "West·EU", "FR": "West·EU", "NO": "EFTA", "CH": "EFTA"}

obs = pd.read_csv(OUT / "cost_observed.csv")
fc = pd.read_csv(OUT / "cost_forecast.csv")
rel = json.loads((OUT / "cost_relationship.json").read_text(encoding="utf-8"))
panel = pd.read_parquet(ROOT / "data" / "processed" / "panel.parquet")

countries = list((fc[fc.year == 2033].set_index("country")["poor_py"] / M).sort_values(ascending=False).index)
series = {}
for c in countries:
    o = obs[obs.country == c].groupby("year")["poor_py"].sum() / M
    o = o[o.index <= 2024]
    f = fc[fc.country == c].set_index("year")
    series[c] = {
        "name": NAME[c], "region": REGION[c],
        "oy": [int(y) for y in o.index], "ov": [round(v, 1) for v in o.values],
        "fy": [int(y) for y in f.index], "fm": [round(v, 1) for v in (f["poor_py"] / M)],
        "lo": [round(v, 1) for v in (f["poor_lo"] / M)], "hi": [round(v, 1) for v in (f["poor_hi"] / M)],
        "b2024": round(float(o.loc[2024])), "b2033": round(float(f.loc[2033, "poor_py"] / M)),
    }
    series[c]["chg"] = round((series[c]["b2033"] / series[c]["b2024"] - 1) * 100, 1)

tot24 = round(obs[obs.year == 2024]["poor_py"].sum() / M)
tot33 = round(fc[fc.year == 2033]["poor_py"].sum() / M)
totchg = round((tot33 / tot24 - 1) * 100, 1)
# per-person poor-health years, 8-country pop-weighted, 2024
o24 = obs[obs.year == 2024]
pp24 = round(float((o24["poor_pp"] * o24["pop_total"]).sum() / o24["pop_total"].sum()), 1)

# cross-country scatter (2024): burden (M PY) vs NACE-Q value added (€bn)
sc = (panel[panel.year == 2024].groupby("country")
      .agg(poor=("pop_total", lambda x: None)).reset_index())
scrows = []
for c in countries:
    p = panel[(panel.year == 2024) & (panel.country == c)]
    poor = float((p["pop_total"] * (p["le_birth"] - p["hly_birth"])).sum()) / M
    qva = float(p["nace_q_va"].iloc[0]) / 1000  # €bn
    if poor > 0 and qva > 0:
        scrows.append((c, poor, qva))

# ---------- interactive choropleth (default: poor-health burden) ----------
md = json.loads((OUT / "map_data.json").read_text(encoding="utf-8"))
o24 = obs[obs.year == 2024]
f33 = fc[fc.year == 2033].set_index("country")


def _burden_metric():
    d = {"label": "Poor-health burden 2033 (person-years)", "unit": "person-years",
         "total": "sum", "fmt": "millions", "values": {}, "years": {}}
    for c in countries:
        tot = float(f33.loc[c, "poor_py"])
        s24 = o24[o24.country == c].groupby("sex")["poor_py"].sum()
        vals = {"T": round(tot)}
        if s24.sum() > 0:
            sh = s24 / s24.sum()
            vals["F"] = round(tot * float(sh.get("F", 0)))
            vals["M"] = round(tot * float(sh.get("M", 0)))
        d["values"][c] = vals
        d["years"][c] = 2033
    return d


def _pp_metric():
    d = {"label": "Years in poor health per person (LE−HLY), 2024", "unit": "years",
         "total": "wmean", "fmt": "plain", "values": {}, "years": {}}
    for c in countries:
        r = o24[o24.country == c]
        vals = {}
        for s in ("F", "M"):
            rr = r[r.sex == s]
            if len(rr):
                vals[s] = round(float(rr["poor_pp"].iloc[0]), 1)
        if len(r):
            vals["T"] = round(float((r["poor_pp"] * r["pop_total"]).sum() / r["pop_total"].sum()), 1)
        d["values"][c] = vals
        d["years"][c] = 2024
    return d


map_data = {"countries": md["countries"], "regime": md["regime"], "metrics": {
    "burden_2033": _burden_metric(), "poor_pp": _pp_metric(), **md["metrics"]}}
map_html = build_map_section(
    map_data, container="geomap4", default_metric="burden_2033",
    title="Geographic overview — poor-health burden &amp; its drivers",
    intro="Choropleth of the 8 countries. Default = 2033 poor-health burden "
          "(person-years lived in poor health); switch to years-per-person (LE−HLY) "
          "or the underlying life-expectancy / healthy-life-years drivers. Toggle sex; hover a country.")

# ---------- charts ----------
W, H, PLm, PRm, PTm, PBm = 470, 200, 50, 12, 12, 26


def traj_svg(s):
    oy, ov, fy, fm, lo, hi = s["oy"], s["ov"], s["fy"], s["fm"], s["lo"], s["hi"]
    allv = ov + hi + lo
    x0, x1 = min(oy + fy), max(oy + fy)
    y0, y1 = min(allv) * 0.95, max(allv) * 1.05
    X = lambda v: PLm + (v - x0) / (x1 - x0) * (W - PLm - PRm)
    Y = lambda v: H - PBm - (v - y0) / (y1 - y0) * (H - PTm - PBm)
    g = []
    for yr in range(x0, x1 + 1, 4):
        g.append(f'<text x="{X(yr):.1f}" y="{H-9}" fill="#78716C" font-size="10" text-anchor="middle">{yr}</text>')
    for k in range(3):
        v = y0 + (y1 - y0) * k / 2
        g.append(f'<line x1="{PLm}" y1="{Y(v):.1f}" x2="{W-PRm}" y2="{Y(v):.1f}" stroke="#E7E5E4" stroke-width="0.7"/>')
        g.append(f'<text x="{PLm-6}" y="{Y(v)+3:.1f}" fill="#78716C" font-size="10" text-anchor="end">{round(v)}</text>')
    band = " ".join(f"{X(x):.1f},{Y(hi[i]):.1f}" for i, x in enumerate(fy)) + " " + \
           " ".join(f"{X(x):.1f},{Y(lo[i]):.1f}" for i, x in reversed(list(enumerate(fy))))
    obsp = " ".join(f"{X(x):.1f},{Y(ov[i]):.1f}" for i, x in enumerate(oy))
    fcp = " ".join(f"{X(x):.1f},{Y(fm[i]):.1f}" for i, x in enumerate(fy))
    joinp = f"{X(oy[-1]):.1f},{Y(ov[-1]):.1f} {X(fy[0]):.1f},{Y(fm[0]):.1f}"
    cls = "neg" if s["chg"] < 0 else "pos"
    sign = "+" if s["chg"] > 0 else ""
    return (f'<div class="chart"><div class="hd"><div><span class="t">{s["name"]}</span> '
            f'<span class="r">{s["region"]}</span></div>'
            f'<span class="pill {cls}">{sign}{s["chg"]}% by 2033</span></div>'
            f'<svg viewBox="0 0 {W} {H}" width="100%" xmlns="http://www.w3.org/2000/svg">{"".join(g)}'
            f'<polygon points="{band}" fill="rgba(217,119,6,0.15)"/>'
            f'<polyline points="{obsp}" fill="none" stroke="#475569" stroke-width="2"/>'
            f'<polyline points="{joinp}" fill="none" stroke="#D97706" stroke-width="1.5" stroke-dasharray="2 2"/>'
            f'<polyline points="{fcp}" fill="none" stroke="#D97706" stroke-width="2"/>'
            f'</svg></div>')


charts_html = "".join(traj_svg(series[c]) for c in countries)

# scatter svg (log-log burden vs NACE-Q), cross-country
SW, SH = 470, 300
xs = [np.log(p) for _, p, _ in scrows]
ys = [np.log(qv) for _, _, qv in scrows]
x0, x1 = min(xs) * 0.99, max(xs) * 1.01
y0, y1 = min(ys) * 1.05, max(ys) * 0.95
SX = lambda v: 54 + (v - x0) / (x1 - x0) * (SW - 66)
SY = lambda v: SH - 40 - (v - y0) / (y1 - y0) * (SH - 60)
pts = "".join(
    f'<circle cx="{SX(np.log(p)):.1f}" cy="{SY(np.log(qv)):.1f}" r="6" fill="#D97706" stroke="#166534"/>'
    f'<text x="{SX(np.log(p))+9:.1f}" y="{SY(np.log(qv))+4:.1f}" fill="#292524" font-size="11">{c}</text>'
    for c, p, qv in scrows)
scatter = (f'<svg viewBox="0 0 {SW} {SH}" width="100%" xmlns="http://www.w3.org/2000/svg">'
           f'<text x="{SW/2}" y="{SH-8}" fill="#78716C" font-size="11" text-anchor="middle">poor-health burden, 2024 (log million person-years) →</text>'
           f'<text x="14" y="{SH/2}" fill="#78716C" font-size="11" text-anchor="middle" transform="rotate(-90 14 {SH/2})">NACE-Q value added (log €bn) →</text>'
           f'{pts}</svg>')

CSS = """
:root{--bg:#FAFAF9;--card:#FFFFFF;--ink:#292524;--mut:#78716C;--line:#E7E5E4;--acc:#166534;
--up:#15803D;--down:#B91C1C;--obs:#475569;--fc:#D97706;--band:rgba(217,119,6,.15);}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font:15px/1.55 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;padding:32px}
.wrap{max-width:1080px;margin:0 auto}
h1{font-size:26px;margin:0 0 4px}h2{font-size:18px;margin:34px 0 12px;border-bottom:1px solid var(--line);padding-bottom:6px}
.sub{color:var(--mut);margin:0 0 8px}
.formula{background:#F0FDF4;border:1px solid #166534;border-left:5px solid #166534;border-radius:12px;
padding:16px 22px;margin:18px 0;font-size:21px;font-weight:600;text-align:center;line-height:1.45}
.formula b{color:#166534}.formula .u{display:block;font-size:13px;color:var(--mut);font-weight:400;margin-top:5px}
code{background:#F5F5F4;border:1px solid #E7E5E4;border-radius:5px;padding:1px 6px;color:#475569;font-size:13px}
.hero{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--acc);border-radius:12px;padding:18px 20px;margin:20px 0}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:20px 0}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px}
.kpi .v{font-size:22px;font-weight:700}.kpi .l{color:var(--mut);font-size:12px;margin-top:4px}
.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:16px}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.chart{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px}
.chart .hd{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:4px}
.chart .t{font-weight:600}.chart .r{color:var(--mut);font-size:11px}
.pill{font-size:12px;font-weight:700;padding:2px 8px;border-radius:20px}
.pos{color:var(--up);background:rgba(21,128,61,.12)}.neg{color:var(--down);background:rgba(185,28,28,.10)}
table{width:100%;border-collapse:collapse;font-size:14px}
th,td{padding:8px 10px;text-align:right;border-bottom:1px solid var(--line)}
th:first-child,td:first-child{text-align:left}th{color:var(--mut);font-weight:600}
.note{color:var(--mut);font-size:13px;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px;margin-top:10px}.note b{color:var(--ink)}
.lgd{display:flex;gap:16px;color:var(--mut);font-size:12px;margin:6px 0 0;flex-wrap:wrap}
.sw{display:inline-block;width:11px;height:11px;border-radius:2px;margin-right:5px;vertical-align:-1px}
"""

DLINK = data_link()
_obs_d = (obs[["country", "sex", "year", "pop_total", "le_birth", "hly_birth", "poor_py"]]
          .assign(**{"poor-health yrs/person": lambda d: (d.le_birth - d.hly_birth).round(2),
                     "poor-health (M PY)": lambda d: (d.poor_py / M).round(1)})
          [["country", "sex", "year", "poor-health yrs/person", "poor-health (M PY)"]])
_fc_d = (fc.assign(**{"poor-health (M PY)": lambda d: (d.poor_py / M).round(1),
                      "lo (M)": lambda d: (d.poor_lo / M).round(1),
                      "hi (M)": lambda d: (d.poor_hi / M).round(1),
                      "NACE-Q VA (€bn)": lambda d: (d.nace_q_va / 1000).round(1)})
         [["country", "year", "poor-health (M PY)", "lo (M)", "hi (M)", "NACE-Q VA (€bn)"]])
APPENDIX = data_section(
    [("Observed poor-health burden (Pop × (LE−HLY)), by country × sex × year", _obs_d),
     ("Forecast burden 2025–2033 + NACE-Q value added", _fc_d)],
    note="Source: cost_observed.csv, cost_forecast.csv (Pop × (LE−HLY); NACE-Q from nama_10_a64).",
    filename="level4_cost_data")

rows_html = "".join(
    f'<tr><td>{series[c]["name"]}</td><td style="color:#78716C">{series[c]["region"]}</td>'
    f'<td>{series[c]["b2024"]}</td><td>{series[c]["b2033"]}</td>'
    f'<td class="{"neg" if series[c]["chg"]<0 else "pos"}" style="text-align:right">'
    f'{"+" if series[c]["chg"]>0 else ""}{series[c]["chg"]}%</td></tr>' for c in countries)

HTML = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Level 4 — Cost of Unhealthy Years</title><style>{CSS}{appendix_css()}{info_css()}</style></head><body><div class="wrap">
<h1>Level 4 — Cost of Unhealthy Years</h1>
<p class="sub">The <b>poor-health burden</b> in person-years and whether it drives the health &amp; social-work
sector's cost · 8 countries · observed → forecast to 2033.</p>
{DLINK}
<div class="formula"><b>Poor-health burden</b> = Population <b>×</b> (LE − HLY)
<span class="u">total person-years lived in poor health</span></div>
<div class="hero">The burden is <b>near-flat to 2033 ({tot24:,}M → {tot33:,}M person-years, {totchg:+.1f}%)</b>:
ageing pushes it up, but rising healthy-life years pull it down — a second face of the longevity dividend.
And testing it against the <b>NACE-Q</b> (human health &amp; social work) sector, the honest result is that
<b>the burden does not drive the sector's cost in the short run</b> — that sector tracks the economy.</div>
<div class="kpis">
<div class="kpi"><div class="v">{tot24:,} → {tot33:,}M</div><div class="l">Poor-health person-years (2024 → 2033){info_icon("Population × years lived in poor health (life expectancy − healthy life years), summed over sex — the demographic poor-health burden.")}</div></div>
<div class="kpi"><div class="v">{pp24} yrs</div><div class="l">Lived in poor health per person (LE − HLY), 2024{info_icon("Years an average person lives in poor health = life expectancy at birth − healthy life years at birth (HLY is self-perceived, Eurostat GALI).")}</div></div>
<div class="kpi"><div class="v">{rel['q_real_growth_pct']}%/yr</div><div class="l">NACE-Q value-added real growth (economy-driven){info_icon("Annual real growth of the health & social-work sector (NACE section Q) value added — driven by GDP, not the demographic poor-health burden.")}</div></div>
<div class="kpi"><div class="v">{rel['elasticity_within_diff']}</div><div class="l">Within-country burden→cost elasticity (≈ 0){info_icon("How much the health-sector cost moves when the poor-health burden changes, within a country over time. ≈ 0 means no link — the sector tracks GDP, not the burden.")}</div></div>
</div>
{map_html}
<h2>Poor-health burden by country, to 2033</h2>
<div class="lgd"><span><span class="sw" style="background:var(--obs)"></span>Observed</span>
<span><span class="sw" style="background:var(--fc)"></span>Forecast</span>
<span><span class="sw" style="background:var(--band)"></span>80% band</span></div>
<div class="grid">{charts_html}</div>
<h2>Burden table (million person-years)</h2>
<table><thead><tr><th>Country</th><th>Region</th><th>2024</th><th>2033</th><th>Δ%</th></tr></thead>
<tbody>{rows_html}</tbody></table>
<div class="note"><b>How to read it.</b> Poor-health person-years = the whole population × the years each
person is expected to live in poor health (LE − HLY). It rises with ageing but falls as healthy-life years
improve, so the net is near-flat. The East (younger, shorter lives) carries a smaller burden than its
population alone implies; the West's larger elderly cohorts dominate.</div>

<h2>Does the burden drive the sector's cost? (descriptive — no causal claim)</h2>
<p class="sub">We relate the burden to <b>NACE-Q value added</b> (human health &amp; social work). Across
countries the two scale together — but that is a <b>size artefact</b> (big countries have both). Within a
country over time, the link vanishes.</p>
<div class="grid2">
<div class="chart"><div class="t">Cross-country, 2024 (log–log)</div>{scatter}
<div class="note" style="margin-top:6px">Strong cross-sectional fit (FE elasticity {rel['elasticity_levels_fe']},
R²&nbsp;{rel['r2_levels_fe']}) — but this is mostly country size: both burden and sector scale with population.</div></div>
<div class="chart"><div class="t">Within-country, year-on-year</div>
<div class="note" style="margin-top:6px;border:none;background:transparent;padding-top:30px">
First-differenced elasticity <b>{rel['elasticity_within_diff']}</b>, R²&nbsp;<b>{rel['r2_within_diff']}</b>,
correlation <b>{rel['corr_within_diff']}</b> ({rel['n_diff']} obs).<br><br>
In plain terms: <b>changes in the poor-health burden explain essentially none of the year-to-year change
in the sector's value added.</b> NACE-Q grows ~{rel['q_real_growth_pct']}%/yr with wages, prices and the wider
economy, while the burden moves ~{rel['burden_growth_pct']}%/yr — the two are statistically unrelated in the
short run. So we forecast the sector on its own trend, not from the demographic burden.</div></div>
</div>
<div class="note"><b>Honest limitations.</b> • <code>LE − HLY</code> is a mechanical identity, and HLY is a
self-perceived (GALI) survey measure — the burden inherits that subjectivity.<br>
• The cost link is <b>descriptive, not causal</b>; the within-country result says the demographic burden is
<b>not</b> a usable short-run predictor of the NACE-Q sector (which tracks GDP).<br>
• Bracket measures (government health <code>gov_10a_exp</code> GF07 + social GF10, and the SHA health accounts)
tell the same story — sector cost is an economic, not a purely demographic, quantity.</div>

<h2>Data sources — Eurostat dataset codes</h2>
<div class="note"><code>hlth_hlye</code> (LE, HLY) · <code>demo_pjan</code> (population) for the burden;
<code>nama_10_a64</code> (NACE-Q value added) · <code>gov_10a_exp</code> (COFOG health &amp; social) for the cost relationship.</div>
{APPENDIX}
<p class="sub" style="margin-top:24px;font-size:12px"><a href="../index.html">← Overview</a> ·
Generated from outputs/cost_forecast.csv · src/cost_forecast.py, report_level4.py</p>
</div></body></html>"""

(OUT / "level4_cost_report.html").write_text(HTML, encoding="utf-8")
print(f"wrote outputs/level4_cost_report.html  burden {tot24:,}->{tot33:,}M ({totchg:+.1f}%)")
