import pandas as pd
from xgboost import XGBClassifier
import joblib

df = pd.read_csv("creditcard.csv")

X = df.drop("Class", axis=1)
y = df["Class"]

model = XGBClassifier(n_estimators=100, max_depth=4)
model.fit(X, y)

joblib.dump(model, "xgb_model.pkl")

print("✅ Model trained and saved as xgb_model.pkl")