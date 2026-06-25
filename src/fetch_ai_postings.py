# -*- coding: utf-8 -*-
"""
Download the OECD.AI / Lightcast "share of AI job postings" series (the truest
'AI jobs' signal) via Our World in Data's public CSV, filtered to the 8 case
countries. Saves data/raw/ai_job_postings_share__<date>.csv.
"""
from __future__ import annotations
import datetime as dt
import io
from pathlib import Path
import requests
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
TODAY = dt.date.today().isoformat()
URL = ("https://ourworldindata.org/grapher/share-artificial-intelligence-job-postings.csv"
       "?v=1&csvType=full&useColumnShortNames=true")
ISO = {"BGR": "BG", "POL": "PL", "CZE": "CZ", "ROU": "RO",
       "DEU": "DE", "FRA": "FR", "NOR": "NO", "CHE": "CH"}

r = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=60)
r.raise_for_status()
d = pd.read_csv(io.StringIO(r.text))
d = d[d.code.isin(ISO)].copy()
d["country"] = d.code.map(ISO)
d = d.rename(columns={"ai_job_postings_share": "ai_postings_share_pct"})
out = d[["country", "year", "ai_postings_share_pct"]].sort_values(["country", "year"])
out.to_csv(RAW / f"ai_job_postings_share__{TODAY}.csv", index=False)

print("AI job-postings share (% of all online postings) — OECD.AI / Lightcast via OWID")
for c in ["BG", "PL", "CZ", "RO", "DE", "FR", "NO", "CH"]:
    s = out[out.country == c]
    if len(s):
        r2 = s.loc[s.year.idxmax()]
        print(f"  {c}: {r2.ai_postings_share_pct:.3f}%  ({int(r2.year)})   span {int(s.year.min())}–{int(s.year.max())}")
    else:
        print(f"  {c}: NOT covered by Lightcast")
print(f"\nwrote data/raw/ai_job_postings_share__{TODAY}.csv ({len(out)} rows)")
