
# ============================================================
# NeuroShield AI - E2E-04
# Repeated Video Analysis and Result Consistency
# ============================================================

import time
import requests

BASE_URL = "http://127.0.0.1:8000"
VIDEO_URL = "https://www.youtube.com/watch?v=oovO2w5LhsM"


def get_assessment():
    response = requests.post(
        f"{BASE_URL}/analyze-video",
        json={"youtube_url": VIDEO_URL},
        timeout=30
    )
    response.raise_for_status()

    job_id = response.json()["job_id"]

    for _ in range(180):
        response = requests.get(
            f"{BASE_URL}/analysis-status/{job_id}",
            timeout=30
        )
        response.raise_for_status()

        data = response.json()
        status = str(data.get("status", "")).lower()

        if status in ("completed", "complete"):
            return data["result"]

        if status in ("failed", "error"):
            raise RuntimeError(str(data))

        time.sleep(2)

    raise TimeoutError("Analysis timed out.")


def main():
    print()
    print("=" * 65)
    print("                NeuroShield AI - E2E-04")
    print("        Repeated Video Analysis Consistency")
    print("=" * 65)

    print("\nRetrieving first assessment...")
    first = get_assessment()

    print("Retrieving second assessment...")
    second = get_assessment()

    checks = {
        "RF Prediction": (
            first.get("prediction")
            == second.get("prediction")
        ),
        "RF Confidence": (
            first.get("confidence")
            == second.get("confidence")
        ),
        "Developmental Scores": (
            first.get("developmental_scores")
            == second.get("developmental_scores")
        ),
        "Hybrid Assessment": (
            first.get("hybrid_assessment")
            == second.get("hybrid_assessment")
        ),
        "Explainability": (
            first.get("explainability")
            == second.get("explainability")
        ),
        "Multimodal Features": (
            first.get("multimedia_features")
            == second.get("multimedia_features")
        )
    }

    print("\n" + "-" * 65)
    print("CONSISTENCY VERIFICATION")
    print("-" * 65)

    for name, identical in checks.items():
        print(
            f"{name:<25}: "
            f"{'PASS' if identical else 'FAIL'}"
        )

    print("\nFirst Analysis Source :",
          first.get("analysis_source", "Not reported"))

    print("Second Analysis Source:",
          second.get("analysis_source", "Not reported"))

    passed = all(checks.values())

    print("\n" + "-" * 65)
    print(
        f"Tests Passed : {sum(checks.values())}/{len(checks)}"
    )
    print("Test Status  :", "PASS" if passed else "FAIL")
    print("=" * 65)
    print()


if __name__ == "__main__":
    main()
