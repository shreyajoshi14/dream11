"""Two-stage model:
   stage 1  E[fantasy points | player starts]   (LightGBM regressor)
   stage 2  P(player starts | in squad proxy)   (LightGBM classifier)
   expected points = P(start) * E[points | start]    -> used for team selection.
"""
import joblib
import numpy as np
import pandas as pd
import lightgbm as lgb
from sklearn.metrics import roc_auc_score, mean_absolute_error
from . import features as F
from .config import SQUAD_WINDOW, PROC_DIR, ART_DIR, TRAIN_CUTOFF

BASE_COLS = ["match_id", "mord", "date", "fmt", "gender", "venue", "team", "opp", "pid"]


def _fit(model_cls, X, y, Xv, yv, params, rounds=3000):
    m = model_cls(n_estimators=rounds, **params)
    m.fit(X, y, eval_set=[(Xv, yv)], callbacks=[lgb.early_stopping(100, verbose=False)])
    best = m.best_iteration_ or rounds
    final = model_cls(n_estimators=best, **params)
    final.fit(pd.concat([X, Xv]), pd.concat([y, yv]))
    return final, best


def train_models(hist_tr, window=SQUAD_WINDOW, play_years=4, save_training_csv=None, verbose=True):
    log = print if verbose else (lambda *a, **k: None)
    states = F.build_states(hist_tr)
    idx = F.build_team_index(hist_tr)
    last = hist_tr["date"].max()
    val_start = last - pd.Timedelta(days=180)

    # ---- stage 1: points | played
    q = hist_tr[BASE_COLS + ["player", "fantasy_points"]].copy()
    q[["c3", "c5", "c10", "since"]] = F.appearance_for_rows(q, idx, window)
    pts_df = F.attach(q, states)
    X, y = F.to_X(pts_df), pts_df["fantasy_points"]
    is_val = pts_df["date"] >= val_start
    params = dict(learning_rate=0.03, num_leaves=63, min_child_samples=80, subsample=0.8, subsample_freq=1,
                  colsample_bytree=0.8, reg_lambda=5.0, verbose=-1, n_jobs=-1)
    pts_model, best = _fit(lgb.LGBMRegressor, X[~is_val], y[~is_val], X[is_val], y[is_val], params)
    val_pred = lgb.LGBMRegressor(n_estimators=best, **params).fit(X[~is_val], y[~is_val]).predict(X[is_val])
    pts_mae = mean_absolute_error(y[is_val], val_pred)
    base_mae = mean_absolute_error(y[is_val], np.full(is_val.sum(), y[~is_val].mean()))
    log(f"[points] best_iter={best}  val MAE={pts_mae:.2f}  (constant baseline {base_mae:.2f})")

    # ---- stage 2: P(start) over squad-proxy candidates
    tg = (hist_tr[hist_tr["date"] >= last - pd.DateOffset(years=play_years)]
          .drop_duplicates(["match_id", "team"])[["match_id", "mord", "date", "fmt", "gender", "venue", "team", "opp"]])
    cand = F.make_candidates(tg, idx, window)
    cand = cand.merge(hist_tr[["match_id", "team", "pid"]].assign(played=1), on=["match_id", "team", "pid"], how="left")
    cand["played"] = cand["played"].fillna(0).astype(int)
    play_df = F.attach(cand, states)
    Xp, yp = F.to_X(play_df), play_df["played"]
    pv = play_df["date"] >= val_start
    pparams = dict(params, num_leaves=31, min_child_samples=200)
    play_model, pbest = _fit(lgb.LGBMClassifier, Xp[~pv], yp[~pv], Xp[pv], yp[pv], pparams, rounds=1500)
    pv_pred = lgb.LGBMClassifier(n_estimators=pbest, **pparams).fit(Xp[~pv], yp[~pv]).predict_proba(Xp[pv])[:, 1]
    auc = roc_auc_score(yp[pv], pv_pred)
    log(f"[start-prob] best_iter={pbest}  val AUC={auc:.3f}  base rate={yp.mean():.2f}")

    # ---- explainability: global importance from SHAP (LightGBM native pred_contrib)
    samp = X[is_val].sample(min(20000, int(is_val.sum())), random_state=0)
    contrib = pts_model.booster_.predict(samp, pred_contrib=True)[:, :-1]
    imp = (pd.DataFrame({"feature": F.FEATURES, "label": [F.LABELS[f] for f in F.FEATURES],
                         "mean_abs_shap": np.abs(contrib).mean(0)})
           .sort_values("mean_abs_shap", ascending=False).reset_index(drop=True))

    # ---- team info for the UI
    recent = hist_tr[hist_tr["date"] >= last - pd.DateOffset(years=2)]
    team_info = {}
    for t, g in recent.groupby("team"):
        team_info[t] = dict(venues=g["venue"].value_counts().index.tolist()[:10],
                            fmt=g["fmt"].value_counts().index[0], gender=g["gender"].value_counts().index[0],
                            last_match=str(g["date"].max().date()))
    names = hist_tr.sort_values("mord").drop_duplicates("pid", keep="last").set_index("pid")["player"].to_dict()

    if save_training_csv is not None:
        keep = ["match_id", "date", "pid", "player", "team", "opp", "venue"] + F.FEATURES + ["fantasy_points"]
        pts_df[keep].to_csv(save_training_csv, index=False)

    meta = dict(train_end=str(last.date()), train_start=str(hist_tr["date"].min().date()), n_rows=len(pts_df),
                points_val_mae=float(pts_mae), points_baseline_mae=float(base_mae), start_val_auc=float(auc),
                window=window, features=F.FEATURES)
    return dict(pts_model=pts_model, play_model=play_model, states=F.compress_states(states), idx=idx,
                names=names, team_info=team_info, importance=imp, max_mord=int(hist_tr["mord"].max()), meta=meta)


def train_product_model(hist, train_end=TRAIN_CUTOFF, out=None):
    """Product model. HARD RULE: no data after TRAIN_CUTOFF."""
    assert pd.Timestamp(train_end) <= pd.Timestamp(TRAIN_CUTOFF), f"train_end must be <= {TRAIN_CUTOFF}"
    hist_tr = hist[hist["date"] <= pd.Timestamp(train_end)]
    assert hist_tr["date"].max() <= pd.Timestamp(TRAIN_CUTOFF)
    bundle = train_models(hist_tr, save_training_csv=PROC_DIR / f"training_data_{train_end}.csv")
    out = out or ART_DIR / "ProductUI_Model.pkl"
    joblib.dump(bundle, out, compress=3)
    print("saved", out)
    return bundle
