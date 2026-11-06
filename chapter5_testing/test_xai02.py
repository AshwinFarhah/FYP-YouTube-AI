
# ============================================================
# NeuroShield AI - XAI-02
# Supporting and Opposing Feature Verification
# ============================================================

import time
import math
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


def valid_group(group, expected_direction):
    if not isinstance(group, list):
        return False

    for factor in group:
        if not isinstance(factor, dict):
            return False

        if factor.get("direction") != expected_direction:
            return False

        value = factor.get("shap_value")

        try:
            value = float(value)
        except (TypeError, ValueError):
            return False

        if not math.isfinite(value):
            return False

        if expected_direction == "supports" and value <= 0:
            return False

        if expected_direction == "opposes" and value >= 0:
            return False

    return True


def main():
    result = get_assessment()
    explanation = result["explainability"]

    supporting = explanation.get("supporting_factors")
    opposing = explanation.get("opposing_factors")

    supporting_valid = valid_group(supporting, "supports")
    opposing_valid = valid_group(opposing, "opposes")

    print()
    print("=" * 65)
    print("                NeuroShield AI - XAI-02")
    print("         Supporting and Opposing SHAP Factors")
    print("=" * 65)

    print("\nPredicted Label:", explanation.get("predicted_label"))

    print("\n" + "-" * 65)
    print("SUPPORTING FACTORS")
    print("-" * 65)

    if isinstance(supporting, list):
        print("Factors Found:", len(supporting))

        for factor in supporting:
            print(
                f"- {factor.get('friendly_name', factor.get('feature'))}: "
                f"{factor.get('shap_value')}"
            )
    else:
        print("Supporting factors missing or invalid.")

    print("\n" + "-" * 65)
    print("OPPOSING FACTORS")
    print("-" * 65)

    if isinstance(opposing, list):
        print("Factors Found:", len(opposing))

        for factor in opposing:
            print(
                f"- {factor.get('friendly_name', factor.get('feature'))}: "
                f"{factor.get('shap_value')}"
            )
    else:
        print("Opposing factors missing or invalid.")

    print("\n" + "-" * 65)
    print("VALIDATION RESULTS")
    print("-" * 65)

    print(
        "Supporting Factors:",
        "PASS" if supporting_valid else "FAIL"
    )
    print(
        "Opposing Factors  :",
        "PASS" if opposing_valid else "FAIL"
    )

    passed = supporting_valid and opposing_valid

    print("\nTest Status:", "PASS" if passed else "FAIL")
    print("=" * 65)
    print()


if __name__ == "__main__":
    main()
