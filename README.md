# brasileirão-bump-chart

*[English version](README-eng.md)*

Uma **corrida de barras animada** (bump / bar-chart race) do Campeonato Brasileiro Série A,
reconstruída rodada a rodada: a barra de cada clube cresce conforme os pontos acumulados e se
reordena pela classificação oficial após cada rodada, com escudos dos clubes, barras nas cores
do clube, jogos disputados, datas das rodadas, linhas da Libertadores (G4) e do rebaixamento (Z4),
e uma camada de técnicos que mostra cada contratação e demissão (o avatar do técnico que chega
pulsa quando ele assume).

O resultado é um único `dist/index.html` autossuficiente (todos os dados e imagens embutidos) —
abra em qualquer navegador, clique em **Play**, arraste o controle deslizante ou toque num clube
para destacá-lo.

## Dados atuais

- **Temporada:** 2026 · **Jogos:** completos até a **rodada 34** de 38
- **Classificação:** calculada a partir dos resultados com os critérios de desempate brasileiros
  (pontos, vitórias, saldo de gols, gols pró)
- **Técnicos:** verificados até a rodada 23; rodadas 24+ adicionadas a partir de notícias da
  imprensa, com rodadas de troca aproximadas. Veja `data/meta.json` e a skill de atualização.

## Como é construído

```
data/matches.csv            # uma linha por jogo disputado (round,home,home_goals,away_goals,away)
      │
      ▼  python scripts/compute_standings.py
data/standings.json         # posição / pontos / jogos por time, em cada rodada
      │
      ▼  python scripts/generate.py   (+ data/teams.json, data/coaches.json, data/meta.json, assets/)
dist/index.html             # gráfico interativo autossuficiente
```

Regenerar tudo:

```bash
python3 scripts/compute_standings.py
python3 scripts/generate.py
```

### Opcional: exportar um MP4

Requer Node com Playwright (Chromium) e `ffmpeg`:

```bash
node scripts/capture_video.mjs     # gera frames/ tirando prints do HTML rodada a rodada
bash scripts/encode_video.sh       # frames/ -> dist/brasileirao-bump-chart.mp4
```

## Imagens / assets

`assets/crests/*.png` (escudos dos clubes) e `assets/coaches/*.jpg` (fotos dos técnicos) são
imagens de terceiros, incluídas aqui para um projeto **privado**. O gerador as trata como
opcionais: um clube sem arquivo de escudo cai para um selo com **monograma** colorido, e um técnico
sem foto cai para as **iniciais**. Para adicionar ou trocar uma, coloque um arquivo nomeado pelo
slug do clube/técnico na pasta correspondente e rode `generate.py` novamente.

## Atualizando os dados

Um agente futuro (ou você) pode atualizar resultados e técnicos seguindo a skill em
`skills/update-brasileirao-data/SKILL.md`.

## Estrutura do projeto

```
data/      matches.csv, teams.json, coaches.json, meta.json, standings.json (gerado)
assets/    crests/, coaches/
scripts/   compute_standings.py, generate.py, capture_video.mjs, encode_video.sh
dist/      index.html (gerado)
skills/update-brasileirao-data/SKILL.md
```
