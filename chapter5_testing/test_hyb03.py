
# ============================================================
# NeuroShield AI - HYB-03
# Hybrid Risk Classification Threshold Verification
# ============================================================

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.hybrid_assessment import (
    get_hybrid_category,
    LOW_MEDIUM_THRESHOLD,
    MEDIUM_HIGH_THRESHOLD
)

test_cases = [
    (0.00, "Low"),
    (27.99, "Low"),
    (28.00, "Medium"),
    (28.01, "Medium"),
    (50.00, "Medium"),
    (68.49, "Medium"),
    (68.50, "High"),
    (68.51, "High"),
    (100.00, "High"),
]

print()
print("=" * 62)
print("              NeuroShield AI - HYB-03")
print("        Hybrid Risk Classification Thresholds")
print("=" * 62)

print(f"\nLow/Medium Threshold : {LOW_MEDIUM_THRESHOLD}")
print(f"Medium/High Threshold: {MEDIUM_HIGH_THRESHOLD}")

print("\n" + "-" * 62)
print(f"{'Score':<12}{'Expected':<14}{'Actual':<14}{'Status'}")
print("-" * 62)

passed_count = 0

for score, expected in test_cases:
    actual = get_hybrid_category(score)
    passed = actual == expected

    if passed:
        passed_count += 1

    print(
        f"{score:<12.2f}"
        f"{expected:<14}"
        f"{actual:<14}"
        f"{'PASS' if passed else 'FAIL'}"
    )

print("\n" + "-" * 62)
print(f"Tests Passed : {passed_count}/{len(test_cases)}")
print(
    "Test Status :",
    "PASS" if passed_count == len(test_cases) else "FAIL"
)
print("=" * 62)
