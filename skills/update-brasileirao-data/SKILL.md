---
name: update-brasileirao-data
description: Refresh the brasileirao-bump-chart repo with newer match results and coaching changes, then regenerate the self-contained chart. Use when bringing the season up to a later round, or correcting/adding coaches and their photos.
---

# Updating the Brasileirão bump-chart data

This repo turns factual football data into a self-contained animated chart. Everything is
driven by the files in `data/`; the images in `assets/` are optional. After any data change,
regenerate and sanity-check.

## 1. Add new match results

`data/matches.csv` has one row per **played** match:

```
round,home,home_goals,away_goals,away
34,Palmeiras,6,1,Remo
```

Append the newly played rounds. Use a round-by-round results source such as
`https://brasileiraoemrodadas.com.br/docs/serie_a_2026/` (fetch it and read the scores).
Use the exact team names already in the file (e.g. `Athletico-PR`, `Atlético-MG`, `São Paulo`).
Only add matches that have a final score. Do not edit past rows.

## 2. Update round dates

In `data/meta.json`, extend `round_dates` so there is one short date (e.g. `"02 nov"`) per
round present in `matches.csv`, and set `last_data_round` to the latest round.

## 3. Update coaches

`data/coaches.json` maps each club to an ordered list of stints:

```json
{ "name": "Fernando Seabra", "short": "Seabra", "from_round": 32, "photo": "assets/coaches/fernando_seabra.jpg" }
```

- `from_round` is the first round the coach was in charge. The first stint is usually `from_round: 1`.
- When a club hires a new coach, append a stint. The chart draws the old coach crossed-out and
  pulses the new one at `from_round`.
- `short` is the small label shown under the club name.
- `photo` points to `assets/coaches/<slug>.jpg`. The slug is the name lowercased, accents removed,
  non-alphanumerics to `_` (e.g. `Luiz Felipe Scolari` -> `luiz_felipe_scolari`). If the file is
  missing, the chart falls back to the coach's initials — that is fine.

Coach changes come from press reports (search e.g. "<club> novo técnico <year>"). Record the
club, outgoing coach, incoming coach, and the round the new coach started (map the announcement
date to a round via `round_dates`). Keep `coaches_current_through_round` and the `coaches_pending_*`
hints in `meta.json` accurate.

## 4. Add images (optional)

- Coach headshot: a roughly square, face-centred JPG at `assets/coaches/<slug>.jpg`.
- Club crest: a PNG at `assets/crests/<club-slug>.png` (club slug from the team name the same way).
These are third-party images; this repo is intended to be **private**.

## 5. Regenerate the chart

```bash
python3 scripts/compute_standings.py   # rebuilds data/standings.json; prints final top/bottom 4
python3 scripts/generate.py            # rebuilds dist/index.html (self-contained, all data + images embedded)
```

Verify: the printed final top-4/bottom-4 match the official current table; open `dist/index.html`,
press Play, confirm the leader and the round date at the final round look right, and that coach
badges pulse at the rounds you set.

## 6. Regenerate the MP4 (optional, git-ignored)

The video `dist/brasileirao-bump-chart.mp4` is listed in `.gitignore` and is **not** committed, so
rebuild it locally whenever the data changes. Always run step 5 first so the video reflects the new
data. Requirements: Node with Playwright + its Chromium, and `ffmpeg` on PATH.

```bash
# one-time setup if needed:
npm install playwright && npx playwright install chromium
# then, after step 5:
node scripts/capture_video.mjs     # screenshots dist/index.html round by round -> frames/
bash scripts/encode_video.sh       # frames/ -> dist/brasileirao-bump-chart.mp4 (20 fps, h264)
```

`capture_video.mjs` reads the round count from the page and drives it via `window.__setRound`, so it
automatically covers however many rounds are in the data. Tweak `PER` (frames per round) in that
script for a slower/faster video. Delete `frames/` when done (it is also git-ignored).

## 7. Keep the data clean

This repo must contain **no personal information** (no names/emails of the maintainer, no social
handles in code or watermarks). Only football facts, the generator, and the optional assets.
