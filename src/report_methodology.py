# -*- coding: utf-8 -*-
"""
Methodology report — how the model works (3 diagrams + English narrative).
Static, self-contained HTML+SVG. -> outputs/methodology_report.html
"""
import sys
import json
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from data_appendix import appendix_css, data_link, data_section  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"

# ---- empirical test: one horizon-aware ensemble vs separate per-horizon models ----
# (the answer to "wouldn't separate 3/6/9-year models be more accurate?")
HZ = json.loads((OUT / "horizon_models_compare.json").read_text(encoding="utf-8"))
_HS = HZ["horizons"]
_ENS = [HZ["ensemble_mape"][str(h)] for h in _HS]
_DIR = [HZ["direct_mape"][str(h)] for h in _HS]
_NAI = [HZ["naive_mape"][str(h)] for h in _HS]
_PAIRS = [HZ["direct_pairs_med"][str(h)] for h in _HS]


def _hz_mape_svg():
    W, H, L, R, T, B = 460, 250, 40, 14, 16, 42
    ymax = max(_ENS + _DIR + _NAI) * 1.12
    X = lambda h: L + (h - 1) / (len(_HS) - 1) * (W - L - R)
    Y = lambda v: H - B - v / ymax * (H - T - B)
    grid = "".join(
        f'<line x1="{L}" y1="{Y(g):.1f}" x2="{W-R}" y2="{Y(g):.1f}" stroke="#E7E5E4"/>'
        f'<text x="{L-6}" y="{Y(g)+3:.1f}" font-size="10" fill="#78716C" text-anchor="end">{g}%</text>'
        for g in (0, 2, 4, 6))

    def line(vals, col, dash="", dots=True):
        pts = " ".join(f"{X(h):.1f},{Y(vals[i]):.1f}" for i, h in enumerate(_HS))
        d = f' stroke-dasharray="{dash}"' if dash else ""
        c = f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="2.4"{d}/>'
        if dots:
            c += "".join(f'<circle cx="{X(h):.1f}" cy="{Y(vals[i]):.1f}" r="3" fill="{col}"/>' for i, h in enumerate(_HS))
        return c
    xlab = "".join(f'<text x="{X(h):.1f}" y="{H-22}" font-size="10" fill="#78716C" text-anchor="middle">{h}</text>' for h in _HS)
    return (f'<svg viewBox="0 0 {W} {H}" width="100%" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif">{grid}'
            f'{line(_NAI, "#A8A29E", dash="4 3", dots=False)}{line(_DIR, "#B91C1C")}{line(_ENS, "#166534")}'
            f'{xlab}<text x="{(L+W-R)/2:.0f}" y="{H-6}" font-size="11" fill="#78716C" text-anchor="middle">forecast horizon (years ahead) →</text>'
            f'</svg>')


def _pairs_svg():
    W, H, L, R, T, B = 460, 250, 40, 14, 16, 42
    hl = {3, 6, 9}
    nmax = max(_PAIRS) * 1.15
    bw = (W - L - R) / len(_HS) * 0.62
    X = lambda h: L + (h - 0.5) / len(_HS) * (W - L - R)
    Y = lambda n: H - B - n / nmax * (H - T - B)
    bars = []
    for i, h in enumerate(_HS):
        n = _PAIRS[i]
        col = "#B91C1C" if h in hl else "#A8A29E"
        bars.append(f'<rect x="{X(h)-bw/2:.1f}" y="{Y(n):.1f}" width="{bw:.1f}" height="{H-B-Y(n):.1f}" rx="2" fill="{col}"/>')
        bars.append(f'<text x="{X(h):.1f}" y="{Y(n)-4:.1f}" font-size="10" fill="{"#B91C1C" if h in hl else "#78716C"}" font-weight="700" text-anchor="middle">{n}</text>')
        bars.append(f'<text x="{X(h):.1f}" y="{H-22}" font-size="10" fill="#78716C" text-anchor="middle">{h}</text>')
    yax = "".join(f'<text x="{L-6}" y="{Y(g)+3:.1f}" font-size="10" fill="#78716C" text-anchor="end">{g}</text>' for g in (0, 5, 10, 15))
    return (f'<svg viewBox="0 0 {W} {H}" width="100%" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif">'
            f'<line x1="{L}" y1="{H-B}" x2="{W-R}" y2="{H-B}" stroke="#E7E5E4"/>{yax}{"".join(bars)}'
            f'<text x="{(L+W-R)/2:.0f}" y="{H-6}" font-size="11" fill="#78716C" text-anchor="middle">training pairs a direct h-year model gets →</text>'
            f'</svg>')


HZ_MAPE_SVG = _hz_mape_svg()
PAIRS_SVG = _pairs_svg()

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
              "population to 2033 (detailed in §1), then combine into healthy person-years.",
         chip='<b>Supply</b> = healthy workers × working life'),
    dict(c="#D97706", kick="Level 2", title="Labour demand", icon="bag",
         desc="Forecast employment (rate × population) and job vacancies (anchored Beveridge) → jobs, "
              "scaled by the required length of service for a full pension.",
         chip='<b>Demand</b> = (employed + vacancies) × service'),
    dict(c="#166534", kick="Level 3", title="Balance — the headline", icon="scale",
         desc="Subtract the two stocks, by country × sex, to 2033 with Monte-Carlo uncertainty bands; "
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

# ---- "data behind this report" appendix: the Eurostat sources feeding the model ----
APPENDIX_CSS = appendix_css()
_sources = pd.DataFrame([
    ("hlth_hlye", "Life expectancy & healthy life years (LE, HLY)", "Level 1 — supply"),
    ("demo_pjan / demo_pjangroup", "Population by age & sex (working-age)", "Levels 1–2"),
    ("proj_23np", "Eurostat population projection (baseline + migration)", "Levels 1–3"),
    ("lfsi_dwl_a", "Expected duration of working life", "Level 1 — supply"),
    ("lfsa_egan", "Employment by sex & age", "Level 2 — demand"),
    ("jvs_q_r21", "Job vacancies (NACE Rev 2.1, quarterly→annual)", "Level 2 — demand"),
    ("une_rt_a", "Unemployment rate (Beveridge vacancy model)", "Level 2 — vacancies"),
    ("MISSOC / OECD Pensions at a Glance", "Statutory retirement age & required service", "Level 2 — demand"),
], columns=["Eurostat code / source", "Provides", "Used in"])
DLINK = data_link("Data sources behind the model")
APPENDIX = data_section(
    [("Eurostat datasets & external sources feeding the engine", _sources)],
    heading="Data behind this report",
    note="Every series the model consumes. Per-country × sex × year values are in the "
         "Level 1–3 reports' own data appendices.",
    filename="methodology_sources")

CSS = """
:root{--bg:#FAFAF9;--card:#FFFFFF;--ink:#292524;--mut:#78716C;--line:#E7E5E4;--acc:#166534;}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font:16px/1.65 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;padding:32px}
.wrap{max-width:880px;margin:0 auto}
h1{font-size:27px;margin:0 0 4px}h2{font-size:19px;margin:34px 0 10px}
.sub{color:var(--mut);margin:0 0 8px}
.fig{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px;margin:16px 0}
.cap{color:var(--mut);font-size:13px;margin-top:8px;text-align:center}
.g2{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:16px 0}
.g2 .fig{margin:0}.g2 .ft{font-weight:650;font-size:13.5px;margin-bottom:4px}
@media(max-width:680px){.g2{grid-template-columns:1fr}}
.swatch{display:inline-block;width:11px;height:11px;border-radius:2px;margin:0 4px -1px 0}
.note{color:var(--mut);font-size:14.5px;background:var(--card);border:1px solid var(--line);
border-radius:12px;padding:16px 18px;margin:14px 0}.note b{color:var(--ink)}
.formula{background:#F0FDF4;border:1px solid #166534;border-left:5px solid #166534;border-radius:12px;
padding:14px 20px;margin:14px 0;font-size:19px;font-weight:600;text-align:center;line-height:1.45}
.formula b{color:#166534}.formula .u{display:block;font-size:13px;color:var(--mut);font-weight:400;margin-top:5px}
.codebox{background:#1f2937;border-radius:10px;padding:16px 16px 14px;margin:14px 0;overflow-x:auto;position:relative}
.codebox code{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:14px;color:#86efac;white-space:pre}
.codebox .lbl{position:absolute;top:7px;right:12px;font-size:10px;letter-spacing:1px;text-transform:uppercase;color:#94a3b8}
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
/* scroll reveal: each block lights up as you reach it; level badges glow */
.reveal{opacity:.32;transform:translateY(16px);transition:opacity .6s ease,transform .6s ease}
.reveal.shown{opacity:1;transform:none}
.hnum{transition:box-shadow .4s ease}
.hnum.glow{animation:levelup 1.1s ease-out}
@keyframes levelup{0%{box-shadow:0 0 0 0 var(--gc,rgba(22,101,52,.55));transform:scale(1)}
35%{transform:scale(1.18)}100%{box-shadow:0 0 0 16px rgba(22,101,52,0);transform:scale(1)}}
@media(prefers-reduced-motion:reduce){.reveal{opacity:1;transform:none;transition:none}.hnum.glow{animation:none}}
"""

HTML = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Methodology — how the model works</title><style>{CSS}{APPENDIX_CSS}</style></head><body><div class="wrap">
<h1>Methodology — how the model works</h1>
<p class="sub">A transparent ensemble of simple statistical models + Monte-Carlo — deliberately
<b>no neural networks</b> (short series, defensibility required). Three diagrams describe the core model
(Levels 0–3); Levels 4–6 reuse the same engine for the health, retirement and macroeconomic extensions.</p>
{DLINK}

<h2>Method in one paragraph</h2>
<div class="note">Each driver series is forecast on its full history by an <b>ensemble of simple
models</b> (linear trend, damped Holt, drift, naive, AR(1)) — damping and the naive anchor stop saturating
rates from over-extrapolating, and the member weights adapt by forecast horizon. <b>Population</b> uses
Eurostat's projection <code>proj_23np</code>, calibrated to observed 2024. <b>Supply</b> = healthy working-age
people × expected working life; <b>demand</b> = (employed + vacancies) × required service. <b>Monte-Carlo bands</b>
combine model disagreement, out-of-sample backtest error and demographic uncertainty.</div>

<h2>The pipeline — Levels 0 → 3</h2>
<p class="sub">Where each step sits and what it produces. Levels 1–2 run every driver through the
ensemble engine (§1), then combine via the identities below; Level 3 subtracts the two.</p>
{ENGINE}

<h2><span class="hnum" style="background:#166534">1</span>Ensemble forecast engine</h2>
<p>For each time series (for every country × sex, over its full history) we do not rely on a
single model — we average <b>5 simple models</b>: <b>linear trend</b>, <b>damped Holt</b>, <b>drift</b>,
<b>naive</b> (last value held flat) and <b>AR(1)</b> mean-reversion. In the code that is exactly one line:</p>
<div class="codebox"><span class="lbl">src/forecast.py</span><code>DEFAULT_MEMBERS = ("linear", "holt", "drift", "naive", "ar1")</code></div>
<p>Damped Holt and the naive anchor guard against over-extrapolation (socio-economic rates saturate, they do
not grow linearly forever), while AR(1) pulls cyclical series back toward their long-run mean — and the member
weights adapt by forecast horizon (see below).</p>
<div class="fig">{svg1}</div>
<div class="note" style="border-left:4px solid #166534">👉 <b>Try it live:</b> the
<a href="ensemble_visualizer.html">interactive ensemble uncertainty visualizer</a> — drag the ensemble size and
sampling noise and watch a cloud of simple models (and their average) form the uncertainty band, exactly as
described here. No neural nets, just simple models + Monte-Carlo.</div>
<p>The uncertainty band (the amber area in the reports) is assembled from <b>three sources</b>, combined
in quadrature: (1) the <b>disagreement between the models</b>; (2) the <b>real out-of-sample
error from backtesting</b> — we re-forecast history and measure how far off we are; and (3) the
<b>demographic uncertainty</b> of the population. That is why the bands are a realistic <b>12–43%</b>
wide, not a falsely narrow ±5%.</p>
<p><b>On the supply side</b>, the engine forecasts <b>life expectancy</b>, the <b>healthy-life share
(HLY/LE)</b>, <b>working-life duration</b> and the <b>working-age population</b> to 2033, which are then
combined into healthy person-years.</p>
<div class="formula"><b>Supply</b> = healthy working-age people × expected working life
<span class="u">person-years</span></div>

<h2><span class="hnum" style="background:#166534">1b</span>Wouldn't separate 3/6/9-year models be more accurate? We tested it — no.</h2>
<p>A natural question: surely a model <i>dedicated</i> to the 9-year forecast would beat one general model? We
checked it directly. In a rolling-origin backtest over the smooth supply drivers, we compared our single
<b style="color:#166534">horizon-aware ensemble</b> against <b style="color:#B91C1C">separate "direct" models</b> —
one fitted specifically for each horizon (an OLS of the value h years ahead on today's value). The ensemble wins
at <b>every</b> horizon, and the gap <b>widens</b> the further out you go.</p>
<div class="g2">
<div class="fig"><div class="ft">Forecast error by horizon — ensemble vs separate models</div>{HZ_MAPE_SVG}
<div class="cap"><span class="swatch" style="background:#166534"></span>one horizon-aware ensemble
<span class="swatch" style="background:#B91C1C;margin-left:8px"></span>separate per-horizon models
<span class="swatch" style="background:#A8A29E;margin-left:8px"></span>naive floor — lower MAPE is better</div></div>
<div class="fig"><div class="ft">…because a dedicated long-horizon model <i>starves</i></div>{PAIRS_SVG}
<div class="cap">A separate <b>9-year</b> model can only learn from <b>{_PAIRS[8]}</b> (year, year+9) training pairs —
far too few, so it overfits and does worse exactly where you hoped it would help.</div></div>
</div>
<p>The reason is data, not cleverness: every extra year of horizon throws away another year of usable training
pairs ({_PAIRS[0]} → {_PAIRS[-1]}), so a long-horizon specialist is estimated from almost nothing and overfits.
The single ensemble pools the full history and stays close to the naive floor (the best achievable on these
near-random-walk drivers). One horizon-aware ensemble is the more accurate <i>and</i> more honest choice.
(See the <a href="model_validation_report.html">Model trust</a> report for the full error-by-horizon.)</p>

<h2><span class="hnum" style="background:#D97706">2</span>Building labour demand</h2>
<p>From the forecast components we build demand using the formula from the case brief. Population is
<b>not</b> extrapolated naively — we take Eurostat's official projection <code>proj_23np</code>,
calibrated to the observed 2024 value.</p>
<div class="fig">{svg2}</div>

<h2><span class="hnum" style="background:#475569">3</span>Building labour supply</h2>
<p>The same logic as demand, but with two health–demographic multipliers. Both multipliers —
the <b>healthy-years share (HLY ÷ LE)</b> and <b>expected working life</b> — are forecast with the
<b>same 5-model ensemble</b> from the first diagram. The result is in <b>person-years</b>, exactly
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

<h2>Levels 4–6 — open horizons (the same engine, reused)</h2>
<p>The three extension levels forecast different health–demographic quantities with the <b>same 5-model
ensemble</b>, then test — <b>honestly and descriptively</b> — whether each drives an economic outcome. These are
<b>relationships and an identity decomposition, not causal predictors</b>: where the link turns out to be ≈ 0,
we say so plainly rather than pretend to forecast it.</p>

<h2><span class="hnum" style="background:#B91C1C">4</span>Cost of unhealthy years</h2>
<p>The poor-health burden is population × the years lived in poor health (life expectancy minus healthy-life
years), by sex, summed and forecast to 2033. We then relate it to the <b>NACE-Q health &amp; social-work
sector's</b> value added: across countries it co-moves (mostly country size), but <b>within</b> a country over
time the elasticity is ≈ 0 — the sector tracks GDP, not the demographic burden.</p>
<div class="formula"><b>Burden</b> = Population × (LE − HLY)<span class="u">person-years lived in poor health</span></div>

<h2><span class="hnum" style="background:#D97706">5</span>Healthy retirement dividend</h2>
<p>Healthy years lived <i>beyond</i> the statutory retirement age (floored at zero), population-scaled, by sex,
forecast to 2033. Tested against <b>leisure / education / culture consumption</b> (COICOP CP09–11): cross-country
it co-moves, but within-country the link is ≈ 0 — consumption tracks household income, not the dividend.</p>
<div class="formula"><b>Dividend</b> = Population × max(0, HLY − retirement age)<span class="u">healthy person-years after retirement</span></div>

<h2><span class="hnum" style="background:#166534">6</span>Longevity in the macroeconomy</h2>
<p>Real GDP is decomposed by the identity <b>GDP = employment × productivity</b>; growth accounting splits each
country's projected growth into a <b>labour</b> channel (where longevity acts) and a <b>productivity</b> channel.
The reverse arrow — does <i>healthy</i> longevity lift productivity? — is absent: cross-country the correlation
has the wrong sign (a self-perceived-health / GALI artifact) and within a country it is ≈ 0.</p>
<div class="formula"><b>Real GDP</b> = Employment × Productivity<span class="u">growth = labour + productivity</span></div>

{APPENDIX}
<p class="foot">See also the <a href="model_validation_report.html">“Model trust”</a> report for the
backtest accuracy of this ensemble. · Code: <code>src/forecast.py</code>, <code>balance_forecast.py</code></p>
</div>
<script>
// Light up each section as it scrolls into view; pulse the level badge as you reach it.
(function(){{
  if(window.matchMedia && window.matchMedia('(prefers-reduced-motion:reduce)').matches) return;
  const sel='.wrap h2,.wrap p,.wrap .fig,.wrap .formula,.wrap .codebox,.wrap .g2,.wrap .note,.wrap ol,.wrap table,.wrap .engine';
  const els=[...document.querySelectorAll(sel)];
  els.forEach(el=>el.classList.add('reveal'));
  const io=new IntersectionObserver((entries)=>{{
    entries.forEach(e=>{{
      if(!e.isIntersecting) return;
      e.target.classList.add('shown');
      const badge=e.target.querySelector && e.target.querySelector('.hnum');
      if(badge){{
        const m=(badge.getAttribute('style')||'').match(/#[0-9a-fA-F]{{6}}/);
        badge.style.setProperty('--gc', (m?m[0]:'#166534')+'88');
        badge.classList.add('glow');
      }}
      io.unobserve(e.target);
    }});
  }},{{threshold:0.12, rootMargin:'0px 0px -7% 0px'}});
  els.forEach(el=>io.observe(el));
}})();
</script>
</body></html>"""

(OUT / "methodology_report.html").write_text(HTML, encoding="utf-8")
print(f"wrote outputs/methodology_report.html ({len(HTML)} bytes)")
