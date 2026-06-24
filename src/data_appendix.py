"""
Reusable "data behind this report" appendix for the HTML reports.

appendix_css()  -> CSS for the link pill + collapsible tables (uses theme vars).
data_link()     -> a small pill link near the top that jumps to the appendix.
data_section()  -> the appendix: an <h2 id> + one collapsible <details> per table.

Tables are full data (all countries × sex × year). Collapsed by default so they
stay "behind" the report and open on click. Self-contained — no extra files.
"""
from __future__ import annotations
import math
import pandas as pd

ANCHOR = "data-behind"


def appendix_css() -> str:
    return (
        "a.dlink{display:inline-block;margin:2px 0 16px;font-size:13px;font-weight:600;"
        "color:var(--acc);text-decoration:none;border:1px solid var(--line);"
        "border-radius:20px;padding:6px 15px;background:var(--card)}"
        "a.dlink:hover{border-color:var(--acc)}"
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
    return f'<a class="dlink" href="#{ANCHOR}">\U0001F4CB {label} &darr;</a>'


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


def _table(df: pd.DataFrame) -> str:
    thead = "".join(f"<th>{c}</th>" for c in df.columns)
    rows = []
    for _, r in df.iterrows():
        tds = "".join(f"<td>{_fmt(v)}</td>" for v in r)
        rows.append(f"<tr>{tds}</tr>")
    return (f'<div class="dscroll"><table><thead><tr>{thead}</tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div>')


def data_section(frames, heading: str = "Data behind this report",
                 note: str = "", open_first: bool = False) -> str:
    """frames: list of (title, DataFrame). Returns the appendix HTML."""
    parts = [f'<h2 id="{ANCHOR}">{heading}</h2>']
    if note:
        parts.append(f'<p class="sub">{note}</p>')
    for i, (title, df) in enumerate(frames):
        op = " open" if (open_first and i == 0) else ""
        parts.append(f'<details class="data"{op}><summary>{title} '
                     f'<span style="color:var(--mut);font-weight:400">· {len(df):,} rows</span>'
                     f'</summary>{_table(df)}</details>')
    return "\n".join(parts)
