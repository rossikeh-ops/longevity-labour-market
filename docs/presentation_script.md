# Presentation script — *Longevity & the Labour Market*  ·  **20-minute version**

A spoken, story-style narration for **two presenters**, matching the site's **Presentation track** (the numbered 1–10 strip on the homepage). Total run-time **~19 minutes** of talking, leaving ~1 min for the handoff and a quick question — **inside 20 minutes**.

- **Presenter A — "The answer"** — stops 1–6 (~10 min): the question, the findings, what they mean.
- **Presenter B — "Why believe it"** — stops 7–10 (~9 min): how it works, and how far to trust it.

**Pacing:** written lean, for ~115 spoken words/min, so the live demos (stops 8 and 10) and natural pauses fit *inside* the budget rather than blowing it. Each stop shows its **budget** and the **running total**. Each opens with a **stage cue** (what to click); cut the *italic asides* first if you're running long.

> Open the live site and click straight down the homepage track. Everything is bilingual (BG | EN) — toggle top-right, carries across every page.

---
---

# 🟢 PRESENTER A — "The answer"  *(stops 1–6 · ~10 min)*

## 1 · Intro + KPIs — the question  *(2 min · total 2:00)*
*On screen: homepage, then click **1 · Intro + KPIs**.*

Good morning. We'll split this: I'll show you **what we found**, then my colleague shows you **why you can trust it**.

Europe is getting older — and across much of the East, smaller. So our question is: by 2033, can each economy still supply the labour its jobs actually need? The hard part is units — you can't weigh a life-expectancy number against a job vacancy. So we built a translator: we convert demographic averages into **one common currency, human-working-years**, for eight countries — Bulgaria, Poland, Czechia, Romania, Germany, France, Norway, Switzerland — by sex, out to 2033. It's one equation: **supply** is healthy working-age people times how long they work; **demand** is the jobs the economy runs times the service those careers require; **balance** is the difference. All from live Eurostat data, deliberately simple models — no neural networks.

And here's the headline, in the KPI board: in aggregate Europe is **roughly balanced** — about **+89 million** human-working-years. But that average hides everything. Underneath is a sharp **East–West divide**: the East runs a surplus of about **+370 million**, the West and EFTA a shortage of about **−280 million**. *That one fact — surplus East, shortage West — is the demographic engine behind much of Europe's migration.* Let me show you how it's built.

---

## 2 · Level 1 · Supply — who can work  *(1.5 min · total 3:30)*
*On screen: click **2 · Supply**; show the map.*

Level one: **supply** — healthy working-age people times their expected working life.

Here's the surprise. Working-age populations are **shrinking**, especially in the East — yet total supply **barely moves**: from about **4,490 down to 4,390 million**, only minus two-and-a-half percent. Why so flat? Three forces push back: people are **healthier**, they **work longer**, and **participation is rising** — especially women and older workers. That's the **longevity dividend**, already holding the line.

But the average hides the geography: **Romania and Bulgaria fall hardest** — emigration plus ageing — while **Germany, France and Norway gain**. The map shows that gradient at a glance. *One honest caveat: this is a **potential ceiling** — before skills mismatch and frictions — and every number carries a band.*

---

## 3 · Level 2 · Demand — what the economy needs  *(1.5 min · total 5:00)*
*On screen: click **3 · Demand**.*

Level two: **demand** — the jobs the economy runs, employees plus vacancies, times required service. Same currency, directly comparable to supply.

And demand is also **broadly flat**: about **4,420 down to 4,310 million**, again minus two-and-a-half percent. That's the key point — **demand doesn't run away**. The imbalance isn't an explosion in labour needs; it's about **where the working-age people are**. Geography, not appetite.

One honest piece of engineering: **vacancies are our weakest input** — shock-driven, almost a random walk — so instead of extrapolating them, we tie them to unemployment through a **Beveridge curve**: vacancies fall when unemployment rises. That keeps them stable and scenario-able. *My colleague will show you exactly how reliable that is.*

---

## 4 · Level 3 · Balance — the climax  *(2.5 min · total 7:30)*
*On screen: click **4 · Balance**; show the balance map.*

Now the headline. **Balance is supply minus demand** — and because it's a small difference of two huge numbers, this is where it sharpens.

At the European level they almost cancel: a net of about **plus 89 million**. On its own that sounds like "Europe is fine." But it's a **mirage**. Split East versus West and the real structure appears. The **East runs a surplus of about +370 million** — Poland, Romania, Czechia, Bulgaria have more potential labour than their economies demand. The **West and EFTA run a shortage of about −280 million** — Germany, France, Switzerland, Norway need more than they have. So it isn't one balanced continent; it's **two opposite imbalances that cancel on paper** — and that's precisely the demographic basis for West-bound migration.

*Now the honesty:* balance is a small difference of two big forecasts, so its relative error is amplified — around twenty-odd percent. So we don't read it as a precise point; we read it as a **direction with wide bands** — a structural East-surplus, West-shortage signal — and one we stress-tested by holding out the COVID years and predicting straight through them. If you remember one thing from my half, make it this map.

---

## 5 · Open horizons · Levels 4–6  *(1 min · total 8:30)*
*On screen: click **5 · Open horizons**.*

Three "open horizons" — and here the key is what we **honestly did not find**. Level four is the **poor-health burden**; level five the **healthy-retirement dividend**; level six the **macroeconomy** — GDP growing from about eight to eight-and-a-half trillion euros, under one percent a year, almost all of it productivity.

Across countries these all *look* strongly linked to health. But look **within a country, over time**, and the link is essentially **zero** — spending tracks GDP and income, not the longevity quantity. *So we report these as descriptions, never cause and effect.* That restraint is the result.

---

## 6 · Implications & shocks  *(1.5 min · total 10:00)*
*On screen: click **6 · Implications & shocks**.*

So what moves it? Only **three levers**: **increase supply** — participation, retention, migration; **ease demand** — automation and productivity; or **maintain balance** — education and retirement-age policy. The East's surplus and the West's shortage are the map for where each one bites.

And because the real world isn't only slow demographics, this page measures the **shocks** from our own data: the **COVID** vacancy collapse — Poland down over forty percent, then a sharp rebound; the **Ukraine war** as a refugee supply boost to Poland and Czechia; and **AI** as the slow structural force, with adoption from nearly **thirty percent of firms in Norway** down to **five in Romania**. *That's the answer and the stakes — over to my colleague for why you can believe it.*

---
---

# 🔵 PRESENTER B — "Why believe it"  *(stops 7–10 · ~9 min)*

## 7 · Methodology — how it works  *(2 min · total 12:00)*
*On screen: click **7 · Methodology**; point at the engine diagram.*

Thank you. A forecast you can't explain is one you can't trust — so let me open the hood.

For every series we don't bet on one model. We **average five simple ones**: linear, damped Holt, drift, naïve, and a mean-reverting AR-one. The simplicity is deliberate — our histories are short, about thirteen to twenty points, and we use **no neural networks**: with this little data, flexible models overfit and mislead.

And we tested that. A fair challenge: surely a model dedicated to the nine-year forecast beats one general model? The chart says no — at every horizon the single ensemble wins, because a dedicated nine-year model trains on a median of just **three** data points and starves. We go further in honesty: on these slow series the **naïve "last value" is the hardest thing to beat**, so the win is restraint that hugs that floor. And the **bands** aren't decoration — they combine model disagreement, real backtest error, and migration uncertainty, which is why they're honestly twelve-to-forty percent wide. Let me make that tangible.

---

## 8 · Model playground — drag it live  *(2.5 min · total 14:30)*
*On screen: click **8 · Model playground**; actually drag the sliders.*

The method you can *touch* — two live toys, and watch the screen, not me.

First, **ensemble uncertainty**. As I add more simple models and a little noise — watch — a *cloud* of forecasts forms, and our band is just the spread of that cloud. No magic: the uncertainty is literally the **disagreement among honest simple models**.

Second — my favourite — **flexibility, the bias–variance tradeoff**, on a real Healthy-Life-Years series for Czechia. This slider is model flexibility. Drag it left, to a flat line — too rigid, it **underfits**. Drag it right, to a wiggly curve, and watch the bottom chart: the **training error keeps falling**, but the **cross-validated error explodes** — from about **0.7 up to 15**. That's overfitting, live — the model memorising noise. The sweet spot sits at a **modest** flexibility, degree three here — which is exactly why we use simple models, and why a neural network would land far to the right, deep in the overfit zone. *You've now seen, with your own eyes, what's on either side of the choice we made.*

---

## 9 · Trust & critique — on the stand  *(2.5 min · total 17:00)*
*On screen: click **9 · Trust & critique**.*

The part I'm proudest of: we put **our own model on trial**.

**The case for it:** rolling-origin cross-validation — hold out the last years, forecast from history only. Life expectancy at **1.2 percent** error, employment under two; the composed **supply at 3.6 percent, demand at 2.2**. We even added a proper scoring rule, **CRPS**, which grades the whole band, not just the point — and skill versus naïve is **positive for every driver, averaging +0.29**. Even vacancies score well, because our bands are **well-calibrated**: the model knows what it doesn't know.

**The case against — our own audit.** Three findings. One: **bootstrap confidence intervals** on every number — vacancies aren't "24 percent," they're 24 with a range of **16 to 34**. Real precision, not false. Two — the big one: the East–West split partly rides on **self-reported health**, which isn't comparable across countries; strip it out and the surplus and shortage **nearly collapse into each other**. So we flag the cross-country split as our **least robust** headline. Three: across countries the longevity-to-spending links look powerful — R-squared near **0.99**; *within* a country they fall to **zero**. The 0.99 is pure country size.

And **every** time we reached for a fancier tool — a regression tree, gradient boosting, per-horizon specialists — we measured it, and it **lost**. *We didn't just prefer simple; we proved simple wins.*

---

## 10 · What-if sandbox — the finale  *(2 min · total 19:00)*
*On screen: click **10 · What-if sandbox**; take a scenario from the audience.*

Let me end where it gets personal — because behind every number is a human question: who keeps working, who retires, who needs care, and who fills the concert halls and the adult-education classes?

This is a **live sandbox**: three dials — **healthy life years**, **retirement age**, **participation** — and four answers that update instantly, all on the same identities you've seen, even showing occupied jobs and open listings move in real time.

Give me a scenario — anyone. *[Take one; otherwise:]* Say people stay **healthy two years longer** and we nudge **participation** up — watch supply rise and the shortage shrink. Now push the **retirement age** the other way, and watch *who* it helps and *who* it strains — because the answer isn't the same in Sofia as in Stuttgart.

That's the whole point: not a prophecy, a **transparent engine you can interrogate** — honest about what it knows and what it doesn't, reproducible from raw data to this slider. The structural message is robust: the **longevity dividend is real** and holding supply up, but it sits on a deep **East–West divide** — and these dials are where policy meets it. Thank you — happy to take questions.

---
---

### Timing summary
| | Presenter | Stop | Budget | Running |
|---|---|---|---|---|
| 1 | 🟢 A | Intro + KPIs | 2:00 | 2:00 |
| 2 | 🟢 A | Supply (L1) | 1:30 | 3:30 |
| 3 | 🟢 A | Demand (L2) | 1:30 | 5:00 |
| 4 | 🟢 A | Balance (L3) | 2:30 | 7:30 |
| 5 | 🟢 A | Open horizons (L4–6) | 1:00 | 8:30 |
| 6 | 🟢 A | Implications & shocks | 1:30 | 10:00 |
| 7 | 🔵 B | Methodology | 2:00 | 12:00 |
| 8 | 🔵 B | Model playground | 2:30 | 14:30 |
| 9 | 🔵 B | Trust & critique | 2:30 | 17:00 |
| 10 | 🔵 B | What-if sandbox | 2:00 | 19:00 |

**A = 10:00 · B = 9:00 · Total talking = 19:00** (≈ 1 min buffer for handoff + one question, inside 20 min).

> **Tight on time?** Drop stop 5 to 30 seconds and cut the italic asides — buys ~1½ min. **Need to stretch to a full 20?** Linger on the two demos (stops 8 and 10) and take a second audience scenario.
