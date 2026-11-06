
# ============================================================
# NeuroShield AI - DS-01 to DS-04
# Developmental Score Validation
# ============================================================

from pathlib import Path
import sys
import time
import math
import requests

BASE_URL = "http://127.0.0.1:8000"
VIDEO_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

TESTS = [
    ("DS-01", "Cognitive", "cognitive"),
    ("DS-02", "Behavioural", "behavioural"),
    ("DS-03", "Emotional", "emotional"),
    ("DS-04", "Overall", "overall"),
]


def retrieve_assessment():
    response = requests.post(
        f"{BASE_URL}/analyze-video",
        json={"youtube_url": VIDEO_URL},
        timeout=30
    )
    response.raise_for_status()

    job = response.json()
    job_id = job["job_id"]

    for _ in range(180):
        response = requests.get(
            f"{BASE_URL}/analysis-status/{job_id}",
            timeout=30
        )
        response.raise_for_status()

        data = response.json()
        status = str(data.get("status", "")).lower()

        if status in ("complete", "completed"):
            return data.get("result", data)

        if status in ("failed", "error"):
            raise RuntimeError(
                f"Backend analysis failed: {data}"
            )

        time.sleep(2)

    raise TimeoutError(
        "Analysis did not finish within 360 seconds."
    )


def validate_score(value):
    if isinstance(value, bool):
        return False

    try:
        number = float(value)
        return math.isfinite(number) and 0 <= number <= 100
    except (TypeError, ValueError):
        return False


def main():
    result = retrieve_assessment()

    scores = result.get("developmental_scores")

    if not isinstance(scores, dict):
        raise ValueError(
            "developmental_scores missing or not a dictionary. "
            f"Available result keys: {list(result.keys())}"
        )

    print()
    print("=" * 65)
    print("              NeuroShield AI - DS-01 to DS-04")
    print("             Developmental Score Validation")
    print("=" * 65)

    print(f"\nVideo ID        : dQw4w9WgXcQ")
    print(f"Analysis Source : {result.get('analysis_source', 'Not reported')}")

    print("\n" + "-" * 65)
    print("INDIVIDUAL TEST RESULTS")
    print("-" * 65)

    all_valid = True

    for test_id, label, key in TESTS:
        value = scores.get(key)
        valid = validate_score(value)

        if not valid:
            all_valid = False

        formatted = (
            f"{float(value):.2f}"
            if valid else str(value)
        )

        status = "PASS" if valid else "FAIL"

        print(
            f"{test_id} | {label:<12} | "
            f"Score: {formatted:<8} | {status}"
        )

    print("\n" + "-" * 65)
    print("OVERALL VALIDATION")
    print("-" * 65)

    print(f"Valid Score Range : 0 - 100")
    print(f"All Scores Valid  : {all_valid}")

    print(
        "Overall Test Status:",
        "PASS" if all_valid else "FAIL"
    )

    print(
        "\nNote: DS-04 aggregation formula correctness "
        "requires a separate calculation check."
    )

    print("=" * 65)
    print()


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"\nTEST ERROR: {error}")
        sys.exit(1)
