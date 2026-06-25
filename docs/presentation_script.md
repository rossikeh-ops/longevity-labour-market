# Presentation script — *Longevity & the Labour Market*

A spoken, story-style narration to walk an audience through the site, **one page at a time**.

**Pacing:** each section is written for **~1.5 minutes** at a normal speaking rate (~135 words/min ≈ 200 words). The full walk-through runs **~20 minutes**. Read it conversationally — these are *talking* lines, not slides. Each section starts with a quick **stage cue** (what to have on screen).

> Tip: open the live site at the start and just scroll/click as you talk. The whole site is bilingual (BG | EN) via the toggle, top-right.

---

## 1 · Home — the opening  *(~1.5 min)*
*On screen: the homepage.*

Good morning. Europe is getting older — and across much of the East, smaller. So here's the question we set out to answer: by 2033, can each economy still supply the labour its jobs actually need? The hard part is that you can't compare a life-expectancy number with a job vacancy — they're different units. So we built a translator. We convert demographic averages into a single common currency we call **human-working-years**, and we do it for eight countries — Bulgaria, Poland, Czechia, Romania, Germany, France, Norway and Switzerland — split by sex, all the way to 2033. Everything you'll see is built from live Eurostat data, with deliberately simple, transparent models — no neural networks, no black boxes. This home page is the table of contents: the headline numbers up top, then each level as a guided story or a full report, an interactive what-if, and an honest "can we trust it" section. And there's a QR code right here — scan it to open the repository on your phone and follow along. Let's start with the question itself.

---

## 2 · Introduction — the framing  *(~1.5 min)*
*On screen: the introduction page.*

This page frames the whole study. Europe's ageing isn't a future problem — it's already in the numbers. Age-related public spending across the EU is already about a quarter of GDP, and the ratio of over-65s to working-age people is set to jump from 36% to 55% by 2050. So the stakes are real and near. Our approach is one clean idea: turn everything into human-working-years. **Supply** is healthy, working-age people times how long they actually work. **Demand** is the jobs the economy runs — employees plus vacancies — times the length of service those careers require. **Balance** is simply the difference. And here's our headline preview: in aggregate, Europe is *roughly balanced* — but that average hides a sharp East–West divide. The East runs a big labour surplus; the West and EFTA run a shortage. That one fact — surplus East, shortage West — is the demographic engine behind much of Europe's migration. The introduction also lays out the only three levers that can move this balance: increase supply, ease demand, or keep them aligned. Everything that follows puts numbers on those levers.

---

## 3 · Methodology — under the hood  *(~1.5 min)*
*On screen: the methodology page; point at the engine diagram.*

A quick look under the hood — because a forecast you can't explain is a forecast you can't trust. For every series — life expectancy, healthy years, employment — we don't bet on one model. We average **five simple ones**: a linear trend, damped Holt smoothing, drift, naive, and a mean-reverting AR-one. That's the whole engine, and it's literally one line of code. Why so simple? Because the histories are short — about thirteen years — and we deliberately use no neural networks; with this little data, fancy models overfit and mislead. We even tested whether separate three-, six-, and nine-year models would be more accurate — and the answer, shown right here, is no: a dedicated nine-year model trains on a handful of points and does *worse*. The uncertainty bands you'll see aren't decorative — they combine model disagreement, real out-of-sample backtest error, and demographic uncertainty, which is why they're an honest twelve-to-forty-percent wide, not a fake plus-or-minus five. And there's a live visualizer where you can drag the noise yourself and watch the ensemble form the band.

---

## 4 · Level 1 · Supply — who can work  *(~1.5 min)*
*On screen: Level 1 report / story; show the map.*

Level one: labour **supply** — who can actually work. We take healthy, working-age people and multiply by their expected working life, giving supply in human-working-years. Here's the surprising part. Working-age populations are shrinking — especially in the East — yet total supply barely moves: from about 4,490 down to 4,390 million by 2033, just minus two-and-a-half percent. Why so flat? Because three forces push back against the falling headcount: people are healthier, they work longer, and participation is rising — especially women and older workers. That's the **longevity dividend**, and it's already holding the line. The split is starkly demographic: Romania and Bulgaria fall hardest — emigration plus ageing — while Germany, France and Norway actually gain a few percent. The map shows that gradient at a glance. One honest caveat we keep front and centre: supply here is a *potential ceiling* — net of health and working-life, but before skills mismatch and frictions. So it's the maximum the demography allows, not a promise. Every number carries a band, and you can download the underlying data as Excel from any report.

---

## 5 · Level 2 · Demand — what the economy needs  *(~1.5 min)*
*On screen: Level 2 report / story.*

Level two flips to the other side of the ledger: labour **demand** — the work the economy needs done. We build it as the number of jobs — employed people plus open vacancies — times the required length of service for a full career. Forecast to 2033, demand is also remarkably flat: from about 4,420 down to 4,310 million, again around minus two-and-a-half percent. That message matters: demand doesn't run away. The imbalance we're about to see doesn't come from an explosion in how much labour Europe needs — it comes from *where* the working-age people are. Two modelling notes. Vacancies are the hard part — they're shock-driven and cyclical, so we forecast them through an anchored Beveridge curve that ties them to unemployment, rather than letting a trend run wild. And the required service length comes from each country's actual pension rules, by sex. There's also a scenario here — what happens if participation plateaus instead of rising. As always: per-country bands, a sex split, and the full data appendix.

---

## 6 · Level 3 · Balance — the headline  *(~1.5 min)*
*On screen: Level 3 — the diverging bars / map.*

This is the headline — level three. We simply subtract: supply minus demand, country by country, to 2033. And here's the result that defines the whole study. In total, the eight countries are *roughly balanced* — a net of just plus eighty-nine million, which on stocks of over four billion is essentially zero. But that aggregate is misleading — and this is the key insight: it hides a sharp **East–West divide**. The East — Poland, Romania, Czechia, Bulgaria — runs a surplus of about **plus 370 million** human-working-years. The West and EFTA — Germany, France, Switzerland, Norway — run a shortage of about **minus 280 million**. Poland's reserve alone roughly offsets Germany's, France's and Switzerland's shortfalls combined. That is the demographic basis of West-bound migration, in one number. The diverging bars and the map make it vivid — green East, red West. One honesty point: the balance is a small difference of two large forecasts, so its relative error is amplified. Read it as a robust *structural signal* — surplus East, shortage West — with wide bands, not a precise point. And we've validated exactly that with a leakage-safe backtest.

---

## 7 · Level 4 · Cost of unhealthy years  *(~1.5 min)*
*On screen: Level 4.*

From here we open the horizons. Level four asks: what's the human cost of longer lives that aren't fully healthy? We measure the **poor-health burden** — population times the years lived in poor health, that's life expectancy minus healthy life years. To 2033 it stays high — around 4,260 million person-years. Then we did something we think matters: we tested, honestly, whether that burden actually drives the health-and-social-care sector's output. And the answer is *no*. Across countries it looks correlated — but that's mostly country size. Within a country, over time, the link is essentially zero: the sector tracks GDP and incomes, not the demographic burden. So we report it as a descriptive relationship, not a predictor — we refuse to dress a correlation up as causation. And there's an honesty thread through this whole level and the next two: healthy life years come from a *self-perceived* survey question — Eurostat's GALI. So levels are partly cultural — Switzerland reports low healthy years despite the highest life expectancy. We read shifts and directions, not absolute levels — and we say so on every page.

---

## 8 · Level 5 · Healthy-retirement dividend  *(~1.5 min)*
*On screen: Level 5 — the diverging per-person bar.*

Level five is the optimistic flip side — the **healthy-retirement dividend**. The idea: how many healthy years do people get *after* the retirement age — healthy life years minus the statutory retirement age. And the spread is striking: from plus five-point-six years per person in Bulgaria, all the way to minus six-point-six in Switzerland — meaning in several countries, self-reported health declines before people even reach retirement. Scaled by population, the dividend — all those active, healthy retirees — grows from about 200 to 438 million person-years by 2033. These are the people who fill the concert halls, the courses, the travel. So we tested: does that dividend drive leisure, education and culture spending? Same honest answer — across countries it co-moves, but within a country it's basically zero. Consumption tracks income, not the demographic dividend. So: a real, meaningful demographic quantity, but not a usable predictor of spending — and we present it that way. Remember the GALI caveat: Switzerland's minus-six-point-six is low *self-reported* health, not short lives. Read the sign and the ranking, not the exact level.

---

## 9 · Level 6 · Longevity in the macroeconomy  *(~1.5 min)*
*On screen: Level 6 — the labour-vs-productivity decomposition.*

Level six connects everything to the bottom line — real GDP. We use a simple identity: GDP equals employment times productivity. So growth splits cleanly into a **labour** channel — the one our longevity engine drives — and a **productivity** channel. Decomposed to 2033, the pattern is clear: the East grows mainly on productivity catch-up, with flat or even shrinking labour — Romania's labour channel is actually negative, a demographic drag. The West leans more on labour, because its productivity growth is slow. Combined, real GDP rises from about eight to eight-point-six trillion euros — roughly point-eight percent a year, mostly productivity-led. Then the reverse question: does *healthier* longevity make workers more productive? You'd hope so. But the data says no — and the wrong way: across countries, healthy share and productivity correlate minus zero-point-eight-seven — the most productive countries report the *lowest* healthy share. That's the GALI artifact again, not reality. Within countries, the link is zero. So the honest capstone: longevity reaches the economy through the *number* of healthy people working — the labour channel — not a per-worker productivity premium. Which is exactly why the supply levers matter.

---

## 10 · What-if sandbox — play with it  *(~1.5 min)*
*On screen: the what-if; drag the Healthy-life-years dial as you talk.*

Now the part I'd really encourage you to play with yourselves. This sandbox ties levels one, four and five into one live model. Three dials. One: do people live longer *in good health* — shift healthy life years. Two: do they retire later. Three: do more of them work — participation. And four answers update instantly: who keeps working, who retires, who needs healthcare, and who fills the concert halls. Watch one move. If I add three healthy years for all eight countries — just this dial — the workforce grows nearly five percent, the care burden falls seventeen percent, and the active healthy-retiree pool more than triples. One lever, three wins. We've also put the jobs view right by the participation dial: as participation rises, you can watch occupied jobs go up and open job-listings fall — the vacancies get filled. It's a deterministic, central-path scenario — illustrative, not a full labour-market model — but it makes the trade-offs tangible. And these are exactly the questions finance and labour ministries are paying to answer.

---

## 11 · Model trust — the honesty audit  *(~1.5 min)*
*On screen: the model-trust report.*

Before you believe any of this — can we trust it? This page is our honesty audit. We use rolling-origin cross-validation: hold out the last few years, forecast them from history only, and measure how far off we are. The structural drivers do well — life expectancy at one-point-two percent error, working-life and employment under two. The composed outputs are tight too: supply at three-point-six percent, demand at two-point-two. And we're equally upfront about the weak spots. Healthy share and job vacancies are near-random-walks — vacancies sit at twenty-four percent, which exactly ties a naive last-year guess, because year-to-year vacancies are genuinely unforecastable. We don't hide that; we model them at their honest ceiling. The balance, being a small difference of two big numbers, carries about twenty-three percent relative error — so we call it a direction, not a point. There's a train-versus-backtest table showing the models aren't overfitting, and a small side-study on occupied posts. The whole philosophy here: state the error, show the failure points, never over-claim.

---

## 12 · Practical applications — so what  *(~1.5 min)*
*On screen: the applications page.*

So — who actually uses this, and why does it matter? This page makes the case that none of it is academic. Pensions and retirement policy: ministries use the healthy-years-after-retirement number to judge how far retirement ages can credibly rise. Health and long-term-care planning: the poor-health burden projects demand for hospitals and carers — the fastest-rising line in the EU's own Ageing Report. Labour and migration policy: that East-surplus, West-shortage divide is the demographic basis for mobility and immigration. Macro and fiscal sustainability: treasuries and central banks need the labour-versus-productivity split for potential-output and tax-base projections. Employers, pension funds and insurers price longevity and plan automation against the shrinking supply. And the silver economy — Europe's healthy, active over-fifties — is already a 3.7-trillion-euro market supporting 78 million jobs. Each tile links straight to the level that supports it, all grounded in the European Commission's 2024 Ageing Report and its Silver Economy study. The point: convert demography into human-working-years, and suddenly all of these decisions become comparable and quantifiable — while there's still time to act.

---

## 13 · Close  *(~1.5 min)*
*On screen: back to the homepage / the QR code.*

To wrap up. We took an ageing continent and a simple but stubborn problem — you can't weigh life expectancy against jobs — and we built a translator: human-working-years. With that one move — eight countries, both sexes, out to 2033 — the picture snapped into focus. Europe is roughly balanced in total, but structurally split: a labour surplus in the East, a shortage in the West. Longevity is quietly holding supply flat against a shrinking population; the human costs and the healthy-retirement dividend are real, but they don't mechanically drive spending; and in the macroeconomy, longevity works through the *number* of healthy workers, not a productivity boost. Throughout, we chose transparency over sophistication — five simple models, honest bands, no black boxes — and we were candid about what we can't predict. Everything is reproducible: every chart, every number, downloadable, with the full pipeline in the repository. And the whole site is bilingual, one click. So please — scan the QR, open it on your phones, drag the what-if dials, and challenge the numbers. Thank you.

---

*~13 pages × ~1.5 min ≈ 20 minutes. Trim Levels 4–6 or the applications page to reach ~12 minutes; drop the close for a hard 10.*
