#!/usr/bin/env python3
"""news-image-20261122 v1 entrypoint (Python 3.13, standard library only).

The front page is drawn by gen.py (build-time tool, Pillow) into the
entry.png shipped beside this file; this program copies that image to the
output directory. Deterministic: the same bytes are written on every run.

Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
  mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""
import os
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))

OUT.mkdir(parents=True, exist_ok=True)
shutil.copyfile(HERE / "entry.png", OUT / "entry.png")
