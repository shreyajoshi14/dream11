"""Text + audio guidance. Uses Claude when ANTHROPIC_API_KEY is set, otherwise a deterministic template.
Audio uses gTTS (needs internet) and degrades silently if unavailable."""
import io, os


def template_story(team, t1, t2, venue):
    c, vc = team.iloc[0], team.iloc[1]
    s = [f"Here is your Dream11 team for {t1} versus {t2} at {venue}.",
         f"Captain {c.player}: {c.reason.split(';')[0]}.",
         f"Vice-captain {vc.player}: {vc.reason.split(';')[0]}."]
    low = team.sort_values("p_start").iloc[0]
    s.append(f"Watch out: {low.player} has the lowest chance of starting, at {low.p_start:.0%}.")
    s.append(f"Total expected points for this team: {team.exp_pts.sum():.0f}.")
    return " ".join(s)


def story(team, t1, t2, venue):
    base = template_story(team, t1, t2, venue)
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        return base
    try:
        import anthropic
        facts = team[["player", "team", "role", "captain", "p_start", "exp_pts", "reason"]].round(2).to_csv(index=False)
        msg = anthropic.Anthropic(api_key=key).messages.create(
            model=os.getenv("CLAUDE_MODEL", "claude-sonnet-5-5"), max_tokens=500,
            messages=[{"role": "user", "content":
                       f"You are a friendly cricket analyst. In under 120 words, narrate this Dream11 team for {t1} vs {t2} at {venue}. "
                       f"Use ONLY these model facts (reasons are SHAP contributions); do not invent stats:\n{facts}"}])
        return msg.content[0].text
    except Exception:
        return base


def audio_bytes(text):
    try:
        from gtts import gTTS
        buf = io.BytesIO(); gTTS(text).write_to_fp(buf); return buf.getvalue()
    except Exception:
        return None
