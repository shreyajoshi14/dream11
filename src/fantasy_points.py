"""Parse Cricsheet JSON -> one row per (match, player) with Dream11-style fantasy points.

ASSUMPTION: the PDF links to the official point table but its contents are not in the
text, so standard Dream11 rules per format are encoded in RULES below. Edit RULES if the
official table differs; everything downstream recomputes automatically.
"""
import json
from collections import defaultdict
from pathlib import Path
import pandas as pd
from tqdm import tqdm

RULES = {
    "t20": dict(run=1, four=4, six=6, bonus={25: 4, 50: 8, 75: 12, 100: 16}, duck=-2, wkt=25, lbw_bowled=8,
                haul={3: 4, 4: 8, 5: 16}, maiden=12, dot=1, catch=8, catch3=4, stump=12, ro_direct=12, ro_indirect=6,
                playing=4, eco_min_overs=2, eco=[(5, 6), (6, 4), (7.0001, 2), (10, 0), (11.0001, -2), (12.0001, -4), (999, -6)],
                sr_min_balls=10, sr=[(60, -6), (70, -4), (100.0001, -2), (130, 0), (150.0001, 2), (170.0001, 4), (9999, 6)]),
    "odi": dict(run=1, four=1, six=2, bonus={50: 4, 100: 8}, duck=-3, wkt=25, lbw_bowled=8,
                haul={4: 4, 5: 8}, maiden=4, dot=0, catch=8, catch3=4, stump=12, ro_direct=12, ro_indirect=6,
                playing=4, eco_min_overs=5, eco=[(2.5, 6), (3.5, 4), (4.5, 2), (7.0001, 0), (8.0001, -2), (9.0001, -4), (999, -6)],
                sr_min_balls=20, sr=[(30, -6), (40, -4), (50.0001, -2), (100, 0), (120.0001, 2), (140.0001, 4), (9999, 6)]),
    "test": dict(run=1, four=1, six=2, bonus={50: 4, 100: 8}, duck=-4, wkt=16, lbw_bowled=8,
                 haul={4: 4, 5: 8}, maiden=0, dot=0, catch=8, catch3=4, stump=12, ro_direct=12, ro_indirect=6,
                 playing=4, eco_min_overs=999, eco=[], sr_min_balls=9999, sr=[]),
}
FMT = {"T20": "t20", "IT20": "t20", "ODI": "odi", "ODM": "odi", "Test": "test", "MDM": "test"}
BOWLER_WICKETS = {"bowled", "caught", "lbw", "caught and bowled", "stumped", "hit wicket"}


def _band(value, bands, default=0):
    for upper, pts in bands:
        if value < upper:
            return pts
    return default


def score(s, fmt):
    r = RULES[fmt]
    p = r["playing"] if s["played"] else 0
    p += s["runs"] * r["run"] + s["fours"] * r["four"] + s["sixes"] * r["six"]
    # bonus tiers are exclusive (highest reached applies)
    reached = [b for thr, b in r["bonus"].items() if s["runs"] >= thr]
    p += max(reached) if reached else 0
    if s["out"] and s["runs"] == 0 and s["balls"] > 0:
        p += r["duck"]
    if s["balls"] >= r["sr_min_balls"]:
        p += _band(s["runs"] / s["balls"] * 100, r["sr"])
    p += s["wkts"] * r["wkt"] + s["lbw_bowled"] * r["lbw_bowled"]
    reached = [b for thr, b in r["haul"].items() if s["wkts"] >= thr]
    p += max(reached) if reached else 0
    p += s["maidens"] * r["maiden"] + s["dots"] * r["dot"]
    if s["bowl_balls"] / 6 >= r["eco_min_overs"] and r["eco"]:
        p += _band(s["bowl_runs"] / (s["bowl_balls"] / 6), r["eco"])
    p += s["catches"] * r["catch"] + (r["catch3"] if s["catches"] >= 3 else 0)
    p += s["stumps"] * r["stump"] + s["ro_direct"] * r["ro_direct"] + s["ro_indirect"] * r["ro_indirect"]
    return p


def parse_match(path):
    d = json.load(open(path))
    info = d["info"]
    fmt = FMT.get(info.get("match_type"))
    if fmt is None or "dates" not in info or len(info.get("teams", [])) != 2:
        return []
    reg = info.get("registry", {}).get("people", {})
    teams = info["teams"]
    team_of = {}
    for t, plist in info["players"].items():
        for n in plist:
            team_of[n] = t
    S = defaultdict(lambda: defaultdict(float))
    order = defaultdict(dict)  # innings -> name -> bat position
    total_runs = defaultdict(float)
    for n in team_of:
        S[n]["played"] = 1
    for inn_no, inn in enumerate(d.get("innings", [])):
        if inn.get("super_over"):
            continue
        bat_team = inn.get("team")
        pos = 0
        for ov in inn.get("overs", []):
            bowl_runs_ov, legal, bowler_ov = 0, 0, None
            for dl in ov["deliveries"]:
                b, bw, ns = dl["batter"], dl["bowler"], dl["non_striker"]
                for who in (b, ns):
                    if who not in order[inn_no]:
                        pos += 1
                        order[inn_no][who] = pos
                ex = dl.get("extras", {})
                wide, nb = "wides" in ex, "noballs" in ex
                rb = dl["runs"]["batter"]
                total_runs[bat_team] += dl["runs"]["total"]
                if not wide:
                    S[b]["balls"] += 1
                S[b]["runs"] += rb
                if rb == 4 and not dl["runs"].get("non_boundary"):
                    S[b]["fours"] += 1
                if rb == 6 and not dl["runs"].get("non_boundary"):
                    S[b]["sixes"] += 1
                conceded = rb + ex.get("wides", 0) + ex.get("noballs", 0)
                S[bw]["bowl_runs"] += conceded
                bowl_runs_ov += conceded
                bowler_ov = bw
                if not (wide or nb):
                    S[bw]["bowl_balls"] += 1
                    legal += 1
                    if rb == 0 and dl["runs"]["total"] - ex.get("byes", 0) - ex.get("legbyes", 0) == 0:
                        S[bw]["dots"] += 1
                for w in dl.get("wickets", []):
                    po, kind = w["player_out"], w["kind"]
                    S[po]["out"] = 1
                    if kind in BOWLER_WICKETS:
                        S[bw]["wkts"] += 1
                        if kind in ("bowled", "lbw"):
                            S[bw]["lbw_bowled"] += 1
                    fl = [f["name"] for f in w.get("fielders", []) if f.get("name") in team_of]
                    if kind == "caught":
                        for f in fl[:1]:
                            S[f]["catches"] += 1
                    elif kind == "caught and bowled":
                        S[bw]["catches"] += 1
                    elif kind == "stumped":
                        for f in fl[:1]:
                            S[f]["stumps"] += 1
                    elif kind == "run out":
                        if len(fl) == 1:
                            S[fl[0]]["ro_direct"] += 1
                        else:
                            for f in fl:
                                S[f]["ro_indirect"] += 1
            if legal == 6 and bowl_runs_ov == 0 and bowler_ov:
                S[bowler_ov]["maidens"] += 1
    date = pd.Timestamp(info["dates"][0])
    mid = Path(path).stem
    venue, city = info.get("venue", "NA"), info.get("city", "NA")
    rows = []
    for n, t in team_of.items():
        s = S[n]
        opp = teams[1] if t == teams[0] else teams[0]
        bp = [order[i][n] for i in order if n in order[i]]
        rows.append(dict(match_id=mid, date=date, fmt=fmt, gender=info.get("gender", "male"), venue=venue, city=city,
                         team=t, opp=opp, player=n, pid=reg.get(n, n), runs=s["runs"], balls=s["balls"], wkts=s["wkts"],
                         bowl_balls=s["bowl_balls"], bowl_runs=s["bowl_runs"], stumps=s["stumps"], catches=s["catches"],
                         bat_pos=bp[0] if bp else 11, did_bat=int(s["balls"] > 0 or s["out"] > 0),
                         team_runs=total_runs[t], opp_runs=total_runs[opp],
                         fantasy_points=score(s, fmt)))
    return rows


def build_player_match_table(raw_dir, out_csv=None):
    rows = []
    for p in tqdm(sorted(Path(raw_dir).glob("*.json")), desc="parsing"):
        try:
            rows += parse_match(p)
        except Exception as e:  # malformed file: skip, never crash the pipeline
            print("skip", p.name, e)
    df = pd.DataFrame(rows)
    df = df.sort_values(["date", "match_id"]).reset_index(drop=True)
    if out_csv:
        df.to_csv(out_csv, index=False)
    return df
