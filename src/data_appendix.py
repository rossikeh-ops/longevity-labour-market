"""
Reusable "data behind this report" appendix for the HTML reports.

appendix_css()  -> CSS for the link pill + collapsible tables + download button.
data_link()     -> a small pill link near the top that jumps to the appendix.
data_section()  -> the appendix: an <h2 id>, an Excel-download button, and one
                   collapsible <details> per table.

Tables are full data (all countries × sex × year). Collapsed by default so they
stay "behind" the report and open on click. The download button exports every
table to a real multi-sheet .xlsx workbook client-side via SheetJS (CDN) — works
on the static GitHub Pages site, no server needed.
"""
from __future__ import annotations
import json
import math
import re
import pandas as pd

ANCHOR = "data-behind"
SHEETJS = "https://cdn.sheetjs.com/xlsx-0.20.3/package/dist/xlsx.full.min.js"


def appendix_css() -> str:
    return (
        "a.dlink{display:inline-block;margin:2px 0 16px;font-size:13px;font-weight:600;"
        "color:var(--acc,#166534);text-decoration:none;border:1px solid var(--line,#E7E5E4);"
        "border-radius:20px;padding:6px 15px;background:var(--card,#FFFFFF)}"
        "a.dlink:hover{border-color:var(--acc,#166534)}"
        "button.dlbtn{display:inline-block;margin:2px 0 14px;font-size:13px;font-weight:600;"
        "color:#fff;background:var(--acc,#166534);border:1px solid var(--acc,#166534);"
        "border-radius:20px;padding:7px 16px;cursor:pointer}"
        "button.dlbtn:hover{filter:brightness(1.08)}"
        "details.data{margin:12px 0;border:1px solid var(--line);border-radius:12px;"
        "background:var(--card);padding:0 16px}"
        "details.data>summary{cursor:pointer;font-weight:600;padding:14px 2px;list-style:none}"
        "details.data>summary::-webkit-details-marker{display:none}"
        "details.data>summary::before{content:'\\25B8  ';color:var(--acc)}"
        "details.data[open]>summary::before{content:'\\25BE  '}"
        ".dscroll{max-height:440px;overflow:auto;margin:0 0 16px;border-top:1px solid var(--line)}"
        ".dscroll table{font-size:12.5px}"
        ".dscroll thead th{position:sticky;top:0;background:var(--card);z-index:1}"
    )


def data_link(label: str = "Data behind this report") -> str:
    return (f'<a class="dlink" href="#{ANCHOR}">\U0001F4CB {label} &darr;</a> '
            f'<button type="button" class="dlbtn">⬇ Excel (.xlsx)</button>')


def _fmt(v) -> str:
    if v is None:
        return "—"
    if isinstance(v, str):
        return v
    try:
        f = float(v)
    except (TypeError, ValueError):
        return str(v)
    if math.isnan(f):
        return "—"
    if f == int(f):
        iv = int(f)
        return str(iv) if 1900 <= iv <= 2100 else f"{iv:,}"   # years: no separator
    return f"{f:,.1f}" if abs(f) >= 1 else f"{f:,.3f}"


def _table(df: pd.DataFrame, tid: str) -> str:
    thead = "".join(f"<th>{c}</th>" for c in df.columns)
    rows = []
    for _, r in df.iterrows():
        tds = "".join(f"<td>{_fmt(v)}</td>" for v in r)
        rows.append(f"<tr>{tds}</tr>")
    return (f'<div class="dscroll"><table id="{tid}"><thead><tr>{thead}</tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div>')


def _sheet_name(title: str, used: set) -> str:
    """Excel-safe, unique, <=31 chars."""
    s = re.sub(r"[\\/?*\[\]:]", "", title).strip()[:28] or "Sheet"
    base, i, name = s, 2, s
    while name in used:
        name = f"{base[:25]} {i}"
        i += 1
    used.add(name)
    return name


def data_section(frames, heading: str = "Data behind this report",
                 note: str = "", open_first: bool = False,
                 filename: str = "report_data") -> str:
    """frames: list of (title, DataFrame). Returns the appendix HTML with a button
    that downloads every table as one .xlsx workbook (one sheet per table)."""
    parts = [f'<h2 id="{ANCHOR}">{heading}</h2>']
    parts.append('<button type="button" class="dlbtn" id="dl-xlsx">'
                 '⬇ Download as Excel (.xlsx)</button>')
    if note:
        parts.append(f'<p class="sub">{note}</p>')
    used, sheets = set(), []
    for i, (title, df) in enumerate(frames):
        tid = f"dtab-{i}"
        sheets.append({"id": tid, "name": _sheet_name(title, used)})
        op = " open" if (open_first and i == 0) else ""
        parts.append(f'<details class="data"{op}><summary>{title} '
                     f'<span style="color:var(--mut);font-weight:400">· {len(df):,} rows</span>'
                     f'</summary>{_table(df, tid)}</details>')
    parts.append(f'<script src="{SHEETJS}"></script>')
    parts.append(
        "<script>(function(){"
        f"var SHEETS={json.dumps(sheets)};"
        "function run(){"
        "if(!window.XLSX){alert('Excel export library is still loading — please try again.');return;}"
        "var wb=XLSX.utils.book_new();"
        "SHEETS.forEach(function(s){var t=document.getElementById(s.id);"
        "if(t){var ws=XLSX.utils.table_to_sheet(t);XLSX.utils.book_append_sheet(wb,ws,s.name);}});"
        f"XLSX.writeFile(wb,'{filename}.xlsx');}}"
        "document.querySelectorAll('.dlbtn').forEach(function(b){b.addEventListener('click',run);});"
        "})();</script>")
    return "\n".join(parts)
