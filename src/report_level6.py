# -*- coding: utf-8 -*-
"""
Level 6 — The longevity dividend in the macroeconomy (growth accounting).
Static SVG, earthy theme, map + decomposition + GDP forecast + honest relationship.
Reads outputs/macro_{observed,forecast,growth_accounting}.csv + macro_relationship.json
-> outputs/level6_macro_report.html
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
T = 1e6                                  # MEUR -> trillion EUR
NAME = {"BG": "Bulgaria", "PL": "Poland", "CZ": "Czechia", "RO": "Romania",
        "DE": "Germany", "FR": "France", "NO": "Norway", "CH": "Switzerland"}
REGION = {"BG": "East·EU", "PL": "East·EU", "CZ": "East·EU", "RO": "East·EU",
          "DE": "West·EU", "FR": "West·EU", "NO": "EFTA", "CH": "EFTA"}

obs = pd.read_csv(OUT / "macro_observed.csv")
fc = pd.read_csv(OUT / "macro_forecast.csv")
ga = pd.read_csv(OUT / "macro_growth_accounting.csv")
rel = json.loads((OUT / "macro_relationship.json").read_text(encoding="utf-8"))

gap = ga[ga.kind == "projected"].set_index("country")     # projected decomposition
gah = ga[ga.kind == "observed"].set_index("country")
order = list(gap.sort_values("g_gdp", ascending=False).index)   # fastest GDP first

gdp24 = obs[obs.year == 2024]["gdp"].sum() / T
gdp33 = fc[fc.year == 2033]["gdp"].sum() / T
cagr_agg = ((gdp33 / gdp24) ** (1 / 9) - 1) * 100

# ---------- interactive choropleth ----------
md = json.loads((OUT / "map_data.json").read_text(encoding="utf-8"))


def _flat(c, v, nd=2):
    """Whole-economy quantity (not sex-split): same value for T/F/M so the sex toggle stays valid."""
    return {"T": round(v, nd), "F": round(v, nd), "M": round(v, nd)}


def _labour_metric():
    d = {"label": "Projected labour-channel contribution to GDP growth, 2024–2033 (pp/yr)",
         "unit": "pp/yr", "total": "wmean", "fmt": "plain", "values": {}, "years": {}, "diverging": True}
    for c in NAME:
        d["values"][c] = _flat(c, float(gap.loc[c, "g_labour"]))
        d["years"][c] = 2033
    return d


def _prod_metric():
    d = {"label": "Labour productivity (real GDP per worker), 2024", "unit": "€000s/worker",
         "total": "wmean", "fmt": "plain", "values": {}, "years": {}}
    o24 = obs[obs.year == 2024].set_index("country")
    for c in NAME:
        d["values"][c] = _flat(c, float(o24.loc[c, "prod"]), 0)
        d["years"][c] = 2024
    return d


map_data = {"countries": md["countries"], "regime": md["regime"], "metrics": {
    "labour_contrib": _labour_metric(), "productivity": _prod_metric(), **md["metrics"]}}
map_html = build_map_section(
    map_data, container="geomap6", default_metric="labour_contrib",
    title="Geographic overview — the labour channel of growth",
    intro="Choropleth of the 8 countries. Default = the <b>labour channel</b>'s projected contribution to "
          "GDP growth to 2033 (pp/yr): <b>green = labour adds to growth, red = a demographic drag</b>. Switch "
          "to labour productivity (€/worker) or the underlying drivers. Macro aggregates are whole-economy "
          "(not sex-split); toggle sex shows the same value. Hover for details.")

# ---------- growth-accounting decomposition (projected 2024→2033) ----------
W1, rh = 920, 40
NAMEX, PLOTL, PLOTR = 14, 150, W1 - 80
span = PLOTR - PLOTL
vals = {c: (float(gap.loc[c, "g_labour"]), float(gap.loc[c, "g_prod"]), float(gap.loc[c, "g_gdp"])) for c in order}
lo = min(0, min(v[0] for v in vals.values()))               # most negative labour
hi = max(v[0] + v[1] for v in vals.values())                # max total
rng = hi - lo + 1e-9
X = lambda v: PLOTL + (v - lo) / rng * span
bars = []
for i, c in enumerate(order):
    gL, gP, gG = vals[c]
    y = i * rh + 8
    yc = y + 10
    # productivity segment [0, gP] (forest), labour segment stacked to total (slate; negative goes left)
    xp0, xp1 = X(0), X(gP)
    xl0, xl1 = X(gP), X(gP + gL)
    bars.append(f'<text x="{NAMEX}" y="{yc:.1f}" fill="#292524" font-size="13" dominant-baseline="middle">{NAME[c]} <tspan fill="#78716C" font-size="10">{REGION[c]}</tspan></text>')
    bars.append(f'<rect x="{min(xp0,xp1):.1f}" y="{y}" width="{abs(xp1-xp0):.1f}" height="20" rx="2.5" fill="#166534" opacity="0.88"/>')
    bars.append(f'<rect x="{min(xl0,xl1):.1f}" y="{y}" width="{abs(xl1-xl0):.1f}" height="20" rx="2.5" fill="#475569" opacity="0.9"/>')
    tx = X(gP + gL) + (6 if gL >= 0 else -6)
    anc = "start" if gL >= 0 else "end"
    bars.append(f'<text x="{tx:.1f}" y="{yc:.1f}" fill="#292524" font-size="12" font-weight="600" text-anchor="{anc}" dominant-baseline="middle">{gG:+.2f}</text>')
bars.append(f'<line x1="{X(0):.1f}" y1="4" x2="{X(0):.1f}" y2="{len(order)*rh+2}" stroke="#78716C" stroke-width="1"/>')
bars.append(f'<text x="{X(0):.1f}" y="{len(order)*rh+16}" fill="#78716C" font-size="10" text-anchor="middle">0</text>')
decomp_svg = f'<svg viewBox="0 0 {W1} {len(order)*rh+22}" width="100%" xmlns="http://www.w3.org/2000/svg">{"".join(bars)}</svg>'

# ---------- GDP forecast trajectories (€ trillion) ----------
W, H, PLm, PRm, PTm, PBm = 470, 190, 50, 12, 12, 26


def traj_svg(c):
    o = obs[obs.country == c].sort_values("year")
    f = fc[fc.country == c].sort_values("year")
    oy = [int(y) for y in o.year]; ov = [v / T for v in o.gdp]
    fy = [int(y) for y in f.year]; fm = [v / T for v in f.gdp]
    flo = [v / T for v in f.gdp_lo]; fhi = [v / T for v in f.gdp_hi]
    # bridge observed last point into the forecast line
    fy = [oy[-1]] + fy; fm = [ov[-1]] + fm; flo = [ov[-1]] + flo; fhi = [ov[-1]] + fhi
    allv = ov + fhi + flo
    x0, x1 = min(oy + fy), max(oy + fy)
    y0, y1 = min(allv) * 0.96, max(allv) * 1.04 or 1
    Xg = lambda v: PLm + (v - x0) / (x1 - x0) * (W - PLm - PRm)
    Yg = lambda v: H - PBm - (v - y0) / (y1 - y0 + 1e-9) * (H - PTm - PBm)
    g = [f'<text x="{Xg(yr):.1f}" y="{H-9}" fill="#78716C" font-size="10" text-anchor="middle">{yr}</text>'
         for yr in range(x0 - x0 % 5, x1 + 1, 5)]
    band = " ".join(f"{Xg(x):.1f},{Yg(fhi[i]):.1f}" for i, x in enumerate(fy)) + " " + \
           " ".join(f"{Xg(x):.1f},{Yg(flo[i]):.1f}" for i, x in reversed(list(enumerate(fy))))
    obsp = " ".join(f"{Xg(x):.1f},{Yg(ov[i]):.1f}" for i, x in enumerate(oy))
    fcp = " ".join(f"{Xg(x):.1f},{Yg(fm[i]):.1f}" for i, x in enumerate(fy))
    return (f'<div class="chart"><div class="hd"><div><span class="t">{NAME[c]}</span> '
            f'<span class="r">{REGION[c]} · {gap.loc[c,"g_gdp"]:+.1f}%/yr</span></div></div>'
            f'<svg viewBox="0 0 {W} {H}" width="100%" xmlns="http://www.w3.org/2000/svg">{"".join(g)}'
            f'<polygon points="{band}" fill="rgba(217,119,6,0.15)"/>'
            f'<polyline points="{obsp}" fill="none" stroke="#475569" stroke-width="2"/>'
            f'<polyline points="{fcp}" fill="none" stroke="#D97706" stroke-width="2" stroke-dasharray="2 2"/>'
            f'</svg></div>')


charts_html = "".join(traj_svg(c) for c in order)

# ---------- longevity ↔ productivity: cross-country scatter + within cloud ----------
cyear = rel["cross_year"]
cx = obs[obs.year == cyear].dropna(subset=["prod", "healthy_share"])
SW, SH = 470, 300
lx = np.log(cx["prod"].to_numpy(float)); hx = cx["healthy_share"].to_numpy(float)
xr = (hx.min() * 0.99, hx.max() * 1.01); yr = (lx.min() * 0.98, lx.max() * 1.02)
SX = lambda v: 54 + (v - xr[0]) / (xr[1] - xr[0] + 1e-9) * (SW - 80)
SY = lambda v: SH - 42 - (v - yr[0]) / (yr[1] - yr[0] + 1e-9) * (SH - 64)
cs_pts = ""
for _, r in cx.iterrows():
    px, py = SX(r["healthy_share"]), SY(np.log(r["prod"]))
    cs_pts += (f'<circle cx="{px:.1f}" cy="{py:.1f}" r="5" fill="#D97706" stroke="#166534" stroke-width="1"/>'
               f'<text x="{px+7:.1f}" y="{py+3:.1f}" font-size="10" fill="#292524">{r["country"]}</text>')
# trend line
b1, b0 = np.polyfit(hx, lx, 1)
tl = f'<line x1="{SX(xr[0]):.1f}" y1="{SY(b0+b1*xr[0]):.1f}" x2="{SX(xr[1]):.1f}" y2="{SY(b0+b1*xr[1]):.1f}" stroke="#B91C1C" stroke-width="1.5" stroke-dasharray="4 3"/>'
cross_svg = (f'<svg viewBox="0 0 {SW} {SH}" width="100%" xmlns="http://www.w3.org/2000/svg">{tl}'
             f'<text x="{SW/2}" y="{SH-8}" fill="#78716C" font-size="11" text-anchor="middle">healthy share (HLY / LE), {cyear} →</text>'
             f'<text x="14" y="{SH/2}" fill="#78716C" font-size="11" text-anchor="middle" transform="rotate(-90 14 {SH/2})">log productivity (GDP/worker) →</text>'
             f'{cs_pts}</svg>')

# within-country differenced cloud (Δ ln prod vs Δ healthy share)
dd = []
for c in NAME:
    g = obs[obs.country == c].dropna(subset=["prod", "healthy_share"]).sort_values("year")
    if len(g) < 5:
        continue
    dl = np.diff(np.log(g["prod"].to_numpy(float))) * 100
    dh = np.diff(g["healthy_share"].to_numpy(float)) * 100      # pp
    dd += list(zip(dh, dl))
xs = [a for a, _ in dd]; ys = [b for _, b in dd]
xr2 = (min(xs), max(xs)); yr2 = (min(ys), max(ys))
DX = lambda v: 54 + (v - xr2[0]) / (xr2[1] - xr2[0] + 1e-9) * (SW - 70)
DY = lambda v: SH - 40 - (v - yr2[0]) / (yr2[1] - yr2[0] + 1e-9) * (SH - 60)
dpts = "".join(f'<circle cx="{DX(a):.1f}" cy="{DY(b):.1f}" r="4" fill="rgba(71,85,105,.5)"/>' for a, b in dd)
within_svg = (f'<svg viewBox="0 0 {SW} {SH}" width="100%" xmlns="http://www.w3.org/2000/svg">'
              f'<line x1="54" y1="{DY(0):.1f}" x2="{SW-16}" y2="{DY(0):.1f}" stroke="#E7E5E4"/>'
              f'<line x1="{DX(0):.1f}" y1="20" x2="{DX(0):.1f}" y2="{SH-40}" stroke="#E7E5E4"/>'
              f'<text x="{SW/2}" y="{SH-8}" fill="#78716C" font-size="11" text-anchor="middle">Δ healthy share (pp/yr) →</text>'
              f'<text x="14" y="{SH/2}" fill="#78716C" font-size="11" text-anchor="middle" transform="rotate(-90 14 {SH/2})">Δ productivity (%/yr) →</text>'
              f'{dpts}</svg>')

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
_obs_d = (obs.assign(**{"GDP (€bn, real)": lambda d: (d.gdp / 1000).round(1),
                       "employed (000s)": lambda d: d.employed_ths.round(0),
                       "GDP/worker (€000s)": lambda d: d["prod"].round(1),
                       "healthy share": lambda d: d.healthy_share.round(3)})
          [["country", "year", "GDP (€bn, real)", "employed (000s)", "GDP/worker (€000s)", "healthy share"]])
_fc_d = (fc.assign(**{"GDP (€bn)": lambda d: (d.gdp / 1000).round(1),
                     "lo (€bn)": lambda d: (d.gdp_lo / 1000).round(1),
                     "hi (€bn)": lambda d: (d.gdp_hi / 1000).round(1),
                     "employed (000s)": lambda d: d.employed_ths.round(0),
                     "GDP/worker": lambda d: d["prod"].round(1)})
         [["country", "year", "GDP (€bn)", "lo (€bn)", "hi (€bn)", "employed (000s)", "GDP/worker"]])
_ga_d = (ga.assign(**{"GDP %/yr": lambda d: d.g_gdp.round(2), "labour %/yr": lambda d: d.g_labour.round(2),
                     "productivity %/yr": lambda d: d.g_prod.round(2)})
         [["country", "period", "kind", "GDP %/yr", "labour %/yr", "productivity %/yr"]])
APPENDIX = data_section(
    [("Observed GDP, employment, productivity & healthy share, by country × year", _obs_d),
     ("Forecast GDP 2025–2033 = employment × productivity (with 80% band)", _fc_d),
     ("Growth-accounting decomposition (observed & projected CAGR)", _ga_d)],
    note="Source: macro_observed.csv, macro_forecast.csv, macro_growth_accounting.csv. "
         "Real GDP = nama_10_gdp (B1GQ, chain-linked 2015). Productivity = real GDP ÷ employment.",
    filename="level6_macro_data")

corr, within = rel["cross_corr"], rel["within_elasticity"]
HTML = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Level 6 — Longevity in the Macroeconomy</title><style>{CSS}{appendix_css()}{info_css()}</style></head><body><div class="wrap">
<h1>Level 6 — The longevity dividend in the macroeconomy</h1>
<p class="sub">Open horizons · how longevity and the labour force feed real GDP — and whether <i>healthy</i>
longevity lifts productivity · 8 countries · observed → growth-accounted forecast to 2033.</p>
{DLINK}
<div class="formula"><b>Real GDP</b> = Employment <b>×</b> Productivity &nbsp;⟹&nbsp;
growth = <b style="color:#475569">labour</b> + <b style="color:#166534">productivity</b>
<span class="u">the labour channel is the one the longevity / supply engine moves</span></div>
<div class="hero"><b>Longevity reaches GDP through labour, not a productivity boost.</b> Combined real GDP
rises <b>€{gdp24:.1f}T → €{gdp33:.1f}T</b> by 2033 (≈ {cagr_agg:.1f}%/yr). Decomposed, the <b>East</b>
(BG, PL, CZ, RO) grows <b style="color:#166534">productivity-led</b> (catch-up convergence) with a flat-to-shrinking
labour channel, while the <b>West/EFTA</b> leans more on <b style="color:#475569">labour</b>. And the reverse
arrow is absent: across countries, self-reported <i>healthy</i> share and productivity correlate
<b style="color:var(--down)">{corr:+.2f}</b> (the wrong sign — a GALI artifact), and within a country the link is
<b>nil</b> (slope {within:+.2f}, R²&nbsp;{rel['within_r2']}).</div>
<div class="kpis">
<div class="kpi"><div class="v">€{gdp24:.1f} → €{gdp33:.1f}T</div><div class="l">Real GDP 2024 → 2033 (8 countries){info_icon("Combined real GDP (chain-linked volumes, 2015 prices) across the 8 countries, rebuilt as employment × productivity.")}</div></div>
<div class="kpi"><div class="v">{cagr_agg:.1f}%/yr</div><div class="l">Aggregate real growth, mostly productivity{info_icon("Average annual real GDP growth to 2033. Most of it comes from the productivity channel (output per worker), not the labour channel.")}</div></div>
<div class="kpi"><div class="v" style="color:var(--down)">{corr:+.2f}</div><div class="l">Cross-country corr: healthy share vs productivity{info_icon("Correlation across countries between self-perceived healthy share (HLY/LE) and GDP per worker. Negative = the wrong sign — a GALI self-reporting artifact.")}</div></div>
<div class="kpi"><div class="v">{within:+.2f}</div><div class="l">Within-country health→productivity slope (≈ 0){info_icon("How much productivity moves with healthy share, within a country over time. ≈ 0 means longevity reaches GDP through the number of healthy workers, not a per-worker premium.")}</div></div>
</div>
{map_html}
<h2>What drives projected growth: labour vs productivity (2024 → 2033)</h2>
<p class="sub">Each bar splits projected real-GDP growth (CAGR) into the
<b style="color:#166534">productivity</b> channel and the <b style="color:#475569">labour</b> channel
(employment — where demography and the longevity dividend act). The number is total GDP growth. A
<b>negative labour segment</b> (e.g. Romania) is a demographic drag the productivity channel must offset.</p>
<div class="lgd"><span><span class="sw" style="background:#166534"></span>Productivity (GDP per worker)</span>
<span><span class="sw" style="background:#475569"></span>Labour (employment)</span></div>
<div class="panel">{decomp_svg}</div>
<div class="note"><b>How to read it.</b> Productivity dominates in the East (rapid catch-up), so even shrinking
workforces still grow. In the West, productivity growth is slow, so the <b>labour channel matters more</b> —
which is exactly where raising participation, healthy working life and migration (the supply levers of Levels 1–3)
have macro leverage. Growth-accounting is descriptive: it apportions, it does not prove causation.</div>

<h2>Real GDP to 2033 — employment × productivity (€ trillion)</h2>
<div class="lgd"><span><span class="sw" style="background:var(--obs)"></span>Observed</span>
<span><span class="sw" style="background:var(--fc)"></span>Forecast (L × productivity)</span>
<span><span class="sw" style="background:var(--band)"></span>80% band</span></div>
<div class="grid">{charts_html}</div>
<div class="note">GDP is rebuilt as the product of two independently-forecast series (employment, productivity),
so the band combines both channels' uncertainty. It inherits the supply-side accuracy (Levels 1–3) plus the
productivity trend — wider where either series is volatile.</div>

<h2>Does healthy longevity raise productivity? (descriptive — no causal claim)</h2>
<p class="sub">The reverse arrow (Direction 3): if longer <i>healthy</i> lives make a more productive workforce,
healthy share (HLY/LE) and GDP-per-worker should move together. They don't.</p>
<div class="grid2">
<div class="chart"><div class="t">Cross-country ({cyear})</div>{cross_svg}
<div class="note" style="margin-top:6px">The fitted line slopes the <b>wrong way</b> (corr {corr:+.2f}): the most
productive countries (CH, NO) report the <i>lowest</i> healthy share, the least productive (BG) the highest —
self-perceived health (GALI) reflects expectations, not output.</div></div>
<div class="chart"><div class="t">Within-country, year-on-year</div>{within_svg}
<div class="note" style="margin-top:6px">A shapeless cloud: changes in healthy share explain none of the change in
productivity (slope <b>{within:+.2f}</b>, R²&nbsp;<b>{rel['within_r2']}</b>, n={rel['n_within']}). Productivity grows
~<b>{rel['prod_real_growth_pct']}%/yr</b> on capital, technology and convergence — not the health measure.</div></div>
</div>
<div class="note"><b>The capstone, honestly.</b> The longevity dividend is <b>real but it acts on the labour
quantity</b> — more healthy people working longer (Levels 1–3) — not on a measurable per-worker productivity premium.
Where the workforce shrinks (Romania, Bulgaria), productivity convergence still carries growth for now; where
convergence is exhausted (the West), the labour channel — and therefore the supply levers — is what moves the needle.</div>

<div class="note"><b>Honest limitations.</b> • Growth-accounting is an <b>identity decomposition</b>, not a structural/causal
model (no separate capital or TFP term — productivity bundles capital deepening and technology).<br>
• <b>Healthy share uses self-perceived HLY (GALI)</b>, which is not internationally comparable in levels — hence the
perverse cross-country sign.<br>• GDP and productivity are forecast with the same simple ensemble (no neural nets);
the productivity trend is the larger swing factor at 9 years.</div>

<h2>Data sources — Eurostat dataset codes</h2>
<div class="note"><code>nama_10_gdp</code> (real GDP B1GQ, CLV15) · <code>lfsa_egan</code> (employment) for productivity ·
<code>hlth_hlye</code> (HLY/LE) for the healthy share. Built on the Level 1–3 supply/demand engine.</div>
{APPENDIX}
<p class="sub" style="margin-top:24px;font-size:12px"><a href="../index.html">← Overview</a> ·
Generated from outputs/macro_forecast.csv · src/macro_forecast.py, report_level6.py</p>
</div></body></html>"""

(OUT / "level6_macro_report.html").write_text(HTML, encoding="utf-8")
print(f"wrote outputs/level6_macro_report.html  GDP {gdp24:.1f}->{gdp33:.1f}T, corr {corr}, within {within}")
