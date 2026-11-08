# brasileirão-bump-chart

An animated **bump / bar-chart race** of the Campeonato Brasileiro Série A, rebuilt
round by round: each club's bar grows with its accumulated points and reorders to the
official classification after every round, with club crests, club-colour bars, games
played, round dates, Libertadores (G4) and relegation (Z4) lines, and a coaching layer
that shows every hiring and firing (the incoming coach's badge pulses when they take over).

The output is a single self-contained `dist/index.html` (all data and images embedded) —
open it in any browser, press **Play**, drag the slider, or tap a club to highlight it.

## Current data

- **Season:** 2026 · **Matches:** complete through **round 34** of 38
- **Standings:** computed from match results with Brazilian tiebreakers (points, wins,
  goal difference, goals for)
- **Coaches:** verified through round 23; rounds 24+ added from press reports with
  approximate change-rounds. A few incoming coaches / headshots are still pending —
  see `data/meta.json` and the update skill.

## How it's built

```
data/matches.csv            # one row per played match (round,home,home_goals,away_goals,away)
      │
      ▼  python scripts/compute_standings.py
data/standings.json         # position / points / games played per team, every round
      │
      ▼  python scripts/generate.py   (+ data/teams.json, data/coaches.json, data/meta.json, assets/)
dist/index.html             # self-contained interactive chart
```

Regenerate everything:

```bash
python3 scripts/compute_standings.py
python3 scripts/generate.py
```

### Optional: export an MP4

Requires Node with Playwright (Chromium) and `ffmpeg`:

```bash
node scripts/capture_video.mjs     # renders frames/ by screenshotting the HTML round by round
bash scripts/encode_video.sh       # frames/ -> dist/brasileirao-bump-chart.mp4
```

## Images / assets

`assets/crests/*.png` (club crests) and `assets/coaches/*.jpg` (coach headshots) are
third-party images included here for a **private** project. The generator treats them as
optional: a club with no crest file falls back to a colour **monogram** badge, and a coach
with no photo falls back to **initials**. To add or replace one, drop a file named after the
club/coach slug into the matching folder and re-run `generate.py`.

## Updating the data

A future agent (or you) can refresh results and coaches by following the skill at
`skills/update-brasileirao-data/SKILL.md`.

## Project layout

```
data/      matches.csv, teams.json, coaches.json, meta.json, standings.json (generated)
assets/    crests/, coaches/
scripts/   compute_standings.py, generate.py, capture_video.mjs, encode_video.sh
dist/      index.html (generated)
skills/update-brasileirao-data/SKILL.md
```
