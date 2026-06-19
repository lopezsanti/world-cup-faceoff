"""
ml_model.py

Builds a leakage-free training set from historical international results,
trains a match-outcome classifier (XGBoost, with a RandomForest fallback),
and exposes a WorldCupPredictor for generating head-to-head predictions.
"""

import time
from collections import deque

import numpy as np
import pandas as pd

from data_processor import (
    load_raw_data,
    calculate_elo,
    build_feature_vector,
    recent_form,
    head_to_head,
    get_top_scorers,
    save_model_cache,
    load_model_cache,
    resolve_team_name,
    display_team_name,
    STARTING_ELO,
    CONTINENTAL_CHAMPIONSHIPS,
)

try:
    from data_processor import _k_factor as _elo_k_factor
except ImportError:
    def _elo_k_factor(tournament):
        if not isinstance(tournament, str):
            return 20
        name = tournament.strip().lower()
        if name == "fifa world cup":
            return 60
        if "world cup qualification" in name:
            return 40
        for champ in CONTINENTAL_CHAMPIONSHIPS:
            if champ in name:
                return 50
        if "friendly" in name:
            return 20
        return 20

from sklearn.base import clone
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score

try:
    from xgboost import XGBClassifier
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False


TRAINING_CUTOFF_DATE = pd.Timestamp("1990-01-01")
FORM_WINDOW = 10


# ---------------------------------------------------------------------------
# Sample weighting by tournament importance
# ---------------------------------------------------------------------------

def _sample_weight_for_tournament(tournament):
    """World Cup=3, continental championships=2, qualifiers=1.5, friendlies/other=0.5."""
    if not isinstance(tournament, str):
        return 0.5

    name = tournament.strip().lower()

    if name == "fifa world cup":
        return 3.0
    for champ in CONTINENTAL_CHAMPIONSHIPS:
        if champ in name:
            return 2.0
    if "qualification" in name:
        return 1.5
    return 0.5


# ---------------------------------------------------------------------------
# Leakage-free training dataset construction
# ---------------------------------------------------------------------------

def _form_stats_from_deque(team_deque):
    """Replicate data_processor.recent_form's point/goal/recency math from a rolling deque."""
    num = len(team_deque)
    if num == 0:
        return 0, 0.0, 0, 0

    weights = [1.0 - 0.1 * i for i in range(num)]
    weights.reverse()  # oldest -> smallest weight, most recent -> 1.0

    points = sum(p for p, _, _ in team_deque)
    goals_scored = sum(gs for _, gs, _ in team_deque)
    goals_conceded = sum(gc for _, _, gc in team_deque)
    recency_weighted_points = sum(p * w for (p, _, _), w in zip(team_deque, weights))

    return points, round(recency_weighted_points, 3), goals_scored, goals_conceded


def _h2h_perspective(h2h_state, key, home, away):
    """Translate the canonical (alphabetically-ordered) h2h tally into home/away perspective."""
    if key[0] == home:
        home_wins = h2h_state["x_wins"]
        away_wins = h2h_state["y_wins"]
        goal_diff = h2h_state["x_goals"] - h2h_state["y_goals"]
    else:
        home_wins = h2h_state["y_wins"]
        away_wins = h2h_state["x_wins"]
        goal_diff = h2h_state["y_goals"] - h2h_state["x_goals"]
    return home_wins, h2h_state["draws"], away_wins, goal_diff


def build_training_dataset(results_df, elo_ratings):
    """
    Build a leakage-free training set by replaying all matches chronologically.

    For each match (filtered to 1990 onwards for the actual training rows),
    features are computed using ONLY data strictly before that match's date:
    rolling ELO, rolling last-10-match form, and rolling head-to-head tallies.

    Note: the `elo_ratings` argument (final, present-day ratings) is accepted
    for API consistency but intentionally NOT used as a starting point here —
    seeding historical matches with final ratings would leak future
    information backwards in time. Ratings are recomputed from scratch
    (starting at 1500) while replaying matches chronologically.

    Returns: (X, y, sample_weights, meta_df)
        X: np.ndarray of shape (n_samples, 15)
        y: np.ndarray of shape (n_samples,) with 0=home win, 1=draw, 2=away win
        sample_weights: np.ndarray of shape (n_samples,)
        meta_df: DataFrame with 'date' and 'tournament' columns aligned to X/y,
                 useful for diagnostics such as World-Cup-only evaluation.
    """
    print("[ml_model] Building leakage-free training dataset ...")

    empty = (
        np.zeros((0, 15)),
        np.zeros((0,)),
        np.zeros((0,)),
        pd.DataFrame(columns=["date", "tournament"]),
    )

    if results_df is None or results_df.empty:
        print("[ml_model] WARNING: empty results dataframe; cannot build training set")
        return empty

    required_cols = {"home_team", "away_team", "home_score", "away_score", "date"}
    if not required_cols.issubset(set(results_df.columns)):
        print(f"[ml_model] ERROR: results dataframe missing required columns: {required_cols}")
        return empty

    df = results_df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date", "home_team", "away_team", "home_score", "away_score"])
    df = df.sort_values("date").reset_index(drop=True)

    elo = {}
    form_windows = {}  # team -> deque[(points, goals_scored, goals_conceded)]
    h2h_state_map = {}  # (team_x, team_y) sorted -> {x_wins, y_wins, draws, x_goals, y_goals}

    X_rows, y_rows, weight_rows = [], [], []
    meta_dates, meta_tournaments = [], []

    for _, row in df.iterrows():
        try:
            home = row["home_team"]
            away = row["away_team"]
            home_score = row["home_score"]
            away_score = row["away_score"]
            tournament = row.get("tournament", "")
            match_date = row["date"]

            elo.setdefault(home, STARTING_ELO)
            elo.setdefault(away, STARTING_ELO)
            form_windows.setdefault(home, deque(maxlen=FORM_WINDOW))
            form_windows.setdefault(away, deque(maxlen=FORM_WINDOW))

            key = tuple(sorted((home, away)))
            h2h_state = h2h_state_map.setdefault(
                key, {"x_wins": 0, "y_wins": 0, "draws": 0, "x_goals": 0, "y_goals": 0}
            )

            # ---- snapshot state BEFORE this match (no leakage) ----
            elo_home_before = elo[home]
            elo_away_before = elo[away]

            home_points, home_recency, home_gs, home_gc = _form_stats_from_deque(form_windows[home])
            away_points, away_recency, away_gs, away_gc = _form_stats_from_deque(form_windows[away])

            h2h_home_wins, h2h_draws, h2h_away_wins, h2h_goal_diff = _h2h_perspective(
                h2h_state, key, home, away
            )

            if match_date >= TRAINING_CUTOFF_DATE:
                feature_row = [
                    elo_home_before,
                    elo_away_before,
                    elo_home_before - elo_away_before,
                    home_points,
                    home_recency,
                    home_gs,
                    home_gc,
                    away_points,
                    away_recency,
                    away_gs,
                    away_gc,
                    h2h_home_wins,
                    h2h_draws,
                    h2h_away_wins,
                    h2h_goal_diff,
                ]

                if home_score > away_score:
                    label = 0
                elif home_score == away_score:
                    label = 1
                else:
                    label = 2

                X_rows.append(feature_row)
                y_rows.append(label)
                weight_rows.append(_sample_weight_for_tournament(tournament))
                meta_dates.append(match_date)
                meta_tournaments.append(tournament)

            # ---- update rolling state AFTER using it (for future matches) ----
            expected_home = 1 / (1 + 10 ** ((elo_away_before - elo_home_before) / 400))
            expected_away = 1 - expected_home

            if home_score > away_score:
                actual_home, actual_away = 1.0, 0.0
                home_match_points, away_match_points = 3, 0
            elif home_score < away_score:
                actual_home, actual_away = 0.0, 1.0
                home_match_points, away_match_points = 0, 3
            else:
                actual_home, actual_away = 0.5, 0.5
                home_match_points, away_match_points = 1, 1

            k = _elo_k_factor(tournament)
            elo[home] = elo_home_before + k * (actual_home - expected_home)
            elo[away] = elo_away_before + k * (actual_away - expected_away)

            form_windows[home].append((home_match_points, home_score, away_score))
            form_windows[away].append((away_match_points, away_score, home_score))

            if key[0] == home:
                h2h_state["x_goals"] += home_score
                h2h_state["y_goals"] += away_score
            else:
                h2h_state["y_goals"] += home_score
                h2h_state["x_goals"] += away_score

            if home_score > away_score:
                winner = home
            elif away_score > home_score:
                winner = away
            else:
                winner = None

            if winner is None:
                h2h_state["draws"] += 1
            elif winner == key[0]:
                h2h_state["x_wins"] += 1
            else:
                h2h_state["y_wins"] += 1

        except Exception as exc:
            print(f"[ml_model] WARNING: skipping malformed row during training set build: {exc}")
            continue

    X = np.array(X_rows, dtype=float) if X_rows else np.zeros((0, 15))
    y = np.array(y_rows, dtype=int) if y_rows else np.zeros((0,), dtype=int)
    sample_weights = np.array(weight_rows, dtype=float) if weight_rows else np.zeros((0,))
    meta_df = pd.DataFrame({"date": meta_dates, "tournament": meta_tournaments})

    print(f"[ml_model] Training dataset built: {len(X)} matches (1990 onwards)")
    return X, y, sample_weights, meta_df


# ---------------------------------------------------------------------------
# Predictor
# ---------------------------------------------------------------------------

class WorldCupPredictor:
    """Trains a match-outcome model and serves head-to-head predictions."""

    CLASS_LABELS = {0: "team_a", 1: "draw", 2: "team_b"}

    def __init__(self):
        init_start = time.time()
        print("[ml_model] Initializing WorldCupPredictor ...")

        self.results_df, self.goalscorers_df, self.shootouts_df = load_raw_data()

        self.model = None
        self.calibrated_model = None
        self.elo_ratings = {}
        self.cache_used = False
        self.X_train = np.zeros((0, 15))
        self.y_train = np.zeros((0,), dtype=int)
        self.sample_weights = np.zeros((0,))
        self.meta_df = pd.DataFrame(columns=["date", "tournament"])

        cached_payload = load_model_cache()
        if cached_payload:
            try:
                self.model = cached_payload["model"]
                self.calibrated_model = cached_payload.get("calibrated_model")
                self.elo_ratings = cached_payload["elo_ratings"]
                self.cache_used = True
                print("[ml_model] Restored trained model and ELO ratings from model_cache.pkl")
            except (KeyError, TypeError) as exc:
                print(f"[ml_model] WARNING: model cache payload malformed ({exc}); retraining")
                self.model = None
                self.calibrated_model = None
                self.elo_ratings = {}
                self.cache_used = False

        if not self.cache_used:
            self.elo_ratings = calculate_elo(self.results_df)

            X, y, sample_weights, meta_df = build_training_dataset(self.results_df, self.elo_ratings)
            self.X_train, self.y_train, self.sample_weights, self.meta_df = X, y, sample_weights, meta_df

            self.model = self._build_base_estimator()

            if len(X) == 0:
                print("[ml_model] WARNING: no training data available; predictor will use default outputs")
            else:
                try:
                    self.model.fit(X, y, sample_weight=sample_weights)
                    train_accuracy = self.model.score(X, y)
                    print(f"[ml_model] Training accuracy: {train_accuracy * 100:.2f}%")
                except Exception as exc:
                    print(f"[ml_model] ERROR: model training failed: {exc}")

                self._fit_calibrated_model(X, y, sample_weights)
                self._evaluate_world_cup_cv(meta_df, X, y)

                save_model_cache({
                    "model": self.model,
                    "calibrated_model": self.calibrated_model,
                    "elo_ratings": self.elo_ratings,
                })

        self.training_time_seconds = round(time.time() - init_start, 2)
        print(
            f"[ml_model] Predictor ready in {self.training_time_seconds}s "
            f"(cache_used={self.cache_used})"
        )

    # -- model construction -------------------------------------------------

    def _build_base_estimator(self):
        if XGBOOST_AVAILABLE:
            try:
                return XGBClassifier(
                    n_estimators=200,
                    max_depth=5,
                    learning_rate=0.05,
                    use_label_encoder=False,
                    eval_metric="mlogloss",
                )
            except TypeError:
                # Newer xgboost releases removed use_label_encoder entirely.
                print("[ml_model] use_label_encoder unsupported by installed xgboost; retrying without it")
                try:
                    return XGBClassifier(
                        n_estimators=200,
                        max_depth=5,
                        learning_rate=0.05,
                        eval_metric="mlogloss",
                    )
                except Exception as exc:
                    print(f"[ml_model] ERROR constructing XGBClassifier: {exc}; falling back to RandomForest")

        print("[ml_model] xgboost unavailable; falling back to RandomForestClassifier")
        return RandomForestClassifier(n_estimators=200, max_depth=5, random_state=42)

    def _fit_calibrated_model(self, X, y, sample_weights):
        try:
            base = clone(self.model)
            n_classes = len(np.unique(y))
            cv_folds = 3 if len(X) >= 3 * n_classes else max(2, n_classes)

            try:
                self.calibrated_model = CalibratedClassifierCV(
                    estimator=base, method="sigmoid", cv=cv_folds
                )
            except TypeError:
                # Older scikit-learn uses base_estimator instead of estimator.
                self.calibrated_model = CalibratedClassifierCV(
                    base_estimator=base, method="sigmoid", cv=cv_folds
                )

            self.calibrated_model.fit(X, y, sample_weight=sample_weights)
            print("[ml_model] Calibrated probability model trained successfully")
        except Exception as exc:
            print(f"[ml_model] WARNING: calibration failed ({exc}); falling back to base model probabilities")
            self.calibrated_model = None

    def _evaluate_world_cup_cv(self, meta_df, X, y):
        try:
            if meta_df.empty:
                return
            wc_mask = meta_df["tournament"].astype(str).str.strip().str.lower() == "fifa world cup"
            X_wc, y_wc = X[wc_mask.values], y[wc_mask.values]

            if len(X_wc) < 10 or len(np.unique(y_wc)) < 2:
                print("[ml_model] Not enough World Cup matches for a meaningful cross-validation score")
                return

            cv_folds = min(5, len(np.unique(y_wc)) * 2, len(X_wc) // 5 or 1)
            cv_folds = max(cv_folds, 2)

            fresh_model = clone(self.model)
            scores = cross_val_score(fresh_model, X_wc, y_wc, cv=cv_folds, scoring="accuracy")
            print(
                f"[ml_model] World Cup-only cross-validation accuracy: "
                f"{scores.mean() * 100:.2f}% (+/- {scores.std() * 100:.2f}%) over {len(X_wc)} matches"
            )
        except Exception as exc:
            print(f"[ml_model] WARNING: World Cup cross-validation failed: {exc}")

    # -- prediction -----------------------------------------------------

    def _predict_proba(self, features):
        model = self.calibrated_model if self.calibrated_model is not None else self.model
        return model.predict_proba(features.reshape(1, -1))[0]

    @staticmethod
    def _confidence_label(max_prob_pct):
        if max_prob_pct >= 55:
            return "High"
        if max_prob_pct >= 40:
            return "Medium"
        return "Low"

    def _build_key_factors(self, team_a, team_b, elo_a, elo_b, form_a, form_b, h2h):
        factors = []

        elo_diff = elo_a - elo_b
        if abs(elo_diff) >= 50:
            leader, hi, lo = (team_a, elo_a, elo_b) if elo_diff > 0 else (team_b, elo_b, elo_a)
            factors.append(
                f"{leader} has a significantly higher ELO rating ({int(round(hi))} vs {int(round(lo))})"
            )
        else:
            factors.append(
                f"ELO ratings are closely matched between {team_a} and {team_b} "
                f"({int(round(elo_a))} vs {int(round(elo_b))})"
            )

        matches_a = form_a["wins"] + form_a["draws"] + form_a["losses"]
        matches_b = form_b["wins"] + form_b["draws"] + form_b["losses"]
        if form_a["wins"] > form_b["wins"]:
            factors.append(
                f"{team_a} has won {form_a['wins']} of the last {matches_a} matches with strong recent form"
            )
        elif form_b["wins"] > form_a["wins"]:
            factors.append(
                f"{team_b} has won {form_b['wins']} of the last {matches_b} matches with strong recent form"
            )
        elif form_a["recency_weighted_points"] != form_b["recency_weighted_points"]:
            better = team_a if form_a["recency_weighted_points"] > form_b["recency_weighted_points"] else team_b
            factors.append(f"{better} has the slight edge in recent form")
        else:
            factors.append(f"{team_a} and {team_b} have similar recent form")

        total = h2h["total_matches"]
        if total == 0:
            factors.append(f"No previous head-to-head meetings recorded between {team_a} and {team_b}")
        elif h2h["team_a_wins"] > h2h["team_b_wins"]:
            factors.append(
                f"Historical head-to-head favors {team_a} "
                f"({h2h['team_a_wins']}W {h2h['draws']}D {h2h['team_b_wins']}L)"
            )
        elif h2h["team_b_wins"] > h2h["team_a_wins"]:
            factors.append(
                f"Historical head-to-head favors {team_b} "
                f"({h2h['team_b_wins']}W {h2h['draws']}D {h2h['team_a_wins']}L)"
            )
        else:
            factors.append(f"Historical head-to-head is evenly matched ({total} meetings, {h2h['draws']} draws)")

        return factors

    def predict(self, team_a, team_b):
        """Predict the outcome of a match between team_a and team_b.

        team_a/team_b are display names (e.g. "USA"); internally they're
        resolved to whatever name the historical dataset uses (e.g.
        "United States") so ELO/form/head-to-head lookups hit real data
        instead of silently falling back to defaults.
        """
        try:
            internal_a = resolve_team_name(team_a)
            internal_b = resolve_team_name(team_b)

            elo_a = self.elo_ratings.get(internal_a, STARTING_ELO)
            elo_b = self.elo_ratings.get(internal_b, STARTING_ELO)

            form_a = recent_form(internal_a, self.results_df)
            form_b = recent_form(internal_b, self.results_df)
            h2h = head_to_head(internal_a, internal_b, self.results_df)

            if self.model is not None:
                features = build_feature_vector(internal_a, internal_b, self.results_df, self.elo_ratings)
                probs = self._predict_proba(features)
                team_a_prob, draw_prob, team_b_prob = probs[0], probs[1], probs[2]
            else:
                team_a_prob = draw_prob = team_b_prob = 1.0 / 3.0

            team_a_prob_pct = round(float(team_a_prob) * 100, 1)
            draw_prob_pct = round(float(draw_prob) * 100, 1)
            team_b_prob_pct = round(float(team_b_prob) * 100, 1)

            probs_pct = {"team_a": team_a_prob_pct, "draw": draw_prob_pct, "team_b": team_b_prob_pct}
            predicted_winner = max(probs_pct, key=probs_pct.get)
            confidence = self._confidence_label(probs_pct[predicted_winner])

            key_factors = self._build_key_factors(team_a, team_b, elo_a, elo_b, form_a, form_b, h2h)

            return {
                "team_a": team_a,
                "team_b": team_b,
                "team_a_win_prob": team_a_prob_pct,
                "draw_prob": draw_prob_pct,
                "team_b_win_prob": team_b_prob_pct,
                "predicted_winner": predicted_winner,
                "confidence": confidence,
                "team_a_elo": int(round(elo_a)),
                "team_b_elo": int(round(elo_b)),
                "team_a_form": form_a,
                "team_b_form": form_b,
                "head_to_head": h2h,
                "team_a_top_scorers": get_top_scorers(internal_a, self.goalscorers_df),
                "team_b_top_scorers": get_top_scorers(internal_b, self.goalscorers_df),
                "key_factors": key_factors,
            }

        except Exception as exc:
            print(f"[ml_model] ERROR: predict failed for {team_a} vs {team_b}: {exc}")
            return {
                "team_a": team_a,
                "team_b": team_b,
                "team_a_win_prob": 33.3,
                "draw_prob": 33.3,
                "team_b_win_prob": 33.4,
                "predicted_winner": "draw",
                "confidence": "Low",
                "team_a_elo": int(self.elo_ratings.get(resolve_team_name(team_a), STARTING_ELO)),
                "team_b_elo": int(self.elo_ratings.get(resolve_team_name(team_b), STARTING_ELO)),
                "team_a_form": {},
                "team_b_form": {},
                "head_to_head": {},
                "team_a_top_scorers": [],
                "team_b_top_scorers": [],
                "key_factors": ["Prediction unavailable due to an internal error"],
            }

    def get_all_teams(self, min_matches=20):
        """Return a sorted list of teams that have played at least min_matches matches."""
        try:
            if self.results_df is None or self.results_df.empty:
                return []

            appearances = pd.concat(
                [self.results_df["home_team"], self.results_df["away_team"]]
            ).value_counts()

            eligible = appearances[appearances >= min_matches].index.tolist()
            eligible = {display_team_name(team) for team in eligible}
            return sorted(eligible)

        except Exception as exc:
            print(f"[ml_model] WARNING: get_all_teams failed: {exc}")
            return []


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

predictor = None


def get_predictor():
    """Lazily initialize and return the shared WorldCupPredictor instance."""
    global predictor
    if predictor is None:
        try:
            predictor = WorldCupPredictor()
        except Exception as exc:
            print(f"[ml_model] FATAL: failed to initialize WorldCupPredictor: {exc}")
            raise
    return predictor
