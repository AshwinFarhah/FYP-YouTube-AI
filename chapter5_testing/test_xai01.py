
# ============================================================
# NeuroShield AI - XAI-01
# SHAP Explanation Generation
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
    result = get_assessment()
    explanation = result.get("explainability")

    print()
    print("=" * 65)
    print("                NeuroShield AI - XAI-01")
    print("              SHAP Explanation Generation")
    print("=" * 65)

    print("\nVideo ID        : oovO2w5LhsM")
    print(
        "Analysis Source :",
        result.get("analysis_source", "Not reported")
    )

    print("\n" + "-" * 65)
    print("EXPLAINABILITY VALIDATION")
    print("-" * 65)

    if not isinstance(explanation, dict):
        print("Explainability Object : MISSING")
        print("Test Status           : FAIL")
        return

    predicted_class = explanation.get("predicted_class")
    predicted_label = explanation.get("predicted_label")
    parent_text = explanation.get("parent_explanation")
    contributions = explanation.get("feature_contributions")

    checks = {
        "Predicted Class": (
            isinstance(predicted_class, int)
            and not isinstance(predicted_class, bool)
        ),
        "Predicted Label": (
            isinstance(predicted_label, str)
            and bool(predicted_label.strip())
        ),
        "Parent Explanation": (
            isinstance(parent_text, str)
            and bool(parent_text.strip())
        ),
        "Feature Contributions": (
            isinstance(contributions, list)
            and len(contributions) > 0
        )
    }

    for name, valid in checks.items():
        print(
            f"{name:<24}: "
            f"{'PASS' if valid else 'FAIL'}"
        )

    print("\n" + "-" * 65)
    print("EXPLANATION DETAILS")
    print("-" * 65)

    print("Predicted Class :", predicted_class)
    print("Predicted Label :", predicted_label)

    print("\nParent Explanation:")
    print(parent_text)

    print(
        "\nFeature Contributions Count:",
        len(contributions)
        if isinstance(contributions, list)
        else 0
    )

    if isinstance(contributions, list) and contributions:
        print("\nFirst Feature Contribution:")
        print(contributions[0])

    passed = all(checks.values())

    print("\n" + "-" * 65)
    print("OVERALL VALIDATION")
    print("-" * 65)

    print(
        "Tests Passed :",
        f"{sum(checks.values())}/{len(checks)}"
    )
    print("Test Status  :", "PASS" if passed else "FAIL")
    print("=" * 65)
    print()


if __name__ == "__main__":
    main()
