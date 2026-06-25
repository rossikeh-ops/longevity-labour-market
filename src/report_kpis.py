# -*- coding: utf-8 -*-
"""
Build outputs/kpis.html — "KPIs at a glance" on its own page (bilingual BG|EN,
earthy theme). Headline numbers across every level, computed from the outputs so
they never drift, each tile linking to the report that produces it.
"""
from __future__ import annotations
import sys
import json
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from i18n import lang_css, lang_toggle  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
M = 1e6
WEST = ["DE", "FR", "CH", "NO"]
EAST = ["PL", "RO", "CZ", "BG"]

bf = pd.read_csv(OUT / "balance_forecast.csv").query("year == 2033")
net = round(bf.balance.sum() / M)
west = round(bf[bf.country.isin(WEST)].balance.sum() / M)
east = round(bf[bf.country.isin(EAST)].balance.sum() / M)
so = pd.read_csv(OUT / "supply_observed.csv")
sf = pd.read_csv(OUT / "supply_forecast.csv")
df = pd.read_csv(OUT / "demand_forecast.csv")
s24, s33 = so[so.year == 2024].supply_realized.sum() / M, sf[sf.year == 2033].supply_realized.sum() / M
d24, d33 = so[so.year == 2024].demand.sum() / M, df[df.year == 2033].demand.sum() / M
schg, dchg = (s33 / s24 - 1) * 100, (d33 / d24 - 1) * 100
burden = round(pd.read_csv(OUT / "cost_forecast.csv").query("year == 2033").poor_py.sum() / M)
dividend = round(pd.read_csv(OUT / "dividend_forecast.csv").query("year == 2033").dividend_py.sum() / M)
mo = pd.read_csv(OUT / "macro_observed.csv")
mf = pd.read_csv(OUT / "macro_forecast.csv")
gdp33 = mf[mf.year == 2033].gdp.sum() / 1e6
cagr = ((gdp33 / (mo[mo.year == 2024].gdp.sum() / 1e6)) ** (1 / 9) - 1) * 100
la = json.loads((OUT / "validation_metrics.json").read_text(encoding="utf-8"))["level_acc"]


def tile(href, value, color, en, bg):
    col = f' style="color:{color}"' if color else ""
    return (f'<a class="ktile" href="{href}"><div class="v"{col}>{value}</div>'
            f'<div class="l"><span lang="en">{en}</span><span lang="bg">{bg}</span></div></a>')


def group(en, bg, tiles):
    return (f'<div class="kgroup"><span lang="en">{en}</span><span lang="bg">{bg}</span></div>'
            f'<div class="kdash">{"".join(tiles)}</div>')


GREEN, RED, AMBER = "var(--ok)", "#B91C1C", "var(--warn)"
BODY = (
    group("Headline · labour-market balance 2033 (human-working-years)",
          "Заглавно · баланс на пазара на труда 2033 (човеко-работни години)", [
              tile("level3.html", f"{net:+,}M", GREEN, "Net balance (≈ balanced in aggregate)", "Нетен баланс (≈ балансиран сумарно)"),
              tile("level3.html", f"{east:+,}M", GREEN, "East surplus (PL, RO, CZ, BG)", "Излишък на Изток (PL, RO, CZ, BG)"),
              tile("level3.html", f"{west:+,}M", RED, "West/EFTA shortage (DE, FR, CH, NO)", "Недостиг Запад/ЕАСТ (DE, FR, CH, NO)"),
          ]) +
    group("Building blocks · supply &amp; demand (2024 → 2033)",
          "Градивни елементи · предлагане и търсене (2024 → 2033)", [
              tile("level1.html", f"{round(s33):,}M", None, f"Labour supply, human-working-years ({schg:+.1f}%)", f"Предлагане на труд, човеко-работни години ({schg:+.1f}%)"),
              tile("level2.html", f"{round(d33):,}M", None, f"Labour demand, human-working-years ({dchg:+.1f}%)", f"Търсене на труд, човеко-работни години ({dchg:+.1f}%)"),
          ]) +
    group("Open horizons · health, retirement &amp; macro (2033)",
          "Отворени хоризонти · здраве, пенсиониране и макро (2033)", [
              tile("level4.html", f"{burden:,}M", None, "Poor-health person-years (LE − HLY)", "Човеко-години в лошо здраве (ОПЖ − ЗГЖ)"),
              tile("level5.html", f"{dividend:,}M", None, "Healthy-retirement dividend (+5.6 to −6.6 yrs/person)", "Дивидент от здраво пенсиониране (+5.6 до −6.6 г./човек)"),
              tile("level6.html", f"€{gdp33:.1f}T", None, f"Real GDP (≈{cagr:.1f}%/yr, productivity-led)", f"Реален БВП (≈{cagr:.1f}%/год., водено от производителност)"),
          ]) +
    group("Can we trust it? · leakage-safe backtest accuracy (MAPE)",
          "Можем ли да вярваме? · точност при бектест без изтичане (MAPE)", [
              tile("model_validation_report.html", f"{la['supply_mape']}%", GREEN, "Supply forecast error", "Грешка в прогнозата за предлагане"),
              tile("model_validation_report.html", f"{la['demand_mape']}%", GREEN, "Demand forecast error", "Грешка в прогнозата за търсене"),
              tile("model_validation_report.html", f"~{la['balance_rel']}%", AMBER, "Balance (a difference of two large stocks)", "Баланс (разлика на две големи величини)"),
          ]))

CSS = """
:root{--bg:#FAFAF9;--card:#FFFFFF;--ink:#292524;--mut:#78716C;--line:#E7E5E4;--acc:#166534;--ok:#15803D;--warn:#D97706;}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font:16px/1.6 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;padding:36px 24px}
.wrap{max-width:980px;margin:0 auto}
.home{color:var(--mut);text-decoration:none;font-size:13px}.home:hover{color:var(--acc)}
h1{font-size:28px;margin:6px 0 4px}.sub{color:var(--mut);margin:0 0 10px;max-width:820px}
.kgroup{color:var(--mut);font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.6px;margin:22px 0 8px}
.kdash{display:grid;grid-template-columns:repeat(auto-fit,minmax(155px,1fr));gap:12px}
a.ktile{display:block;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px 18px;
text-decoration:none;color:inherit;transition:border-color .15s,transform .15s}
a.ktile:hover{border-color:var(--acc);transform:translateY(-2px)}
a.ktile .v{font-size:23px;font-weight:750;line-height:1.1}
a.ktile .l{color:var(--mut);font-size:12.5px;margin-top:4px}
.foot{color:var(--mut);font-size:13px;margin-top:28px}a{color:var(--acc)}
"""

HTML = f"""<!doctype html><html lang="bg" data-lang="bg"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>KPIs at a glance — longevity &amp; the labour market</title>
<style>{CSS}{lang_css()}</style></head><body>{lang_toggle()}<div class="wrap">
<a class="home" href="../index.html"><span lang="en">← Overview</span><span lang="bg">← Обзор</span></a>
<h1><span lang="en">KPIs at a glance</span><span lang="bg">Ключови показатели накратко</span></h1>
<p class="sub"><span lang="en">The headline numbers across every level, for 2033 — click any tile to open its report.
Computed live from the model outputs, so they never drift.</span><span lang="bg">Основните числа по всички нива за 2033 г. —
щракнете върху плочка, за да отворите доклада ѝ. Изчислени директно от изходите на модела, така че не се разминават.</span></p>
{BODY}
<p class="foot"><a href="../index.html"><span lang="en">← Back to overview</span><span lang="bg">← Обратно към обзора</span></a> · src/report_kpis.py</p>
</div></body></html>"""

(OUT / "kpis.html").write_text(HTML, encoding="utf-8")
print(f"wrote outputs/kpis.html  (net {net:+}M, supply {round(s33)}M, GDP €{gdp33:.1f}T)")
