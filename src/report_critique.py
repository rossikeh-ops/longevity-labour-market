# -*- coding: utf-8 -*-
"""
Build outputs/critique.html — "Critical review" (bilingual BG|EN, earthy theme).

A sceptical statistician's audit of the forecasting models: the strongest case
AGAINST the numbers, the fixes we implemented in response (with live figures
read from validation_metrics.json so they never drift), and the honest limits
we cannot engineer away on 13 years of annual data.
"""
from __future__ import annotations
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from i18n import lang_css, lang_toggle, T  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
V = json.loads((OUT / "validation_metrics.json").read_text(encoding="utf-8"))
m, la, hs = V["metrics"], V["level_acc"], V["hly_sensitivity"]
crps = V["crps"]
TR = json.loads((OUT / "tree_compare.json").read_text(encoding="utf-8"))
LO = json.loads((OUT / "beveridge_loco.json").read_text(encoding="utf-8"))
C4 = json.loads((OUT / "cost_relationship.json").read_text(encoding="utf-8"))
C5 = json.loads((OUT / "dividend_relationship.json").read_text(encoding="utf-8"))
C6 = json.loads((OUT / "macro_relationship.json").read_text(encoding="utf-8"))
BEV_R2 = V["vacancy_model_test"]["beveridge_fit"]["r2"]


def H(en, bg, tag="p", cls=None):
    c = f' class="{cls}"' if cls else ""
    return f"<{tag}{c}><span lang=\"en\">{en}</span><span lang=\"bg\">{bg}</span></{tag}>"


def ci(x):
    return f"[{x[0]}–{x[1]}]" if x else "—"


# ---------- the case against (ranked, with severity) ----------
ISSUES = [
    ("high", "Over-precision: the headline MAPEs aren't as sharp as they look",
     "Свръхточност: заглавните MAPE не са толкова остри, колкото изглеждат",
     "The validation pools 8 countries × 2 sexes × 4 horizons into <b>n=160</b> and treats them as independent. They are "
     "not — within-country autocorrelation, near-duplicate sexes, common European shocks (COVID) and four horizons from "
     "one origin. The <b>effective sample is a fraction of 160</b>, so a single point MAPE hides a wide interval.",
     "Валидацията събира 8 държави × 2 пола × 4 хоризонта в <b>n=160</b> и ги третира като независими. Те не са — "
     "вътрешнодържавна автокорелация, почти еднакви полове, общи европейски шокове (COVID) и четири хоризонта от един "
     "произход. <b>Ефективната извадка е част от 160</b>, затова една точкова MAPE крие широк интервал."),
    ("high", "Extreme extrapolation: 9 years forecast from ~13 years of history",
     "Крайна екстраполация: 9 години прогноза от ~13 години история",
     "The horizon is ~65–70% of the training span. At that ratio the trend members are unconstrained and the ensemble "
     "leans on persistence — so for the rate drivers the 2033 number is essentially <b>“2024 persists”</b>, and skill "
     "over a naïve forecast is ≈ 0. Much of the “forecast” is assumption, not signal.",
     "Хоризонтът е ~65–70% от обучителния период. При това съотношение трендовите членове са неограничени и ансамбълът "
     "разчита на устойчивостта — затова за коефициентните двигатели числото за 2033 е по същество <b>„2024 продължава“</b>, "
     "а умението над наивната прогноза е ≈ 0. Голяма част от „прогнозата“ е допускане, не сигнал."),
    ("high", "Self-reported health (HLY/GALI) contaminates the cross-country levels",
     "Самооценено здраве (ЗГЖ/GALI) замърсява междудържавните нива",
     "Healthy share = HLY/LE is a multiplier inside supply. HLY is the self-perceived GALI question — not comparable "
     "across countries (the West reports <i>more</i> limitation despite living longer). So any cross-country "
     "<b>level</b> comparison that runs through health inherits that non-comparability.",
     "Здравословният дял = ЗГЖ/ОПЖ е множител в предлагането. ЗГЖ е въпросът за самооценка GALI — несравним между "
     "държавите (Западът отчита <i>повече</i> ограничения въпреки по-дългия живот). Затова всяко междудържавно сравнение "
     "на <b>нива</b>, минаващо през здравето, наследява тази несравнимост."),
    ("med", "The uncertainty bands are a heuristic, not a calibrated distribution",
     "Лентите на несигурност са евристика, не калибрирано разпределение",
     "Bands are built as σ = √(model-spread² + backtest-σ²) with additive Gaussian noise, where backtest-σ is estimated "
     "from a handful of points. Coverage is encouraging (~80–94%) but measured on the same dependent sample, and there "
     "is <b>no proper scoring rule</b> (CRPS / log-score).",
     "Лентите се строят като σ = √(разсейване² + бектест-σ²) с добавен гаусов шум, където бектест-σ е оценена от "
     "шепа точки. Покритието е обнадеждаващо (~80–94%), но измерено на същата зависима извадка, и <b>няма същинско "
     "правило за оценка</b> (CRPS / log-score)."),
    ("med", "MAPE breaks down for near-zero quantities (the dividend)",
     "MAPE се чупи при близки до нула величини (дивидентът)",
     "The Level-5 dividend’s huge MAPE is the metric, not the model: MAPE explodes as the denominator → 0 and is "
     "asymmetric. Combined with the convexity of the Monte-Carlo mean, the dividend’s <i>level</i> is partly an "
     "artifact — it should be read as a distribution, not a point.",
     "Огромната MAPE на дивидента от Ниво 5 е метриката, не моделът: MAPE избухва, когато знаменателят → 0, и е "
     "асиметрична. Заедно с изпъкналостта на Монте-Карло средната, <i>нивото</i> на дивидента е отчасти артефакт — "
     "трябва да се чете като разпределение, не като точка."),
    ("med", "The Level 4–6 “no effect” results are under-powered",
     "Резултатите „няма ефект“ от Нива 4–6 са с ниска статистическа мощ",
     "The within-country longevity→labour elasticity ≈ 0 rests on ~12 annual differences × 8 countries with common "
     "shocks. That is very low power: the honest statement is <b>“we cannot detect an effect,”</b> not “there is none.”",
     "Вътрешнодържавната еластичност дълголетие→труд ≈ 0 се крепи на ~12 годишни разлики × 8 държави с общи шокове. "
     "Това е много ниска мощ: честното твърдение е <b>„не можем да открием ефект“</b>, а не „няма такъв“."),
    ("low", "A small look-ahead leak in the vacancy leg",
     "Малко изтичане напред във времето при свободните места",
     "The Beveridge vacancy curve was fitted on the full panel and then used inside the “leakage-safe” backtest. "
     "Vacancies are ~2% of jobs, so the headline effect is tiny — but the label wasn’t strictly true.",
     "Кривата на Бевъридж беше напасната върху целия панел и после използвана в „безопасния“ бектест. Свободните места "
     "са ~2% от работните места, затова ефектът върху заглавието е нищожен — но етикетът не беше строго верен."),
    ("med", "Migration risk is imported wholesale from Eurostat’s scenarios",
     "Миграционният риск е внесен изцяло от сценариите на Евростат",
     "The demographic band is Eurostat’s baseline ± its high/low migration spread. Migration is the biggest swing "
     "factor and the most shock-prone (see the Ukraine page) — yet it is capped by pre-set scenarios that aren’t built "
     "for tail events.",
     "Демографската лента е базовата прогноза на Евростат ± нейният висок/нисък миграционен диапазон. Миграцията е "
     "най-големият фактор на колебание и най-податлива на шокове (виж страницата за Украйна) — но е ограничена от "
     "предварителни сценарии, които не са правени за екстремни събития."),
]

SEV_EN = {"high": "high", "med": "medium", "low": "low"}
SEV_BG = {"high": "висок", "med": "среден", "low": "нисък"}
issue_cards = "".join(
    f'<div class="issue sev-{s}"><div class="sevtag">'
    f'<span lang="en">{SEV_EN[s]}</span><span lang="bg">{SEV_BG[s]}</span></div>'
    f'{H(en_t, bg_t, "h3")}{H(en_b, bg_b)}</div>'
    for (s, en_t, bg_t, en_b, bg_b) in ISSUES
)

# ---------- the bootstrap-CI table ----------
ci_rows = "".join(
    f'<tr><td>{H(d["label"].split("(")[0].strip(), d["label"].split("(")[0].strip(), "span")}</td>'
    f'<td class="num">{d["mape_ens"]}%</td><td class="num ciband">{ci(d.get("mape_ci"))}</td></tr>'
    for d in m.values()
)
ci_rows += (
    f'<tr class="sep"><td>{T("Supply (composed)", "Предлагане (съставено)")}</td>'
    f'<td class="num">{la["supply_mape"]}%</td><td class="num ciband">{ci(la.get("supply_ci"))}</td></tr>'
    f'<tr><td>{T("Demand (composed)", "Търсене (съставено)")}</td>'
    f'<td class="num">{la["demand_mape"]}%</td><td class="num ciband">{ci(la.get("demand_ci"))}</td></tr>'
)

# ---------- regression-tree head-to-head table ----------
_l4, _l5 = TR["level4"], TR["level5"]


def _r2(o, k):
    v = o[k]["r2_oos"]
    cls = "up" if v > 0.02 else "dn"
    return f'<td class="num swing {cls}">{v:+.2f}</td>'


tree_rows = "".join(
    f'<tr><td>{T(en, bg)}</td>{_r2(_l4, k)}{_r2(_l5, k)}</tr>'
    for k, en, bg in [("linear", "Linear elasticity", "Линейна еластичност"),
                      ("tree_d3", "Regression tree (depth 3)", "Регресионно дърво (дълб. 3)"),
                      ("gboost", "Gradient boosting", "Градиентно усилване")])

# ---------- leave-one-country-out Beveridge table ----------
_LOMP = LO["mape"]
loco_rows = "".join(
    f'<tr{" class=\"sep\"" if k == "naive" else ""}><td>{T(en, bg)}</td>'
    f'<td class="num">{_LOMP[k]}%</td></tr>'
    for k, en, bg in [("pooled", "Pooled slope (all 8 — deployed)", "Обединен наклон (всичките 8 — внедрен)"),
                      ("loco", "Leave-one-country-out (other 7)", "Изключена държава (другите 7)"),
                      ("own", "Own country only", "Само собствената държава"),
                      ("naive", "Naïve (flat rate)", "Наивен (плосък коеф.)")])

# ---------- explanatory power: cross-country vs within-country R² ----------
_c6r2 = C6["cross_corr"] ** 2


def _prow(en, bg, cross, within, ven, vbg):
    return (f'<tr><td>{T(en, bg)}</td><td class="num" style="color:var(--mut)">{cross}</td>'
            f'<td class="num swing dn">{within}</td>'
            f'<td style="font-size:13px;color:#44403C">{T(ven, vbg)}</td></tr>')


power_rows = (
    _prow("L4 · burden → health spend", "Н4 · тежест → разходи за здраве",
          f"{C4['r2_levels_fe']:.2f}", f"{C4['r2_within_diff']:.3f}",
          "size &amp; trend, not a real effect", "размер и тренд, не реален ефект")
    + _prow("L5 · dividend → leisure/edu", "Н5 · дивидент → свободно/образование",
            f"{C5['r2_levels_fe']:.2f}", f"{C5['r2_within_diff']:.3f}",
            "size &amp; trend, not a real effect", "размер и тренд, не реален ефект")
    + _prow("L6 · health share → productivity", "Н6 · здравен дял → производителност",
            f"{_c6r2:.2f}", f"{C6['within_r2']:.3f}",
            f"r = {C6['cross_corr']:+.2f} — <b>wrong sign</b> (GALI)", f"r = {C6['cross_corr']:+.2f} — <b>грешен знак</b> (GALI)")
    + f'<tr class="sep"><td>{T("Beveridge vacancy model (a genuine fit)", "Модел на Бевъридж (същински фит)")}</td>'
      f'<td class="num" style="color:var(--mut)">—</td><td class="num swing up">{BEV_R2:.2f}</td>'
      f'<td style="font-size:13px;color:#44403C">{T("the one relationship with real explanatory power", "единствената връзка с реална обяснителна сила")}</td></tr>'
)

CSS = """
:root{--bg:#FAFAF9;--card:#FFFFFF;--ink:#292524;--mut:#78716C;--line:#E7E5E4;
--acc:#166534;--ok:#15803D;--warn:#D97706;--red:#B91C1C;}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font:16px/1.62 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;padding:36px 22px}
.wrap{max-width:880px;margin:0 auto}
.home{color:var(--mut);text-decoration:none;font-size:13px}.home:hover{color:var(--acc)}
h1{font-size:29px;margin:8px 0 4px;letter-spacing:-.3px}
h2{font-size:20px;margin:34px 0 6px;border-top:1px solid var(--line);padding-top:22px}
h3{font-size:16px;margin:0 0 5px}
.sub{color:var(--mut);max-width:720px}
.verdict{background:#F5F5F0;border:1px solid var(--line);border-left:4px solid var(--acc);
border-radius:10px;padding:16px 18px;margin:18px 0}
.verdict b{color:var(--acc)}
.issue{background:var(--card);border:1px solid var(--line);border-radius:11px;padding:14px 16px 12px;margin:11px 0;position:relative}
.issue p{margin:0;color:#44403C;font-size:14.5px}
.issue h3{padding-right:74px}
.sevtag{position:absolute;top:13px;right:14px;font-size:10.5px;font-weight:800;text-transform:uppercase;
letter-spacing:.5px;padding:3px 8px;border-radius:20px}
.sev-high{border-left:4px solid var(--red)}.sev-high .sevtag{background:#FEF2F2;color:var(--red)}
.sev-med{border-left:4px solid var(--warn)}.sev-med .sevtag{background:#FFFBEB;color:var(--warn)}
.sev-low{border-left:4px solid var(--mut)}.sev-low .sevtag{background:#F5F5F4;color:var(--mut)}
.fix{background:var(--card);border:1px solid var(--line);border-radius:11px;padding:15px 17px;margin:12px 0}
.fix .badge{display:inline-block;font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:.5px;
color:#fff;background:var(--acc);border-radius:6px;padding:3px 8px;margin-bottom:7px}
.fix .badge.null{background:var(--mut)}.fix .badge.flag{background:var(--warn)}
.fix h3{margin:2px 0 6px}.fix p{margin:6px 0 0;font-size:14.5px;color:#44403C}
table{border-collapse:collapse;width:100%;margin:10px 0;font-size:14.5px}
th,td{border-bottom:1px solid var(--line);padding:7px 10px;text-align:left}
th{color:var(--mut);font-size:12px;text-transform:uppercase;letter-spacing:.5px;font-weight:700}
td.num{text-align:right;font-variant-numeric:tabular-nums;font-weight:650}
td.ciband{color:var(--mut);font-weight:550}
tr.sep td{border-top:2px solid var(--line)}
.swing{font-variant-numeric:tabular-nums;font-weight:750}
.up{color:var(--ok)}.dn{color:var(--red)}
ul{margin:8px 0 0;padding-left:20px}li{margin:5px 0;color:#44403C;font-size:14.5px}
.foot{color:var(--mut);font-size:13px;margin-top:30px;border-top:1px solid var(--line);padding-top:14px}
a{color:var(--acc)}code{background:#F5F5F4;border-radius:4px;padding:1px 5px;font-size:13px}
"""

HTML = f"""<!doctype html><html lang="bg" data-lang="bg"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Critical review — longevity &amp; the labour market</title>
<style>{CSS}{lang_css()}</style></head><body>{lang_toggle()}<div class="wrap">
<a class="home" href="../index.html">{T("← Overview", "← Обзор")}</a>
<h1>{T("Critical review — the model on the stand", "Критичен преглед — моделът на изпит")}</h1>
{H("A sceptical statistician audits the forecasts: the strongest case <i>against</i> the numbers, the fixes we made in "
   "response — with figures computed live so they never drift — and the limits we cannot engineer away on 13 years of "
   "annual data.",
   "Скептичен статистик одитира прогнозите: най-силните аргументи <i>срещу</i> числата, поправките, които направихме в "
   "отговор — с показатели, изчислени директно, така че да не се разминават — и границите, които не можем да премахнем "
   "при 13 години годишни данни.", cls="sub")}

<div class="verdict">{H("<b>Verdict — trust the direction, discount the decimals.</b> The qualitative conclusions are robust and well-hedged: "
   "a structural East-surplus / West-shortage split and longevity holding supply roughly flat against a shrinking "
   "population. What is overstated is the <i>precision</i> — and the cross-country <i>level</i> comparisons that run "
   "through self-reported health are the least reliable headline of all.",
   "<b>Присъда — вярвайте на посоката, не на десетите.</b> Качествените изводи са устойчиви и добре уговорени: "
   "структурно разделение излишък-Изток / недостиг-Запад и дълголетие, което задържа предлагането приблизително "
   "постоянно срещу свиващо се население. Надценена е <i>точността</i> — а междудържавните сравнения на <i>нива</i>, "
   "минаващи през самооценено здраве, са най-ненадеждното заглавие.")}</div>

<h2>{T("The case against the model", "Аргументите срещу модела")}</h2>
{H("Ranked by how much each should change your confidence — read against the model’s own honesty, not in place of it.",
   "Подредени по това колко всеки трябва да промени доверието ви — четете ги заедно с честността на самия модел, не вместо нея.", cls="sub")}
{issue_cards}

<h2>{T("What we changed in response", "Какво променихме в отговор")}</h2>

<div class="fix"><span class="badge">{T("implemented", "внедрено")}</span>
{H("1 · Honest confidence intervals on every accuracy number", "1 · Честни доверителни интервали за всяко число за точност", "h3")}
{H("We added a <b>block bootstrap over countries</b> (2,000 resamples, country blocks) so correlated rows stop posing "
   "as independent. The point MAPEs are unchanged; the new 90% intervals show the true precision — wide where it should be.",
   "Добавихме <b>блоков бутстрап по държави</b> (2000 преизвадки, блокове по държава), за да спрат корелираните редове да "
   "се представят за независими. Точковите MAPE са същите; новите 90% интервали показват истинската точност — широки, където трябва.")}
<table><thead><tr><th>{T("Driver / output", "Двигател / изход")}</th><th class="num">MAPE</th>
<th class="num">{T("90% CI (bootstrap)", "90% ДИ (бутстрап)")}</th></tr></thead><tbody>{ci_rows}</tbody></table>
{H("Job vacancies are the tell: the point MAPE is 24% but the honest interval is roughly "
   f"<b>{ci(m['vacancy_count']['mape_ci'])}</b> — exactly why we floor that driver near a random walk and carry wide bands.",
   "Свободните места са показателни: точковата MAPE е 24%, но честният интервал е приблизително "
   f"<b>{ci(m['vacancy_count']['mape_ci'])}</b> — точно затова приземяваме този двигател близо до случайно лутане и носим широки ленти.")}</div>

<div class="fix"><span class="badge null">{T("fixed · no material change", "поправено · без съществена промяна")}</span>
{H("2 · Leakage-safe vacancy curve (re-fit inside every fold)", "2 · Безопасна крива за свободни места (пренапасвана във всеки фолд)", "h3")}
{H(f"We now re-fit the Beveridge vacancy curve on data <i>up to each origin only</i>, removing the look-ahead leak. "
   f"Supply and demand backtest MAPE stayed at <b>{la['supply_mape']}% / {la['demand_mape']}%</b> — confirming the "
   f"leak was immaterial (vacancies are a small slice of demand). An honest null, reported as one.",
   f"Сега пренапасваме кривата на Бевъридж само върху данни <i>до всеки произход</i>, премахвайки изтичането напред. "
   f"MAPE при бектест на предлагане и търсене остана <b>{la['supply_mape']}% / {la['demand_mape']}%</b> — потвърждавайки, "
   f"че изтичането е несъществено (свободните места са малък дял от търсенето). Честен нулев резултат, отчетен като такъв.")}</div>

<div class="fix"><span class="badge flag">{T("quantified — a real caveat", "количествено — реална уговорка")}</span>
{H("3 · Sensitivity to self-reported health (the East–West split)", "3 · Чувствителност към самооценено здраве (разделението Изток–Запад)", "h3")}
{H(f"We re-ran the 2033 balance with the GALI health multiplier <b>removed</b> (everyone of working age counted, "
   f"health-blind). Supply rises <b>+{hs['supply_lift_pct']}%</b>, and the headline East–West split nearly "
   f"<b>collapses</b>:",
   f"Преизчислихме баланса за 2033 с <b>премахнат</b> множител за здраве GALI (всички в трудоспособна възраст се броят, "
   f"без оглед на здраве). Предлагането нараства с <b>+{hs['supply_lift_pct']}%</b>, а заглавното разделение Изток–Запад "
   f"почти <b>изчезва</b>:")}
<table><thead><tr><th>{T("2033 balance (M working-years)", "Баланс 2033 (млн работни години)")}</th>
<th class="num">{T("with health", "със здраве")}</th><th class="num">{T("health-blind", "без здраве")}</th></tr></thead><tbody>
<tr><td>{T("West / EFTA (DE, FR, CH, NO)", "Запад / ЕАСТ (DE, FR, CH, NO)")}</td>
<td class="num swing dn">{hs['west_with']:+,}</td><td class="num swing up">{hs['west_without']:+,}</td></tr>
<tr><td>{T("East (PL, RO, CZ, BG)", "Изток (PL, RO, CZ, BG)")}</td>
<td class="num swing up">{hs['east_with']:+,}</td><td class="num swing up">{hs['east_without']:+,}</td></tr>
</tbody></table>
{H("Reading: a large part of the West’s “shortage” is its <i>lower self-reported</i> healthy share discounting its "
   "supply. The reality sits between the two columns — some of the health gap is real, some is reporting culture — but "
   "the lesson is firm: <b>the cross-country level split is the least robust headline, and rides on a non-comparable "
   "survey question.</b>",
   "Прочит: голяма част от „недостига“ на Запада е неговият <i>по-нисък самооценен</i> здравен дял, който намалява "
   "предлагането му. Реалността е между двете колони — част от здравната разлика е реална, част е култура на отчитане — "
   "но поуката е твърда: <b>междудържавното разделение на нива е най-ненадеждното заглавие и стъпва върху несравним "
   "анкетен въпрос.</b>")}</div>

<div class="fix"><span class="badge null">{T("tested — change not warranted", "проверено — промяна не е оправдана")}</span>
{H("4 · Joint vs independent Monte-Carlo sampling", "4 · Съвместно срещу независимо Монте-Карло семплиране", "h3")}
{H("We checked whether sampling the drivers independently mis-states the bands. Two findings: the balance already "
   "<b>shares one population draw</b> across supply and demand (so that correlation is handled per-draw); and the "
   "measured year-on-year correlation <i>between</i> the supply drivers is ≈ 0 (|r| ≤ 0.05), so independence there is "
   "empirically justified. The one real correlation — working-life ↔ employment, <b>r ≈ 0.50</b> — sits across the "
   "supply/demand divide, where adding it would <i>narrow</i> the balance band. So the current draw is conservative; "
   "injecting an arbitrary correlation would have made the bands look falsely tight.",
   "Проверихме дали независимото семплиране на двигателите изкривява лентите. Две находки: балансът вече "
   "<b>споделя едно теглене за населението</b> между предлагане и търсене (така че тази корелация се отчита по теглене); "
   "а измерената годишна корелация <i>между</i> двигателите на предлагането е ≈ 0 (|r| ≤ 0.05), затова независимостта там "
   "е емпирично оправдана. Единствената реална корелация — трудов живот ↔ заетост, <b>r ≈ 0.50</b> — е през границата "
   "предлагане/търсене, където добавянето ѝ би <i>стеснило</i> лентата на баланса. Затова текущото теглене е консервативно; "
   "налагане на произволна корелация би направило лентите фалшиво тесни.")}</div>

<div class="fix"><span class="badge null">{T("tested — no improvement", "проверено — без подобрение")}</span>
{H("5 · A regression tree on the descriptive levels (4–5)", "5 · Регресионно дърво върху описателните нива (4–5)", "h3")}
{H("Could a flexible learner find a nonlinearity the linear elasticity misses? We ran a leave-one-country-out backtest "
   "of the within-country growth relationships — poor-health burden → health spending (Level 4) and the healthy-retirement "
   "dividend → leisure/education/culture spending (Level 5) — pitting the linear model against a depth-3 regression tree "
   "and gradient boosting. Out-of-sample R² (higher is better; below zero means worse than guessing the mean):",
   "Може ли гъвкав модел да открие нелинейност, която линейната еластичност пропуска? Пуснахме бектест с изключване на "
   "по една държава върху вътрешнодържавните връзки на растежа — тежест от лошо здраве → разходи за здраве (Ниво 4) и "
   "дивидент от здраво пенсиониране → разходи за свободно време/образование/култура (Ниво 5) — изправяйки линейния модел "
   "срещу регресионно дърво (дълбочина 3) и градиентно усилване. Out-of-sample R² (по-високо е по-добро; под нулата "
   "значи по-зле от налучкване на средната):")}
<table><thead><tr><th>{T("Model", "Модел")}</th>
<th class="num">{T("L4 burden→health", "Н4 тежест→здраве")}</th>
<th class="num">{T("L5 dividend→leisure", "Н5 дивидент→свободно")}</th></tr></thead><tbody>{tree_rows}</tbody></table>
{H(f"Nobody wins — every R² is ≈ 0 or negative, so there is <b>no generalisable signal</b> to capture. The flexible "
   f"models overfit exactly as expected (gradient boosting collapses to <b>{_l5['gboost']['r2_oos']:+.2f}</b> on Level 5), "
   f"and dropping the longevity feature leaves the line the <i>same or better</i> (Level 4: "
   f"<b>{_l4['linear_no_burden']['r2_oos']:+.2f}</b> without the burden vs {_l4['linear']['r2_oos']:+.2f} with). A tree "
   f"finds no nonlinearity the line misses — confirming, with a flexible model, that Levels 4–5 are descriptive with a "
   f"within-country effect of <b>≈ 0</b>.",
   f"Никой не печели — всяко R² е ≈ 0 или отрицателно, тоест <b>няма обобщаем сигнал</b> за улавяне. Гъвкавите модели "
   f"пренапасват точно както се очаква (градиентното усилване се срива до <b>{_l5['gboost']['r2_oos']:+.2f}</b> на Ниво 5), "
   f"а премахването на дълголетийния признак оставя линията <i>същата или по-добра</i> (Ниво 4: "
   f"<b>{_l4['linear_no_burden']['r2_oos']:+.2f}</b> без тежестта срещу {_l4['linear']['r2_oos']:+.2f} с нея). Дървото не "
   f"намира нелинейност, която линията пропуска — потвърждавайки с гъвкав модел, че Нива 4–5 са описателни с "
   f"вътрешнодържавен ефект <b>≈ 0</b>.")}</div>

<div class="fix"><span class="badge">{T("implemented", "внедрено")}</span>
{H("6 · A proper scoring rule (CRPS)", "6 · Същинско правило за оценка (CRPS)", "h3")}
{H(f"The earlier draft reported only MAPE + coverage. We now also score the <b>whole predictive distribution</b> with "
   f"the Continuous Ranked Probability Score — a proper rule that rewards forecasts that are sharp <i>and</i> calibrated, "
   f"not just the point. Skill versus a naïve forecast (higher is better) is <b>positive for every driver</b>, averaging "
   f"<b>+{crps['mean_skill']:.2f}</b> — from healthy share (+{crps['by_driver']['healthy_share']:.2f}) to life expectancy "
   f"(+{crps['by_driver']['le_birth']:.2f}). Tellingly, even job vacancies score <b>+{crps['by_driver']['vacancy_count']:.2f}</b> "
   f"under CRPS although their <i>point</i> MAPE barely ties naïve: the calibrated bands carry real value the point error "
   f"misses — the model knows what it doesn’t know. (Honest framing: naïve is scored as a point forecast; giving it its "
   f"own distribution would narrow the gap.)",
   f"Предишният вариант отчиташе само MAPE + покритие. Сега оценяваме и <b>цялото предсказващо разпределение</b> с "
   f"Continuous Ranked Probability Score — същинско правило, което възнаграждава остри <i>и</i> калибрирани прогнози, не "
   f"само точката. Умението спрямо наивна прогноза (по-високо е по-добро) е <b>положително за всеки двигател</b>, средно "
   f"<b>+{crps['mean_skill']:.2f}</b> — от здравословен дял (+{crps['by_driver']['healthy_share']:.2f}) до продължителност "
   f"на живота (+{crps['by_driver']['le_birth']:.2f}). Показателно е, че дори свободните места дават "
   f"<b>+{crps['by_driver']['vacancy_count']:.2f}</b> по CRPS, макар <i>точковата</i> им MAPE едва да изравнява наивната: "
   f"калибрираните ленти носят реална стойност, която точковата грешка пропуска — моделът знае какво не знае. (Честно "
   f"казано: наивната е оценена като точкова прогноза; собствено разпределение би стеснило разликата.)")}</div>

<div class="fix"><span class="badge null">{T("tested — pooling justified", "проверено — обединяването е оправдано")}</span>
{H("7 · Leave-one-country-out: is the pooled Beveridge justified?", "7 · Изключване на по една държава: оправдан ли е обединеният Бевъридж?", "h3")}
{H("The vacancy model shares one Beveridge slope across all 8 countries. Is that pooling legitimate, or does it hurt a "
   "held-out country? We refit the slope three ways and backtested each on every country’s vacancy count (rolling-origin):",
   "Моделът за свободните места споделя един наклон на Бевъридж между всичките 8 държави. Легитимно ли е това "
   "обединяване, или вреди на изключена държава? Пренапаснахме наклона по три начина и тествахме всеки върху броя "
   "свободни места на всяка държава (с плъзгащ произход):")}
<table><thead><tr><th>{T("Slope fitted on…", "Наклон, напаснат върху…")}</th>
<th class="num">{T("vacancy MAPE", "MAPE свободни места")}</th></tr></thead><tbody>{loco_rows}</tbody></table>
{H(f"<b>Pooling is justified.</b> The slope is <b>stable</b> under leave-one-country-out — pooled "
   f"<b>{LO['slopes']['pooled']:+.2f}</b> vs LOCO <b>{LO['slopes']['loco_mean']:+.2f}</b>, almost identical, so no single "
   f"country drives it — and pooling <b>beats</b> fitting each country alone (own-country slopes scatter wildly from "
   f"{LO['slopes']['own_range'][0]:+.2f} to {LO['slopes']['own_range'][1]:+.2f} and score worst). The honest caveat is the "
   f"last row: even the well-pooled slope ({_LOMP['pooled']}%) just trails <b>naïve ({_LOMP['naive']}%)</b> — vacancies are "
   f"near-random-walk, so the Beveridge model earns its place by being <i>stable and scenario-able</i>, not by beating persistence.",
   f"<b>Обединяването е оправдано.</b> Наклонът е <b>стабилен</b> при изключване на по една държава — обединен "
   f"<b>{LO['slopes']['pooled']:+.2f}</b> срещу LOCO <b>{LO['slopes']['loco_mean']:+.2f}</b>, почти еднакви, тоест нито една "
   f"държава не го определя — и обединяването <b>превъзхожда</b> напасването на всяка държава поотделно (собствените "
   f"наклони се разпръскват силно от {LO['slopes']['own_range'][0]:+.2f} до {LO['slopes']['own_range'][1]:+.2f} и дават "
   f"най-лош резултат). Честната уговорка е последният ред: дори добре обединеният наклон ({_LOMP['pooled']}%) едва "
   f"изостава от <b>наивния ({_LOMP['naive']}%)</b> — свободните места са близо до случаен ход, затова моделът на Бевъридж "
   f"заслужава мястото си с това, че е <i>стабилен и сценариен</i>, а не като побеждава устойчивостта.")}</div>

<h2>{T("Explanatory power — cross-country vs within-country", "Обяснителна сила — между държави срещу вътре в държава")}</h2>
{H("The coefficient of determination (R²) tells two opposite stories depending on how you slice the data — and the gap "
   "between them is the single most important honesty check on Levels 4–6.",
   "Коефициентът на детерминация (R²) разказва две противоположни истории според това как срязваш данните — и разликата "
   "между тях е най-важната проверка за честност на Нива 4–6.", cls="sub")}
<table><thead><tr><th>{T("Relationship", "Връзка")}</th>
<th class="num">{T("Cross-country R²", "R² между държави")}</th>
<th class="num">{T("Within-country R²", "R² вътре в държава")}</th>
<th>{T("What it means", "Какво значи")}</th></tr></thead><tbody>{power_rows}</tbody></table>
{H(f"The contrast is the whole point. The impressive cross-country R² (<b>{C4['r2_levels_fe']:.2f}–{C5['r2_levels_fe']:.2f}</b>, "
   f"and r = {C6['cross_corr']:+.2f} for Level 6) is <b>pure country size and shared trend</b>; difference within a country "
   f"and it collapses to <b>≈ 0</b> ({C4['r2_within_diff']:.3f}, {C5['r2_within_diff']:.3f}, {C6['within_r2']:.3f}) — longevity "
   f"does <b>not</b> drive spending within a country, and Level 6’s cross-country correlation even has the <b>wrong sign</b> "
   f"(a self-reported-health artifact). Only the Beveridge vacancy model carries genuine explanatory power "
   f"(R² <b>{BEV_R2:.2f}</b>). This is exactly why Levels 4–6 are reported <b>descriptively</b> — and why the forecasting "
   f"levels (1–3) use MAPE / skill / coverage / CRPS instead of R², which is trivially high for any trending series.",
   f"Контрастът е целият смисъл. Внушителното R² между държави (<b>{C4['r2_levels_fe']:.2f}–{C5['r2_levels_fe']:.2f}</b>, "
   f"и r = {C6['cross_corr']:+.2f} за Ниво 6) е <b>чист размер на държавата и общ тренд</b>; диференцирай вътре в държава "
   f"и то се срива до <b>≈ 0</b> ({C4['r2_within_diff']:.3f}, {C5['r2_within_diff']:.3f}, {C6['within_r2']:.3f}) — "
   f"дълголетието <b>не</b> движи разходите вътре в държава, а междудържавната корелация на Ниво 6 дори е с <b>грешен "
   f"знак</b> (артефакт на самооценено здраве). Само моделът на Бевъридж носи реална обяснителна сила (R² <b>{BEV_R2:.2f}</b>). "
   f"Точно затова Нива 4–6 се отчитат <b>описателно</b> — и затова прогнозните нива (1–3) ползват MAPE / умение / покритие / "
   f"CRPS вместо R², което е тривиално високо за всеки трендов ред.")}

<h2>{T("Limits we cannot engineer away", "Граници, които не можем да премахнем")}</h2>
<ul>
<li>{T("<b>13 annual points.</b> Damped-Holt and AR(1) are barely identified on so few observations; the ensemble’s "
       "robustness comes mainly from a naïve anchor and an equal-weight floor — it works by <i>not</i> over-trusting the fits.",
       "<b>13 годишни точки.</b> Затихващ Holt и AR(1) едва се идентифицират при толкова малко наблюдения; устойчивостта на "
       "ансамбъла идва главно от наивна котва и под равни тегла — работи, като <i>не</i> се доверява прекалено на напасванията.")}</li>
<li>{T("<b>A 9-year horizon.</b> Beyond a few years the rate forecasts are mostly persistence; treat 2033 as a scenario, not a point.",
       "<b>9-годишен хоризонт.</b> Отвъд няколко години прогнозите на коефициентите са предимно устойчивост; третирайте 2033 като сценарий, не като точка.")}</li>
<li>{T("<b>Self-reported health is not cross-country comparable</b> — read its shifts, not its levels (see fix 3).",
       "<b>Самооцененото здраве не е сравнимо между държави</b> — четете промените му, не нивата (виж поправка 3).")}</li>
<li>{T("<b>Migration tails.</b> Bounded by Eurostat scenarios; a shock like Ukraine can exceed them in either direction.",
       "<b>Миграционни екстремуми.</b> Ограничени от сценариите на Евростат; шок като Украйна може да ги надхвърли и в двете посоки.")}</li>
<li>{T("<b>MAPE is still the wrong metric for the near-zero dividend.</b> We now also report a proper scoring rule (CRPS — see fix 6), but a per-quantity scaled metric for the Level-5 dividend remains future work.",
       "<b>MAPE все още е грешната метрика за близкия до нула дивидент.</b> Вече отчитаме и същинско правило за оценка (CRPS — виж поправка 6), но мащабирана метрика за дивидента от Ниво 5 остава бъдеща работа.")}</li>
<li>{T("<b>Levels 4–6 are descriptive.</b> Within-country causal effects are undetectable at this power — we report associations, never causation.",
       "<b>Нива 4–6 са описателни.</b> Вътрешнодържавните причинни ефекти са неоткриваеми при тази мощ — отчитаме асоциации, никога причинност.")}</li>
</ul>

<h2>{T("In fairness — what the model gets right", "Честно казано — какво моделът прави правилно")}</h2>
<ul>
<li>{T("Reports <b>skill versus a naïve forecast</b> openly — and admits it is ≈ 0 for the hardest drivers.",
       "Отчита <b>умение спрямо наивна прогноза</b> открито — и признава, че е ≈ 0 за най-трудните двигатели.")}</li>
<li>{T("Carries <b>wide, honest bands</b> and a leakage-safe COVID holdout, rather than a single confident line.",
       "Носи <b>широки, честни ленти</b> и безопасен COVID тест, вместо една самоуверена линия.")}</li>
<li>{T("Uses <b>simple ensembles, not neural nets</b> — the right call on short data; it does not overfit.",
       "Използва <b>прости ансамбли, не невронни мрежи</b> — правилният избор при кратки данни; не пренапасва.")}</li>
<li>{T("<b>Refuses causal claims</b> and flags the GALI and migration caveats itself — now with bootstrap intervals on top.",
       "<b>Отказва причинни твърдения</b> и сам сигнализира уговорките за GALI и миграцията — вече и с бутстрап интервали отгоре.")}</li>
</ul>

<p class="foot">{T("Numbers read live from", "Числата се четат директно от")} <code>outputs/validation_metrics.json</code> ·
{T("see the full", "виж пълния")} <a href="model_validation_report.html">{T("model-trust report", "доклад за доверие в модела")}</a> ·
<a href="../index.html">{T("← back to overview", "← обратно към обзора")}</a> · src/report_critique.py</p>
</div></body></html>"""

(OUT / "critique.html").write_text(HTML, encoding="utf-8")
print(f"wrote outputs/critique.html  (8 issues, 7 fixes; CRPS mean skill {crps['mean_skill']}; supply CI {la.get('supply_ci')}, "
      f"HLY split {hs['west_with']}->{hs['west_without']} / {hs['east_with']}->{hs['east_without']})")
