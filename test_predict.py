"""
test_predict.py

Local, dependency-light smoke test for the World Cup Face-Off prediction
pipeline. Run with: python test_predict.py

Not a pytest/unittest suite on purpose -- this is a quick manual sanity
check you run after changing data_processor.py / ml_model.py / main.py to
confirm the model still trains and the API still responds.
"""

import json
import pprint
import sys

TEST_MATCHUPS = [
    ("Argentina", "France"),
    ("Brazil", "Germany"),
    ("Spain", "England"),
]


def print_section(title):
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)


def run_prediction_tests():
    print_section("Loading predictor (this trains the model, ~30-60s)...")

    from ml_model import get_predictor

    predictor = get_predictor()
    print("Predictor ready.")

    for team_a, team_b in TEST_MATCHUPS:
        print_section(f"PREDICTION: {team_a} vs {team_b}")
        try:
            result = predictor.predict(team_a, team_b)
            pprint.pprint(result, sort_dicts=False, width=100)
        except Exception as exc:
            print(f"FAILED: {team_a} vs {team_b} raised an exception: {exc}")
            raise


def run_health_check_test():
    print_section("Flask health-check test (GET /api/health)")

    import main

    client = main.app.test_client()
    response = client.get("/api/health")
    data = response.get_json()

    print(f"Status code: {response.status_code}")
    print(f"Response body: {json.dumps(data)}")

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert data.get("status") == "ok", f"Expected status 'ok', got {data.get('status')}"

    print("PASSED: /api/health returned status 'ok'.")


def main_runner():
    try:
        run_prediction_tests()
        run_health_check_test()
    except Exception as exc:
        print_section("TEST RUN FAILED")
        print(f"Error: {exc}")
        sys.exit(1)

    print_section("ALL TESTS PASSED")


if __name__ == "__main__":
    main_runner()
