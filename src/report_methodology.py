# -*- coding: utf-8 -*-
"""
Methodology report — how the model works (3 diagrams + English narrative).
Static, self-contained HTML+SVG. -> outputs/methodology_report.html
"""
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "outputs"

C = {  # fill, stroke
    "blue": ("#EEF2F6", "#166534"), "teal": ("#ECFDF3", "#4ADE80"),
    "amber": ("#FEF3E2", "#D97706"), "gray": ("#F5F5F4", "#78716C"),
    "green": ("#ECFDF3", "#15803D"), "purple": ("#EEF2F6", "#475569"),
}
FONT = "font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif"


def box(x, y, w, h, title, sub, color):
    fill, stroke = C[color]
    cx = x + w / 2
    if sub:
        t = (f'<text x="{cx}" y="{y+h/2-5}" fill="#292524" font-size="14" font-weight="600" '
             f'text-anchor="middle" dominant-baseline="middle">{title}</text>'
             f'<text x="{cx}" y="{y+h/2+13}" fill="#78716C" font-size="11.5" '
             f'text-anchor="middle" dominant-baseline="middle">{sub}</text>')
    else:
        t = (f'<text x="{cx}" y="{y+h/2}" fill="#292524" font-size="14" font-weight="600" '
             f'text-anchor="middle" dominant-baseline="middle">{title}</text>')
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="1.2"/>{t}')


def arrow(x1, y1, x2, y2, mid):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#78716C" stroke-width="1.3" marker-end="url(#{mid})"/>'


def svg(vb_w, vb_h, mid, body):
    defs = (f'<defs><marker id="{mid}" markerWidth="9" markerHeight="9" refX="6" refY="3" '
            f'orient="auto"><path d="M0,0 L6,3 L0,6" fill="none" stroke="#78716C" '
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

# ---- creative "engine" pipeline: iconographic stage nodes + animated flow conduit ----
_ICON = {
    "db": '<ellipse cx="12" cy="6" rx="7" ry="3"/><path d="M5 6v12c0 1.7 3.1 3 7 3s7-1.3 7-3V6"/>'
          '<path d="M5 12c0 1.7 3.1 3 7 3s7-1.3 7-3"/>',
    "heart": '<path d="M12 20s-6.6-4.2-6.6-8.6A3.5 3.5 0 0112 8a3.5 3.5 0 016.6 3.4C18.6 15.8 12 20 12 20z"/>',
    "bag": '<rect x="3.5" y="7.5" width="17" height="11" rx="2"/>'
           '<path d="M9 7.5V6a2 2 0 012-2h2a2 2 0 012 2v1.5"/><path d="M3.5 12h17"/>',
    "scale": '<path d="M12 4v16"/><path d="M6 20h12"/><path d="M4 7h16"/>'
             '<path d="M4 7l-2.2 4.6a2.4 2.4 0 004.8 0z"/><path d="M20 7l-2.2 4.6a2.4 2.4 0 004.8 0z"/>',
}
STAGES = [
    dict(c="#475569", kick="Level 0", title="Data foundation", icon="db",
         desc="Pull every Eurostat series, clean &amp; impute gaps, and assemble one tidy panel — "
              "8 countries × sex × year, full coverage, reproducible.",
         chip='raw Eurostat &nbsp;→&nbsp; <b>panel.parquet</b>'),
    dict(c="#166534", kick="Level 1", title="Labour supply", icon="heart",
         desc="Forecast life expectancy, healthy-life share, working-life duration and working-age "
              "population to 2035 (detailed in §1), then combine into healthy person-years.",
         chip='<b>Supply</b> = healthy workers × working life'),
    dict(c="#D97706", kick="Level 2", title="Labour demand", icon="bag",
         desc="Forecast employment (rate × population) and job vacancies (anchored Beveridge) → jobs, "
              "scaled by the required length of service for a full pension.",
         chip='<b>Demand</b> = (employed + vacancies) × service'),
    dict(c="#166534", kick="Level 3", title="Balance — the headline", icon="scale",
         desc="Subtract the two stocks, by country × sex, to 2035 with Monte-Carlo uncertainty bands; "
              "surfaces the East-surplus / West-shortage divide.",
         chip='<b>Balance</b> = Supply − Demand &nbsp;→&nbsp; human-working-years'),
]


def _stage(i, s):
    nxt = STAGES[i + 1]["c"] if i + 1 < len(STAGES) else s["c"]
    icon = f'<svg viewBox="0 0 24 24" width="27" height="27">{_ICON[s["icon"]]}</svg>'
    return (f'<div class="estage" style="--c:{s["c"]};--c2:{nxt}">'
            f'<div class="enode">{icon}</div>'
            f'<div class="ecard"><div class="kick">{s["kick"]}</div>'
            f'<h3>{s["title"]}</h3><p>{s["desc"]}</p>'
            f'<div class="chip">{s["chip"]}</div></div></div>')


ENGINE = '<div class="engine">' + "".join(_stage(i, s) for i, s in enumerate(STAGES)) + '</div>'

CSS = """
:root{--bg:#FAFAF9;--card:#FFFFFF;--ink:#292524;--mut:#78716C;--line:#E7E5E4;--acc:#166534;}
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
/* animated "engine" pipeline: icon nodes + colour-transitioning conduit + flow pulses */
.engine{margin:22px 0}
.estage{display:flex;gap:18px;align-items:flex-start;position:relative;padding-bottom:24px}
.estage:last-child{padding-bottom:0}
.estage:not(:last-child)::before{content:"";position:absolute;left:26px;top:58px;bottom:0;width:4px;
border-radius:2px;background:linear-gradient(var(--c),var(--c2));opacity:.4}
.estage:not(:last-child)::after{content:"";position:absolute;left:22px;top:58px;width:12px;height:12px;
border-radius:50%;background:#166534;box-shadow:0 0 10px 2px var(--c);animation:flowdot 2.4s ease-in-out infinite}
.estage:nth-child(2)::after{animation-delay:.8s}.estage:nth-child(3)::after{animation-delay:1.6s}
@keyframes flowdot{0%{top:58px;opacity:0}12%{opacity:1}88%{opacity:1}100%{top:calc(100% - 6px);opacity:0}}
.enode{flex:0 0 54px;height:54px;border-radius:16px;background:var(--c);display:flex;align-items:center;
justify-content:center;box-shadow:0 6px 16px rgba(0,0,0,.32);position:relative;z-index:1}
.enode svg{stroke:#FFFFFF;fill:none;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round}
.ecard{flex:1;background:var(--card);border:1px solid var(--line);border-left:3px solid var(--c);
border-radius:14px;padding:13px 18px}
.ecard .kick{font-size:11px;letter-spacing:1px;text-transform:uppercase;color:var(--c);font-weight:700}
.ecard h3{margin:2px 0 5px;font-size:16px}.ecard p{margin:3px 0;font-size:13.5px;color:var(--mut)}
.ecard .chip{display:inline-block;margin-top:10px;background:#F5F5F4;border:1px solid var(--line);
border-radius:20px;padding:5px 13px;font-size:12.5px;color:var(--ink)}
.ecard .chip b{color:var(--c)}.ecard code{font-size:12px}
@media (prefers-reduced-motion:reduce){.estage::after{animation:none;opacity:0}}
h2 .hnum{display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;
border-radius:8px;font-size:16px;font-weight:800;color:#FFFFFF;margin-right:10px;vertical-align:-6px}
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
{ENGINE}

<h2><span class="hnum" style="background:#166534">1</span>Ensemble forecast engine</h2>
<p>For each time series (for every country × sex, over its full history) we do not rely on a
single model — we average <b>4 simple models</b>. Damped Holt and the naive anchor guard against
over-extrapolation: socio-economic rates saturate, they do not grow linearly forever.</p>
<div class="fig">{svg1}</div>
<p>The uncertainty band (the amber area in the reports) is assembled from <b>three sources</b>, combined
in quadrature: (1) the <b>disagreement between the four models</b>; (2) the <b>real out-of-sample
error from backtesting</b> — we re-forecast history and measure how far off we are; and (3) the
<b>demographic uncertainty</b> of the population. That is why the bands are a realistic <b>12–43%</b>
wide, not a falsely narrow ±5%.</p>
<p><b>On the supply side</b>, the engine forecasts <b>life expectancy</b>, the <b>healthy-life share
(HLY/LE)</b>, <b>working-life duration</b> and the <b>working-age population</b> to 2035, which are then
combined into healthy person-years.</p>
<div class="formula"><b>Supply</b> = healthy working-age people × expected working life
<span class="u">person-years</span></div>

<h2><span class="hnum" style="background:#D97706">2</span>Building labour demand</h2>
<p>From the forecast components we build demand using the formula from the case brief. Population is
<b>not</b> extrapolated naively — we take Eurostat's official projection <code>proj_23np</code>,
calibrated to the observed 2024 value.</p>
<div class="fig">{svg2}</div>

<h2><span class="hnum" style="background:#475569">3</span>Building labour supply</h2>
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
