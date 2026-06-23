# -*- coding: utf-8 -*-
"""
Methodology report — how the model works (3 diagrams + Bulgarian narrative).
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
    box(240, 18, 200, 52, "Времева редица", "история по държава × пол", "gray"),
    arrow(320, 70, 120, 100, "a1"), arrow(333, 70, 258, 100, "a1"),
    arrow(347, 70, 422, 100, "a1"), arrow(360, 70, 560, 100, "a1"),
    box(19, 104, 150, 56, "Линеен тренд", "OLS регресия", "blue"),
    box(183, 104, 150, 56, "Затихващ Holt", "изглажда тренда", "teal"),
    box(347, 104, 150, 56, "Дрейф", "случ. блуждаене", "amber"),
    box(511, 104, 150, 56, "Наивен", "последна стойност", "gray"),
    arrow(94, 160, 300, 204, "a1"), arrow(258, 160, 328, 204, "a1"),
    arrow(422, 160, 352, 204, "a1"), arrow(586, 160, 380, 204, "a1"),
    box(215, 206, 250, 52, "Средна прогноза (ансамбъл)", "= средното от 4-те модела", "green"),
    arrow(340, 258, 340, 294, "a1"),
    box(130, 296, 420, 64, "Монте Карло × 1000 + backtest грешка",
        "точкова прогноза + 80% доверителна лента", "purple"),
])
svg1 = svg(680, 384, "a1", d1)

# ---- Diagram 2: demand construction ----
d2 = "".join([
    box(150, 20, 380, 56, "Население 15–64", "Eurostat proj_23np · калибрирано към 2024", "blue"),
    arrow(340, 76, 340, 108, "a2"),
    box(150, 112, 380, 56, "Заетост", "= население × коефициент на заетост (прогноза)", "teal"),
    arrow(340, 168, 340, 200, "a2"),
    box(150, 204, 380, 56, "Работни места", "= заетост + свободни места (вакансии)", "amber"),
    arrow(340, 260, 340, 292, "a2"),
    box(150, 296, 380, 56, "Търсене на труд — човекогодини", "= работни места × изискуем стаж (MISSOC)", "green"),
])
svg2 = svg(680, 372, "a2", d2)

# ---- Diagram 3: supply construction ----
d3 = "".join([
    box(150, 24, 380, 56, "Население 15–64", "Eurostat proj_23np · калибрирано към 2024", "blue"),
    arrow(340, 80, 340, 120, "a3"),
    box(150, 124, 380, 56, "Здрави работоспособни хора", "= население × дял здрави години (HLY ÷ LE)", "teal"),
    arrow(340, 180, 340, 220, "a3"),
    box(150, 224, 380, 56, "Предлагане на труд — човекогодини", "= здрави хора × очаквана трудова кариера", "green"),
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
"""

HTML = f"""<!doctype html><html lang="bg"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Методология — как работи моделът</title><style>{CSS}</style></head><body><div class="wrap">
<h1>Методология — как работи моделът</h1>
<p class="sub">Прозрачен ансамбъл от прости статистически модели + Монте Карло — съзнателно
<b>без невронни мрежи</b> (кратки редици, нужна е защитимост). Три диаграми описват целия модел.</p>

<h2>1 · Ансамблов прогнозен двигател</h2>
<p>За всяка времева редица (за всяка държава × пол, върху цялата история) не разчитаме на
един модел, а осредняваме <b>4 прости модела</b>. Затихващият Holt и наивната котва пазят от
свръх-екстраполация — социално-икономическите норми се насищат, не растат линейно вечно.</p>
<div class="fig">{svg1}</div>
<p>Лентата на несигурност (жълтото поле в отчетите) се сглобява от <b>три източника</b>, събрани
«в квадратура»: (1) <b>разминаването между четирите модела</b>; (2) <b>реалната out-of-sample
грешка от backtest</b> — преогнозяваме историята назад и мерим колко грешим; и (3) <b>демографската
несигурност</b> на населението. Затова лентите вече са широки <b>12–43%</b>, а не фалшиво тесните ±5%.</p>

<h2>2 · Сглобяване на търсенето на труд</h2>
<p>От прогнозираните компоненти изграждаме търсенето по формулата от заданието. Населението
<b>не</b> се екстраполира наивно — взима се официалната прогноза на Eurostat <code>proj_23np</code>,
калибрирана към наблюдаваната 2024 г.</p>
<div class="fig">{svg2}</div>

<h2>3 · Сглобяване на предлагането на труд</h2>
<p>Същата логика като при търсенето, но с два «здравно-демографски» множителя. Двата множителя —
<b>«дял здрави години» (HLY ÷ LE)</b> и <b>«очаквана трудова кариера»</b> — се прогнозират със
<b>същия 4-моделен ансамбъл</b> от първата диаграма. Резултатът е в <b>човекогодини</b>, точно
както търсенето — затова двете са пряко сравними.</p>
<div class="fig">{svg3}</div>

<h2>Заедно — целият модел</h2>
<ol>
<li><b>Ансамблов прогнозен двигател</b> — как се прогнозира една редица.</li>
<li><b>Търсене</b> = работни места × изискуем стаж.</li>
<li><b>Предлагане</b> = здрави работоспособни × трудова кариера.</li>
</ol>
<p><b>Ниво 3</b> просто изважда: <b>Баланс = Предлагане − Търсене</b> (в човекогодини) — заглавният
резултат, визуализиран в отчета за баланса.</p>

<p class="foot">Виж и отчета <a href="model_validation_report.html">«Доверие към модела»</a> за
backtest точността на този ансамбъл. · Код: <code>src/forecast.py</code>, <code>balance_forecast.py</code></p>
</div></body></html>"""

(OUT / "methodology_report.html").write_text(HTML, encoding="utf-8")
print(f"wrote outputs/methodology_report.html ({len(HTML)} bytes)")
