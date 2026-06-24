# -*- coding: utf-8 -*-
"""
Level 5 — Healthy retirement dividend. Static SVG, earthy theme, map + appendix + Excel.
Reads outputs/{dividend_observed,dividend_forecast}.csv + dividend_relationship.json
-> outputs/level5_dividend_report.html
"""
from __future__ import annotations
import sys
import json
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from data_appendix import appendix_css, data_link, data_section  # noqa: E402
from map_section import build_map_section  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
M = 1e6
NAME = {"BG": "Bulgaria", "PL": "Poland", "CZ": "Czechia", "RO": "Romania",
        "DE": "Germany", "FR": "France", "NO": "Norway", "CH": "Switzerland"}
REGION = {"BG": "East·EU", "PL": "East·EU", "CZ": "East·EU", "RO": "East·EU",
          "DE": "West·EU", "FR": "West·EU", "NO": "EFTA", "CH": "EFTA"}

obs = pd.read_csv(OUT / "dividend_observed.csv")
fc = pd.read_csv(OUT / "dividend_forecast.csv")
rel = json.loads((OUT / "dividend_relationship.json").read_text(encoding="utf-8"))
panel = pd.read_parquet(ROOT / "data" / "processed" / "panel.parquet")

# per-person healthy-retirement years (2024, pop-weighted over sex)
o24 = obs[obs.year == 2024]
pp = {}
for c in NAME:
    r = o24[o24.country == c]
    pp[c] = round(float((r["hdiv_pp"] * r["pop_total"]).sum() / r["pop_total"].sum()), 1)
order_pp = sorted(NAME, key=lambda c: pp[c])      # most negative -> most positive

# dividend person-years trajectories (M), per country
countries = list((fc[fc.year == 2033].set_index("country")["dividend_py"] / M).sort_values(ascending=False).index)
series = {}
for c in countries:
    o = obs[obs.country == c].groupby("year")["hdiv_py"].sum() / M
    o = o[o.index <= 2024]
    f = fc[fc.country == c].set_index("year")
    series[c] = {"name": NAME[c], "region": REGION[c],
                 "oy": [int(y) for y in o.index], "ov": [round(v, 1) for v in o.values],
                 "fy": [int(y) for y in f.index], "fm": [round(v, 1) for v in (f["dividend_py"] / M)],
                 "lo": [round(v, 1) for v in (f["dividend_lo"] / M)], "hi": [round(v, 1) for v in (f["dividend_hi"] / M)]}
    a, b = series[c]["ov"][-1] if series[c]["ov"] else 0, series[c]["fm"][-1]
    series[c]["chg"] = round((b / a - 1) * 100, 1) if a else 0

div24 = round(obs[obs.year == 2024]["hdiv_py"].sum() / M)
div33 = round(fc[fc.year == 2033]["dividend_py"].sum() / M)

# within-country differenced cloud (Δdividend vs Δleisure)
panel = panel.copy()
rp = pd.read_csv(ROOT / "data" / "retirement_params.csv")
ret = {(r.country, r.sex): r.statutory_retirement_age for r in rp.itertuples()}
panel["retage"] = panel.apply(lambda r: ret.get((r.country, r.sex), np.nan), axis=1)
panel["hdiv_py"] = panel["pop_total"] * (panel["hly_birth"] - panel["retage"]).clip(lower=0)
panel["leisure"] = panel[["coicop_recreation", "coicop_education", "coicop_hotels_rest"]].sum(axis=1)
agg = panel.groupby(["country", "year"]).agg(d=("hdiv_py", "sum"), l=("leisure", "first")).reset_index().dropna()
agg = agg[(agg["d"] > 0) & (agg["l"] > 0)]
dpts = []
for c, g in agg.groupby("country"):
    g = g.sort_values("year")
    dl = np.diff(np.log(g["d"].to_numpy(float))) * 100
    dy = np.diff(np.log(g["l"].to_numpy(float))) * 100
    dpts += list(zip(dl, dy))

# ---------- interactive choropleth (default: healthy-retirement years, diverging) ----------
md = json.loads((OUT / "map_data.json").read_text(encoding="utf-8"))


def _hr_metric():
    d = {"label": "Healthy years after retirement (HLY − retire age), 2024", "unit": "years",
         "total": "wmean", "fmt": "plain", "values": {}, "years": {}, "diverging": True}
    for c in NAME:
        r = o24[o24.country == c]
        vals = {}
        for s in ("F", "M"):
            rr = r[r.sex == s]
            if len(rr):
                vals[s] = round(float(rr["hdiv_pp"].iloc[0]), 1)
        if len(r):
            vals["T"] = round(float((r["hdiv_pp"] * r["pop_total"]).sum() / r["pop_total"].sum()), 1)
        d["values"][c] = vals
        d["years"][c] = 2024
    return d


def _div_metric():
    f33 = fc[fc.year == 2033].set_index("country")
    o24s = o24.groupby(["country", "sex"])["hdiv_py"].sum()
    d = {"label": "Healthy-retirement dividend 2033 (person-years)", "unit": "person-years",
         "total": "sum", "fmt": "millions", "values": {}, "years": {}}
    for c in NAME:
        tot = float(f33.loc[c, "dividend_py"]) if c in f33.index else 0
        sh = o24s.loc[c] if c in o24s.index.get_level_values(0) else None
        vals = {"T": round(tot)}
        if sh is not None and sh.sum() > 0:
            vals["F"] = round(tot * float(sh.get("F", 0) / sh.sum()))
            vals["M"] = round(tot * float(sh.get("M", 0) / sh.sum()))
        d["values"][c] = vals
        d["years"][c] = 2033
    return d


map_data = {"countries": md["countries"], "regime": md["regime"], "metrics": {
    "healthy_retire": _hr_metric(), "dividend_2033": _div_metric(), **md["metrics"]}}
map_html = build_map_section(
    map_data, container="geomap5", default_metric="healthy_retire",
    title="Geographic overview — healthy years after retirement",
    intro="Choropleth of the 8 countries. Default = healthy years after retirement "
          "(HLY − retirement age): <b>green = healthy retirement, red = health declines first</b>. "
          "Switch to the 2033 dividend (person-years) or the HLY / life-expectancy drivers. Toggle sex; hover.")

# ---------- charts ----------
# diverging bar: healthy-retirement years per person by country
W1, rh = 920, 32
NAMEX, PLOTL, PLOTR = 14, 150, W1 - 70
cx, half = (PLOTL + PLOTR) / 2, (PLOTR - PLOTL) / 2
maxabs = max(abs(pp[c]) for c in NAME)
bars = []
for i, c in enumerate(order_pp):
    v = pp[c]
    yc = i * rh + rh / 2 + 4
    w = abs(v) / maxabs * half
    col = "#15803D" if v >= 0 else "#B91C1C"
    x = cx if v >= 0 else cx - w
    lab_x = (cx + w + 8) if v >= 0 else (cx - w - 8)
    anc = "start" if v >= 0 else "end"
    bars.append(
        f'<text x="{NAMEX}" y="{yc:.1f}" fill="#292524" font-size="13" dominant-baseline="middle">{NAME[c]}</text>'
        f'<rect x="{x:.1f}" y="{i*rh+8}" width="{w:.1f}" height="16" rx="3" fill="{col}" opacity="0.85"/>'
        f'<text x="{lab_x:.1f}" y="{yc:.1f}" fill="{col}" font-size="12" text-anchor="{anc}" dominant-baseline="middle">{"+" if v>0 else ""}{v}y</text>')
bars.append(f'<line x1="{cx}" y1="4" x2="{cx}" y2="{len(NAME)*rh+2}" stroke="#78716C" stroke-width="1"/>')
diverge_svg = (f'<svg viewBox="0 0 {W1} {len(NAME)*rh+10}" width="100%" xmlns="http://www.w3.org/2000/svg">{"".join(bars)}</svg>')

# differenced scatter
SW, SH = 470, 300
xs = [a for a, _ in dpts]; ys = [b for _, b in dpts]
xr = (min(xs), max(xs)); yr = (min(ys), max(ys))
SX = lambda v: 54 + (v - xr[0]) / (xr[1] - xr[0] + 1e-9) * (SW - 70)
SY = lambda v: SH - 40 - (v - yr[0]) / (yr[1] - yr[0] + 1e-9) * (SH - 60)
sc_pts = "".join(f'<circle cx="{SX(a):.1f}" cy="{SY(b):.1f}" r="4" fill="rgba(71,85,105,.55)"/>' for a, b in dpts)
diff_svg = (f'<svg viewBox="0 0 {SW} {SH}" width="100%" xmlns="http://www.w3.org/2000/svg">'
            f'<line x1="54" y1="{SY(0):.1f}" x2="{SW-16}" y2="{SY(0):.1f}" stroke="#E7E5E4"/>'
            f'<text x="{SW/2}" y="{SH-8}" fill="#78716C" font-size="11" text-anchor="middle">Δ dividend (%/yr) →</text>'
            f'<text x="14" y="{SH/2}" fill="#78716C" font-size="11" text-anchor="middle" transform="rotate(-90 14 {SH/2})">Δ leisure/education consumption (%/yr) →</text>'
            f'{sc_pts}</svg>')

# per-country forecast trajectories
W, H, PLm, PRm, PTm, PBm = 470, 190, 50, 12, 12, 26


def traj_svg(s):
    oy, ov, fy, fm, lo, hi = s["oy"], s["ov"], s["fy"], s["fm"], s["lo"], s["hi"]
    allv = ov + hi + lo + [0]
    x0, x1 = min(oy + fy), max(oy + fy)
    y0, y1 = min(allv) * 0.95, max(allv) * 1.05 or 1
    X = lambda v: PLm + (v - x0) / (x1 - x0) * (W - PLm - PRm)
    Y = lambda v: H - PBm - (v - y0) / (y1 - y0 + 1e-9) * (H - PTm - PBm)
    g = [f'<text x="{X(yr):.1f}" y="{H-9}" fill="#78716C" font-size="10" text-anchor="middle">{yr}</text>'
         for yr in range(x0, x1 + 1, 4)]
    band = " ".join(f"{X(x):.1f},{Y(hi[i]):.1f}" for i, x in enumerate(fy)) + " " + \
           " ".join(f"{X(x):.1f},{Y(lo[i]):.1f}" for i, x in reversed(list(enumerate(fy))))
    obsp = " ".join(f"{X(x):.1f},{Y(ov[i]):.1f}" for i, x in enumerate(oy))
    fcp = " ".join(f"{X(x):.1f},{Y(fm[i]):.1f}" for i, x in enumerate(fy))
    return (f'<div class="chart"><div class="hd"><div><span class="t">{s["name"]}</span> '
            f'<span class="r">{s["region"]}</span></div></div>'
            f'<svg viewBox="0 0 {W} {H}" width="100%" xmlns="http://www.w3.org/2000/svg">{"".join(g)}'
            f'<polygon points="{band}" fill="rgba(217,119,6,0.15)"/>'
            f'<polyline points="{obsp}" fill="none" stroke="#475569" stroke-width="2"/>'
            f'<polyline points="{fcp}" fill="none" stroke="#D97706" stroke-width="2" stroke-dasharray="2 2"/>'
            f'</svg></div>')


charts_html = "".join(traj_svg(series[c]) for c in countries)

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
.panel{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px}
.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:16px}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.chart{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px}
.chart .hd{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:4px}
.chart .t{font-weight:600}.chart .r{color:var(--mut);font-size:11px}
.note{color:var(--mut);font-size:13px;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px;margin-top:10px}.note b{color:var(--ink)}
.lgd{display:flex;gap:16px;color:var(--mut);font-size:12px;margin:6px 0 0;flex-wrap:wrap}
.sw{display:inline-block;width:11px;height:11px;border-radius:2px;margin-right:5px;vertical-align:-1px}
"""

DLINK = data_link()
_obs_d = (obs[["country", "sex", "year", "hly_birth", "retage", "hdiv_pp", "hdiv_py"]]
          .assign(**{"healthy yrs after retire": lambda d: d.hdiv_pp.round(2),
                     "dividend (M PY)": lambda d: (d.hdiv_py / M).round(2)})
          [["country", "sex", "year", "hly_birth", "retage", "healthy yrs after retire", "dividend (M PY)"]])
_fc_d = (fc.assign(**{"dividend (M PY)": lambda d: (d.dividend_py / M).round(1),
                      "lo (M)": lambda d: (d.dividend_lo / M).round(1),
                      "hi (M)": lambda d: (d.dividend_hi / M).round(1),
                      "leisure (€bn)": lambda d: (d.leisure / 1000).round(1)})
         [["country", "year", "dividend (M PY)", "lo (M)", "hi (M)", "leisure (€bn)"]])
APPENDIX = data_section(
    [("Observed healthy-retirement years & dividend, by country × sex × year", _obs_d),
     ("Forecast dividend 2025–2033 + leisure/education/culture consumption", _fc_d)],
    note="Source: dividend_observed.csv, dividend_forecast.csv (HLY − retirement age; COICOP CP09/10/11).",
    filename="level5_dividend_data")

HTML = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Level 5 — Healthy Retirement Dividend</title><style>{CSS}{appendix_css()}</style></head><body><div class="wrap">
<h1>Level 5 — Healthy Retirement Dividend</h1>
<p class="sub">Healthy years lived <b>after</b> retirement, and whether they drive leisure, education &amp;
culture consumption · 8 countries · observed → forecast to 2033.</p>
{DLINK}
<div class="formula"><b>Healthy retirement</b> = Population <b>×</b> (HLY − retirement age)
<span class="u">person-years of healthy life beyond the statutory retirement age</span></div>
<div class="hero">Whether retirement is healthy is <b>not guaranteed</b>: it ranges from
<b style="color:var(--up)">+{pp[order_pp[-1]]} years in {NAME[order_pp[-1]]}</b> to
<b style="color:var(--down)">{pp[order_pp[0]]} years in {NAME[order_pp[0]]}</b> — in several countries
self-reported health declines <i>before</i> the retirement age. The aggregate dividend grows
({div24:,}→{div33:,}M person-years) as healthy-life years rise. But tested against leisure/education/culture
spending, the link is <b>statistically negligible within a country</b> — consumption tracks income.</div>
<div class="kpis">
<div class="kpi"><div class="v" style="color:var(--up)">+{pp[order_pp[-1]]} yrs</div><div class="l">Healthiest retirement — {NAME[order_pp[-1]]}</div></div>
<div class="kpi"><div class="v" style="color:var(--down)">{pp[order_pp[0]]} yrs</div><div class="l">Health declines first — {NAME[order_pp[0]]}</div></div>
<div class="kpi"><div class="v">{div24:,} → {div33:,}M</div><div class="l">Dividend person-years (2024 → 2033)</div></div>
<div class="kpi"><div class="v">{rel['elasticity_within_diff']}</div><div class="l">Within-country dividend→consumption elasticity (≈ 0)</div></div>
</div>
{map_html}
<h2>Healthy years after retirement, by country (2024)</h2>
<p class="sub">HLY − statutory retirement age, population-weighted. Green = healthy years to enjoy in retirement;
red = health declines before retirement age is even reached.</p>
<div class="panel">{diverge_svg}</div>
<h2>The healthy-retirement dividend to 2033 (million person-years)</h2>
<div class="lgd"><span><span class="sw" style="background:var(--obs)"></span>Observed</span>
<span><span class="sw" style="background:var(--fc)"></span>Forecast</span>
<span><span class="sw" style="background:var(--band)"></span>80% band</span></div>
<div class="grid">{charts_html}</div>
<div class="note"><b>How to read it.</b> The dividend = population × the <i>positive</i> healthy years beyond
retirement. It grows quickly where rising HLY pushes more of the population across the retirement threshold —
so it is sensitive to the HLY forecast (a self-perceived measure). Countries currently below zero (DE, CH, CZ)
contribute little until their healthy-life years catch up to the retirement age.</div>

<h2>Does the dividend drive consumption? (descriptive — no causal claim)</h2>
<p class="sub">We relate it to <b>leisure, education &amp; culture</b> spending (COICOP CP09 recreation, CP10
education, CP11 restaurants/hotels). Across countries they co-move — but within a country over time, they don't.</p>
<div class="grid2">
<div class="chart"><div class="t">Within-country, year-on-year</div>{diff_svg}
<div class="note" style="margin-top:6px">A shapeless cloud: changes in the dividend explain none of the change in
spending (within-diff elasticity <b>{rel['elasticity_within_diff']}</b>, correlation <b>{rel['corr_within_diff']}</b>).</div></div>
<div class="chart"><div class="t">The honest reading</div>
<div class="note" style="margin-top:6px;border:none;background:transparent">
Cross-country the fit looks strong (FE elasticity {rel['elasticity_levels_fe']}, R²&nbsp;{rel['r2_levels_fe']}),
but that is mostly <b>country size</b>. Leisure/education/culture consumption grows
~<b>{rel['leisure_real_growth_pct']}%/yr</b> with household income and prices, statistically unrelated to the
healthy-retirement dividend in the short run. So the dividend is a meaningful <b>demographic</b> quantity, but
<b>not a usable predictor</b> of consumption — we report it descriptively.</div></div>
</div>
<div class="note"><b>Honest limitations.</b> • <code>HLY − retirement age</code> uses self-perceived HLY (GALI), so
the sign (healthy retirement or not) is partly subjective — Switzerland's −6.6y largely reflects low self-reported
health.<br>• The dividend forecast is <b>sensitive</b> to HLY crossing the retirement threshold (clipped at zero).<br>
• The consumption link is <b>descriptive, not causal</b>; the demographic dividend does not predict spending, which
tracks income.</div>

<h2>Data sources — Eurostat dataset codes</h2>
<div class="note"><code>hlth_hlye</code> (HLY) · <code>demo_pjan</code> (population) · retirement age (MISSOC / OECD)
for the dividend; <code>nama_10_co3_p3</code> (COICOP CP09/10/11) for consumption.</div>
{APPENDIX}
<p class="sub" style="margin-top:24px;font-size:12px"><a href="../index.html">← Overview</a> ·
Generated from outputs/dividend_forecast.csv · src/dividend_forecast.py, report_level5.py</p>
</div></body></html>"""

(OUT / "level5_dividend_report.html").write_text(HTML, encoding="utf-8")
print(f"wrote outputs/level5_dividend_report.html  per-person {pp[order_pp[0]]}..{pp[order_pp[-1]]}y, dividend {div24}->{div33}M")
