#!/usr/bin/env python3
"""Compute round-by-round standings from data/matches.csv.

Reads data/matches.csv (round,home,home_goals,away_goals,away) and writes
data/standings.json: for each team, position/points/played after every round,
plus the final table. Brazilian tiebreakers: points, wins, goal difference,
goals for, then name.
"""
import csv, json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main():
    matches = []
    with open(os.path.join(ROOT, "data/matches.csv"), encoding="utf-8") as f:
        for r in csv.DictReader(f):
            matches.append((int(r["round"]), r["home"], int(r["home_goals"]),
                            int(r["away_goals"]), r["away"]))
    teams = sorted({m[1] for m in matches} | {m[4] for m in matches})
    max_round = max(m[0] for m in matches)
    st = {t: dict(P=0, W=0, D=0, L=0, GF=0, GA=0, Pts=0) for t in teams}
    rank, pts, played = ({t: [] for t in teams} for _ in range(3))

    def order():
        return sorted(teams, key=lambda t: (-st[t]["Pts"], -st[t]["W"],
                      -(st[t]["GF"] - st[t]["GA"]), -st[t]["GF"], t))

    for rd in range(1, max_round + 1):
        for (R, H, hg, ag, A) in matches:
            if R != rd:
                continue
            st[H]["P"] += 1; st[A]["P"] += 1
            st[H]["GF"] += hg; st[H]["GA"] += ag
            st[A]["GF"] += ag; st[A]["GA"] += hg
            if hg > ag:
                st[H]["W"] += 1; st[H]["Pts"] += 3; st[A]["L"] += 1
            elif hg < ag:
                st[A]["W"] += 1; st[A]["Pts"] += 3; st[H]["L"] += 1
            else:
                st[H]["D"] += 1; st[A]["D"] += 1; st[H]["Pts"] += 1; st[A]["Pts"] += 1
        for pos, t in enumerate(order(), 1):
            rank[t].append(pos); pts[t].append(st[t]["Pts"]); played[t].append(st[t]["P"])

    final = [{"pos": i + 1, "team": t, **st[t], "GD": st[t]["GF"] - st[t]["GA"]}
             for i, t in enumerate(order())]
    out = {"max_round": max_round, "teams": teams,
           "rank": rank, "points": pts, "played": played, "final_table": final}
    with open(os.path.join(ROOT, "data/standings.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"Computed standings through round {max_round}.")
    print("Final top 4:", [f'{r["team"]} {r["Pts"]}' for r in final[:4]])
    print("Final bottom 4:", [f'{r["team"]} {r["Pts"]}' for r in final[-4:]])

if __name__ == "__main__":
    main()
