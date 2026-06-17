"""
main.py

Flask application serving the World Cup Face-Off prediction API.
"""

import threading
import time
from datetime import datetime

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from ml_model import get_predictor
from players import get_player_data, get_flag, get_all_wc_teams

app = Flask(__name__, static_folder="static")
CORS(app)

_state_lock = threading.Lock()
_state = {
    "model_ready": False,
    "teams_loaded": 0,
    "training_time_seconds": None,
    "cache_used": False,
}


def _load_model_background():
    """Train (or load from cache) the predictor off the main thread so the
    server can start accepting requests immediately."""
    print("[main] Background model loading thread started ...")
    try:
        predictor = get_predictor()
        with _state_lock:
            _state["model_ready"] = True
            _state["teams_loaded"] = len(predictor.get_all_teams())
            _state["training_time_seconds"] = predictor.training_time_seconds
            _state["cache_used"] = predictor.cache_used
        print("[main] Model loaded and ready.")
    except Exception as exc:
        print(f"[main] ERROR: failed to load model in background thread: {exc}")


print("[main] Starting Flask app; model will load in a background thread ...")
threading.Thread(target=_load_model_background, daemon=True).start()


# ---------------------------------------------------------------------------
# Request logging
# ---------------------------------------------------------------------------

@app.before_request
def _start_timer():
    request._start_time = time.time()


@app.after_request
def _log_request(response):
    duration_ms = (time.time() - getattr(request, "_start_time", time.time())) * 1000
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {request.method} {request.path} -> {response.status_code} ({duration_ms:.1f}ms)")
    return response


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/", methods=["GET"])
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/teams", methods=["GET"])
def api_teams():
    try:
        wc_teams = set(get_all_wc_teams())
        historical_teams = set()

        # Avoid blocking this request on the (possibly still-training) model;
        # historical teams simply join the list once it's ready.
        if _state["model_ready"]:
            try:
                historical_teams = set(get_predictor().get_all_teams())
            except Exception as exc:
                print(f"[main] WARNING: could not fetch historical teams: {exc}")

        all_teams = sorted(wc_teams | historical_teams)
        return jsonify({"teams": all_teams})

    except Exception as exc:
        print(f"[main] ERROR in /api/teams: {exc}")
        return jsonify({"error": str(exc)}), 500


@app.route("/api/predict", methods=["POST"])
def api_predict():
    if not _state["model_ready"]:
        return jsonify({"error": "Model loading, please wait"}), 503

    try:
        data = request.get_json(force=True, silent=True) or {}
        team_a = data.get("team_a")
        team_b = data.get("team_b")

        if not team_a or not team_b:
            return jsonify({"error": "Both 'team_a' and 'team_b' are required"}), 400

        predictor = get_predictor()
        result = predictor.predict(team_a, team_b)

        result["team_a_players"] = get_player_data(team_a)
        result["team_b_players"] = get_player_data(team_b)
        result["team_a_flag"] = get_flag(team_a)
        result["team_b_flag"] = get_flag(team_b)

        return jsonify(result)

    except Exception as exc:
        print(f"[main] ERROR in /api/predict: {exc}")
        return jsonify({"error": str(exc)}), 500


@app.route("/api/status", methods=["GET"])
def api_status():
    with _state_lock:
        return jsonify(dict(_state))


@app.route("/api/health", methods=["GET"])
def api_health():
    return jsonify({"status": "ok", "model_loaded": _state["model_ready"]})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
