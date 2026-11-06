
# ============================================================
# NeuroShield AI - HYB-01 and HYB-02
# Hybrid Weight and Calculation Verification
# ============================================================

import time
import math
import requests

BASE_URL = "http://127.0.0.1:8000"
VIDEO_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

def get_result():
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

        if status in ("complete", "completed"):
            return data["result"]

        if status in ("failed", "error"):
            raise RuntimeError(str(data))

        time.sleep(2)

    raise TimeoutError("Analysis timed out.")


def main():
    result = get_result()
    hybrid = result["hybrid_assessment"]

    rf_weight = float(hybrid["rf_weight"])
    dev_weight = float(hybrid["developmental_weight"])

    rf_evidence = float(hybrid["rf_risk_evidence"])
    dev_impact = float(hybrid["developmental_impact"])

    backend_score = float(hybrid["score"])

    calculated_score = (
        rf_weight * rf_evidence
        + dev_weight * dev_impact
    )

    weight_sum = rf_weight + dev_weight

    difference = abs(calculated_score - backend_score)

    # The API rounds component scores to 2 decimal places.
    tolerance = 0.02

    hyb01 = (
        math.isclose(rf_weight, 0.50, abs_tol=0.0001)
        and math.isclose(dev_weight, 0.50, abs_tol=0.0001)
        and math.isclose(weight_sum, 1.0, abs_tol=0.0001)
    )

    hyb02 = (
        all(math.isfinite(x) for x in (
            rf_evidence, dev_impact,
            backend_score, calculated_score
        ))
        and 0 <= rf_evidence <= 100
        and 0 <= dev_impact <= 100
        and 0 <= backend_score <= 100
        and difference <= tolerance
    )

    print()
    print("=" * 60)
    print("        NeuroShield AI - HYB-01 and HYB-02")
    print("        Hybrid Assessment Verification")
    print("=" * 60)

    print("\nHYB-01: WEIGHT VERIFICATION")
    print("-" * 60)
    print(f"RF Weight            : {rf_weight:.2f}")
    print(f"Developmental Weight : {dev_weight:.2f}")
    print(f"Total Weight         : {weight_sum:.2f}")
    print(f"Test Status          : {'PASS' if hyb01 else 'FAIL'}")

    print("\nHYB-02: CALCULATION VERIFICATION")
    print("-" * 60)
    print(f"RF Risk Evidence     : {rf_evidence:.2f}")
    print(f"Developmental Impact : {dev_impact:.2f}")
    print(f"Calculated Score     : {calculated_score:.4f}")
    print(f"Backend Score        : {backend_score:.2f}")
    print(f"Difference           : {difference:.4f}")
    print(f"Tolerance            : {tolerance:.2f}")
    print(f"Hybrid Category      : {hybrid['category']}")
    print(f"Test Status          : {'PASS' if hyb02 else 'FAIL'}")

    print("\n" + "=" * 60)
    print(
        "OVERALL TEST STATUS:",
        "PASS" if hyb01 and hyb02 else "FAIL"
    )
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
