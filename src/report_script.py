# -*- coding: utf-8 -*-
"""
Build outputs/script.html — the 20-minute, two-presenter PRESENTATION RUN-SHEET
as a page on the site (bilingual BG|EN, earthy theme). Mirrors the homepage
Presentation track: Presenter A (stops 1-6) and B (stops 7-10), each stop a
clickable card (links to the page it narrates) with a minute budget, a running
clock, a stage cue, and the spoken script. Source of truth for the spoken lines
is also docs/presentation_script.md.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from i18n import lang_css, lang_toggle, T  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "outputs"

# (n, who, href, budget, running, title_en, title_bg, cue_en, cue_bg, say_en, say_bg)
STOPS = [
    (1, "A", "introduction.html", "2:00", "2:00",
     "Intro + KPIs — the question", "Въведение + КПИ — въпросът",
     "Homepage, then click <b>1 · Intro + KPIs</b>.", "Начална страница, после щракнете <b>1 · Въведение + КПИ</b>.",
     """<p>Good morning. We'll split this: I'll show you <b>what we found</b>, then my colleague shows you <b>why you can trust it</b>.</p>
<p>Europe is getting older — and across much of the East, smaller. So our question is: by 2033, can each economy still supply the labour its jobs actually need? The hard part is units — you can't weigh a life-expectancy number against a job vacancy. So we built a translator: we convert demographic averages into <b>one common currency, human-working-years</b>, for eight countries — Bulgaria, Poland, Czechia, Romania, Germany, France, Norway, Switzerland — by sex, out to 2033. It's one equation: <b>supply</b> is healthy working-age people times how long they work; <b>demand</b> is the jobs the economy runs times the service those careers require; <b>balance</b> is the difference. All from live Eurostat data, deliberately simple models — no neural networks.</p>
<p>And here's the headline, in the KPI board: in aggregate Europe is <b>roughly balanced</b> — about <b>+89 million</b> human-working-years. But that average hides everything. Underneath is a sharp <b>East–West divide</b>: the East runs a surplus of about <b>+370 million</b>, the West and EFTA a shortage of about <b>−280 million</b>. <em>That one fact — surplus East, shortage West — is the demographic engine behind much of Europe's migration.</em> Let me show you how it's built.</p>""",
     """<p>Добро утро. Ще разделим това: аз ще ви покажа <b>какво открихме</b>, а колегата ми — <b>защо можете да му вярвате</b>.</p>
<p>Европа застарява — и в голяма част от Изтока намалява. Затова въпросът ни е: до 2033 г. може ли всяка икономика да осигури труда, който работните ѝ места реално изискват? Трудното са мерните единици — не можете да претеглите продължителност на живота срещу свободно работно място. Затова изградихме преводач: превръщаме демографските средни стойности в <b>една обща валута — човеко-работни години</b> — за осем държави: България, Полша, Чехия, Румъния, Германия, Франция, Норвегия, Швейцария — по пол, до 2033 г. Това е едно уравнение: <b>предлагането</b> е здрави хора в трудоспособна възраст по това колко дълго работят; <b>търсенето</b> е работните места по изисквания стаж; <b>балансът</b> е разликата. Всичко от живи данни на Евростат, умишлено прости модели — без невронни мрежи.</p>
<p>А ето заглавието, в таблото с КПИ: сумарно Европа е <b>горе-долу балансирана</b> — около <b>+89 милиона</b> човеко-работни години. Но тази средна стойност крие всичко. Отдолу е рязко <b>разделение Изток–Запад</b>: Изтокът има излишък от около <b>+370 милиона</b>, а Западът и ЕАСТ — недостиг от около <b>−280 милиона</b>. <em>Този единствен факт — излишък на Изток, недостиг на Запад — е демографският двигател зад голяма част от миграцията в Европа.</em> Нека ви покажа как се изгражда.</p>"""),

    (2, "A", "level1.html", "1:30", "3:30",
     "Level 1 · Supply — who can work", "Ниво 1 · Предлагане — кой може да работи",
     "Click <b>2 · Supply</b>; show the map.", "Щракнете <b>2 · Предлагане</b>; покажете картата.",
     """<p>Level one: <b>supply</b> — healthy working-age people times their expected working life.</p>
<p>Here's the surprise. Working-age populations are <b>shrinking</b>, especially in the East — yet total supply <b>barely moves</b>: from about <b>4,490 down to 4,390 million</b>, only minus two-and-a-half percent. Why so flat? Three forces push back: people are <b>healthier</b>, they <b>work longer</b>, and <b>participation is rising</b> — especially women and older workers. That's the <b>longevity dividend</b>, already holding the line.</p>
<p>But the average hides the geography: <b>Romania and Bulgaria fall hardest</b> — emigration plus ageing — while <b>Germany, France and Norway gain</b>. The map shows that gradient at a glance. <em>One honest caveat: this is a potential ceiling — before skills mismatch and frictions — and every number carries a band.</em></p>""",
     """<p>Ниво едно: <b>предлагане</b> — здрави хора в трудоспособна възраст по очаквания им трудов живот.</p>
<p>Ето изненадата. Населението в трудоспособна възраст <b>намалява</b>, особено на Изток — а общото предлагане <b>почти не помръдва</b>: от около <b>4490 до 4390 милиона</b>, само минус два и половина процента. Защо толкова равно? Три сили противодействат: хората са <b>по-здрави</b>, работят <b>по-дълго</b> и <b>участието расте</b> — особено жени и по-възрастни. Това е <b>дивидентът от дълголетие</b>, който вече държи фронта.</p>
<p>Но средната стойност крие географията: <b>Румъния и България падат най-силно</b> — емиграция плюс застаряване — докато <b>Германия, Франция и Норвегия печелят</b>. Картата показва този градиент с един поглед. <em>Една честна уговорка: това е потенциален таван — преди несъответствие на уменията и фрикции — и всяко число носи лента.</em></p>"""),

    (3, "A", "level2.html", "1:30", "5:00",
     "Level 2 · Demand — what the economy needs", "Ниво 2 · Търсене — какво иска икономиката",
     "Click <b>3 · Demand</b>.", "Щракнете <b>3 · Търсене</b>.",
     """<p>Level two: <b>demand</b> — the jobs the economy runs, employees plus vacancies, times required service. Same currency, directly comparable to supply.</p>
<p>And demand is also <b>broadly flat</b>: about <b>4,420 down to 4,310 million</b>, again minus two-and-a-half percent. That's the key point — <b>demand doesn't run away</b>. The imbalance isn't an explosion in labour needs; it's about <b>where the working-age people are</b>. Geography, not appetite.</p>
<p>One honest piece of engineering: <b>vacancies are our weakest input</b> — shock-driven, almost a random walk — so instead of extrapolating them, we tie them to unemployment through a <b>Beveridge curve</b>: vacancies fall when unemployment rises. That keeps them stable and scenario-able. <em>My colleague will show you exactly how reliable that is.</em></p>""",
     """<p>Ниво две: <b>търсене</b> — работните места, които икономиката поддържа, заети плюс свободни, по изисквания стаж. Същата валута, пряко сравнима с предлагането.</p>
<p>И търсенето също е <b>като цяло равно</b>: от около <b>4420 до 4310 милиона</b>, отново минус два и половина процента. Това е ключът — <b>търсенето не избягва</b>. Дисбалансът не е взрив в нуждата от труд; той е за това <b>къде са хората в трудоспособна възраст</b>. География, не апетит.</p>
<p>Една честна инженерна подробност: <b>свободните места са най-слабият ни вход</b> — водени от шокове, почти случаен ход — затова вместо да ги екстраполираме, ги свързваме с безработицата чрез <b>крива на Бевъридж</b>: свободните места падат, когато безработицата расте. Това ги държи стабилни и сценарийни. <em>Колегата ми ще ви покаже точно колко надеждно е това.</em></p>"""),

    (4, "A", "level3.html", "2:30", "7:30",
     "Level 3 · Balance — the climax", "Ниво 3 · Баланс — кулминацията",
     "Click <b>4 · Balance</b>; show the balance map.", "Щракнете <b>4 · Баланс</b>; покажете картата на баланса.",
     """<p>Now the headline. <b>Balance is supply minus demand</b> — and because it's a small difference of two huge numbers, this is where it sharpens.</p>
<p>At the European level they almost cancel: a net of about <b>plus 89 million</b>. On its own that sounds like “Europe is fine.” But it's a <b>mirage</b>. Split East versus West and the real structure appears. The <b>East runs a surplus of about +370 million</b> — Poland, Romania, Czechia, Bulgaria have more potential labour than their economies demand. The <b>West and EFTA run a shortage of about −280 million</b> — Germany, France, Switzerland, Norway need more than they have. So it isn't one balanced continent; it's <b>two opposite imbalances that cancel on paper</b> — and that's precisely the demographic basis for West-bound migration.</p>
<p><em>Now the honesty:</em> balance is a small difference of two big forecasts, so its relative error is amplified — around twenty-odd percent. So we don't read it as a precise point; we read it as a <b>direction with wide bands</b> — a structural East-surplus, West-shortage signal — and one we stress-tested by holding out the COVID years and predicting straight through them. If you remember one thing from my half, make it this map.</p>""",
     """<p>Сега заглавието. <b>Балансът е предлагане минус търсене</b> — и понеже е малка разлика на две огромни числа, тук всичко се изостря.</p>
<p>На европейско ниво почти се компенсират: нето от около <b>плюс 89 милиона</b>. Само по себе си звучи като „Европа е добре“. Но е <b>мираж</b>. Разделете Изток срещу Запад и истинската структура се появява. <b>Изтокът има излишък от около +370 милиона</b> — Полша, Румъния, Чехия, България имат повече потенциален труд, отколкото икономиките им изискват. <b>Западът и ЕАСТ имат недостиг от около −280 милиона</b> — Германия, Франция, Швейцария, Норвегия се нуждаят от повече, отколкото имат. Така че това не е един балансиран континент; това са <b>два противоположни дисбаланса, които се компенсират на хартия</b> — и точно това е демографската основа за миграцията на Запад.</p>
<p><em>Сега честността:</em> балансът е малка разлика на две големи прогнози, затова относителната му грешка е усилена — около двайсетина процента. Затова не го четем като точна стойност; четем го като <b>посока с широки ленти</b> — структурен сигнал излишък-Изток, недостиг-Запад — и го тествахме, като изключихме годините на COVID и прогнозирахме право през тях. Ако запомните едно нещо от моята част, нека е тази карта.</p>"""),

    (5, "A", "level4.html", "1:00", "8:30",
     "Open horizons · Levels 4–6", "Отворени хоризонти · Нива 4–6",
     "Click <b>5 · Open horizons</b>.", "Щракнете <b>5 · Отворени хоризонти</b>.",
     """<p>Three “open horizons” — and here the key is what we <b>honestly did not find</b>. Level four is the <b>poor-health burden</b>; level five the <b>healthy-retirement dividend</b>; level six the <b>macroeconomy</b> — GDP growing from about eight to eight-and-a-half trillion euros, under one percent a year, almost all of it productivity.</p>
<p>Across countries these all <em>look</em> strongly linked to health. But look <b>within a country, over time</b>, and the link is essentially <b>zero</b> — spending tracks GDP and income, not the longevity quantity. <em>So we report these as descriptions, never cause and effect.</em> That restraint is the result.</p>""",
     """<p>Три „отворени хоризонта“ — и тук ключът е какво <b>честно не открихме</b>. Ниво четири е <b>тежестта от лошо здраве</b>; ниво пет — <b>дивидентът от здраво пенсиониране</b>; ниво шест — <b>макроикономиката</b>: БВП расте от около осем до осем и половина трилиона евро, под един процент годишно, почти изцяло от производителност.</p>
<p>Между държавите всички те <em>изглеждат</em> силно свързани със здравето. Но погледнете <b>вътре в държава, във времето</b>, и връзката е по същество <b>нула</b> — разходите следват БВП и доходите, не дълголетийната величина. <em>Затова ги отчитаме като описания, никога като причина и следствие.</em> Тази сдържаност е резултатът.</p>"""),

    (6, "A", "implications.html", "1:30", "10:00",
     "Implications &amp; shocks", "Последици и сътресения",
     "Click <b>6 · Implications &amp; shocks</b>.", "Щракнете <b>6 · Последици и сътресения</b>.",
     """<p>So what moves it? Only <b>three levers</b>: <b>increase supply</b> — participation, retention, migration; <b>ease demand</b> — automation and productivity; or <b>maintain balance</b> — education and retirement-age policy. The East's surplus and the West's shortage are the map for where each one bites.</p>
<p>And because the real world isn't only slow demographics, this page measures the <b>shocks</b> from our own data: the <b>COVID</b> vacancy collapse — Poland down over forty percent, then a sharp rebound; the <b>Ukraine war</b> as a refugee supply boost to Poland and Czechia; and <b>AI</b> as the slow structural force, with adoption from nearly thirty percent of firms in Norway down to five in Romania. <em>That's the answer and the stakes — over to my colleague for why you can believe it.</em></p>""",
     """<p>И така, какво го движи? Само <b>три лоста</b>: <b>увеличи предлагането</b> — участие, задържане, миграция; <b>намали търсенето</b> — автоматизация и производителност; или <b>поддържай баланс</b> — образование и политика за пенсионна възраст. Излишъкът на Изток и недостигът на Запад са картата за това къде хваща всеки от тях.</p>
<p>И понеже реалният свят не е само бавна демография, тази страница измерва <b>сътресенията</b> от собствените ни данни: сривът на свободните места при <b>COVID</b> — Полша надолу с над четирийсет процента, после рязко възстановяване; войната в <b>Украйна</b> като бежански тласък в предлагането за Полша и Чехия; и <b>ИИ</b> като бавната структурна сила, с внедряване от близо трийсет процента от фирмите в Норвегия до пет в Румъния. <em>Това е отговорът и залогът — давам думата на колегата за това защо можете да вярвате.</em></p>"""),

    (7, "B", "methodology_report.html", "2:00", "12:00",
     "Methodology — how it works", "Методология — как работи",
     "Click <b>7 · Methodology</b>; point at the engine diagram.", "Щракнете <b>7 · Методология</b>; посочете диаграмата на двигателя.",
     """<p>Thank you. A forecast you can't explain is one you can't trust — so let me open the hood.</p>
<p>For every series we don't bet on one model. We <b>average five simple ones</b>: linear, damped Holt, drift, naïve, and a mean-reverting AR-one. The simplicity is deliberate — our histories are short, about thirteen to twenty points, and we use <b>no neural networks</b>: with this little data, flexible models overfit and mislead.</p>
<p>And we tested that. A fair challenge: surely a model dedicated to the nine-year forecast beats one general model? The chart says no — at every horizon the single ensemble wins, because a dedicated nine-year model trains on a median of just <b>three</b> data points and starves. We go further in honesty: on these slow series the <b>naïve “last value” is the hardest thing to beat</b>, so the win is restraint that hugs that floor. And the <b>bands</b> aren't decoration — they combine model disagreement, real backtest error, and migration uncertainty, which is why they're honestly twelve-to-forty percent wide. Let me make that tangible.</p>""",
     """<p>Благодаря. Прогноза, която не можете да обясните, е такава, на която не можете да вярвате — затова нека отворя капака.</p>
<p>За всеки ред не залагаме на един модел. <b>Усредняваме пет прости</b>: линеен, затихващ Holt, дрейф, наивен и връщащ се към средното AR-едно. Простотата е умишлена — историите ни са кратки, около тринайсет до двайсет точки, и не ползваме <b>невронни мрежи</b>: при толкова малко данни гъвкавите модели пренапасват и подвеждат.</p>
<p>И го проверихме. Честно предизвикателство: със сигурност модел, посветен на деветгодишната прогноза, бие един общ модел? Графиката казва не — на всеки хоризонт единият ансамбъл печели, защото посветен деветгодишен модел се обучава на медиана от едва <b>три</b> точки и гладува. Отиваме по-далеч в честността: при тези бавни редове <b>наивната „последна стойност“ е най-трудното за побеждаване</b>, затова победата е сдържаност, която се придържа към този под. А <b>лентите</b> не са украса — те съчетават несъгласие на моделите, реална бектест грешка и миграционна несигурност, затова са честно широки дванайсет до четирийсет процента. Нека го направя осезаемо.</p>"""),

    (8, "B", "playground.html", "2:30", "14:30",
     "Model playground — drag it live", "Лаборатория на модела — на живо",
     "Click <b>8 · Model playground</b>; actually drag the sliders.", "Щракнете <b>8 · Лаборатория на модела</b>; наистина плъзгайте.",
     """<p>The method you can <em>touch</em> — two live toys, and watch the screen, not me.</p>
<p>First, <b>ensemble uncertainty</b>. As I add more simple models and a little noise — watch — a <b>cloud</b> of forecasts forms, and our band is just the spread of that cloud. No magic: the uncertainty is literally the disagreement among honest simple models.</p>
<p>Second — my favourite — <b>flexibility, the bias–variance tradeoff</b>, on a real Healthy-Life-Years series for Czechia. This slider is model flexibility. Drag it left, to a flat line — too rigid, it <b>underfits</b>. Drag it right, to a wiggly curve, and watch the bottom chart: the <b>training error keeps falling</b>, but the <b>cross-validated error explodes</b> — from about 0.7 up to 15. That's overfitting, live — the model memorising noise. The sweet spot sits at a <b>modest</b> flexibility, degree three here — which is exactly why we use simple models, and why a neural network would land far to the right, deep in the overfit zone. <em>You've now seen, with your own eyes, what's on either side of the choice we made.</em></p>""",
     """<p>Методът, който можете да <em>докоснете</em> — две живи играчки, и гледайте екрана, не мен.</p>
<p>Първо, <b>несигурност на ансамбъла</b>. Докато добавям още прости модели и малко шум — гледайте — образува се <b>облак</b> от прогнози, а лентата ни е просто обхватът на този облак. Без магия: несигурността е буквално несъгласието между честни прости модели.</p>
<p>Второ — любимото ми — <b>гъвкавост, компромисът отклонение–дисперсия</b>, върху реален ред за Здрави години живот за Чехия. Този плъзгач е гъвкавостта на модела. Дръпнете го наляво, до права линия — твърде сковано, <b>недонапасва</b>. Дръпнете надясно, до извиваща се крива, и гледайте долната графика: <b>грешката при обучение продължава да пада</b>, но <b>крос-валидираната грешка избухва</b> — от около 0,7 до 15. Това е пренапасване на живо — моделът запаметява шум. Оптимумът е при <b>умерена</b> гъвкавост, тук степен три — точно затова ползваме прости модели, и затова невронна мрежа би попаднала далеч вдясно, дълбоко в зоната на пренапасване. <em>Току-що видяхте, със собствените си очи, какво има от двете страни на избора, който направихме.</em></p>"""),

    (9, "B", "critique.html", "2:30", "17:00",
     "Trust &amp; critique — on the stand", "Доверие и критика — на изпит",
     "Click <b>9 · Trust &amp; critique</b>.", "Щракнете <b>9 · Доверие и критика</b>.",
     """<p>The part I'm proudest of: we put <b>our own model on trial</b>.</p>
<p><b>The case for it:</b> rolling-origin cross-validation — hold out the last years, forecast from history only. Life expectancy at <b>1.2 percent</b> error, employment under two; the composed <b>supply at 3.6 percent, demand at 2.2</b>. We even added a proper scoring rule, <b>CRPS</b>, which grades the whole band, not just the point — and skill versus naïve is <b>positive for every driver, averaging +0.29</b>. Even vacancies score well, because our bands are well-calibrated: the model knows what it doesn't know.</p>
<p><b>The case against — our own audit.</b> Three findings. One: <b>bootstrap confidence intervals</b> on every number — vacancies aren't “24 percent,” they're 24 with a range of <b>16 to 34</b>. Real precision, not false. Two — the big one: the East–West split partly rides on <b>self-reported health</b>, which isn't comparable across countries; strip it out and the surplus and shortage <b>nearly collapse into each other</b>. So we flag the cross-country split as our least robust headline. Three: across countries the longevity-to-spending links look powerful — R-squared near <b>0.99</b>; within a country they fall to <b>zero</b>. The 0.99 is pure country size.</p>
<p>And every time we reached for a fancier tool — a regression tree, gradient boosting, per-horizon specialists — we measured it, and it <b>lost</b>. <em>We didn't just prefer simple; we proved simple wins.</em></p>""",
     """<p>Частта, с която най-много се гордея: подложихме <b>собствения си модел на съд</b>.</p>
<p><b>Аргументът за него:</b> крос-валидация с плъзгащ произход — изключваме последните години, прогнозираме само от историята. Продължителност на живота с <b>1,2 процента</b> грешка, заетост под два; съставеното <b>предлагане с 3,6 процента, търсене с 2,2</b>. Добавихме дори същинско правило за оценка, <b>CRPS</b>, което оценява цялата лента, не само точката — и умението спрямо наивното е <b>положително за всеки двигател, средно +0,29</b>. Дори свободните места се представят добре, защото лентите ни са добре калибрирани: моделът знае какво не знае.</p>
<p><b>Аргументът срещу — собственият ни одит.</b> Три находки. Едно: <b>бутстрап доверителни интервали</b> за всяко число — свободните места не са „24 процента“, а 24 с диапазон от <b>16 до 34</b>. Истинска точност, не фалшива. Две — голямата: разделението Изток–Запад отчасти стъпва върху <b>самооценено здраве</b>, което не е сравнимо между държавите; махнете го и излишъкът и недостигът <b>почти се сливат</b>. Затова отбелязваме междудържавното разделение като най-ненадеждното ни заглавие. Три: между държавите връзките дълголетие–разходи изглеждат мощни — R-квадрат близо <b>0,99</b>; вътре в държава падат до <b>нула</b>. Тези 0,99 са чист размер на държавата.</p>
<p>И всеки път, когато посегнехме към по-сложен инструмент — регресионно дърво, градиентно усилване, специалисти по хоризонт — го измервахме и той <b>губеше</b>. <em>Не просто предпочетохме простото; доказахме, че простото печели.</em></p>"""),

    (10, "B", "whatif.html", "2:00", "19:00",
     "What-if sandbox — the finale", "Пясъчник „какво-ако“ — финалът",
     "Click <b>10 · What-if sandbox</b>; take a scenario from the audience.", "Щракнете <b>10 · Пясъчник „какво-ако“</b>; вземете сценарий от публиката.",
     """<p>Let me end where it gets personal — because behind every number is a human question: who keeps working, who retires, who needs care, and who fills the concert halls and the adult-education classes?</p>
<p>This is a <b>live sandbox</b>: three dials — <b>healthy life years</b>, <b>retirement age</b>, <b>participation</b> — and four answers that update instantly, all on the same identities you've seen, even showing occupied jobs and open listings move in real time.</p>
<p>Give me a scenario — anyone. <em>[Take one; otherwise:]</em> Say people stay healthy two years longer and we nudge participation up — watch supply rise and the shortage shrink. Now push the retirement age the other way, and watch <em>who</em> it helps and <em>who</em> it strains — because the answer isn't the same in Sofia as in Stuttgart.</p>
<p>That's the whole point: not a prophecy, a <b>transparent engine you can interrogate</b> — honest about what it knows and what it doesn't, reproducible from raw data to this slider. The structural message is robust: the <b>longevity dividend is real</b> and holding supply up, but it sits on a deep <b>East–West divide</b> — and these dials are where policy meets it. Thank you — happy to take questions.</p>""",
     """<p>Нека завърша там, където става лично — защото зад всяко число стои човешки въпрос: кой продължава да работи, кой се пенсионира, кой има нужда от грижи и кой пълни концертните зали и курсовете за възрастни?</p>
<p>Това е <b>жив пясъчник</b>: три плъзгача — <b>здрави години живот</b>, <b>пенсионна възраст</b>, <b>участие</b> — и четири отговора, които се обновяват мигновено, всички на същите тъждества, които видяхте, дори показвайки как заетите места и свободните обяви се движат в реално време.</p>
<p>Дайте ми сценарий — който и да е. <em>[Вземете един; иначе:]</em> Да кажем, че хората остават здрави две години повече и побутнем участието нагоре — гледайте как предлагането расте и недостигът се свива. Сега бутнете пенсионната възраст в обратната посока и вижте <em>на кого</em> помага и <em>кого</em> натоварва — защото отговорът не е същият в София, както в Щутгарт.</p>
<p>Това е целият смисъл: не пророчество, а <b>прозрачен двигател, който можете да разпитвате</b> — честен за това какво знае и какво не, възпроизводим от сурови данни до този плъзгач. Структурното послание е устойчиво: <b>дивидентът от дълголетие е реален</b> и държи предлагането нагоре, но седи върху дълбоко <b>разделение Изток–Запад</b> — и тези плъзгачи са там, където политиката го среща. Благодаря — с радост ще отговорим на въпроси.</p>"""),
]


def act(title_en, title_bg, who, stops):
    cards = ""
    for n, w, href, bud, run, ten, tbg, cen, cbg, sen, sbg in stops:
        cards += (
            f'<div class="stop s-{w}"><div class="sh">'
            f'<span class="num">{n}</span>'
            f'<a class="st" href="{href}"><span lang="en">{ten}</span><span lang="bg">{tbg}</span> ↗</a>'
            f'<span class="bud">{bud} · ⏱ {run}</span></div>'
            f'<div class="cue"><span lang="en">📺 {cen}</span><span lang="bg">📺 {cbg}</span></div>'
            f'<div class="say"><div lang="en">{sen}</div><div lang="bg">{sbg}</div></div></div>')
    return (f'<div class="acthead h-{who}"><span lang="en">{title_en}</span><span lang="bg">{title_bg}</span></div>{cards}')


A = act("Presenter A — “The answer” · stops 1–6 · ~10 min",
        "Представящ А — „Отговорът“ · стъпки 1–6 · ~10 мин", "A", [s for s in STOPS if s[1] == "A"])
B = act("Presenter B — “Why believe it” · stops 7–10 · ~9 min",
        "Представящ Б — „Защо да вярваме“ · стъпки 7–10 · ~9 мин", "B", [s for s in STOPS if s[1] == "B"])

TROWS = "".join(
    f'<tr class="t-{w}"><td>{n}</td><td>{"A" if w=="A" else "B"}</td>'
    f'<td><span lang="en">{ten}</span><span lang="bg">{tbg}</span></td>'
    f'<td class="num">{bud}</td><td class="num">{run}</td></tr>'
    for n, w, href, bud, run, ten, tbg, *_ in STOPS)

CSS = """
:root{--bg:#FAFAF9;--card:#FFFFFF;--ink:#292524;--mut:#78716C;--line:#E7E5E4;
--acc:#166534;--slate:#475569;}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font:16px/1.62 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;padding:34px 22px}
.wrap{max-width:840px;margin:0 auto}
.home{color:var(--mut);text-decoration:none;font-size:13px}.home:hover{color:var(--acc)}
h1{font-size:27px;margin:8px 0 4px;letter-spacing:-.3px}
.sub{color:var(--mut);max-width:720px;margin:0 0 14px}
.acthead{font-size:14px;font-weight:800;letter-spacing:.2px;margin:26px 0 10px;padding:9px 14px;border-radius:10px}
.h-A{color:var(--acc);background:#F0F5F1;border-left:4px solid var(--acc)}
.h-B{color:var(--slate);background:#F1F3F5;border-left:4px solid var(--slate)}
.stop{background:var(--card);border:1px solid var(--line);border-radius:13px;padding:14px 16px;margin:11px 0}
.s-A{border-left:4px solid var(--acc)}.s-B{border-left:4px solid var(--slate)}
.sh{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.num{flex:none;width:28px;height:28px;border-radius:50%;display:grid;place-items:center;font-weight:800;font-size:13px;color:#fff}
.s-A .num{background:var(--acc)}.s-B .num{background:var(--slate)}
.st{flex:1;font-weight:750;font-size:16px;text-decoration:none;color:var(--ink);min-width:200px}.st:hover{color:var(--acc)}
.bud{color:var(--mut);font-size:12.5px;font-variant-numeric:tabular-nums;white-space:nowrap}
.cue{color:var(--mut);font-size:13px;font-style:italic;margin:6px 0 8px}
.say p{margin:0 0 9px}.say p:last-child{margin-bottom:0}.say em{color:var(--mut)}
table{border-collapse:collapse;width:100%;margin:12px 0;font-size:14px}
th,td{border-bottom:1px solid var(--line);padding:7px 10px;text-align:left}
th{color:var(--mut);font-size:12px;text-transform:uppercase;letter-spacing:.5px}
td.num{text-align:right;font-variant-numeric:tabular-nums;font-weight:650}
tr.t-A td:nth-child(2){color:var(--acc);font-weight:800}tr.t-B td:nth-child(2){color:var(--slate);font-weight:800}
.tot{font-weight:750;margin-top:6px}
.note{color:#44403C;font-size:14px;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:13px 15px;margin-top:14px}
.foot{color:var(--mut);font-size:13px;margin-top:24px;border-top:1px solid var(--line);padding-top:14px}a{color:var(--acc)}
"""

HTML = (f'<!doctype html><html lang="bg" data-lang="bg"><head><meta charset="utf-8">'
        f'<meta name="viewport" content="width=device-width, initial-scale=1">'
        f'<title>Presentation run-sheet — 20 min, 2 presenters</title>'
        f'<style>{CSS}{lang_css()}</style></head><body>{lang_toggle()}<div class="wrap">'
        f'<a class="home" href="../index.html">{T("← Overview", "← Обзор")}</a>'
        f'<h1>{T("Presentation run-sheet — 20 minutes, 2 presenters", "Сценарий за презентация — 20 минути, 2-ма представящи")}</h1>'
        f'{T("Spoken, story-style lines for the homepage track. Presenter <b>A</b> tells the answer (stops 1–6); presenter <b>B</b> shows why to trust it (7–10). Each stop is clickable — it opens the page it narrates. Total talking ≈ 19 min, inside 20.", "Изговорени, разказвателни реплики за маршрута от началната страница. Представящ <b>А</b> разказва отговора (стъпки 1–6); представящ <b>Б</b> показва защо да му вярваме (7–10). Всяка стъпка е кликаема — отваря страницата, която описва. Общо говорене ≈ 19 мин, в рамките на 20.", "p")}'
        f'<p class="sub">{T("Tip: read at a measured pace; the live demos (stops 8 &amp; 10) fill the time. Trim the <em>italic asides</em> first if you run long.", "Съвет: четете с премерено темпо; живите демота (стъпки 8 и 10) запълват времето. Съкратете първо <em>курсивните вмятания</em>, ако надхвърляте.")}</p>'
        f'{A}{B}'
        f'<h2 style="font-size:18px;margin:28px 0 4px">{T("Timing", "Тайминг")}</h2>'
        f'<table><thead><tr><th>#</th><th>{T("Who","Кой")}</th><th>{T("Stop","Стъпка")}</th>'
        f'<th class="num">{T("Budget","Бюджет")}</th><th class="num">{T("Running","Текущо")}</th></tr></thead><tbody>{TROWS}</tbody></table>'
        f'<p class="tot">{T("A = 10:00 · B = 9:00 · Total talking = 19:00", "А = 10:00 · Б = 9:00 · Общо говорене = 19:00")} '
        f'<span class="bud">({T("≈ 1 min buffer, inside 20", "≈ 1 мин резерв, в рамките на 20")})</span></p>'
        f'<div class="note">{T("<b>Tight on time?</b> Drop stop 5 to 30 seconds and cut the italic asides — buys ~1½ min. <b>Need the full 20?</b> Linger on the two demos and take a second audience scenario.", "<b>Малко време?</b> Свалете стъпка 5 до 30 секунди и махнете курсивните вмятания — печели ~1½ мин. <b>Нужни са пълните 20?</b> Задръжте се на двете демота и вземете втори сценарий от публиката.")}</div>'
        f'<p class="foot"><a href="../index.html">{T("← back to overview", "← обратно към обзора")}</a> · '
        f'{T("plain-text source", "текстов източник")}: docs/presentation_script.md · src/report_script.py</p>'
        f'</div></body></html>')

(OUT / "script.html").write_text(HTML, encoding="utf-8")
print(f"wrote outputs/script.html  ({len(STOPS)} stops, A/B, 19:00 total)")
