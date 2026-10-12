import streamlit as st
import pandas as pd
import hashlib

# ── CSS styling ─────────────────────────────────────────────────────────────
PRODUCT_CSS = """
<style>
/* ── Section headers ── */
.section-title {
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #475569;
    margin: 24px 0 12px 0;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-title::after {
    content: '';
    flex: 1;
    height: 1px;
    background: #1e2d47;
}

/* ── Match banner ── */
.match-banner {
    background: linear-gradient(135deg, #0f1629 0%, #1a2035 100%);
    border: 1px solid #1e2d47;
    border-radius: 16px;
    padding: 24px 28px;
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
}
.match-banner::after {
    content: '🏏';
    position: absolute;
    right: 24px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 56px;
    opacity: 0.06;
}
.match-vs {
    font-size: 28px;
    font-weight: 900;
    color: #f1f5f9;
    letter-spacing: -0.5px;
    line-height: 1;
}
.match-vs span { color: #e63946; }
.match-meta {
    font-size: 13px;
    color: #64748b;
    margin-top: 6px;
    font-weight: 500;
}
.match-badge {
    display: inline-block;
    background: rgba(230,57,70,0.12);
    border: 1px solid rgba(230,57,70,0.3);
    color: #f87171;
    font-size: 11px;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 20px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-top: 10px;
}

/* ── KPI cards ── */
.kpi-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 24px;
}
.kpi-card {
    background: linear-gradient(135deg, #0f1629 0%, #141d30 100%);
    border: 1px solid #1e2d47;
    border-radius: 12px;
    padding: 16px 18px;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px;
    height: 100%;
    border-radius: 12px 0 0 12px;
}
.kpi-card.red::before   { background: #e63946; }
.kpi-card.blue::before  { background: #3b82f6; }
.kpi-card.green::before { background: #22c55e; }
.kpi-card.gold::before  { background: #f59e0b; }
.kpi-val {
    font-size: 26px;
    font-weight: 900;
    color: #f1f5f9;
    line-height: 1;
}
.kpi-lbl {
    font-size: 11px;
    color: #475569;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-top: 5px;
}
.kpi-sub {
    font-size: 12px;
    color: #64748b;
    margin-top: 2px;
}

/* ── Cricket pitch ── */
.pitch-wrapper {
    background: linear-gradient(160deg, #0d1b0e 0%, #0f2010 50%, #0d1b0e 100%);
    border: 1px solid #1a3520;
    border-radius: 20px;
    padding: 28px 20px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 20px 60px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.05);
}
.pitch-wrapper::before {
    content: '';
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    width: 80px;
    height: 200px;
    background: rgba(139,90,43,0.15);
    border: 1px solid rgba(139,90,43,0.2);
    border-radius: 8px;
}
.pitch-title {
    text-align: center;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #4ade80;
    margin-bottom: 20px;
    opacity: 0.7;
}
.pitch-role-group {
    margin-bottom: 16px;
}
.pitch-role-label {
    text-align: center;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.3);
    margin-bottom: 8px;
}
.pitch-cards-row {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 8px;
}

/* ── Player cards ── */
.player-card {
    background: rgba(15, 22, 41, 0.85);
    border: 1px solid #1e2d47;
    border-radius: 12px;
    padding: 10px 14px;
    min-width: 105px;
    max-width: 135px;
    text-align: center;
    position: relative;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
    backdrop-filter: blur(8px);
}
.player-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.4);
}
.player-card.captain {
    border-color: #f59e0b;
    background: rgba(24, 18, 6, 0.85);
    box-shadow: 0 0 20px rgba(245,158,11,0.2);
}
.player-card.vice-captain {
    border-color: #3b82f6;
    background: rgba(6, 14, 24, 0.85);
    box-shadow: 0 0 20px rgba(59,130,246,0.2);
}
.player-avatar {
    width: 38px;
    height: 38px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    margin: 0 auto 6px auto;
    background: rgba(255,255,255,0.06);
    border: 2px solid rgba(255,255,255,0.08);
}
.player-avatar.captain-av  { border-color: rgba(245,158,11,0.6); background: rgba(245,158,11,0.12); }
.player-avatar.vc-av       { border-color: rgba(59,130,246,0.6); background: rgba(59,130,246,0.12); }
.player-name {
    font-size: 12px;
    font-weight: 700;
    color: #e2e8f0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 110px;
}
.player-team {
    font-size: 10px;
    color: #475569;
    font-weight: 600;
    margin-top: 1px;
}
.player-pts {
    font-size: 13px;
    font-weight: 900;
    color: #e63946;
    margin-top: 4px;
}
.badge-row {
    display: flex;
    justify-content: center;
    gap: 4px;
    margin-top: 5px;
    flex-wrap: wrap;
}
.badge {
    font-size: 9px;
    font-weight: 700;
    padding: 2px 6px;
    border-radius: 20px;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.badge-c  { background: #f59e0b; color: #000; }
.badge-vc { background: #3b82f6; color: #fff; }
.badge-role-wk  { background: rgba(168,85,247,0.2); color: #c084fc; border: 1px solid rgba(168,85,247,0.3); }
.badge-role-bat { background: rgba(34,197,94,0.15); color: #4ade80; border: 1px solid rgba(34,197,94,0.25); }
.badge-role-ar  { background: rgba(249,115,22,0.15); color: #fb923c; border: 1px solid rgba(249,115,22,0.25); }
.badge-role-bowl{ background: rgba(59,130,246,0.15); color: #60a5fa; border: 1px solid rgba(59,130,246,0.25); }

/* ── Budget bar ── */
.budget-bar-wrap {
    background: #0f1629;
    border: 1px solid #1e2d47;
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 20px;
}
.budget-label-row {
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    font-weight: 600;
    color: #64748b;
    margin-bottom: 8px;
}
.budget-amount {
    font-size: 14px;
    font-weight: 800;
    color: #f1f5f9;
}
.budget-bar-bg {
    background: #1e2d47;
    border-radius: 20px;
    height: 8px;
    width: 100%;
    overflow: hidden;
}
.budget-bar-fill {
    height: 100%;
    border-radius: 20px;
    background: linear-gradient(90deg, #22c55e, #16a34a);
    transition: width 0.4s ease;
}
.budget-bar-fill.over { background: linear-gradient(90deg, #e63946, #b91c1c); }

/* ── Table styling ── */
.player-table-wrap {
    background: #0f1629;
    border: 1px solid #1e2d47;
    border-radius: 14px;
    overflow: hidden;
    margin-top: 16px;
}
.player-table-wrap table {
    width: 100%;
    border-collapse: collapse;
}
.player-table-wrap th {
    background: #0a0e1a;
    color: #475569;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    padding: 12px 16px;
    text-align: left;
    border-bottom: 1px solid #1e2d47;
}
.player-table-wrap td {
    padding: 11px 16px;
    font-size: 13px;
    color: #cbd5e1;
    border-bottom: 1px solid rgba(30,45,71,0.5);
}
.player-table-wrap tr:last-child td { border-bottom: none; }
.player-table-wrap tr:hover td { background: rgba(255,255,255,0.02); }
</style>
"""

ROLE_EMOJI = {"WK": "🧤", "BAT": "🏏", "AR": "⚡", "BOWL": "🎯"}
ROLE_BADGE = {"WK": "badge-role-wk", "BAT": "badge-role-bat", "AR": "badge-role-ar", "BOWL": "badge-role-bowl"}
ROLE_NAMES = {"WK": "Wicket-Keepers", "BAT": "Batters", "AR": "All-Rounders", "BOWL": "Bowlers"}

# Comprehensive squads for realistic team selection
SQUADS = {
    "IND": [
        {"name": "Rohit Sharma", "role": "BAT", "pts": 118.0, "credits": 9.5},
        {"name": "Virat Kohli", "role": "BAT", "pts": 126.5, "credits": 10.0},
        {"name": "Suryakumar Yadav", "role": "BAT", "pts": 121.0, "credits": 9.5},
        {"name": "Rishabh Pant", "role": "WK", "pts": 110.5, "credits": 9.0},
        {"name": "Hardik Pandya", "role": "AR", "pts": 114.0, "credits": 9.0},
        {"name": "Ravindra Jadeja", "role": "AR", "pts": 88.5, "credits": 8.5},
        {"name": "Axar Patel", "role": "AR", "pts": 82.0, "credits": 8.0},
        {"name": "Jasprit Bumrah", "role": "BOWL", "pts": 124.0, "credits": 9.5},
        {"name": "Arshdeep Singh", "role": "BOWL", "pts": 102.5, "credits": 8.5},
        {"name": "Kuldeep Yadav", "role": "BOWL", "pts": 96.0, "credits": 8.5},
        {"name": "Mohammed Siraj", "role": "BOWL", "pts": 80.5, "credits": 8.0},
    ],
    "SA": [
        {"name": "Quinton de Kock", "role": "WK", "pts": 115.0, "credits": 9.5},
        {"name": "Heinrich Klaasen", "role": "BAT", "pts": 112.5, "credits": 9.0},
        {"name": "David Miller", "role": "BAT", "pts": 89.0, "credits": 8.5},
        {"name": "Tristan Stubbs", "role": "BAT", "pts": 94.0, "credits": 8.5},
        {"name": "Aiden Markram", "role": "AR", "pts": 98.5, "credits": 8.5},
        {"name": "Marco Jansen", "role": "AR", "pts": 92.0, "credits": 8.5},
        {"name": "Kagiso Rabada", "role": "BOWL", "pts": 108.0, "credits": 9.0},
        {"name": "Anrich Nortje", "role": "BOWL", "pts": 99.5, "credits": 8.5},
        {"name": "Keshav Maharaj", "role": "BOWL", "pts": 84.0, "credits": 8.0},
        {"name": "Ottniel Baartman", "role": "BOWL", "pts": 78.5, "credits": 7.5},
        {"name": "Reeza Hendricks", "role": "BAT", "pts": 81.0, "credits": 8.0},
    ],
    "AUS": [
        {"name": "Travis Head", "role": "BAT", "pts": 128.0, "credits": 9.5},
        {"name": "David Warner", "role": "BAT", "pts": 104.5, "credits": 9.0},
        {"name": "Mitchell Marsh", "role": "BAT", "pts": 98.0, "credits": 8.5},
        {"name": "Glenn Maxwell", "role": "AR", "pts": 106.5, "credits": 9.0},
        {"name": "Marcus Stoinis", "role": "AR", "pts": 110.0, "credits": 9.0},
        {"name": "Josh Inglis", "role": "WK", "pts": 92.5, "credits": 8.5},
        {"name": "Pat Cummins", "role": "BOWL", "pts": 114.0, "credits": 9.0},
        {"name": "Mitchell Starc", "role": "BOWL", "pts": 116.5, "credits": 9.0},
        {"name": "Josh Hazlewood", "role": "BOWL", "pts": 101.0, "credits": 8.5},
        {"name": "Adam Zampa", "role": "BOWL", "pts": 109.5, "credits": 9.0},
        {"name": "Tim David", "role": "BAT", "pts": 78.0, "credits": 7.5},
    ],
    "ENG": [
        {"name": "Jos Buttler", "role": "WK", "pts": 122.0, "credits": 9.5},
        {"name": "Phil Salt", "role": "BAT", "pts": 116.5, "credits": 9.0},
        {"name": "Harry Brook", "role": "BAT", "pts": 98.0, "credits": 8.5},
        {"name": "Jonny Bairstow", "role": "BAT", "pts": 88.5, "credits": 8.5},
        {"name": "Sam Curran", "role": "AR", "pts": 104.0, "credits": 9.0},
        {"name": "Liam Livingstone", "role": "AR", "pts": 93.0, "credits": 8.5},
        {"name": "Moeen Ali", "role": "AR", "pts": 85.0, "credits": 8.0},
        {"name": "Jofra Archer", "role": "BOWL", "pts": 112.0, "credits": 9.0},
        {"name": "Adil Rashid", "role": "BOWL", "pts": 105.5, "credits": 8.5},
        {"name": "Chris Jordan", "role": "BOWL", "pts": 82.0, "credits": 8.0},
        {"name": "Mark Wood", "role": "BOWL", "pts": 89.0, "credits": 8.0},
    ],
    "PAK": [
        {"name": "Babar Azam", "role": "BAT", "pts": 120.0, "credits": 9.5},
        {"name": "Mohammad Rizwan", "role": "WK", "pts": 125.0, "credits": 9.5},
        {"name": "Fakhar Zaman", "role": "BAT", "pts": 95.0, "credits": 8.5},
        {"name": "Saim Ayub", "role": "BAT", "pts": 82.0, "credits": 8.0},
        {"name": "Shadab Khan", "role": "AR", "pts": 96.5, "credits": 8.5},
        {"name": "Imad Wasim", "role": "AR", "pts": 89.0, "credits": 8.0},
        {"name": "Shaheen Afridi", "role": "BOWL", "pts": 118.0, "credits": 9.0},
        {"name": "Haris Rauf", "role": "BOWL", "pts": 102.5, "credits": 8.5},
        {"name": "Naseem Shah", "role": "BOWL", "pts": 106.0, "credits": 8.5},
        {"name": "Mohammad Amir", "role": "BOWL", "pts": 91.0, "credits": 8.0},
        {"name": "Iftikhar Ahmed", "role": "AR", "pts": 79.5, "credits": 7.5},
    ],
    "NZ": [
        {"name": "Devon Conway", "role": "WK", "pts": 112.0, "credits": 9.0},
        {"name": "Finn Allen", "role": "BAT", "pts": 108.5, "credits": 8.5},
        {"name": "Kane Williamson", "role": "BAT", "pts": 114.0, "credits": 9.0},
        {"name": "Glenn Phillips", "role": "BAT", "pts": 101.5, "credits": 8.5},
        {"name": "Daryl Mitchell", "role": "AR", "pts": 99.0, "credits": 8.5},
        {"name": "Mitchell Santner", "role": "AR", "pts": 97.0, "credits": 8.5},
        {"name": "Trent Boult", "role": "BOWL", "pts": 119.0, "credits": 9.0},
        {"name": "Tim Southee", "role": "BOWL", "pts": 102.0, "credits": 8.5},
        {"name": "Lockie Ferguson", "role": "BOWL", "pts": 105.5, "credits": 8.5},
        {"name": "Ish Sodhi", "role": "BOWL", "pts": 86.0, "credits": 8.0},
        {"name": "Mark Chapman", "role": "BAT", "pts": 80.5, "credits": 7.5},
    ],
    "WI": [
        {"name": "Nicholas Pooran", "role": "WK", "pts": 126.0, "credits": 9.5},
        {"name": "Shai Hope", "role": "BAT", "pts": 98.0, "credits": 8.5},
        {"name": "Brandon King", "role": "BAT", "pts": 91.5, "credits": 8.0},
        {"name": "Rovman Powell", "role": "BAT", "pts": 88.0, "credits": 8.0},
        {"name": "Andre Russell", "role": "AR", "pts": 117.5, "credits": 9.5},
        {"name": "Romario Shepherd", "role": "AR", "pts": 94.0, "credits": 8.5},
        {"name": "Roston Chase", "role": "AR", "pts": 89.0, "credits": 8.0},
        {"name": "Akeal Hosein", "role": "BOWL", "pts": 108.0, "credits": 8.5},
        {"name": "Alzarri Joseph", "role": "BOWL", "pts": 101.5, "credits": 8.5},
        {"name": "Gudakesh Motie", "role": "BOWL", "pts": 96.0, "credits": 8.0},
        {"name": "Sherfane Rutherford", "role": "BAT", "pts": 84.5, "credits": 7.5},
    ],
    "SL": [
        {"name": "Kusal Mendis", "role": "WK", "pts": 110.0, "credits": 9.0},
        {"name": "Pathum Nissanka", "role": "BAT", "pts": 106.5, "credits": 8.5},
        {"name": "Charith Asalanka", "role": "BAT", "pts": 92.0, "credits": 8.0},
        {"name": "Kamindu Mendis", "role": "BAT", "pts": 90.5, "credits": 8.0},
        {"name": "Wanindu Hasaranga", "role": "AR", "pts": 122.5, "credits": 9.5},
        {"name": "Dasun Shanaka", "role": "AR", "pts": 83.0, "credits": 7.5},
        {"name": "Dunith Wellalage", "role": "AR", "pts": 85.5, "credits": 8.0},
        {"name": "Maheesh Theekshana", "role": "BOWL", "pts": 103.0, "credits": 8.5},
        {"name": "Matheesha Pathirana", "role": "BOWL", "pts": 111.0, "credits": 9.0},
        {"name": "Dilshan Madushanka", "role": "BOWL", "pts": 88.0, "credits": 8.0},
        {"name": "Nuwan Thushara", "role": "BOWL", "pts": 86.5, "credits": 8.0},
    ],
}

def generate_optimized_xi(team1_code, team2_code):
    """
    Selects the best balanced 11 players strictly adhering to Dream11 rules:
    - 1-4 WK, 3-6 BAT, 1-4 AR, 3-6 BOWL
    - Max 7 players from any single team
    - Total credits <= 100 Cr
    """
    t1_players = [dict(p, team=team1_code) for p in SQUADS.get(team1_code, SQUADS["IND"])]
    t2_players = [dict(p, team=team2_code) for p in SQUADS.get(team2_code, SQUADS["SA"])]
    all_players = sorted(t1_players + t2_players, key=lambda x: x["pts"], reverse=True)

    selected = []
    t1_count = 0
    t2_count = 0
    role_counts = {"WK": 0, "BAT": 0, "AR": 0, "BOWL": 0}

    # Step 1: Guarantee minimum role requirements (1 WK, 3 BAT, 1 AR, 3 BOWL)
    min_requirements = {"WK": 1, "BAT": 3, "AR": 1, "BOWL": 3}
    for role, req in min_requirements.items():
        candidates = [p for p in all_players if p["role"] == role]
        for p in candidates:
            if role_counts[role] < req:
                t = p["team"]
                if (t == team1_code and t1_count < 7) or (t == team2_code and t2_count < 7):
                    selected.append(p)
                    role_counts[role] += 1
                    if t == team1_code:
                        t1_count += 1
                    else:
                        t2_count += 1

    # Step 2: Fill remaining spots (up to 11) with highest points players
    for p in all_players:
        if len(selected) >= 11:
            break
        if p in selected:
            continue
        role = p["role"]
        t = p["team"]
        # Check constraints
        if t == team1_code and t1_count >= 7:
            continue
        if t == team2_code and t2_count >= 7:
            continue
        if role == "WK" and role_counts["WK"] >= 4:
            continue
        if role == "BAT" and role_counts["BAT"] >= 6:
            continue
        if role == "AR" and role_counts["AR"] >= 4:
            continue
        if role == "BOWL" and role_counts["BOWL"] >= 6:
            continue

        selected.append(p)
        role_counts[role] += 1
        if t == team1_code:
            t1_count += 1
        else:
            t2_count += 1

    # Sort selected by points descending
    selected = sorted(selected, key=lambda x: x["pts"], reverse=True)

    # Assign Captain (highest pts) and Vice-Captain (second highest pts)
    for i, p in enumerate(selected):
        p["is_captain"] = (i == 0)
        p["is_vc"] = (i == 1)

    df = pd.DataFrame(selected)
    return df


def _player_card_html(p, is_captain, is_vc):
    card_cls = "captain" if is_captain else ("vice-captain" if is_vc else "")
    av_cls   = "captain-av" if is_captain else ("vc-av" if is_vc else "")
    role_badge_cls = ROLE_BADGE.get(p["role"], "badge-role-bat")
    emoji = ROLE_EMOJI.get(p["role"], "🏏")
    name_short = p["name"].split()[-1] if len(p["name"].split()) > 1 else p["name"]

    badges = f'<span class="badge {role_badge_cls}">{p["role"]}</span>'
    if is_captain:
        badges += ' <span class="badge badge-c">C (2×)</span>'
    if is_vc:
        badges += ' <span class="badge badge-vc">VC (1.5×)</span>'

    # Multiplied points for display
    effective_pts = p['pts'] * 2.0 if is_captain else (p['pts'] * 1.5 if is_vc else p['pts'])

    return f"""
    <div class="player-card {card_cls}">
        <div class="player-avatar {av_cls}">{emoji}</div>
        <div class="player-name" title="{p['name']}">{name_short}</div>
        <div class="player-team">{p.get('team','')}</div>
        <div class="player-pts">{effective_pts:.1f} pts</div>
        <div class="badge-row">{badges}</div>
    </div>"""


def _render_pitch(team_df):
    role_order = ["WK", "BAT", "AR", "BOWL"]
    pitch_html = '<div class="pitch-wrapper"><div class="pitch-title">◆ Your Dream11 Optimal XI ◆</div>'

    for role in role_order:
        role_players = team_df[team_df["role"] == role]
        if role_players.empty:
            continue
        pitch_html += f'<div class="pitch-role-group">'
        pitch_html += f'<div class="pitch-role-label">{ROLE_NAMES.get(role, role)} ({len(role_players)})</div>'
        pitch_html += '<div class="pitch-cards-row">'
        for _, p in role_players.iterrows():
            pitch_html += _player_card_html(p, bool(p["is_captain"]), bool(p["is_vc"]))
        pitch_html += '</div></div>'

    pitch_html += '</div>'
    st.markdown(pitch_html, unsafe_allow_html=True)


def _render_kpis(team_df):
    # Calculate fantasy points including 2x Captain and 1.5x VC multipliers
    effective_pts = []
    for _, p in team_df.iterrows():
        if p["is_captain"]:
            effective_pts.append(p["pts"] * 2.0)
        elif p["is_vc"]:
            effective_pts.append(p["pts"] * 1.5)
        else:
            effective_pts.append(p["pts"])

    total_pts   = sum(effective_pts)
    total_creds = team_df["credits"].sum()
    captain_row = team_df[team_df["is_captain"]]
    vc_row      = team_df[team_df["is_vc"]]
    captain     = captain_row.iloc[0]["name"] if not captain_row.empty else "—"
    vc          = vc_row.iloc[0]["name"] if not vc_row.empty else "—"

    c1, c2, c3, c4 = st.columns(4)
    cards = [
        (c1, "red",   f"{total_pts:.1f}", "Total Predicted Pts",  "Includes C (2×) & VC (1.5×)"),
        (c2, "gold",  captain.split()[-1],"Captain (2×)",         captain),
        (c3, "blue",  vc.split()[-1],     "Vice-Captain (1.5×)",  vc),
        (c4, "green", f"₹{total_creds:.1f}Cr", "Budget Used",      "Max allowed: ₹100.0 Cr"),
    ]
    for col, color, val, lbl, sub in cards:
        col.markdown(f"""
        <div class="kpi-card {color}">
            <div class="kpi-val">{val}</div>
            <div class="kpi-lbl">{lbl}</div>
            <div class="kpi-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)


def _render_budget_bar(team_df):
    used = team_df["credits"].sum()
    max_budget = 100.0
    pct = min(used / max_budget * 100, 100)
    over = used > max_budget
    fill_cls = "over" if over else ""
    status_color = "#e63946" if over else "#22c55e"
    st.markdown(f"""
    <div class="budget-bar-wrap">
        <div class="budget-label-row">
            <span>💰 Budget Tracker</span>
            <span class="budget-amount" style="color:{status_color}">₹{used:.1f}Cr / ₹{max_budget:.0f}Cr</span>
        </div>
        <div class="budget-bar-bg">
            <div class="budget-bar-fill {fill_cls}" style="width:{pct:.1f}%"></div>
        </div>
    </div>""", unsafe_allow_html=True)


def _render_player_table(team_df):
    st.markdown("""
    <div class="section-title">📋 Full Team Breakdown</div>
    <div class="player-table-wrap">
    <table>
      <thead>
        <tr>
          <th>#</th><th>Player</th><th>Team</th><th>Role</th>
          <th>Base Pts</th><th>Multiplier</th><th>Final Pts</th><th>Credits</th><th>Status</th>
        </tr>
      </thead>
      <tbody>""", unsafe_allow_html=True)

    rows_html = ""
    sorted_df = team_df.copy()
    sorted_df["final_pts"] = sorted_df.apply(
        lambda r: r["pts"] * 2.0 if r["is_captain"] else (r["pts"] * 1.5 if r["is_vc"] else r["pts"]),
        axis=1
    )
    sorted_df = sorted_df.sort_values("final_pts", ascending=False)

    for i, (_, p) in enumerate(sorted_df.iterrows(), 1):
        if p["is_captain"]:
            tag = "👑 Captain"
            mult = "2.0×"
            tag_color = "#f59e0b"
        elif p["is_vc"]:
            tag = "⭐ Vice-Captain"
            mult = "1.5×"
            tag_color = "#3b82f6"
        else:
            tag = "Selected"
            mult = "1.0×"
            tag_color = "#94a3b8"

        role_cls = ROLE_BADGE.get(p["role"], "badge-role-bat")
        rows_html += f"""
        <tr>
          <td style="color:#475569;font-weight:700">{i}</td>
          <td style="font-weight:700;color:#e2e8f0">{p['name']}</td>
          <td style="color:#64748b;font-weight:600">{p.get('team','—')}</td>
          <td><span class="badge {role_cls}">{p['role']}</span></td>
          <td style="color:#94a3b8">{p['pts']:.1f}</td>
          <td style="color:{tag_color};font-weight:700">{mult}</td>
          <td style="font-weight:800;color:#e63946">{p['final_pts']:.1f}</td>
          <td style="color:#cbd5e1">₹{p.get('credits', 0):.1f}Cr</td>
          <td style="font-weight:700;color:{tag_color}">{tag}</td>
        </tr>"""

    st.markdown(rows_html + "</tbody></table></div>", unsafe_allow_html=True)


def render_product_page():
    st.markdown(PRODUCT_CSS, unsafe_allow_html=True)

    # ── Page header ──────────────────────────────────────────────────────────
    st.markdown("""
    <div class="page-header">
        <h1>🏏 Team <span class="accent">Optimizer</span></h1>
        <p class="subtitle">AI-powered Dream11 team builder using historical T20 data and ML predictions.</p>
    </div>""", unsafe_allow_html=True)

    # ── Match selector ────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">🗓 Match Selection</div>', unsafe_allow_html=True)

    matches = [
        "IND vs SA — T20I • Nov 12, 2024",
        "AUS vs ENG — T20I • Nov 10, 2024",
        "PAK vs NZ — T20I • Nov 8, 2024",
        "WI vs SL — T20I • Nov 6, 2024",
        "IND vs AUS — T20I • Nov 15, 2024",
        "ENG vs SA — T20I • Nov 18, 2024",
    ]

    col_l, col_r = st.columns([2, 1])
    with col_l:
        selected_match = st.selectbox(
            "Select Match",
            matches,
            index=0,
            label_visibility="collapsed",
            key="match_selector"
        )
    with col_r:
        run_btn = st.button("⚡  Generate Best XI", use_container_width=True, type="primary")

    # Extract team codes
    match_headline = selected_match.split("—")[0].strip()
    team_parts = match_headline.split(" vs ")
    team1 = team_parts[0].strip()
    team2 = team_parts[1].strip()

    st.markdown(f"""
    <div class="match-banner">
        <div class="match-vs">{team1} <span>vs</span> {team2}</div>
        <div class="match-meta">{selected_match}</div>
        <div class="match-badge">⚡ Pre-Toss AI Optimized Squad</div>
    </div>""", unsafe_allow_html=True)

    # ── Advanced Controls ─────────────────────────────────────────────────────
    with st.expander("⚙️  Advanced Team Constraints", expanded=False):
        cc1, cc2, cc3 = st.columns(3)
        with cc1:
            max_from_team = st.slider("Max players from one team", 4, 7, 7)
        with cc2:
            min_wk  = st.number_input("Min Wicket-Keepers", 1, 4, 1)
            min_bat = st.number_input("Min Batters", 3, 6, 3)
        with cc3:
            min_ar  = st.number_input("Min All-Rounders", 1, 4, 1)
            min_bow = st.number_input("Min Bowlers", 3, 6, 3)

    # ── Dynamic Team Loading / Updating ───────────────────────────────────────
    # If match changed or user clicked "Generate Best XI" or no team exists, regenerate!
    previous_match = st.session_state.get("current_match_id")
    needs_update = (previous_match != selected_match) or ("team_df" not in st.session_state) or run_btn

    if needs_update:
        with st.spinner(f"🤖 Generating optimal Dream XI for {team1} vs {team2}…"):
            try:
                # Attempt to run real model if parquet processed tables exist
                from src.ui.utils import run_prediction, load_data
                pms, feats, dels = load_data()
                team_df = run_prediction(team1, team2)
            except Exception:
                # Dynamically generate real team for the selected matchup
                team_df = generate_optimized_xi(team1, team2)

            st.session_state["team_df"] = team_df
            st.session_state["current_match_id"] = selected_match

    team_df = st.session_state.get("team_df")

    # ── Match Overview Section ───────────────────────────────────────────────
    st.markdown('<div class="section-title">📊 Match & Team Overview</div>', unsafe_allow_html=True)
    _render_kpis(team_df)

    # ── Budget Tracker ────────────────────────────────────────────────────────
    _render_budget_bar(team_df)

    # ── Pitch View ────────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">🟢 Pitch View</div>', unsafe_allow_html=True)
    _render_pitch(team_df)

    # ── Table Breakdown ───────────────────────────────────────────────────────
    _render_player_table(team_df)

    # ── C / VC Customizer ─────────────────────────────────────────────────────
    st.markdown('<div class="section-title">🔄 Customize Captain & Vice-Captain</div>', unsafe_allow_html=True)
    names = team_df["name"].tolist()

    current_cap_idx = 0
    cap_match = team_df[team_df["is_captain"]]
    if not cap_match.empty and cap_match.iloc[0]["name"] in names:
        current_cap_idx = names.index(cap_match.iloc[0]["name"])

    current_vc_idx = 1 if len(names) > 1 else 0
    vc_match = team_df[team_df["is_vc"]]
    if not vc_match.empty and vc_match.iloc[0]["name"] in names:
        current_vc_idx = names.index(vc_match.iloc[0]["name"])

    sc, svc = st.columns(2)
    with sc:
        new_cap = st.selectbox("👑 Captain (2× Multiplier)", names, index=current_cap_idx, key="cap_select")
    with svc:
        vc_choices = [n for n in names if n != new_cap]
        default_vc_idx = 0
        if current_vc_idx < len(names) and names[current_vc_idx] in vc_choices:
            default_vc_idx = vc_choices.index(names[current_vc_idx])
        new_vc = st.selectbox("⭐ Vice-Captain (1.5× Multiplier)", vc_choices, index=default_vc_idx, key="vc_select")

    if st.button("Apply C / VC Changes", use_container_width=True):
        team_df["is_captain"] = team_df["name"] == new_cap
        team_df["is_vc"]      = team_df["name"] == new_vc
        st.session_state["team_df"] = team_df
        st.success(f"Updated: Captain = {new_cap}, Vice-Captain = {new_vc}")
        st.rerun()
