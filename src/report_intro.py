# -*- coding: utf-8 -*-
"""
Build outputs/conclusion.html — the synthesis / "so what" page: the headline
answer, key findings, the three policy levers infographic, honest limitations,
and links into the detailed reports and guided stories. Earthy theme, static.
"""
from __future__ import annotations
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from i18n import lang_css, lang_toggle  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
M = 1e6
WEST = ["DE", "FR", "CH", "NO"]
EAST = ["PL", "RO", "CZ", "BG"]
NAME = {"BG": "Bulgaria", "PL": "Poland", "CZ": "Czechia", "RO": "Romania",
        "DE": "Germany", "FR": "France", "NO": "Norway", "CH": "Switzerland"}

bf = pd.read_csv(OUT / "balance_forecast.csv")
so = pd.read_csv(OUT / "supply_observed.csv")
sf = pd.read_csv(OUT / "supply_forecast.csv")
df = pd.read_csv(OUT / "demand_forecast.csv")

b35 = bf[bf.year == 2033]
net = round(b35["balance"].sum() / M)
west_def = round(b35[b35.country.isin(WEST)]["balance"].sum() / M)
east_sur = round(b35[b35.country.isin(EAST)]["balance"].sum() / M)
by = (b35.groupby("country")["balance"].sum() / M)
worst, best = by.idxmin(), by.idxmax()
sup24 = round(so[so.year == 2024]["supply_realized"].sum() / M)
sup35 = round(sf[sf.year == 2033]["supply_realized"].sum() / M)
dem24 = round(so[so.year == 2024]["demand"].sum() / M)
dem35 = round(df[df.year == 2033]["demand"].sum() / M)
sup_chg = round((sup35 / sup24 - 1) * 100, 1)
dem_chg = round((dem35 / dem24 - 1) * 100, 1)

INFOGRAPHIC = """
<svg viewBox="0 0 960 384" width="100%" style="display:block;margin:6px 0 10px;font-family:inherit" xmlns="http://www.w3.org/2000/svg">
  <path d="M480,184 V342" fill="none" stroke="#475569" stroke-width="2.5"/>
  <path d="M334,236 H442 Q464,236 464,258 V342" fill="none" stroke="#15803D" stroke-width="2.5"/>
  <path d="M626,236 H518 Q496,236 496,258 V342" fill="none" stroke="#D97706" stroke-width="2.5"/>
  <circle cx="480" cy="342" r="4" fill="#292524"/>
  <text x="480" y="368" text-anchor="middle" font-size="13" fill="#78716C">Balanced labour market · 2033</text>
  <circle cx="480" cy="150" r="33" fill="#FFFFFF" stroke="#475569" stroke-width="2.5"/>
  <g transform="translate(480,150)" stroke="#475569" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round">
    <line x1="0" y1="-17" x2="0" y2="-12"/><circle cx="0" cy="-18" r="1.7" fill="#475569" stroke="none"/>
    <rect x="-10" y="-12" width="20" height="16" rx="3"/>
    <circle cx="-4" cy="-4" r="1.7" fill="#475569" stroke="none"/><circle cx="4" cy="-4" r="1.7" fill="#475569" stroke="none"/>
    <line x1="-10" y1="4" x2="-14" y2="9"/><line x1="10" y1="4" x2="14" y2="9"/>
  </g>
  <text x="480" y="52" text-anchor="middle" font-size="16" font-weight="700" fill="#475569">Decrease Labour Demand</text>
  <text x="480" y="73" text-anchor="middle" font-size="13" fill="#78716C">Invest in automation &amp; technology to</text>
  <text x="480" y="89" text-anchor="middle" font-size="13" fill="#78716C">reduce the need for human labour.</text>
  <circle cx="300" cy="236" r="33" fill="#FFFFFF" stroke="#15803D" stroke-width="2.5"/>
  <g transform="translate(300,236)" stroke="#15803D" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="-7" cy="-5" r="3.4"/><path d="M-13,8 a6 6 0 0 1 12 0"/>
    <circle cx="7" cy="-5" r="3.4"/><path d="M1,8 a6 6 0 0 1 12 0"/>
  </g>
  <text x="256" y="220" text-anchor="end" font-size="16" font-weight="700" fill="#15803D">Increase Labour Supply</text>
  <text x="256" y="241" text-anchor="end" font-size="13" fill="#78716C">Encourage participation, retention</text>
  <text x="256" y="257" text-anchor="end" font-size="13" fill="#78716C">&amp; migration to boost the workforce.</text>
  <circle cx="660" cy="236" r="33" fill="#FFFFFF" stroke="#D97706" stroke-width="2.5"/>
  <g transform="translate(660,236)" stroke="#D97706" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round">
    <path d="M-13,-3 L0,-9 L13,-3 L0,3 Z"/><path d="M0,3 V11"/><path d="M8,-0.5 V7 a8 3 0 0 1 -16 0 V-0.5"/>
  </g>
  <text x="704" y="220" text-anchor="start" font-size="16" font-weight="700" fill="#D97706">Maintain Balance</text>
  <text x="704" y="241" text-anchor="start" font-size="13" fill="#78716C">Focus on education &amp; training to</text>
  <text x="704" y="257" text-anchor="start" font-size="13" fill="#78716C">align skills with market needs.</text>
</svg>"""

CSS = """
:root{--bg:#FAFAF9;--card:#FFFFFF;--ink:#292524;--mut:#78716C;--line:#E7E5E4;--acc:#166534;
--up:#15803D;--down:#B91C1C;--slate:#475569;--mustard:#D97706;}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font:16px/1.6 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;padding:36px 24px}
.wrap{max-width:980px;margin:0 auto}
h1{font-size:28px;margin:0 0 6px}h2{font-size:20px;margin:34px 0 12px;border-bottom:1px solid var(--line);padding-bottom:6px}
.sub{color:var(--mut);margin:0 0 8px;max-width:780px}
.hero{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--acc);
border-radius:14px;padding:20px 22px;margin:18px 0;font-size:17px}
.kpis{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:18px 0}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px}
.kpi .v{font-size:23px;font-weight:700}.kpi .l{color:var(--mut);font-size:12px;margin-top:4px}
.cards{display:grid;grid-template-columns:repeat(2,1fr);gap:16px}
.find{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px 18px}
.find h3{margin:0 0 4px;font-size:16px}.find p{margin:0;color:var(--mut);font-size:14px}
.find .t{font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:.6px}
.lever{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-top:10px}
.lv{background:var(--card);border:1px solid var(--line);border-top:3px solid var(--c);border-radius:12px;padding:14px 16px}
.lv h3{margin:0 0 4px;font-size:15px;color:var(--c)}.lv p{margin:0;color:var(--mut);font-size:13.5px}
.note{color:var(--mut);font-size:14px;background:var(--card);border:1px solid var(--line);
border-radius:10px;padding:15px;margin-top:12px}.note b{color:var(--ink)}
.proc{margin:18px 0 6px}
.pstep{position:relative;padding:2px 0 20px 60px;border-left:2px solid var(--line);margin-left:18px}
.pstep:last-child{border-left-color:transparent;padding-bottom:2px}
.pnum{position:absolute;left:-19px;top:-3px;width:36px;height:36px;border-radius:50%;
background:#F5F5F0;border:2px solid var(--acc);color:var(--acc);font-weight:800;
display:grid;place-items:center;font-size:14px}
.pstep h3{margin:0 0 3px;font-size:16px}.pstep h3 .e{margin-right:8px;font-size:18px}
.pstep p{margin:0;color:var(--mut);font-size:14px;max-width:760px}.pstep code{color:var(--acc);font-size:12.5px}
a{color:var(--acc)}.links{display:flex;gap:12px;flex-wrap:wrap;margin-top:10px}
.links a{background:var(--card);border:1px solid var(--line);border-radius:20px;padding:8px 15px;
text-decoration:none;font-size:14px;font-weight:600}.links a:hover{border-color:var(--acc)}
.foot{color:var(--mut);font-size:13px;margin-top:30px}code{color:var(--acc)}
"""

# ---- "how we got here": the data-to-answer pipeline ----
STEPS = [
    ("📥", "Gather the raw evidence", "Събери суровите данни",
     "Pull official series for all 8 countries, by sex, back to ~2011 — population, employment &amp; unemployment, "
     "job vacancies, life expectancy and healthy-life years, retirement rules and government spending — mostly from "
     "<b>Eurostat</b>, plus OECD.AI / OWID for the AI signal.",
     "Изтегли официални редове за всичките 8 държави, по пол, назад до ~2011 г. — население, заетост и безработица, "
     "свободни работни места, продължителност на живота и здрави години живот, пенсионни правила и държавни разходи — "
     "предимно от <b>Евростат</b>, плюс OECD.AI / OWID за сигнала за ИИ."),
    ("🧹", "Harmonize into one panel", "Хармонизирай в един панел",
     "Clean and align everything into a single tidy table (country × sex × year): reconcile units, bridge definition "
     "changes and line up a common timeline — one source of truth in <code>panel.parquet</code>.",
     "Изчисти и подреди всичко в една таблица (държава × пол × година): уеднакви мерните единици, преодолей промени в "
     "дефинициите и подреди обща времева линия — един източник на истина в <code>panel.parquet</code>."),
    ("🧱", "Build the person-year drivers", "Изгради двигателите в човеко-години",
     "Turn raw series into the ingredients the identities need — <b>healthy share</b> (HLY ÷ LE), <b>expected working "
     "life</b>, <b>employment rate</b> and <b>vacancy rate</b> — the dials that convert headcounts into working-years.",
     "Превърни суровите редове в съставките, нужни на тъждествата — <b>здравословен дял</b> (ЗГЖ ÷ ОПЖ), <b>очакван "
     "трудов живот</b>, <b>коефициент на заетост</b> и <b>коефициент на свободни места</b> — лостовете, които "
     "превръщат броя хора в работни години."),
    ("🔮", "Forecast each driver to 2033", "Прогнозирай всеки двигател до 2033",
     "A small ensemble of transparent models (linear, Holt, drift, naïve, AR(1)) extends each driver, with Monte-Carlo "
     "bands for uncertainty — deliberately <b>no neural networks</b>. Population uses Eurostat's own projection, "
     "calibrated to observed 2024.",
     "Малък ансамбъл от прозрачни модели (линеен, Holt, дрейф, наивен, AR(1)) удължава всеки двигател, с Монте-Карло "
     "ленти за несигурност — умишлено <b>без невронни мрежи</b>. Населението използва собствената прогноза на Евростат, "
     "калибрирана към наблюдаваната 2024 г."),
    ("⚙️", "Compose supply, demand &amp; balance", "Сглоби предлагане, търсене и баланс",
     "Feed the forecast drivers through the person-year identities to assemble <b>supply</b>, <b>demand</b> and their "
     "difference — per country × sex, every year to 2033, with the uncertainty bands carried through.",
     "Прекарай прогнозните двигатели през тъждествата в човеко-години, за да сглобиш <b>предлагане</b>, <b>търсене</b> и "
     "разликата им — по държава × пол, всяка година до 2033 г., с пренесените ленти на несигурност."),
    ("🔍", "Stress-test the engine", "Подложи двигателя на тест",
     "Before trusting a number, backtest it: rolling-origin, leakage-safe, a COVID holdout, skill-versus-naïve, and "
     "now <b>bootstrap confidence intervals</b> — so every result arrives with how far it can be trusted.",
     "Преди да се довериш на число, го тествай назад: с плъзгащ произход, без изтичане, COVID тест, умение-срещу-наивно "
     "и вече <b>бутстрап доверителни интервали</b> — така всеки резултат идва с това докъде може да му се вярва."),
    ("🧭", "Read it &amp; translate to choices", "Прочети и преведи в избори",
     "Turn the stock into meaning — the East–West headline, the three policy levers, the what-if sandbox, and Levels "
     "4–6 (health burden, retirement dividend, macroeconomy) read <b>descriptively</b>, never as causation.",
     "Превърни величината в смисъл — заглавието Изток–Запад, трите лоста на политиката, пясъчника „какво-ако“ и Нива "
     "4–6 (тежест на здравето, пенсионен дивидент, макроикономика), четени <b>описателно</b>, никога като причинност."),
]
PROC = '<div class="proc">' + "".join(
    f'<div class="pstep"><div class="pnum">{i}</div>'
    f'<h3><span class="e">{ic}</span><span lang="en">{en_t}</span><span lang="bg">{bg_t}</span></h3>'
    f'<p><span lang="en">{en_b}</span><span lang="bg">{bg_b}</span></p></div>'
    for i, (ic, en_t, bg_t, en_b, bg_b) in enumerate(STEPS, 1)
) + "</div>"

netcol = "var(--up)" if net >= 0 else "var(--down)"
HTML = f"""<!doctype html><html lang="bg" data-lang="bg"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Introduction — balancing longevity &amp; the labour market by 2033</title>
<style>{CSS}{lang_css()}</style></head><body>{lang_toggle()}<div class="wrap">
<h1 lang="en">Introduction — can Europe balance its labour market by 2033?</h1>
<h1 lang="bg">Въведение — може ли Европа да балансира пазара си на труда до 2033 г.?</h1>
<p class="sub" lang="en">Europe is ageing: populations are growing older and, across much of the East, shrinking. As
that happens, can each economy still supply the labour its jobs require? This study answers that by turning
demographic averages into <b>human-working-years</b> — a stock comparable with jobs — for 8 countries, by sex,
to 2033.</p>
<p class="sub" lang="bg">Европа застарява: населението остарява и в голяма част от Изтока намалява. При това положение
може ли всяка икономика да осигури труда, който работните ѝ места изискват? Това изследване отговаря, като
превръща демографските средни стойности в <b>човеко-работни години</b> — величина, съпоставима с работните места —
за 8 държави, по пол, до 2033 г.</p>

<div class="hero" lang="en"><b>The challenge.</b> Headcounts and life-expectancy averages can't be weighed against jobs,
so we build a <b>person-year engine</b>: <b>supply</b> = healthy working-age people × expected working life;
<b>demand</b> = jobs × required length of service; <b>balance</b> = the difference, in human-working-years. The
question is whether that balance holds — and if not, where it breaks and what moves it.</div>
<div class="hero" lang="bg"><b>Предизвикателството.</b> Броят на хората и средната продължителност на живота не могат да се
претеглят спрямо работните места, затова изграждаме <b>двигател на човеко-години</b>: <b>предлагане</b> = здрави
хора в трудоспособна възраст × очакван трудов живот; <b>търсене</b> = работни места × изискван стаж; <b>баланс</b>
= разликата, в човеко-работни години. Въпросът е дали този баланс се запазва — и ако не, къде се къса и какво го движи.</div>

<h2><span lang="en">How we measure it</span><span lang="bg">Как го измерваме</span></h2>
<p class="sub" lang="en">Each driver is forecast on its full history by a small ensemble of transparent models
(deliberately <b>no neural networks</b>) with Monte-Carlo uncertainty, then combined through the identities
below. Population uses Eurostat's own projection, calibrated to observed 2024.</p>
<p class="sub" lang="bg">Всеки показател се прогнозира върху цялата си история от малък ансамбъл от прозрачни модели
(умишлено <b>без невронни мрежи</b>) с Монте-Карло несигурност, после се комбинира чрез тъждествата по-долу.
Населението използва собствената прогноза на Eurostat, калибрирана към наблюдаваната 2024 г.</p>
<div class="lever">
<div class="lv" style="--c:var(--up)"><h3 lang="en">1 · Supply</h3><h3 lang="bg">1 · Предлагане</h3><p lang="en">Healthy working-age people × expected working life — the longevity dividend in person-years.</p><p lang="bg">Здрави хора в трудоспособна възраст × очакван трудов живот — дивидентът от дълголетие в човеко-години.</p></div>
<div class="lv" style="--c:var(--mustard)"><h3 lang="en">2 · Demand</h3><h3 lang="bg">2 · Търсене</h3><p lang="en">(Employed + vacancies) × required length of service — the career-years jobs require.</p><p lang="bg">(Заети + свободни места) × изискван стаж — кариерните години, които работните места изискват.</p></div>
<div class="lv" style="--c:var(--slate)"><h3 lang="en">3 · Balance</h3><h3 lang="bg">3 · Баланс</h3><p lang="en">Supply − demand, by country × sex, to 2033 with honest bands — the headline.</p><p lang="bg">Предлагане − търсене, по държава × пол, до 2033 г. с честни ленти — заглавието.</p></div>
</div>
<p class="sub" style="margin-top:14px" lang="en">Two further levels read the human side of longevity, reported <b>descriptively</b> — patterns, not
causal mechanisms: <b>Level 4</b> measures the <b>poor-health burden</b> (population × the years lived in
poor health, LE − HLY) and tests whether it drives the health sector; <b>Level 5</b> measures the
<b>healthy-retirement dividend</b> (population × healthy years left after the retirement age, HLY − retire)
and tests whether it lifts leisure, education &amp; culture spending. In both, the within-country link is
≈ 0 — they track GDP and income, not demography.</p>
<p class="sub" style="margin-top:14px" lang="bg">Още две нива четат човешката страна на дълголетието, представени <b>описателно</b> — закономерности,
не причинно-следствени механизми: <b>Ниво 4</b> измерва <b>тежестта от лошо здраве</b> (население × годините,
изживени в лошо здраве, ОПЖ − ЗГЖ) и проверява дали тя движи здравния сектор; <b>Ниво 5</b> измерва
<b>дивидента от здраво пенсиониране</b> (население × здравите години след пенсионната възраст, ЗГЖ − пенс.) и
проверява дали повишава разходите за свободно време, образование и култура. И при двете връзката в рамките на
държавата е ≈ 0 — следват БВП и доходите, не демографията.</p>

<h2><span lang="en">How we got here — from raw data to the answer</span><span lang="bg">Как стигнахме дотук — от сурови данни до отговора</span></h2>
<p class="sub" lang="en">Seven steps take public statistics to the headline below. Each is transparent and reproducible — the same
pipeline, run end to end, produces every number on this site.</p>
<p class="sub" lang="bg">Седем стъпки превеждат публичната статистика до заглавието по-долу. Всяка е прозрачна и възпроизводима —
същият процес, пуснат от край до край, произвежда всяко число на този сайт.</p>
{PROC}

<h2><span lang="en">The headline, previewed</span><span lang="bg">Заглавието, накратко</span></h2>
<div class="hero" style="border-left-color:{netcol}" lang="en"><b>Roughly balanced in aggregate — but not where it's
needed.</b> Total supply and demand both stay near {sup35:,}M and {dem35:,}M human-working-years (a net balance
of <b style="color:{netcol}">{net:+,}M</b>), hiding a sharp <b>East–West divide</b>: a West/EFTA shortage of
<b style="color:var(--down)">{west_def:+,}M</b> against an East surplus of
<b style="color:var(--up)">{east_sur:+,}M</b>.</div>
<div class="hero" style="border-left-color:{netcol}" lang="bg"><b>Сумарно горе-долу балансиран — но не там, където
трябва.</b> Общото предлагане и търсене остават близо до {sup35:,} млн. и {dem35:,} млн. човеко-работни години
(нетен баланс от <b style="color:{netcol}">{net:+,} млн.</b>), скривайки рязко <b>разделение Изток–Запад</b>:
недостиг Запад/ЕАСТ от <b style="color:var(--down)">{west_def:+,} млн.</b> срещу излишък на Изток от
<b style="color:var(--up)">{east_sur:+,} млн.</b></div>

<div class="kpis">
<div class="kpi"><div class="v" style="color:{netcol}">{net:+,}M</div><div class="l"><span lang="en">Net balance 2033 (human-working-years)</span><span lang="bg">Нетен баланс 2033 (човеко-работни години)</span></div></div>
<div class="kpi"><div class="v" style="color:var(--down)">{west_def:+,}M</div><div class="l"><span lang="en">West/EFTA shortage — deepest in {NAME[worst]}</span><span lang="bg">Недостиг Запад/ЕАСТ — най-дълбок в {NAME[worst]}</span></div></div>
<div class="kpi"><div class="v" style="color:var(--up)">{east_sur:+,}M</div><div class="l"><span lang="en">East surplus — largest in {NAME[best]}</span><span lang="bg">Излишък на Изток — най-голям в {NAME[best]}</span></div></div>
</div>

<h2><span lang="en">What we find</span><span lang="bg">Какво откриваме</span></h2>
<div class="cards">
<div class="find"><div class="t" style="color:var(--acc)"><span lang="en">The headline</span><span lang="bg">Заглавно</span></div>
<h3 lang="en">A balanced total, an unbalanced map</h3><h3 lang="bg">Балансиран сбор, небалансирана карта</h3>
<p lang="en">Net supply ≈ demand for the 8 countries combined, but {NAME[best]}'s reserve roughly offsets
{NAME[worst]}'s, France's and Switzerland's shortfalls — the demographic basis of West-bound migration.</p>
<p lang="bg">Нетно предлагане ≈ търсене за 8-те държави заедно, но резервът на {NAME[best]} горе-долу компенсира
недостига на {NAME[worst]}, Франция и Швейцария — демографската основа на миграцията на Запад.</p></div>
<div class="find"><div class="t" style="color:var(--acc)"><span lang="en">Supply</span><span lang="bg">Предлагане</span></div>
<h3 lang="en">The longevity dividend holds the line</h3><h3 lang="bg">Дивидентът от дълголетие държи фронта</h3>
<p lang="en">Working-age populations shrink, yet supply is near-flat ({sup24:,}→{sup35:,}M, {sup_chg:+.1f}%): healthier,
longer working lives and rising participation offset the loss. It is the supply lever already in motion.</p>
<p lang="bg">Населението в трудоспособна възраст намалява, но предлагането е почти равно ({sup24:,}→{sup35:,} млн.,
{sup_chg:+.1f}%): по-здравият, по-дълъг трудов живот и нарастващото участие компенсират загубата. Това е лостът на
предлагането, който вече е задействан.</p></div>
<div class="find"><div class="t" style="color:var(--acc)"><span lang="en">Demand</span><span lang="bg">Търсене</span></div>
<h3 lang="en">Broadly flat, ageing-tilted</h3><h3 lang="bg">Като цяло равно, с уклон към застаряване</h3>
<p lang="en">Jobs × required service stays close to {dem24:,}→{dem35:,}M ({dem_chg:+.1f}%). Demand doesn't run away;
the imbalance comes from where the working-age people are, not from an explosion in labour needs.</p>
<p lang="bg">Работни места × изискван стаж остава близо до {dem24:,}→{dem35:,} млн. ({dem_chg:+.1f}%). Търсенето не
избягва; дисбалансът идва от това къде са хората в трудоспособна възраст, не от взрив в нуждата от труд.</p></div>
<div class="find"><div class="t" style="color:var(--acc)"><span lang="en">Honesty</span><span lang="bg">Честност</span></div>
<h3 lang="en">The balance is a direction, not a point</h3><h3 lang="bg">Балансът е посока, не точка</h3>
<p lang="en">It is a small difference of two large forecasts, so its relative error is amplified. Read it as a
<b>structural East-surplus / West-shortage signal with wide bands</b> — validated by a leakage-safe backtest.</p>
<p lang="bg">Той е малка разлика на две големи прогнози, затова относителната му грешка е усилена. Четете го като
<b>структурен сигнал излишък-Изток / недостиг-Запад с широки ленти</b> — валидиран чрез бектест без изтичане.</p></div>
</div>

<h2><span lang="en">Three levers that could balance the market</span><span lang="bg">Три лоста, които биха могли да балансират пазара</span></h2>
<p class="sub" lang="en">Whatever the gap turns out to be, only three families of policy move it — each maps to a term in
the supply–demand identity. This study quantifies how much each lever would have to do.</p>
<p class="sub" lang="bg">Каквато и да се окаже разликата, само три семейства политики я движат — всяко съответства на член
от тъждеството предлагане–търсене. Това изследване количествено определя колко трябва да направи всеки лост.</p>
{INFOGRAPHIC}
<div class="lever">
<div class="lv" style="--c:var(--up)"><h3 lang="en">Increase supply</h3><h3 lang="bg">Увеличи предлагането</h3><p lang="en">Raise participation (esp. women &amp; older
workers), retain healthy 55–70s, and use net migration — the fastest dials, and where the East's surplus sits.</p><p lang="bg">Повиши участието (особено жени и по-възрастни
работници), задръж здравите 55–70-годишни и използвай нетна миграция — най-бързите лостове, и там, където е излишъкът на Изтока.</p></div>
<div class="lv" style="--c:var(--slate)"><h3 lang="en">Ease demand</h3><h3 lang="bg">Намали търсенето</h3><p lang="en">Automation and productivity lower the human
hours each job needs — the slow, structural lever that reduces required labour rather than adding workers.</p><p lang="bg">Автоматизацията и производителността намаляват човешките
часове, които всяко работно място изисква — бавният, структурен лост, който намалява нужния труд, вместо да добавя работници.</p></div>
<div class="lv" style="--c:var(--mustard)"><h3 lang="en">Maintain balance</h3><h3 lang="bg">Поддържай баланс</h3><p lang="en">Education, training and retirement-age /
service-length policy align skills and careers with need — and convert a geographic surplus into usable supply.</p><p lang="bg">Образованието, обучението и политиката за пенсионна
възраст / дължина на стажа съгласуват уменията и кариерите с нуждата — и превръщат географския излишък в използваемо предлагане.</p></div>
</div>

<h2><span lang="en">What to keep in mind</span><span lang="bg">Какво да имаме предвид</span></h2>
<div class="note" lang="en">
• Forecasts run to <b>2033</b> — a policy baseline, shorter than a full pension/ageing horizon.<br>
• <b>Supply is a potential ceiling</b> (net of health and working-life length, before skills mismatch and frictions).<br>
• <b>Healthy-life years</b> (HLY) and <b>vacancies</b> are the weak drivers — both near-random-walk; modelled honestly at their accuracy ceiling.<br>
• Population is Eurostat's own projection (<code>proj_23np</code>), calibrated to 2024; migration is the biggest swing factor.<br>
• Levels 4–6 (health-cost, retirement-dividend, and the macroeconomy) are descriptive relationships and an
identity decomposition, not causal mechanisms.</div>
<div class="note" lang="bg">
• Прогнозите стигат до <b>2033 г.</b> — политическа база, по-къса от пълен пенсионен/застаряващ хоризонт.<br>
• <b>Предлагането е потенциален таван</b> (нето от здраве и дължина на трудовия живот, преди несъответствие на уменията и фрикции).<br>
• <b>Здравите години живот</b> (ЗГЖ) и <b>свободните места</b> са слабите показатели — и двете близо до случаен ход; моделирани честно при тавана на точността им.<br>
• Населението е собствената прогноза на Eurostat (<code>proj_23np</code>), калибрирана към 2024 г.; миграцията е най-големият променлив фактор.<br>
• Нива 4–6 (цена на здравето, пенсионен дивидент и макроикономиката) са описателни връзки и
декомпозиция на тъждество, не причинно-следствени механизми.</div>

<h2><span lang="en">Explore the analysis</span><span lang="bg">Разгледайте анализа</span></h2>
<p class="sub" style="margin-bottom:8px"><span lang="en">Each level opens its guided story with a one-tab switch to the full report.</span><span lang="bg">Всяко ниво отваря водената си презентация с превключване с един раздел към пълния доклад.</span></p>
<div class="links">
<a href="level1.html">👥 L1 Supply</a>
<a href="level2.html">💼 L2 Demand</a>
<a href="level3.html">⚖️ L3 Balance</a>
<a href="level4.html">🏥 L4 Cost</a>
<a href="level5.html">🌅 L5 Dividend</a>
<a href="level6.html">🌍 L6 Macroeconomy</a>
<a href="whatif.html">🎚️ What-if sandbox</a>
<a href="model_validation_report.html">🔍 Model trust</a>
<a href="methodology_report.html">🧭 Methodology</a>
</div>
<p class="foot"><a href="../index.html"><span lang="en">← Back to overview</span><span lang="bg">← Обратно към обзора</span></a> · src/report_intro.py</p>
</div></body></html>"""

(OUT / "introduction.html").write_text(HTML, encoding="utf-8")
print(f"wrote outputs/introduction.html  net {net:+}M (West {west_def:+}M, East {east_sur:+}M)")
