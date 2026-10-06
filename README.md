# Dream11 Next-Gen Team Builder – Inter IIT Tech Meet 13.0

## Run
```bash
pip install -r requirements.txt
python -m src.build_all        # downloads Cricsheet, parses, trains ProductUI_Model (data <= 2024-06-30 ONLY)
streamlit run app.py           # Product UI + Model UI tabs
python -m src.model_ui --train-end 2024-06-30 --test-start 2024-07-01 --test-end 2024-09-22   # CLI Model UI
python -m tests.test_pipeline <dir_with_cricsheet_json>   # leakage + constraint + 10s tests
```
Optional: `ANTHROPIC_API_KEY` enables Claude-written narration (grounded only in model outputs); audio uses gTTS.

## Model (two stages)
1. **E[points | starts]** – LightGBM regressor on per-player-per-match fantasy points.
2. **P(starts | in squad)** – LightGBM classifier. Toss/XI are unknown at prediction time, so squad = players the team used in its last 10 matches.
3. **Expected points = P(starts) x E[points | starts]**, then an exact MILP picks the XI under the rules: 11 players, 1–8 per role, >=1 per team.

Features (all from strictly earlier matches): rolling/EWM form (3/5/10), career avg, per-format, per-venue and per-opponent averages, batting position, balls faced/bowled, share of matches bowling, venue scoring level, team & opposition batting/bowling form, recent-starts counts, days since last match, role.

## No-leakage guarantee
Features come from `merge_asof(..., allow_exact_matches=False)` on a global match-order index; `tests/test_pipeline.py` proves features are unchanged when later matches are deleted. `train_product_model` asserts `train_end <= 2024-06-30`.

## Explainability
LightGBM native SHAP (`pred_contrib`): global importance chart + per-player "top 3 drivers" sentence in the Product UI.

## Assumptions to review
- **Point system**: the PDF's point-system link wasn't readable, so standard Dream11 rules (T20/ODI/Test) are in `src/fantasy_points.py::RULES`. Edit if the official table differs.
- **Roles** are not in Cricsheet; inferred from history (stumpings -> WK; share of matches bowling + batting position -> BOWL/AR/BAT). New players default to BAT.
- **Model UI columns**: "Total Points Predicted" = actual points scored by the predicted XI (consistent with the sample row, 780-623=157); model-predicted sum is an extra column. Predicted players who did not play score 0.
- **Squad mode**: `proxy` (default, honest) vs `xi` (candidates = the 22 who played; upper bound).
- Statement typo: "2024-06-31" does not exist; cutoff used is 2024-06-30.
