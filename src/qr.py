# -*- coding: utf-8 -*-
"""
Generate outputs/qr_repo.svg — a QR code that opens the project's GitHub
repository. Self-contained SVG, earthy forest colour, embedded on the homepage.
"""
from __future__ import annotations
from pathlib import Path
import segno

OUT = Path(__file__).resolve().parents[1] / "outputs"
URL = "https://github.com/rossikeh-ops/longevity-labour-market"

qr = segno.make(URL, error="m")
qr.save(OUT / "qr_repo.svg", scale=5, border=2, dark="#166534", light="#ffffff")
print(f"wrote outputs/qr_repo.svg  ->  {URL}")
