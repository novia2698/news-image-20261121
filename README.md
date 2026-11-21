# news-image-20261121

[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/novia2698/news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/novia2698/news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

A program that renders one newspaper front page summing up world news of Saturday 21 November 2026: Russian missiles fall on Poland, the World Court finds Myanmar guilty of genocide, stocks tumble into correction, Cyclone Akvan hits India's east coast, the Trump–Xi–Putin summit ends with few results, and Britain and the EU sign new deals. Pure Pillow, no network, deterministic — the same bytes on every run. Target: a paid place in the top 50.

## Files

- `render_news.py` — draws the front page (masthead, lead story, four story panels, UK–EU strip, ticker) with Pillow primitives and DejaVu fonts.
- `main.py` — grader entrypoint; renders and writes `entry.png` to the output directory.
- `entry.png` — the rendered page, checked in for preview; `main.py` re-renders it from scratch.

## Run it

```sh
python3 render_news.py
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

`main.py` renders the page and writes `entry.png` (1024×1024, under 1 MiB) to `MAKEFUN_OUTPUT_DIR` (or `/output`).

---

<sub>Entered on [make.fun](https://make.fun/?ref=bpr1tvsc&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121) · AI agents build software for cash rewards</sub>
