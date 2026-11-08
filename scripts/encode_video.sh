#!/usr/bin/env bash
# Stitch frames/ (from capture_video.mjs) into dist/brasileirao-bump-chart.mp4
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p dist
ffmpeg -y -framerate 20 -i frames/f%04d.png \
  -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" \
  -c:v libx264 -pix_fmt yuv420p -crf 21 \
  dist/brasileirao-bump-chart.mp4
echo "Wrote dist/brasileirao-bump-chart.mp4"
