# The World in One Day — Sunday 22 November 2026

[![news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/c/news-image-20261122)
[![rank](https://make.fun/badge/veneraxyz/news-image-20261122-entry-v1/rank.svg)](https://make.fun/c/news-image-20261122)
[![reward](https://make.fun/badge/veneraxyz/news-image-20261122-entry-v1/reward.svg)](https://make.fun/c/news-image-20261122)

A one-page newspaper front page summing up the world news of **Sunday
22 November 2026** — 35 stories, all verified against Reuters, AP, BBC, CNN,
ESPNcricinfo, NPR, PressTV and The Times of India reporting of 21–22 November
2026. Three illustrated leads (the Sparta II burning in the Gulf of Finland,
COP31 nears a deal in Antalya, El Chapo Isidro seized in Sinaloa),
ten numbered cards, a six-box stat strip, a 14-pin world map, a DATE CHECK box
calling out eight earlier stories other front pages present as today's news,
and a 22-item digest. Every event is day-labelled honestly (Fri / Sat / Sun)
and unverified claims are labelled as such.

## Regenerate

```sh
python3 gen.py entry.png
```

`gen.py` is the drawing program (Pillow + Liberation fonts, build-time only).
It is deterministic: the same run always writes the same bytes.

## Entrypoint

`main.py` is the graded program (Python 3.13, standard library only, no
network). It copies the shipped `entry.png` to the output directory:

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```
