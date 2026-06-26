# -*- coding: utf-8 -*-
"""
Build outputs/shocks.html — "Wars & pandemics: how shocks hit the labour market"
(bilingual BG|EN, earthy theme). Empirical COVID analysis from our own panel
(vacancy collapse + rebound), the Ukraine-war refugee supply shock, the
mechanisms, and what it all means for the 2033 forecast.
"""
from __future__ import annotations
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from i18n import lang_css, lang_toggle  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
NAME = {"BG": "Bulgaria", "PL": "Poland", "CZ": "Czechia", "RO": "Romania",
        "DE": "Germany", "FR": "France", "NO": "Norway", "CH": "Switzerland"}

# ---- COVID vacancy collapse (2019->2020) + rebound (2019->2021) from the panel ----
p = pd.read_parquet(ROOT / "data" / "processed" / "panel.parquet")
rows = []
for c in NAME:
    f = p[(p.country == c) & (p.sex == "F")].set_index("year")["vacancy_count"]
    v19, v20, v21 = f.get(2019), f.get(2020), f.get(2021)
    if pd.notna(v19) and pd.notna(v20):
        rows.append({"c": c, "d20": (v20 / v19 - 1) * 100,
                     "d21": (v21 / v19 - 1) * 100 if pd.notna(v21) else None})
rows.sort(key=lambda r: r["d20"])               # deepest collapse first

# ---- chart: red bar = 2020 collapse, dot = where 2021 landed (vs 2019 = 0) ----
W, rh, L = 720, 34, 150
lo, hi = -48, 34
cx0 = L + (0 - lo) / (hi - lo) * (W - L - 40)    # x of the 2019 baseline (=0%)
X = lambda v: L + (v - lo) / (hi - lo) * (W - L - 40)
svg = [f'<line x1="{cx0:.0f}" y1="4" x2="{cx0:.0f}" y2="{len(rows)*rh+4}" stroke="#78716C" stroke-width="1"/>',
       f'<text x="{cx0:.0f}" y="{len(rows)*rh+18}" font-size="10" fill="#78716C" text-anchor="middle">2019 = 0</text>']
for i, r in enumerate(rows):
    y = i * rh + rh / 2 + 2
    x20 = X(r["d20"])
    svg.append(f'<text x="14" y="{y:.0f}" font-size="12.5" fill="#292524" dominant-baseline="middle">{NAME[r["c"]]}</text>')
    svg.append(f'<rect x="{x20:.0f}" y="{i*rh+9}" width="{cx0-x20:.0f}" height="16" rx="3" fill="#B91C1C" opacity="0.85"/>')
    svg.append(f'<text x="{x20-6:.0f}" y="{y:.0f}" font-size="11.5" fill="#B91C1C" text-anchor="end" dominant-baseline="middle">{r["d20"]:.0f}%</text>')
    if r["d21"] is not None:
        x21 = X(r["d21"])
        col = "#15803D" if r["d21"] >= 0 else "#D97706"
        svg.append(f'<circle cx="{x21:.0f}" cy="{y:.0f}" r="5" fill="{col}" stroke="#fff" stroke-width="1.4"/>')
        svg.append(f'<text x="{x21+9:.0f}" y="{y:.0f}" font-size="10.5" fill="{col}" dominant-baseline="middle">{r["d21"]:+.0f}%</text>')
CHART = f'<svg viewBox="0 0 {W} {len(rows)*rh+24}" width="100%" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif">{"".join(svg)}</svg>'

# ---- AI adoption by enterprises (% using any AI), the slow structural force ----
ai = pd.read_csv(sorted((ROOT / "data" / "raw").glob("ai_adoption_enterprises__*.csv"))[-1])
ai = ai[ai.indic_is == "E_AI_TANY"]
AI_Y = int(ai.year.max())
ai = ai[ai.year == AI_Y].sort_values("value", ascending=False)
airows = [(r.country, float(r.value)) for r in ai.itertuples()]
AW, arh, AL = 720, 32, 130
amax = max(v for _, v in airows) * 1.2
AX = lambda v: AL + v / amax * (AW - AL - 56)
asvg = []
for i, (c, v) in enumerate(airows):
    y = i * arh + arh / 2 + 2
    asvg.append(f'<text x="14" y="{y:.0f}" font-size="12.5" fill="#292524" dominant-baseline="middle">{NAME[c]}</text>')
    asvg.append(f'<rect x="{AL}" y="{i*arh+8}" width="{AX(v)-AL:.0f}" height="16" rx="3" fill="#166534" opacity="0.85"/>')
    asvg.append(f'<text x="{AX(v)+7:.0f}" y="{y:.0f}" font-size="11.5" fill="#166534" dominant-baseline="middle">{v:.0f}%</text>')
AICHART = f'<svg viewBox="0 0 {AW} {len(airows)*arh+8}" width="100%" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif">{"".join(asvg)}</svg>'

CSS = """
:root{--bg:#FAFAF9;--card:#FFFFFF;--ink:#292524;--mut:#78716C;--line:#E7E5E4;--acc:#166534;--up:#15803D;--down:#B91C1C;--warn:#D97706;}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font:16px/1.62 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;padding:36px 24px}
.wrap{max-width:980px;margin:0 auto}
.home{color:var(--mut);text-decoration:none;font-size:13px}.home:hover{color:var(--acc)}
h1{font-size:27px;margin:6px 0 4px}h2{font-size:20px;margin:32px 0 12px;border-bottom:1px solid var(--line);padding-bottom:6px}
.sub{color:var(--mut);margin:0 0 8px;max-width:840px}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px;margin:14px 0}
.shape{background:var(--card);border:1px solid var(--line);border-top:3px solid var(--c);border-radius:12px;padding:16px 18px}
.shape h3{margin:0 0 5px;font-size:16px;color:var(--c)}.shape p{margin:0;color:var(--mut);font-size:14px}
.fig{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px;margin:14px 0}
.cap{color:var(--mut);font-size:12.5px;margin-top:8px}.cap b{color:var(--ink)}
.lgd{display:flex;gap:18px;color:var(--mut);font-size:12px;margin:2px 2px 6px;flex-wrap:wrap}
.sw{display:inline-block;width:11px;height:11px;border-radius:2px;margin-right:5px;vertical-align:-1px}
.dot{display:inline-block;width:11px;height:11px;border-radius:50%;margin-right:5px;vertical-align:-1px}
.note{color:var(--mut);font-size:14px;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px 18px;margin:12px 0}.note b{color:var(--ink)}
table{width:100%;border-collapse:collapse;font-size:14px;margin-top:10px}
th,td{padding:9px 11px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
th{color:var(--mut);font-weight:600}td b{color:var(--ink)}
.foot{color:var(--mut);font-size:13px;margin-top:26px}a{color:var(--acc)}
@media(max-width:680px){.grid2{grid-template-columns:1fr}}
"""


def H(en, bg, tag="p", cls=""):
    c = f' class="{cls}"' if cls else ""
    return f'<{tag}{c} lang="en">{en}</{tag}><{tag}{c} lang="bg">{bg}</{tag}>'


HTML = f"""<!doctype html><html lang="bg" data-lang="bg"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Wars &amp; pandemics — shocks to the labour market</title>
<style>{CSS}{lang_css()}</style></head><body>{lang_toggle()}<div class="wrap">
<a class="home" href="../index.html"><span lang="en">← Overview</span><span lang="bg">← Обзор</span></a>
<h1><span lang="en">Wars, pandemics &amp; AI — forces on the labour market</span><span lang="bg">Войни, пандемии и ИИ — сили върху пазара на труда</span></h1>
{H("Three of the biggest forces that move a labour market sit outside the slow demographics our model forecasts. Our "
   "panel already spans the <b>COVID-19 shock</b>, so we measure it directly; for wars, the live case is Ukraine; and "
   "<b>AI</b> is the slow, structural force now reshaping labour demand. Here is what each does — and why it shapes our 2033 forecast.",
   "Три от най-големите сили, които движат пазара на труда, са извън бавната демография, която моделът ни прогнозира. "
   "Нашият панел вече обхваща <b>шока COVID-19</b>, затова го измерваме директно; за войните живият пример е Украйна; а "
   "<b>ИИ</b> е бавната, структурна сила, която сега преоформя търсенето на труд. Ето какво прави всяка — и защо оформя прогнозата ни за 2033 г.", cls="sub")}

<h2><span lang="en">Three different shock shapes</span><span lang="bg">Три различни форми на сътресение</span></h2>
<div class="grid2">
<div class="shape" style="--c:var(--warn)">{H("Pandemic — sharp but transitory", "Пандемия — рязка, но преходна", "h3")}
{H("A broad demand collapse plus a health hit, heavily cushioned by furlough schemes. Tends to be <b>V-shaped</b>: a quick fall, then a quick rebound.",
   "Широк срив в търсенето плюс здравен удар, силно смекчен от схеми за запазване на заетостта. Обикновено е <b>V-образна</b>: бърз спад, после бързо възстановяване.")}</div>
<div class="shape" style="--c:var(--down)">{H("War — structural and persistent", "Война — структурна и трайна", "h3")}
{H("Labour-supply <b>destruction</b> in the warring country (mobilisation, casualties, displacement), but a supply <b>boost</b> (refugees) and demand shocks (energy, defence) in the countries around it.",
   "<b>Унищожаване</b> на предлагането на труд във воюващата страна (мобилизация, жертви, разселване), но <b>увеличение</b> на предлагането (бежанци) и шокове в търсенето (енергия, отбрана) в съседните държави.")}</div>
<div class="shape" style="--c:var(--acc)">{H("AI — slow but structural", "ИИ — бавна, но структурна", "h3")}
{H("Not a sudden shock but a <b>gradual reshaping of demand</b>: automating some tasks, augmenting others, and shifting hiring toward AI and digital skills. No V-shape — a slow tilt, very uneven across countries.",
   "Не внезапен шок, а <b>постепенно преоформяне на търсенето</b>: автоматизира едни задачи, подсилва други и измества наемането към ИИ и дигитални умения. Без V-форма — бавен наклон, много неравномерен между държавите.")}</div>
</div>

<h2><span lang="en">The pandemic — what our data shows</span><span lang="bg">Пандемията — какво показват данните ни</span></h2>
{H("Job <b>vacancies</b> are the shock-absorber — they collapse first and hardest. In 2020 vacancy counts fell by "
   "5–41% across the eight countries; but the rebound was just as fast — by 2021 most were back near, or above, their "
   "2019 level (France +29%, Norway +21%). Unemployment barely moved (furlough schemes turned layoffs into "
   "labour-hoarding), and by 2022 employment rates were <b>above</b> pre-pandemic. A sharp shock — but a short one.",
   "<b>Свободните работни места</b> са амортисьорът — те се сриват първи и най-силно. През 2020 г. броят им падна с "
   "5–41% в осемте държави; но възстановяването беше също толкова бързо — до 2021 г. повечето се върнаха близо до или "
   "над нивото от 2019 г. (Франция +29%, Норвегия +21%). Безработицата почти не помръдна (схемите за запазване на "
   "заетостта превърнаха съкращенията в задържане на труд), а до 2022 г. коефициентите на заетост бяха <b>над</b> "
   "предпандемичните. Рязък шок — но кратък.")}
<div class="lgd"><span><span class="sw" style="background:#B91C1C"></span><span lang="en">2020 collapse (vs 2019)</span><span lang="bg">срив 2020 (спрямо 2019)</span></span>
<span><span class="dot" style="background:#15803D"></span><span lang="en">2021 — recovered ≥ 2019</span><span lang="bg">2021 — възстановено ≥ 2019</span></span>
<span><span class="dot" style="background:#D97706"></span><span lang="en">2021 — still below 2019</span><span lang="bg">2021 — още под 2019</span></span></div>
<div class="fig">{CHART}
{H("<b>Job vacancies, % change vs 2019.</b> The red bar is the 2020 collapse; the dot is where 2021 landed — the V-shape.",
   "<b>Свободни работни места, % промяна спрямо 2019.</b> Червената лента е сривът през 2020; точката е къде стигна 2021 — V-образната форма.", cls="cap")}</div>

<h2><span lang="en">The war — Ukraine 2022, a supply shock for the receivers</span><span lang="bg">Войната — Украйна 2022, шок в предлагането за приемащите</span></h2>
{H("The war in Ukraine is, for these eight countries, mainly a <b>labour-supply shock</b>: over 4 million Ukrainians "
   "took EU temporary protection, with <b>Poland and Czechia</b> absorbing the most per head. Refugee employment runs "
   "highest where labour markets are tight: <b>Poland ~65%</b> (the highest in the OECD), <b>Czechia ~60%</b>, against "
   "<b>Germany ~27%</b> (language, regulation, generous support). Studies of Czechia find <b>no negative effect on "
   "local employment</b> — refugees filled gaps in already-tight markets. Other channels: an energy-price shock "
   "(hitting Germany's energy-intensive industry hardest) and a defence-spending boost to demand.",
   "Войната в Украйна е, за тези осем държави, основно <b>шок в предлагането на труд</b>: над 4 милиона украинци "
   "получиха временна закрила в ЕС, като <b>Полша и Чехия</b> поеха най-много на глава от населението. Заетостта на "
   "бежанците е най-висока там, където пазарите са напрегнати: <b>Полша ~65%</b> (най-високата в ОИСР), "
   "<b>Чехия ~60%</b>, срещу <b>Германия ~27%</b> (език, регулации, щедра подкрепа). Изследвания за Чехия не намират "
   "<b>никакъв отрицателен ефект върху местната заетост</b> — бежанците запълниха празнини в и без това напрегнати "
   "пазари. Други канали: ценови шок при енергията (удрящ най-силно енергоемката индустрия на Германия) и тласък в "
   "търсенето от разходи за отбрана.")}

<h2><span lang="en">AI — the slow, structural force</span><span lang="bg">ИИ — бавната, структурна сила</span></h2>
{H(f"Unlike a war or a pandemic, AI is not a sudden shock — it is a <b>gradual reshaping of labour demand</b>: it "
   f"automates routine tasks, augments others, and tilts hiring toward AI and digital skills. As of {AI_Y}, the share "
   f"of enterprises (10+ employees) using any AI technology runs from <b>~29% in Norway and ~26% in Germany</b> down to "
   f"<b>~5–9% in Romania, Poland and Bulgaria</b> — the same West/Nordic-leads, East-lags gradient we see across this "
   f"study. The demand for the workforce that builds it is large too: ICT specialists range from ~140k in Bulgaria to "
   f"~2.3 million in Germany, and AI-specific job postings reach ~2.9% of all postings in Poland.",
   f"За разлика от война или пандемия, ИИ не е внезапен шок — той е <b>постепенно преоформяне на търсенето на труд</b>: "
   f"автоматизира рутинни задачи, подсилва други и измества наемането към ИИ и дигитални умения. Към {AI_Y} г. делът на "
   f"предприятията (10+ заети), използващи някаква ИИ технология, е от <b>~29% в Норвегия и ~26% в Германия</b> до "
   f"<b>~5–9% в Румъния, Полша и България</b> — същият градиент Запад/Север води, Изток изостава, който виждаме в цялото "
   f"изследване. Търсенето на работната сила, която го изгражда, също е голямо: ИКТ специалистите варират от ~140 хил. в "
   f"България до ~2.3 милиона в Германия, а обявите за ИИ работа достигат ~2.9% от всички в Полша.")}
<div class="lgd"><span><span class="sw" style="background:#166534"></span><span lang="en">Enterprises (10+) using any AI technology, {AI_Y}</span><span lang="bg">Предприятия (10+), използващи ИИ технология, {AI_Y} г.</span></span></div>
<div class="fig">{AICHART}
{H(f"<b>AI adoption by enterprises, {AI_Y}.</b> Switzerland is absent from this EU survey. The honest caveat: whether AI "
   f"is net job-destroying or job-creating is <b>genuinely uncertain</b> — displacement and augmentation run at once, so "
   f"we treat it as a structural risk, not a forecast.",
   f"<b>Внедряване на ИИ от предприятията, {AI_Y} г.</b> Швейцария липсва в това проучване на ЕС. Честната уговорка: дали "
   f"ИИ нетно унищожава или създава работни места е <b>наистина несигурно</b> — изместването и подсилването вървят "
   f"едновременно, затова го третираме като структурен риск, не като прогноза.", cls="cap")}</div>

<h2><span lang="en">The mechanisms, side by side</span><span lang="bg">Механизмите, един до друг</span></h2>
<table><thead><tr><th><span lang="en">Channel</span><span lang="bg">Канал</span></th>
<th><span lang="en">Pandemic</span><span lang="bg">Пандемия</span></th>
<th><span lang="en">War</span><span lang="bg">Война</span></th>
<th><span lang="en">AI</span><span lang="bg">ИИ</span></th></tr></thead><tbody>
<tr><td><b><span lang="en">Supply</span><span lang="bg">Предлагане</span></b></td>
<td><span lang="en">illness; some leave for childcare</span><span lang="bg">болест; някои напускат заради грижи за деца</span></td>
<td><span lang="en">mobilisation &amp; casualties; <b>out</b>-migration (warring) and <b>in</b>-migration (receivers)</span><span lang="bg">мобилизация и жертви; <b>изходяща</b> миграция (воюваща) и <b>входяща</b> (приемащи)</span></td>
<td><span lang="en">skills shift — demand for AI/digital skills, some routine roles obsolete</span><span lang="bg">промяна в уменията — търсене на ИИ/дигитални умения, някои рутинни роли остаряват</span></td></tr>
<tr><td><b><span lang="en">Demand</span><span lang="bg">Търсене</span></b></td>
<td><span lang="en">contact-sector collapse (lockdowns)</span><span lang="bg">срив в контактните сектори (локдауни)</span></td>
<td><span lang="en">defence &amp; reconstruction up; energy/supply-chain hit</span><span lang="bg">отбрана и възстановяване нагоре; удар по енергия/вериги</span></td>
<td><span lang="en">automates routine tasks, augments others — net effect <b>uncertain</b></span><span lang="bg">автоматизира рутинни задачи, подсилва други — нетен ефект <b>несигурен</b></span></td></tr>
<tr><td><b><span lang="en">Policy cushion</span><span lang="bg">Политическа възглавница</span></b></td>
<td><span lang="en">furlough / short-time work</span><span lang="bg">запазване на заетостта / непълно работно време</span></td>
<td><span lang="en">temporary protection + fast labour access</span><span lang="bg">временна закрила + бърз достъп до труд</span></td>
<td><span lang="en">re-skilling, education, AI regulation</span><span lang="bg">преквалификация, образование, регулация на ИИ</span></td></tr>
<tr><td><b><span lang="en">Persistence</span><span lang="bg">Трайност</span></b></td>
<td><span lang="en"><b>transitory</b> — V-shape</span><span lang="bg"><b>преходна</b> — V-образна</span></td>
<td><span lang="en"><b>structural</b> — migration, capital destruction</span><span lang="bg"><b>структурна</b> — миграция, унищожен капитал</span></td>
<td><span lang="en"><b>structural</b>, ongoing — a slow tilt, not a shock</span><span lang="bg"><b>структурна</b>, продължаваща — бавен наклон, не шок</span></td></tr>
</tbody></table>

<h2><span lang="en">Why this matters for the 2033 forecast</span><span lang="bg">Защо това е важно за прогнозата за 2033</span></h2>
<div class="note">{H("Shocks hit <b>vacancies</b> first and hardest — which is exactly why we model them as a near-random-walk (24% "
   "MAPE) at their honest floor, not extrapolated; why we carry a <b>COVID dummy</b>; and why the "
   "<a href='model_validation_report.html'>model-trust report</a> stress-tests the engine by training only to 2019 and "
   "predicting through COVID. The Ukrainian inflow is a live example of the <b>migration swing-factor</b> we flag as "
   "the biggest one — it lifts the <a href='level1.html'>supply side</a> in PL/CZ, partly offsetting their decline, "
   "but temporary protection means it could reverse. Our central path assumes no new mega-shock; a future pandemic or "
   "war would move it mainly through <b>migration (supply)</b> and <b>vacancies (demand)</b> — and that is precisely "
   "the uncertainty our <b>wide bands</b> are built to carry.",
   "Сътресенията удрят <b>свободните работни места</b> първи и най-силно — затова ги моделираме като близо до случаен "
   "ход (24% MAPE) при честния им таван, без екстраполация; затова носим <b>COVID индикатор</b>; и затова "
   "<a href='model_validation_report.html'>докладът за доверие</a> подлага двигателя на стрес-тест, обучавайки само до "
   "2019 г. и прогнозирайки през COVID. Украинският приток е жив пример за <b>миграционния променлив фактор</b>, който "
   "посочваме като най-големия — той повишава <a href='level1.html'>предлагането</a> в PL/CZ, частично компенсирайки "
   "спада им, но временната закрила означава, че може да се обърне. Централната ни пътека приема, че няма нов мега-шок; "
   "бъдеща пандемия или война би я преместила основно през <b>миграцията (предлагане)</b> и <b>свободните места "
   "(търсене)</b> — и точно тази несигурност носят <b>широките ни ленти</b>.")}</div>

<p class="foot" lang="en">Sources: own panel (Eurostat <code>jvs_q_r21</code>, <code>une_rt_a</code>, <code>lfsa_egan</code>) for COVID;
<a href="https://doku.iab.de/forschungsbericht/2024/fb1624en.pdf">IAB 2024</a>,
<a href="https://cepr.org/voxeu/columns/ukrainian-refugee-labour-market-access-shows-no-impact-local-employment-outcomes">CEPR/Czechia</a> and
<a href="https://pie.net.pl/en/65-ukrainian-refugees-work-but-face-many-challenges-in-the-polish-labour-market/">PIE</a> for the Ukraine refugee figures;
Eurostat <code>isoc_eb_ain2</code> (AI adoption), <code>isoc_sks_itsps</code> (ICT specialists) and OECD.AI / Lightcast (AI job postings) for AI.</p>
<p class="foot" lang="bg">Източници: собствен панел (Eurostat <code>jvs_q_r21</code>, <code>une_rt_a</code>, <code>lfsa_egan</code>) за COVID;
<a href="https://doku.iab.de/forschungsbericht/2024/fb1624en.pdf">IAB 2024</a>,
<a href="https://cepr.org/voxeu/columns/ukrainian-refugee-labour-market-access-shows-no-impact-local-employment-outcomes">CEPR/Чехия</a> и
<a href="https://pie.net.pl/en/65-ukrainian-refugees-work-but-face-many-challenges-in-the-polish-labour-market/">PIE</a> за данните за украинските бежанци.</p>
<p class="foot"><a href="../index.html"><span lang="en">← Back to overview</span><span lang="bg">← Обратно към обзора</span></a> · src/report_shocks.py</p>
</div></body></html>"""

(OUT / "shocks.html").write_text(HTML, encoding="utf-8")
print(f"wrote outputs/shocks.html  ({len(rows)} countries, COVID vacancy collapse chart)")
