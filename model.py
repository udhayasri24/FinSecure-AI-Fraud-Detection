import os
print("FILE STARTED")
print("📂 Files in folder:", os.listdir())

import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from imblearn.over_sampling import SMOTE
from collections import Counter

# ---------------- LOAD DATA ----------------
print("➡ Loading data...")

# ✅ FIXED (removed nrows limit)
data = pd.read_csv("creditcard.csv")

print("✅ Data loaded")

# ---------------- PREPARE DATA ----------------
print("➡ Preparing data...")

# Features & Target
X = data.drop("Class", axis=1)
y = data["Class"]

# ---------------- HANDLE IMBALANCE (SMART SMOTE) ----------------
print("➡ Applying SMOTE...")

counter = Counter(y)
min_class = min(counter.values())

# Dynamic k_neighbors (production-level fix)
k = min(5, min_class - 1)

sm = SMOTE(k_neighbors=k, random_state=42)
X_res, y_res = sm.fit_resample(X, y)

print("✅ SMOTE done")

# ---------------- SPLIT DATA ----------------
print("➡ Splitting data...")

X_train, X_test, y_train, y_test = train_test_split(
    X_res, y_res, test_size=0.2, random_state=42
)

print("✅ Data split")

# ---------------- TRAIN MODEL ----------------
print("➡ Training model...")

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

print("✅ Model trained")

# ---------------- SAVE MODEL ----------------
print("➡ Saving model...")

joblib.dump(model, "fraud_model.pkl")

print("✅ Model saved as fraud_model.pkl")

# ---------------- EVALUATE ----------------
print("➡ Evaluating model...")

accuracy = model.score(X_test, y_test)
print(f"🎯 Accuracy: {accuracy:.4f}")

print("🚀 DONE SUCCESSFULLY")