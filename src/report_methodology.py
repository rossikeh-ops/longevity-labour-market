# -*- coding: utf-8 -*-
"""
Methodology report — how the model works (3 diagrams + English narrative).
Static, self-contained HTML+SVG. -> outputs/methodology_report.html
"""
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "outputs"

C = {  # fill, stroke
    "blue": ("#16243a", "#5b9dff"), "teal": ("#11302d", "#2dd4bf"),
    "amber": ("#2e2611", "#fbbf24"), "gray": ("#1b212d", "#94a3b8"),
    "green": ("#13291f", "#34d399"), "purple": ("#221a33", "#a78bfa"),
}
FONT = "font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif"


def box(x, y, w, h, title, sub, color):
    fill, stroke = C[color]
    cx = x + w / 2
    if sub:
        t = (f'<text x="{cx}" y="{y+h/2-5}" fill="#e8edf7" font-size="14" font-weight="600" '
             f'text-anchor="middle" dominant-baseline="middle">{title}</text>'
             f'<text x="{cx}" y="{y+h/2+13}" fill="#94a3b8" font-size="11.5" '
             f'text-anchor="middle" dominant-baseline="middle">{sub}</text>')
    else:
        t = (f'<text x="{cx}" y="{y+h/2}" fill="#e8edf7" font-size="14" font-weight="600" '
             f'text-anchor="middle" dominant-baseline="middle">{title}</text>')
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="1.2"/>{t}')


def arrow(x1, y1, x2, y2, mid):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#94a3b8" stroke-width="1.3" marker-end="url(#{mid})"/>'


def svg(vb_w, vb_h, mid, body):
    defs = (f'<defs><marker id="{mid}" markerWidth="9" markerHeight="9" refX="6" refY="3" '
            f'orient="auto"><path d="M0,0 L6,3 L0,6" fill="none" stroke="#94a3b8" '
            f'stroke-width="1.3"/></marker></defs>')
    return (f'<svg viewBox="0 0 {vb_w} {vb_h}" width="100%" style="{FONT}" '
            f'xmlns="http://www.w3.org/2000/svg">{defs}{body}</svg>')


# ---- Diagram 1: ensemble forecast engine ----
d1 = "".join([
    box(240, 18, 200, 52, "Time series", "history by country × sex", "gray"),
    arrow(320, 70, 120, 100, "a1"), arrow(333, 70, 258, 100, "a1"),
    arrow(347, 70, 422, 100, "a1"), arrow(360, 70, 560, 100, "a1"),
    box(19, 104, 150, 56, "Linear trend", "OLS regression", "blue"),
    box(183, 104, 150, 56, "Damped Holt", "smooths the trend", "teal"),
    box(347, 104, 150, 56, "Drift", "random walk", "amber"),
    box(511, 104, 150, 56, "Naive", "last value", "gray"),
    arrow(94, 160, 300, 204, "a1"), arrow(258, 160, 328, 204, "a1"),
    arrow(422, 160, 352, 204, "a1"), arrow(586, 160, 380, 204, "a1"),
    box(215, 206, 250, 52, "Mean forecast (ensemble)", "= average of the 4 models", "green"),
    arrow(340, 258, 340, 294, "a1"),
    box(130, 296, 420, 64, "Monte-Carlo × 1000 + backtest error",
        "point forecast + 80% confidence band", "purple"),
])
svg1 = svg(680, 384, "a1", d1)

# ---- Diagram 2: demand construction ----
d2 = "".join([
    box(150, 20, 380, 56, "Population 15–64", "Eurostat proj_23np · calibrated to 2024", "blue"),
    arrow(340, 76, 340, 108, "a2"),
    box(150, 112, 380, 56, "Employment", "= working-age population × employment rate (forecast)", "teal"),
    arrow(340, 168, 340, 200, "a2"),
    box(150, 204, 380, 56, "Number of jobs", "= employed + vacancies", "amber"),
    arrow(340, 260, 340, 292, "a2"),
    box(150, 296, 380, 56, "Potential labour demand — person-years", "= jobs × required length of service (MISSOC)", "green"),
])
svg2 = svg(680, 372, "a2", d2)

# ---- Diagram 3: supply construction ----
d3 = "".join([
    box(150, 24, 380, 56, "Population 15–64", "Eurostat proj_23np · calibrated to 2024", "blue"),
    arrow(340, 80, 340, 120, "a3"),
    box(150, 124, 380, 56, "Healthy working-age people", "= population × healthy-years share (HLY ÷ LE)", "teal"),
    arrow(340, 180, 340, 220, "a3"),
    box(150, 224, 380, 56, "Potential labour supply — person-years", "= healthy people × expected working life", "green"),
])
svg3 = svg(680, 300, "a3", d3)

CSS = """
:root{--bg:#0f1420;--card:#171e2e;--ink:#e8edf7;--mut:#94a3b8;--line:#2a3445;--acc:#5b9dff;}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font:16px/1.65 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;padding:32px}
.wrap{max-width:880px;margin:0 auto}
h1{font-size:27px;margin:0 0 4px}h2{font-size:19px;margin:34px 0 10px}
.sub{color:var(--mut);margin:0 0 8px}
.fig{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px;margin:16px 0}
.cap{color:var(--mut);font-size:13px;margin-top:8px;text-align:center}
p{margin:12px 0}b{color:var(--ink)}code{color:var(--acc)}
ol{color:var(--ink)}li{margin:4px 0}
a{color:var(--acc)}.foot{color:var(--mut);font-size:13px;margin-top:30px}
.levels{display:flex;flex-direction:column;gap:12px;margin:18px 0}
.lvl{display:flex;gap:16px;background:var(--card);border:1px solid var(--line);
border-radius:12px;padding:16px 18px}
.lvl .num{flex:0 0 44px;height:44px;border-radius:10px;display:flex;align-items:center;
justify-content:center;font-size:20px;font-weight:800;color:#06203a}
.lvl .body{flex:1}.lvl h3{margin:0 0 3px;font-size:16px}.lvl .body p{margin:3px 0;font-size:14px}
.lvl .io{color:var(--mut);font-size:13px;margin-top:7px;line-height:1.5}
.lvl .io b{color:var(--ink)}.lvl .io code{font-size:12px}
"""

HTML = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Methodology — how the model works</title><style>{CSS}</style></head><body><div class="wrap">
<h1>Methodology — how the model works</h1>
<p class="sub">A transparent ensemble of simple statistical models + Monte-Carlo — deliberately
<b>no neural networks</b> (short series, defensibility required). Three diagrams describe the whole model.</p>

<h2>The pipeline — Levels 0 → 3</h2>
<p class="sub">Where each step sits and what it produces. Levels 1–2 run every driver through the
ensemble engine (§1), then combine via the identities below; Level 3 subtracts the two.</p>
<div class="levels">
<div class="lvl"><div class="num" style="background:#5b9dff">0</div><div class="body">
<h3>Data foundation</h3>
<p>Pull every Eurostat series, clean &amp; impute gaps, and assemble one tidy panel —
8 countries × sex × year, full coverage, reproducible.</p>
<div class="io">Sources <code>hlth_hlye</code> · <code>demo_pjan</code>/<code>demo_pjangroup</code> ·
<code>lfsa_egan</code> · <code>jvs_q_r21</code> · <code>lfsi_dwl_a</code> · <code>une_rt_a</code> ·
<code>proj_23np</code> &nbsp;→&nbsp; <b>panel.parquet</b></div></div></div>
<div class="lvl"><div class="num" style="background:#2dd4bf">1</div><div class="body">
<h3>Labour supply</h3>
<p>Forecast life expectancy, healthy-life share (HLY/LE), working-life duration and working-age
population to 2035, then combine into healthy person-years.</p>
<div class="io"><b>Supply = healthy working-age people × expected working life</b> &nbsp;(person-years)</div></div></div>
<div class="lvl"><div class="num" style="background:#fbbf24">2</div><div class="body">
<h3>Labour demand</h3>
<p>Forecast employment (rate × population) and job vacancies (anchored Beveridge curve) → jobs;
scale by the required length of service for a full pension.</p>
<div class="io"><b>Demand = (employed + vacancies) × required service</b> &nbsp;(person-years)</div></div></div>
<div class="lvl"><div class="num" style="background:#34d399">3</div><div class="body">
<h3>Balance — the headline</h3>
<p>Subtract the two stocks, by country × sex, to 2035, with Monte-Carlo uncertainty bands.
Surfaces the East-surplus / West-shortage divide.</p>
<div class="io"><b>Balance = Supply − Demand</b> &nbsp;(human-working-years)</div></div></div>
</div>

<h2>1 · Ensemble forecast engine</h2>
<p>For each time series (for every country × sex, over its full history) we do not rely on a
single model — we average <b>4 simple models</b>. Damped Holt and the naive anchor guard against
over-extrapolation: socio-economic rates saturate, they do not grow linearly forever.</p>
<div class="fig">{svg1}</div>
<p>The uncertainty band (the amber area in the reports) is assembled from <b>three sources</b>, combined
in quadrature: (1) the <b>disagreement between the four models</b>; (2) the <b>real out-of-sample
error from backtesting</b> — we re-forecast history and measure how far off we are; and (3) the
<b>demographic uncertainty</b> of the population. That is why the bands are a realistic <b>12–43%</b>
wide, not a falsely narrow ±5%.</p>

<h2>2 · Building labour demand</h2>
<p>From the forecast components we build demand using the formula from the case brief. Population is
<b>not</b> extrapolated naively — we take Eurostat's official projection <code>proj_23np</code>,
calibrated to the observed 2024 value.</p>
<div class="fig">{svg2}</div>

<h2>3 · Building labour supply</h2>
<p>The same logic as demand, but with two health–demographic multipliers. Both multipliers —
the <b>healthy-years share (HLY ÷ LE)</b> and <b>expected working life</b> — are forecast with the
<b>same 4-model ensemble</b> from the first diagram. The result is in <b>person-years</b>, exactly
like demand — which is why the two are directly comparable.</p>
<div class="fig">{svg3}</div>

<h2>Together — the whole model</h2>
<ol>
<li><b>Ensemble forecast engine</b> — how a single series is forecast.</li>
<li><b>Demand</b> = jobs × required length of service.</li>
<li><b>Supply</b> = healthy working-age people × expected working life.</li>
</ol>
<p><b>Level 3</b> simply subtracts: <b>Balance = Supply − Demand</b> (in human-working-years) — the
headline result, visualised in the balance report.</p>

<p class="foot">See also the <a href="model_validation_report.html">“Model trust”</a> report for the
backtest accuracy of this ensemble. · Code: <code>src/forecast.py</code>, <code>balance_forecast.py</code></p>
</div></body></html>"""

(OUT / "methodology_report.html").write_text(HTML, encoding="utf-8")
print(f"wrote outputs/methodology_report.html ({len(HTML)} bytes)")
