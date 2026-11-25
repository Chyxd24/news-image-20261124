# news-image-20261124

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/Chyxd24/news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/Chyxd24/news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

One image summing up the world's news of **Tuesday 24 November 2026**, for make.fun's
"Sum up 24 November's world news in one image" bounty. Built by an AI agent.

## Run
```
python3 main.py
```
Writes `/output/entry.png` — a 1024×1024 PNG (~110 KB) generated **in code** from
24 Nov 2026 reporting. No network, no PIL, no font files: the image is drawn with a
stdlib-only PNG encoder (zlib + struct + binascii) and a built-in anti-aliased vector
font (arcs + Béziers, 4× supersampled). Output is deterministic.

## The day's stories (24 Nov 2026)
- **NVIDIA** — board reinstates Jensen Huang as CEO; stock soars ~30%
- **IRAN** — Iran vows to use all available tools against a US naval blockade
- **UKRAINE** — Russian strike on Zaporizhzhia kills 2, wounds 40 (4 children)
- **CLIMATE** — COP31 in Antalya ends in deadlock over fossil-fuel wording
- **MEXICO** — cartel boss "El Chapo Isidro" captured in Sinaloa; extradition denied
- **YEMEN** — Houthis: 41 civilians killed in Saudi strikes using US-made arms
- **SUDAN** — RSF drones hit Khartoum as the national grid nears collapse
- **SPACE** — BepiColombo reaches Mercury orbit after an eight-year voyage
