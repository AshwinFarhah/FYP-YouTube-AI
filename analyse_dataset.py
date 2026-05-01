import pandas as pd

df = pd.read_csv("data/dataset.csv")

# =========================
# ANALYZE DISTRIBUTION
# =========================
print("\n📊 Stim Score Distribution:")
print(df["stim_score"].describe())

# =========================
# COMPUTE THRESHOLDS
# =========================
low_threshold = df["stim_score"].quantile(0.33)
high_threshold = df["stim_score"].quantile(0.66)

print(f"\n✅ Suggested thresholds:")
print(f"Low < {low_threshold:.3f}")
print(f"Medium < {high_threshold:.3f}")
print(f"High >= {high_threshold:.3f}")

def relabel(score):
    if score < low_threshold:
        return "low_stimulation"
    elif score < high_threshold:
        return "medium_stimulation"
    else:
        return "high_stimulation"

df["development_label_refined"] = df["stim_score"].apply(relabel)

df.to_csv("data/dataset_refined.csv", index=False)