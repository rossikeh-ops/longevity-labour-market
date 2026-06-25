# -*- coding: utf-8 -*-
"""
Build outputs/applications.html — "Practical applications: who uses this, and why
it matters" (bilingual BG|EN). Each area links to the level that supports it;
grounded in the EU 2024 Ageing Report and the EU Silver Economy study.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from i18n import lang_css, lang_toggle  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "outputs"

# each area: icon, link, then (en, bg) for title / who / what / link-label
AREAS = [
    ("🏛️", "level5.html",
     ("Pensions &amp; retirement policy", "Пенсии и пенсионна политика"),
     ("Finance &amp; labour ministries, pension regulators, the EU Ageing Working Group, OECD.",
      "Министерства на финансите и труда, пенсионни регулатори, Работната група за застаряването на ЕС, ОИСР."),
     ("Healthy years <i>after</i> retirement (HLY − statutory age) against the headline age show how far retirement "
      "ages can credibly rise and what the <b>effective</b>, not nominal, workforce really is. The what-if sandbox "
      "quantifies the trade-off between later retirement, higher participation and healthier ageing.",
      "Здравите години <i>след</i> пенсиониране (ЗГЖ − законова възраст) спрямо обявената възраст показват докъде "
      "пенсионната възраст може убедително да се повиши и каква е <b>ефективната</b>, не номиналната, работна сила. "
      "Пясъчникът „какво-ако“ количествено определя компромиса между по-късно пенсиониране, по-високо участие и по-здраво застаряване."),
     ("Level 5 · the dividend", "Ниво 5 · дивидентът")),
    ("🏥", "level4.html",
     ("Health &amp; long-term-care planning", "Планиране на здравеопазване и дългосрочни грижи"),
     ("Health ministries, hospital and social-care planners, regional health authorities.",
      "Министерства на здравеопазването, планиращи болници и социални грижи, регионални здравни органи."),
     ("The poor-health burden <b>Pop × (LE − HLY)</b> projects demand for hospitals, carers and social services — "
      "the line that rises in nearly every EU member state through 2070 in the Ageing Report.",
      "Тежестта от лошо здраве <b>Насел. × (ОПЖ − ЗГЖ)</b> прогнозира търсенето на болници, болногледачи и социални "
      "услуги — линията, която расте в почти всяка държава от ЕС до 2070 г. в Доклада за застаряването."),
     ("Level 4 · cost of unhealthy years", "Ниво 4 · цена на нездравите години")),
    ("🌍", "level3.html",
     ("Labour &amp; migration policy", "Политика за труд и миграция"),
     ("Labour ministries, EU mobility &amp; cohesion bodies, regional development agencies.",
      "Министерства на труда, органи на ЕС за мобилност и сближаване, агенции за регионално развитие."),
     ("The sharp <b>East-surplus / West-shortage</b> divide is the demographic basis for labour mobility, targeted "
      "immigration, and participation drives among women and older workers.",
      "Рязкото разделение <b>излишък-Изток / недостиг-Запад</b> е демографската основа за трудова мобилност, "
      "целенасочена имиграция и кампании за участие сред жени и по-възрастни работници."),
     ("Level 3 · the balance", "Ниво 3 · балансът")),
    ("📈", "level6.html",
     ("Macro &amp; fiscal sustainability", "Макро и фискална устойчивост"),
     ("Treasuries, central banks, independent fiscal councils.",
      "Министерства на финансите, централни банки, независими фискални съвети."),
     ("The <b>labour-vs-productivity</b> growth split feeds potential-output and tax-base-versus-spending "
      "projections as the working-age population shrinks — the core tension behind age-related public spending, "
      "already ~24% of EU GDP in 2022.",
      "Разделянето на растежа на <b>труд срещу производителност</b> захранва прогнозите за потенциален продукт и "
      "данъчна основа спрямо разходи, докато населението в трудоспособна възраст намалява — основното напрежение зад "
      "свързаните с възрастта публични разходи, вече ~24% от БВП на ЕС през 2022 г."),
     ("Level 6 · the macroeconomy", "Ниво 6 · макроикономиката")),
    ("💼", "level1.html",
     ("Workforce &amp; actuarial planning", "Планиране на работната сила и актюерство"),
     ("Employers in shortage sectors, pension funds, life and long-term-care insurers.",
      "Работодатели в дефицитни сектори, пенсионни фондове, животозастрахователи и застрахователи за дългосрочни грижи."),
     ("Price longevity and plan recruitment, retention of older workers and automation against the shrinking "
      "labour supply quantified in the supply and demand levels.",
      "Остойностяване на дълголетието и планиране на наемане, задържане на по-възрастни работници и автоматизация "
      "спрямо свиващото се предлагане на труд, количествено определено в нивата за предлагане и търсене."),
     ("Levels 1–2 · supply &amp; demand", "Нива 1–2 · предлагане и търсене")),
    ("🎭", "level5.html",
     ("The “silver economy”", "„Сребърната икономика“"),
     ("Consumer, tourism, education and wellness businesses; investors.",
      "Потребителски, туристически, образователни и уелнес бизнеси; инвеститори."),
     ("Healthy, active retirees — the Level 5 dividend — are the market: Europe's silver economy is already "
      "estimated at <b>~€3.7 trillion and ~78 million jobs</b> in leisure, tourism, lifelong learning and wellness.",
      "Здравите, активни пенсионери — дивидентът от Ниво 5 — са пазарът: сребърната икономика на Европа вече се "
      "оценява на <b>~€3.7 трилиона и ~78 милиона работни места</b> в свободно време, туризъм, учене през целия живот и уелнес."),
     ("Level 5 · the dividend", "Ниво 5 · дивидентът")),
]


def _card(ic, lk, t, who, what, ll):
    return (
        f'<a class="card" href="{lk}"><div class="ic">{ic}</div>'
        f'<h3 lang="en">{t[0]}</h3><h3 lang="bg">{t[1]}</h3>'
        f'<p class="who" lang="en">{who[0]}</p><p class="who" lang="bg">{who[1]}</p>'
        f'<p lang="en">{what[0]}</p><p lang="bg">{what[1]}</p>'
        f'<p class="lk" lang="en">{ll[0]} →</p><p class="lk" lang="bg">{ll[1]} →</p></a>')


CARDS = "".join(_card(*a) for a in AREAS)

CSS = """
:root{--bg:#FAFAF9;--card:#FFFFFF;--ink:#292524;--mut:#78716C;--line:#E7E5E4;--acc:#166534;}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font:16px/1.6 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;padding:36px 24px}
.wrap{max-width:980px;margin:0 auto}
h1{font-size:28px;margin:0 0 6px}h2{font-size:20px;margin:30px 0 12px;border-bottom:1px solid var(--line);padding-bottom:6px}
.home{color:var(--mut);text-decoration:none;font-size:13px}.home:hover{color:var(--acc)}
.sub{color:var(--mut);margin:6px 0 8px;max-width:800px}
.note{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--acc);border-radius:12px;
padding:18px 20px;margin:18px 0;color:var(--ink)}.note b{color:var(--acc)}
.cards{display:grid;grid-template-columns:repeat(2,1fr);gap:16px;margin-top:6px}
a.card{display:block;background:var(--card);border:1px solid var(--line);border-radius:14px;padding:20px;
text-decoration:none;color:inherit;transition:border-color .15s,transform .15s}
a.card:hover{border-color:var(--acc);transform:translateY(-2px)}
a.card .ic{font-size:24px}a.card h3{margin:8px 0 6px;font-size:17px}
a.card .who{margin:0 0 8px;color:var(--ink);font-size:13px;font-weight:600}
a.card p{margin:0;color:var(--mut);font-size:14px}
a.card .lk{margin-top:12px;color:var(--acc);font-weight:600;font-size:13px}
.foot{color:var(--mut);font-size:13px;margin-top:26px}a{color:var(--acc)}
"""

HTML = f"""<!doctype html><html lang="bg" data-lang="bg"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Practical applications — longevity &amp; the labour market</title>
<style>{CSS}{lang_css()}</style></head><body>{lang_toggle()}<div class="wrap">
<a class="home" href="../index.html"><span lang="en">← Overview</span><span lang="bg">← Обзор</span></a>
<h1 lang="en">Practical applications — who uses this, and why it matters</h1>
<h1 lang="bg">Практически приложения — кой ги използва и защо са важни</h1>
<p class="sub" lang="en">This analysis is not academic only: each level answers a question a real decision-maker is already
paying to answer. Here is where the person-year engine is used, and why it matters.</p>
<p class="sub" lang="bg">Този анализ не е само академичен: всяко ниво отговаря на въпрос, за който реален вземащ
решения вече плаща. Ето къде се използва двигателят на човеко-години и защо е важно.</p>

<div class="note" lang="en">Demographic change is slow but decisive. Across the EU, age-related public spending was already
<b>~24% of GDP in 2022</b>, and the old-age dependency ratio (65+ per 100 working-age) is set to climb from
<b>36% to 55% by 2050</b>. Most published projections stop at headcounts and life-expectancy averages — which
can't be weighed against jobs. Turning both into a common unit, <b>human-working-years</b>, lets governments,
planners and businesses see the trade-offs and act while there is still time.</div>
<div class="note" lang="bg">Демографската промяна е бавна, но решаваща. В целия ЕС свързаните с възрастта публични разходи вече
бяха <b>~24% от БВП през 2022 г.</b>, а коефициентът на зависимост на възрастните (65+ на 100 в трудоспособна
възраст) ще се покачи от <b>36% на 55% до 2050 г.</b> Повечето публикувани прогнози спират при броя на хората и
средната продължителност на живота — които не могат да се претеглят спрямо работните места. Превръщането и на
двете в обща единица, <b>човеко-работни години</b>, позволява на правителства, планиращи и бизнеси да видят
компромисите и да действат, докато все още има време.</div>

<h2><span lang="en">Where it is used</span><span lang="bg">Къде се използва</span></h2>
<div class="cards">{CARDS}</div>

<p class="foot" lang="en"><b>Real-world anchors:</b>
<a href="https://economy-finance.ec.europa.eu/publications/2024-ageing-report-economic-and-budgetary-projections-eu-member-states-2022-2070_en">European Commission — 2024 Ageing Report</a> (age-related spending, dependency ratios, pension &amp;
health/long-term-care projections to 2070) ·
<a href="https://digital-strategy.ec.europa.eu/en/library/silver-economy-study-how-stimulate-economy-hundreds-millions-euros-year">European Commission — The Silver Economy study</a> (~€3.7tn, ~78m jobs).</p>
<p class="foot" lang="bg"><b>Реални ориентири:</b>
<a href="https://economy-finance.ec.europa.eu/publications/2024-ageing-report-economic-and-budgetary-projections-eu-member-states-2022-2070_en">Европейска комисия — Доклад за застаряването 2024</a> (свързани с възрастта разходи, коефициенти на зависимост,
прогнози за пенсии и здраве/дългосрочни грижи до 2070) ·
<a href="https://digital-strategy.ec.europa.eu/en/library/silver-economy-study-how-stimulate-economy-hundreds-millions-euros-year">Европейска комисия — Проучване за сребърната икономика</a> (~€3.7 трлн., ~78 млн. раб. места).</p>
<p class="foot"><a href="../index.html"><span lang="en">← Back to overview</span><span lang="bg">← Обратно към обзора</span></a> · src/report_applications.py</p>
</div></body></html>"""

(OUT / "applications.html").write_text(HTML, encoding="utf-8")
print(f"wrote outputs/applications.html ({len(AREAS)} application areas)")
