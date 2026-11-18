# THE WORLD TODAY — Wednesday 18 November 2026

A one-page newspaper front page summing up the world's news of
Wednesday 18 November 2026, built to match the reference broadsheet
exactly: the Gulf lead story beside the night missile-launch photo,
Odesa on the right, three stories in the middle (Shenzhen trilateral,
Meta's AI agent Muse, Germany's electricity tax cut), the "world at a
glance" map band with its three briefs (EU €45bn Ukraine loan, COP31
climate finance, Nvidia's $115.84bn Q3 revenue), and four stories
along the bottom (Voyager 1, COP31, Antarctic ice loss, Japan's
economy). Thirteen stories, six continents, one day.

[![news-image-20261118](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/wahyu779/news-image-20261118/rank.svg)](https://make.fun/bounty/news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/wahyu779/news-image-20261118/reward.svg)](https://make.fun/bounty/news-image-20261118)

## Files

- `page.html` — the front page, hand-written HTML + CSS; every story,
  headline, caption and label is in here
- `render.py` — prepares the photo panels (cropping, the globe cut-out,
  the world-map band) and renders `page.html` to `entry.png` with
  headless Chromium at exactly 1024x1024
- `main.ts` — entry program (copies `entry.png` to the output dir)
- `assets/` — the photographs, generated during the build session
- `entry.png` — the rendered front page, 1024x1024, under 1 MiB

## Build

```sh
python3 render.py   # writes entry.png (deterministic)
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

No network, no clock, no randomness: running `render.py` twice writes
byte-identical PNGs, and `main.ts` copies bytes unchanged, so the two
harness runs produce identical output.
