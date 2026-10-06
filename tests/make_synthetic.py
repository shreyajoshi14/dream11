"""Writes fake Cricsheet-format JSON (8 teams, 2022-2024) so the pipeline can be smoke-tested offline."""
import json, random, sys
from pathlib import Path
import numpy as np

out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
rng = random.Random(1)
TEAMS = [f"Team {c}" for c in "ABCDEFGH"]
squads = {}
pid = 0
for t in TEAMS:
    sq = []
    for i in range(16):
        role = "WK" if i == 0 else ("BOWL" if i in (1, 2, 3, 4, 5) else ("AR" if i in (6, 7, 8) else "BAT"))
        sq.append(dict(name=f"{t[-1]}{i:02d} Player", id=f"id{pid:04d}", role=role, skill=rng.uniform(0.6, 1.4), reg=rng.random() < 0.8))
        pid += 1
    squads[t] = sq
VENUES = [("Ground %d" % i, "City %d" % i, rng.uniform(0.8, 1.3)) for i in range(5)]

def sim_innings(bat_xi, bowl_xi, bat_team, vf):
    bowlers = [p for p in bowl_xi if p["role"] in ("BOWL", "AR")][:5]
    order = bat_xi[:]; overs = []; s, ns, nxt, out = 0, 1, 2, False
    for ov in range(20):
        dels = []
        bw = bowlers[ov % len(bowlers)]
        for b in range(6):
            if out: break
            st = order[s]
            sk = st["skill"] * vf * (1.15 if st["role"] in ("BAT", "WK") else 0.8)
            r = rng.random(); d = {"batter": st["name"], "bowler": bw["name"], "non_striker": order[ns]["name"]}
            p_w = 0.045 / sk * bw["skill"]
            runs = 0
            if r < p_w:
                d["runs"] = {"batter": 0, "extras": 0, "total": 0}
                kind = rng.choice(["bowled", "caught", "lbw", "stumped", "run out"])
                fl = [{"name": rng.choice(bowl_xi)["name"]}]
                if kind == "stumped": fl = [{"name": next(p["name"] for p in bowl_xi if p["role"] == "WK") if any(p["role"] == "WK" for p in bowl_xi) else fl[0]["name"]}]
                d["wickets"] = [{"player_out": st["name"], "kind": kind, "fielders": fl if kind in ("caught", "stumped", "run out") else []}]
                if nxt > 10: out = True
                else: s = nxt; nxt += 1
            else:
                runs = rng.choices([0, 1, 2, 4, 6], weights=[35, 35, 8, 13 * sk, 6 * sk])[0]
                ex = {}
                if rng.random() < 0.04: ex = {"wides": 1}
                tot = runs + sum(ex.values())
                d["runs"] = {"batter": runs, "extras": sum(ex.values()), "total": tot}
                if ex: d["extras"] = ex
                if runs % 2 == 1: s, ns = ns, s
            dels.append(d)
        overs.append({"over": ov, "deliveries": dels})
        s, ns = ns, s
        if out: break
    return {"team": bat_team, "overs": overs}

m = 0
dates = np.arange(np.datetime64("2022-01-01"), np.datetime64("2024-12-20"), 3)
for day in dates:
    a, b = rng.sample(TEAMS, 2)
    xi = {}
    for t in (a, b):
        sq = squads[t]; pool = [p for p in sq if p["reg"]]; extra = [p for p in sq if not p["reg"]]
        pick = pool[:] if len(pool) <= 11 else rng.sample(pool, 11)
        while len(pick) < 11: pick.append(extra.pop())
        xi[t] = sorted(pick, key=lambda p: (p["role"] == "BOWL", -p["skill"]))
    v = rng.choice(VENUES)
    info = {"match_type": "T20", "dates": [str(day)], "teams": [a, b], "gender": "male", "venue": v[0], "city": v[1],
            "players": {t: [p["name"] for p in xi[t]] for t in (a, b)},
            "registry": {"people": {p["name"]: p["id"] for t in (a, b) for p in xi[t]}}}
    inn = [sim_innings(xi[a], xi[b], a, v[2]), sim_innings(xi[b], xi[a], b, v[2])]
    json.dump({"info": info, "innings": inn}, open(out / f"{1000 + m}.json", "w"))
    m += 1
print("wrote", m, "matches")
