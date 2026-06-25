# -*- coding: utf-8 -*-
"""
Shared bilingual (BG | EN) toggle for every generated page.

Mechanism: each translatable element is authored twice, with lang="en" and
lang="bg". A fixed top-right button flips document.documentElement.dataset.lang;
CSS hides the inactive language. The choice is remembered in localStorage so it
carries across every page of the site.

Usage in a generator:
    from i18n import lang_css, lang_toggle, T
    ...<style>{CSS}{lang_css()}</style>...
    <body>{lang_toggle()} ...
    {T('English text', 'Български текст')}            # inline or block pair
"""
from __future__ import annotations


def lang_css() -> str:
    return (
        "html[data-lang='en'] [lang='bg']{display:none!important}"
        "html[data-lang='bg'] [lang='en']{display:none!important}"
        ".langtoggle{position:fixed;top:14px;right:14px;z-index:9999;background:var(--card,#fff);"
        "border:1px solid var(--line,#E7E5E4);border-radius:20px;padding:7px 15px;cursor:pointer;"
        "font:700 13px/1 -apple-system,Segoe UI,Roboto,Arial,sans-serif;color:var(--acc,#166534);"
        "box-shadow:0 2px 10px rgba(0,0,0,.08)}.langtoggle:hover{border-color:var(--acc,#166534)}"
    )


def lang_toggle() -> str:
    """The button + the persistence script. Place just inside <body>."""
    return (
        '<button class="langtoggle" id="langtoggle" aria-label="switch language">БГ</button>'
        "<script>(function(){var r=document.documentElement;"
        "var L=localStorage.getItem('site-lang')||'en';r.dataset.lang=L;"
        "var b=document.getElementById('langtoggle');"
        "function u(){b.textContent=r.dataset.lang==='en'?'БГ':'EN';}"
        "b.onclick=function(){var n=r.dataset.lang==='en'?'bg':'en';r.dataset.lang=n;"
        "localStorage.setItem('site-lang',n);u();};u();})();</script>"
    )


def T(en: str, bg: str, tag: str = "span") -> str:
    """A bilingual pair: shows `en` or `bg` depending on the active language."""
    return f'<{tag} lang="en">{en}</{tag}><{tag} lang="bg">{bg}</{tag}>'
