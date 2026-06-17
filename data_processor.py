"""
data_processor.py

Handles data acquisition (with local caching), ELO rating calculation,
and feature engineering for the World Cup Face-Off prediction tool.
"""

import os
import time
import joblib
import numpy as np
import pandas as pd
import requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DATA_URLS = {
    "results": "https://raw.githubusercontent.com/lopezsanti/international_results/master/results.csv",
    "goalscorers": "https://raw.githubusercontent.com/lopezsanti/international_results/master/goalscorers.csv",
    "shootouts": "https://raw.githubusercontent.com/lopezsanti/international_results/master/shootouts.csv",
}

CACHE_FILES = {
    "results": "results_cache.csv",
    "goalscorers": "goalscorers_cache.csv",
    "shootouts": "shootouts_cache.csv",
}

CACHE_MAX_AGE_SECONDS = 24 * 60 * 60  # 24 hours

STARTING_ELO = 1500
REQUEST_TIMEOUT_SECONDS = 30

# Continental championship tournaments recognized for K-factor purposes.
CONTINENTAL_CHAMPIONSHIPS = [
    "copa america",
    "uefa euro",
    "african cup of nations",
    "afcon",
    "afc asian cup",
    "concacaf championship",
    "concacaf gold cup",
    "gold cup",
    "oceania nations cup",
    "uefa nations league",
]


# ---------------------------------------------------------------------------
# Data loading / caching
# ---------------------------------------------------------------------------

def _is_cache_fresh(cache_path):
    """Return True if cache_path exists and was modified within the last 24h."""
    if not os.path.exists(cache_path):
        return False
    age_seconds = time.time() - os.path.getmtime(cache_path)
    return age_seconds < CACHE_MAX_AGE_SECONDS


def _download_csv(url, cache_path, label):
    """Download a CSV from url, save it to cache_path, and return a DataFrame."""
    print(f"[data_processor] Downloading {label} from {url} ...")
    response = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()

    with open(cache_path, "wb") as f:
        f.write(response.content)

    print(f"[data_processor] Downloaded and cached {label} -> {cache_path}")
    return pd.read_csv(cache_path, encoding="utf-8")


def _load_dataset(key):
    """Load a single dataset, preferring a fresh local cache over re-downloading."""
    url = DATA_URLS[key]
    cache_path = CACHE_FILES[key]

    if _is_cache_fresh(cache_path):
        try:
            print(f"[data_processor] Loading {key} from fresh cache ({cache_path}) ...")
            return pd.read_csv(cache_path, encoding="utf-8")
        except Exception as exc:
            print(f"[data_processor] WARNING: failed to read cache {cache_path}: {exc}")

    try:
        return _download_csv(url, cache_path, key)
    except Exception as exc:
        print(f"[data_processor] WARNING: failed to download {key}: {exc}")
        if os.path.exists(cache_path):
            print(f"[data_processor] Falling back to stale cache for {key} ({cache_path})")
            try:
                return pd.read_csv(cache_path, encoding="utf-8")
            except Exception as inner_exc:
                print(f"[data_processor] ERROR: stale cache for {key} unreadable: {inner_exc}")
        print(f"[data_processor] ERROR: no usable data for {key}; returning empty DataFrame")
        return pd.DataFrame()


def load_raw_data():
    """Load results, goalscorers, and shootouts DataFrames (cache-aware)."""
    print("[data_processor] Loading raw data ...")
    results_df = _load_dataset("results")
    goalscorers_df = _load_dataset("goalscorers")
    shootouts_df = _load_dataset("shootouts")

    for df, name in (
        (results_df, "results"),
        (goalscorers_df, "goalscorers"),
        (shootouts_df, "shootouts"),
    ):
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")

    print(
        f"[data_processor] Loaded results={len(results_df)} rows, "
        f"goalscorers={len(goalscorers_df)} rows, shootouts={len(shootouts_df)} rows"
    )
    return results_df, goalscorers_df, shootouts_df


# ---------------------------------------------------------------------------
# Model cache (trained model + ELO ratings)
# ---------------------------------------------------------------------------

MODEL_CACHE_FILE = "model_cache.pkl"
MODEL_CACHE_MAX_AGE_SECONDS = 48 * 60 * 60  # 48 hours


def is_model_cache_fresh(cache_path=MODEL_CACHE_FILE):
    """Return True if the model cache file exists and was modified within the last 48h."""
    if not os.path.exists(cache_path):
        return False
    age_seconds = time.time() - os.path.getmtime(cache_path)
    return age_seconds < MODEL_CACHE_MAX_AGE_SECONDS


def save_model_cache(payload, cache_path=MODEL_CACHE_FILE):
    """Serialize trained-model artifacts (model, calibrated_model, elo_ratings) to disk."""
    try:
        joblib.dump(payload, cache_path)
        print(f"[data_processor] Saved model cache -> {cache_path}")
        return True
    except Exception as exc:
        print(f"[data_processor] WARNING: failed to save model cache: {exc}")
        return False


def load_model_cache(cache_path=MODEL_CACHE_FILE):
    """Load cached model artifacts from disk if the cache exists and is less than 48h old."""
    if not is_model_cache_fresh(cache_path):
        return None
    try:
        payload = joblib.load(cache_path)
        print(f"[data_processor] Loaded model cache from {cache_path}")
        return payload
    except Exception as exc:
        print(f"[data_processor] WARNING: failed to load model cache ({exc}); will retrain")
        return None


# ---------------------------------------------------------------------------
# ELO ratings
# ---------------------------------------------------------------------------

def _k_factor(tournament):
    """Determine the K-factor for a match based on its tournament name."""
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

    return 20  # default fallback for unclassified tournament types


def calculate_elo(results_df):
    """
    Compute ELO ratings for every team by processing all matches chronologically.

    Returns: {team_name: elo_score}
    """
    print("[data_processor] Calculating ELO ratings ...")

    if results_df is None or results_df.empty:
        print("[data_processor] WARNING: empty results dataframe; no ELO ratings computed")
        return {}

    required_cols = {"home_team", "away_team", "home_score", "away_score"}
    if not required_cols.issubset(set(results_df.columns)):
        print(f"[data_processor] ERROR: results dataframe missing required columns: {required_cols}")
        return {}

    df = results_df.copy()
    if "date" in df.columns:
        df = df.sort_values("date")

    elo = {}

    for _, row in df.iterrows():
        try:
            home_team = row["home_team"]
            away_team = row["away_team"]
            home_score = row["home_score"]
            away_score = row["away_score"]
            tournament = row.get("tournament", "")

            if pd.isna(home_team) or pd.isna(away_team):
                continue
            if pd.isna(home_score) or pd.isna(away_score):
                continue

            elo.setdefault(home_team, STARTING_ELO)
            elo.setdefault(away_team, STARTING_ELO)

            home_elo = elo[home_team]
            away_elo = elo[away_team]

            expected_home = 1 / (1 + 10 ** ((away_elo - home_elo) / 400))
            expected_away = 1 - expected_home

            if home_score > away_score:
                actual_home, actual_away = 1.0, 0.0
            elif home_score < away_score:
                actual_home, actual_away = 0.0, 1.0
            else:
                actual_home, actual_away = 0.5, 0.5

            k = _k_factor(tournament)

            elo[home_team] = home_elo + k * (actual_home - expected_home)
            elo[away_team] = away_elo + k * (actual_away - expected_away)

        except Exception as exc:
            print(f"[data_processor] WARNING: skipping malformed row during ELO calc: {exc}")
            continue

    print(f"[data_processor] ELO ratings computed for {len(elo)} teams")
    return elo


# ---------------------------------------------------------------------------
# Recent form
# ---------------------------------------------------------------------------

def recent_form(team, results_df, n=10):
    """
    Compute recent-form statistics for a team over its last n matches.

    Returns: {
        wins, draws, losses, goals_scored, goals_conceded,
        points, recency_weighted_points
    }
    """
    empty_result = {
        "wins": 0,
        "draws": 0,
        "losses": 0,
        "goals_scored": 0,
        "goals_conceded": 0,
        "points": 0,
        "recency_weighted_points": 0.0,
    }

    if results_df is None or results_df.empty:
        return empty_result

    try:
        team_matches = results_df[
            (results_df["home_team"] == team) | (results_df["away_team"] == team)
        ].copy()

        if "date" in team_matches.columns:
            team_matches = team_matches.sort_values("date")

        team_matches = team_matches.tail(n)

        if team_matches.empty:
            return empty_result

        wins = draws = losses = 0
        goals_scored = goals_conceded = 0
        match_points = []

        for _, row in team_matches.iterrows():
            is_home = row["home_team"] == team
            scored = row["home_score"] if is_home else row["away_score"]
            conceded = row["away_score"] if is_home else row["home_score"]

            if pd.isna(scored) or pd.isna(conceded):
                continue

            goals_scored += scored
            goals_conceded += conceded

            if scored > conceded:
                wins += 1
                match_points.append(3)
            elif scored == conceded:
                draws += 1
                match_points.append(1)
            else:
                losses += 1
                match_points.append(0)

        points = sum(match_points)

        # Most recent match weighted 1.0, next most recent 0.9, etc.
        num_matches = len(match_points)
        weights = [1.0 - 0.1 * i for i in range(num_matches)]
        weights.reverse()  # oldest match gets smallest weight, most recent gets 1.0
        recency_weighted_points = sum(p * w for p, w in zip(match_points, weights))

        return {
            "wins": wins,
            "draws": draws,
            "losses": losses,
            "goals_scored": int(goals_scored),
            "goals_conceded": int(goals_conceded),
            "points": int(points),
            "recency_weighted_points": round(recency_weighted_points, 3),
        }

    except Exception as exc:
        print(f"[data_processor] WARNING: recent_form failed for {team}: {exc}")
        return empty_result


# ---------------------------------------------------------------------------
# Head-to-head
# ---------------------------------------------------------------------------

def head_to_head(team_a, team_b, results_df):
    """
    Compute head-to-head statistics between two teams across all history.

    Returns: {
        team_a_wins, draws, team_b_wins, team_a_goals, team_b_goals,
        total_matches, last_5_results
    }
    """
    empty_result = {
        "team_a_wins": 0,
        "draws": 0,
        "team_b_wins": 0,
        "team_a_goals": 0,
        "team_b_goals": 0,
        "total_matches": 0,
        "last_5_results": [],
    }

    if results_df is None or results_df.empty:
        return empty_result

    try:
        matches = results_df[
            ((results_df["home_team"] == team_a) & (results_df["away_team"] == team_b))
            | ((results_df["home_team"] == team_b) & (results_df["away_team"] == team_a))
        ].copy()

        if "date" in matches.columns:
            matches = matches.sort_values("date")

        if matches.empty:
            return empty_result

        team_a_wins = draws = team_b_wins = 0
        team_a_goals = team_b_goals = 0
        results_chronological = []

        for _, row in matches.iterrows():
            a_is_home = row["home_team"] == team_a
            a_score = row["home_score"] if a_is_home else row["away_score"]
            b_score = row["away_score"] if a_is_home else row["home_score"]

            if pd.isna(a_score) or pd.isna(b_score):
                continue

            team_a_goals += a_score
            team_b_goals += b_score

            if a_score > b_score:
                team_a_wins += 1
                results_chronological.append("A Win")
            elif a_score < b_score:
                team_b_wins += 1
                results_chronological.append("B Win")
            else:
                draws += 1
                results_chronological.append("Draw")

        return {
            "team_a_wins": team_a_wins,
            "draws": draws,
            "team_b_wins": team_b_wins,
            "team_a_goals": int(team_a_goals),
            "team_b_goals": int(team_b_goals),
            "total_matches": len(results_chronological),
            "last_5_results": results_chronological[-5:],
        }

    except Exception as exc:
        print(f"[data_processor] WARNING: head_to_head failed for {team_a} vs {team_b}: {exc}")
        return empty_result


# ---------------------------------------------------------------------------
# Top scorers
# ---------------------------------------------------------------------------

def _is_own_goal(value):
    """Robustly interpret the own_goal column, which may be bool, str, or NaN."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in ("true", "1", "yes")
    return False


def get_top_scorers(team, goalscorers_df, top_n=5):
    """
    Return the top_n all-time goal scorers for a team, excluding own goals.

    Returns: [{"name": scorer_name, "goals": count}, ...]
    """
    if goalscorers_df is None or goalscorers_df.empty:
        return []

    required_cols = {"team", "scorer"}
    if not required_cols.issubset(set(goalscorers_df.columns)):
        print(f"[data_processor] ERROR: goalscorers dataframe missing required columns: {required_cols}")
        return []

    try:
        df = goalscorers_df[goalscorers_df["team"] == team].copy()

        if "own_goal" in df.columns:
            df = df[~df["own_goal"].apply(_is_own_goal)]

        df = df.dropna(subset=["scorer"])

        if df.empty:
            return []

        counts = df.groupby("scorer").size().sort_values(ascending=False).head(top_n)

        return [{"name": name, "goals": int(goals)} for name, goals in counts.items()]

    except Exception as exc:
        print(f"[data_processor] WARNING: get_top_scorers failed for {team}: {exc}")
        return []


# ---------------------------------------------------------------------------
# Feature vector construction
# ---------------------------------------------------------------------------

def build_feature_vector(team_a, team_b, results_df, elo_ratings):
    """
    Build the feature vector consumed by the ML model for a matchup.

    Returns a numpy array:
        [elo_a, elo_b, elo_diff,
         form_points_a, form_recency_a, form_goals_scored_a, form_goals_conceded_a,
         form_points_b, form_recency_b, form_goals_scored_b, form_goals_conceded_b,
         h2h_a_wins, h2h_draws, h2h_b_wins, h2h_goal_diff]
    """
    try:
        elo_a = elo_ratings.get(team_a, STARTING_ELO)
        elo_b = elo_ratings.get(team_b, STARTING_ELO)
        elo_diff = elo_a - elo_b

        form_a = recent_form(team_a, results_df)
        form_b = recent_form(team_b, results_df)

        h2h = head_to_head(team_a, team_b, results_df)
        h2h_goal_diff = h2h["team_a_goals"] - h2h["team_b_goals"]

        features = [
            elo_a,
            elo_b,
            elo_diff,
            form_a["points"],
            form_a["recency_weighted_points"],
            form_a["goals_scored"],
            form_a["goals_conceded"],
            form_b["points"],
            form_b["recency_weighted_points"],
            form_b["goals_scored"],
            form_b["goals_conceded"],
            h2h["team_a_wins"],
            h2h["draws"],
            h2h["team_b_wins"],
            h2h_goal_diff,
        ]

        return np.array(features, dtype=float)

    except Exception as exc:
        print(f"[data_processor] WARNING: build_feature_vector failed for {team_a} vs {team_b}: {exc}")
        return np.zeros(15, dtype=float)


# ---------------------------------------------------------------------------
# Top-level entry point
# ---------------------------------------------------------------------------

def load_all_data():
    """
    Load all datasets and compute ELO ratings.

    Returns: (results_df, goalscorers_df, shootouts_df, elo_ratings)
    """
    results_df, goalscorers_df, shootouts_df = load_raw_data()
    elo_ratings = calculate_elo(results_df)
    print("[data_processor] load_all_data complete.")
    return results_df, goalscorers_df, shootouts_df, elo_ratings
