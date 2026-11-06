
# ============================================================
# NeuroShield AI - XAI-03
# SHAP Prediction Consistency
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

    prediction = result.get("prediction")
    explanation = result.get("explainability")

    print()
    print("=" * 65)
    print("                NeuroShield AI - XAI-03")
    print("               SHAP Prediction Consistency")
    print("=" * 65)

    print("\nVideo ID: oovO2w5LhsM")
    print("Analysis Source:", result.get("analysis_source"))

    if not isinstance(explanation, dict):
        print("\nExplainability object missing.")
        print("Test Status: FAIL")
        return

    shap_class = explanation.get("predicted_class")
    shap_label = explanation.get("predicted_label")

    print("\n" + "-" * 65)
    print("PREDICTION COMPARISON")
    print("-" * 65)

    print("RF Prediction      :", prediction)
    print("SHAP Predicted Class:", shap_class)
    print("SHAP Predicted Label:", shap_label)

    # Check the actual response structure before comparing.
    if isinstance(prediction, dict):
        print("\nRF Prediction Fields:", list(prediction.keys()))

        rf_class = prediction.get(
            "predicted_class",
            prediction.get("class")
        )

        rf_label = prediction.get(
            "predicted_label",
            prediction.get("label")
        )

    else:
        rf_class = prediction
        rf_label = None

    class_match = (
        rf_class is not None
        and shap_class is not None
        and str(rf_class) == str(shap_class)
    )

    label_match = (
        rf_label is not None
        and shap_label is not None
        and str(rf_label).strip().lower()
        == str(shap_label).strip().lower()
    )

    print("\n" + "-" * 65)
    print("VALIDATION RESULTS")
    print("-" * 65)

    print("Class Match :", "PASS" if class_match else "FAIL")

    if rf_label is not None:
        print("Label Match :", "PASS" if label_match else "FAIL")
    else:
        print("Label Match : NOT CHECKED (RF label unavailable)")

    passed = class_match and (
        label_match if rf_label is not None else True
    )

    print("\nTest Status:", "PASS" if passed else "FAIL")
    print("=" * 65)
    print()


if __name__ == "__main__":
    main()
