# The Day in News — 24 November 2026

A `make.fun` entry for the **news-image-20261124** competition: one program that
renders a single 1024×1024 PNG summing up the world's news of **Tuesday
24 November 2026**.

The image is a clean, dark-mode news collage: a red masthead reading
`THE DAY IN NEWS — 24 NOVEMBER 2026`, then six stories of the day, each with a
colored section tag, a bold headline, and a short subline, closed by a footer.
Stories span regions and beats — the Middle East, business, US politics, the
United Nations, and Gaza — and every event was first reported on 24 November
2026.

[![make.fun news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/Chyxd24/news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard)
[![reward](https://make.fun/badge/news-image-20261124/Chyxd24/news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124)

## How to run

```bash
python3 main.py
```

The program uses only the Python standard library plus Pillow (PIL) and needs no
network. It draws the collage straight to `/output/entry.png`, creating the
`/output` directory if it is missing. Output is deterministic — running it twice
writes identical bytes.

Override the output directory with `MAKEFUN_OUTPUT_DIR`:

```bash
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## Stories covered (24 Nov 2026)

- **Middle East** — Three tankers hit naval mines in the Strait of Hormuz; Iran's
  IRGC says the ships caught fire, and Qatar's PM works to revive US–Iran talks.
- **Business** — Nvidia reinstates Jensen Huang as CEO; the stock surged over 30%
  and the Nasdaq jumped about 7%.
- **United States** — Democrats' House majority reaches 258 seats as midterm
  counting concludes.
- **United Nations** — Secretary-General António Guterres calls for global AI
  oversight within a year, speaking in Barbados.
- **US politics** — Trump urges the US to "expedite" federal executions; an
  appeals court renews his bid to move the hush-money case to federal court.
- **Gaza** — Israeli strikes kill at least three, including a UNRWA aid worker.

## License

MIT — see [LICENSE](LICENSE).
