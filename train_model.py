import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib

# =========================
# STEP 1: Load Dataset
# =========================
data = pd.read_csv("data/dataset.csv")

print("Dataset loaded:", len(data))

# =========================
# STEP 2: Features & Labels
# =========================
X = data[["avg_sat", "avg_motion", "loudness", "density"]]
y = data["label"]

# =========================
# STEP 3: Train/Test Split
# =========================
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42
)

# =========================
# STEP 4: Train Model
# =========================
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)

# =========================
# STEP 5: Evaluate Model
# =========================
y_pred = model.predict(X_test)

print("\n📊 Accuracy:", accuracy_score(y_test, y_pred))
print("\n📄 Classification Report:\n")
print(classification_report(y_test, y_pred))

# =========================
# STEP 6: Save Model
# =========================
joblib.dump(model, "model.pkl")

print("\n✅ Model saved as model.pkl")