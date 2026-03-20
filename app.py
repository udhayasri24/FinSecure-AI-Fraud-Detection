import streamlit as st
import pandas as pd
import numpy as np
import requests
import time
import shap
import joblib
import matplotlib.pyplot as plt
import subprocess
import sys
import os
import websocket
import json

from utils.email_alert import send_email_alert
from datetime import datetime
import uuid
import io
from db import save_transaction, get_all_transactions  # ✅ UPDATED

# ---------------- CONFIG ----------------
APP_NAME = "FinSecure AI Fraud Detection"
st.set_page_config(page_title=APP_NAME, page_icon="💳", layout="centered")

API_BASE = "http://127.0.0.1:8000"
PREDICT_URL = f"{API_BASE}/predict"
LOGIN_URL = f"{API_BASE}/login"

# ---------------- WEBSOCKET ----------------
def ws_predict(input_data):
    try:
        ws = websocket.create_connection("ws://127.0.0.1:8000/ws")
        ws.send(json.dumps({"features": input_data}))
        result = json.loads(ws.recv())
        ws.close()
        return result.get("probability", 0)
    except:
        return None

# ---------------- AUTO START API ----------------
def start_api():
    try:
        requests.get(API_BASE, timeout=1)
    except:
        subprocess.Popen([sys.executable, "-m", "uvicorn", "api:app", "--reload"])

start_api()

# ---------------- DATA PREPROCESS ----------------
def preprocess_dataset(df):
    df = df.fillna(0)
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].astype("category").cat.codes
    return df

# ---------------- PREMIUM UI ----------------
st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at top, #0f172a, #020617);
    color: #e2e8f0;
}
.block-container {
    background: rgba(255,255,255,0.05);
    padding: 2rem;
    border-radius: 20px;
}
.header {
    padding: 20px;
    border-radius: 15px;
    background: linear-gradient(90deg,#0ea5e9,#22c55e);
    text-align: center;
    color: white;
    font-size: 22px;
    font-weight: bold;
}

/* Mobile */
@media (max-width: 768px) {
    .block-container {
        padding: 1rem;
    }
}
</style>
""", unsafe_allow_html=True)

# ---------------- LOAD ----------------
@st.cache_resource
def load_model():
    return joblib.load("xgb_model.pkl")

@st.cache_data
def load_data():
    return pd.read_csv("creditcard.csv", nrows=5000)

if not os.path.exists("xgb_model.pkl"):
    st.error("❌ Model not found")
    st.stop()

model = load_model()

# ---------------- SESSION ----------------
if "token" not in st.session_state:
    st.session_state.token = None
if "history" not in st.session_state:
    st.session_state.history = []
if "alerts" not in st.session_state:
    st.session_state.alerts = []
if "report" not in st.session_state:
    st.session_state.report = []
if "username" not in st.session_state:
    st.session_state.username = None  # ✅ NEW

# ---------------- SIDEBAR ----------------
st.sidebar.markdown("## 🔐 Bank Panel")

username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Login"):
    try:
        res = requests.post(LOGIN_URL, json={"username": username, "password": password})
        data = res.json()
        if "token" in data:
            st.session_state.token = data["token"]
            st.session_state.username = username  # ✅ NEW
            st.success("Login Success ✅")
        else:
            st.error("Invalid ❌")
    except:
        st.error("API not running ❌")

# ✅ UPDATED MENU
menu = st.sidebar.radio("Navigation", ["Dashboard", "Analytics", "Admin"])

# ---------------- MAIN ----------------
if st.session_state.token:

    st.markdown(f'<div class="header">{APP_NAME}</div>', unsafe_allow_html=True)

    upload = st.file_uploader("📂 Upload CSV", type=["csv"])

    if upload:
        df = pd.read_csv(upload, nrows=5000)
    else:
        df = load_data()

    if len(df) > 5000:
        df = df.sample(5000)

    df = preprocess_dataset(df)

    numeric_cols = df.columns.tolist()

    # ---------------- TARGET DETECTION ----------------
    target_col = None
    for col in df.columns:
        if df[col].nunique() <= 2:
            target_col = col
            break

    if target_col:
        numeric_cols = [c for c in df.columns if c != target_col]

    feature_names = numeric_cols

    # ---------------- ANALYTICS ----------------
    if menu == "Analytics":
        st.subheader("📊 Advanced Analytics")

        col1, col2, col3 = st.columns(3)
        col1.metric("Total", len(df))

        if target_col:
            col2.metric("Fraud", int(df[target_col].sum()))
            col3.metric("Fraud %", round(df[target_col].mean()*100, 2))

            fig, ax = plt.subplots()
            df[target_col].value_counts().plot.pie(autopct='%1.1f%%', ax=ax)
            st.pyplot(fig)

            st.line_chart(df[target_col].iloc[:1000].rolling(20).mean())

    # ---------------- DASHBOARD ----------------
    if menu == "Dashboard":

        st.subheader("🚀 Fraud Detection")

        auto = st.toggle("⚡ Auto Simulation")

        input_data = []

        if auto:
            if target_col and np.random.rand() > 0.8:
                row = df[df[target_col] == 1].sample(1)
                st.error("🚨 Fraud Transaction")
                label = "Fraud"
            else:
                row = df.sample(1)
                st.success("✅ Normal Transaction")
                label = "Normal"

            input_data = row[feature_names].values.flatten()

        else:
            st.subheader("📱 Manual Input")

            is_mobile = st.sidebar.checkbox("📱 Mobile Mode", value=True)
            cols = st.columns(1 if is_mobile else 2)

            for i, col in enumerate(feature_names[:6]):
                with cols[i % (1 if is_mobile else 2)]:
                    val = st.slider(col, float(df[col].min()), float(df[col].max()), float(df[col].mean()))
                    input_data.append(val)

            if len(feature_names) > 6:
                input_data.extend(df[feature_names[6:]].iloc[0].values.tolist())

            label = "Manual"

        txn_id = str(uuid.uuid4())[:8]
        txn_time = datetime.now().strftime('%H:%M:%S')

        if len(input_data) == 0:
            st.warning("⚠️ No input data")
            st.stop()

        input_array = np.array(input_data).reshape(1, -1)

        prob = ws_predict(input_data)

        if prob is None:
            try:
                res = requests.post(PREDICT_URL, json={"features": input_data}, timeout=3)
                prob = res.json().get("probability", 0)
            except:
                prob = model.predict_proba(input_array)[0][1]

        st.session_state.history.append(prob)
        st.session_state.history = st.session_state.history[-50:]

        st.subheader("🔍 Prediction Result")
        st.progress(float(prob))

        if prob > 0.8:
            st.error(f"🚨 HIGH FRAUD ({prob:.4f})")
            send_email_alert(prob)
            st.session_state.alerts.append(prob)
        elif prob > 0.4:
            st.warning(f"⚠️ Suspicious ({prob:.4f})")
        else:
            st.success(f"✅ Safe ({prob:.4f})")

        st.line_chart(st.session_state.history)

        save_transaction(txn_id, txn_time, prob, label)

        st.session_state.report.append({
            "Transaction_ID": txn_id,
            "Time": txn_time,
            "Type": label,
            "Probability": prob
        })

        if not auto:
            st.subheader("🌊 SHAP Explanation")

            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(input_array)

            if isinstance(shap_values, list):
                vals = shap_values[1][0]
                base = explainer.expected_value[1]
            else:
                vals = shap_values[0]
                base = explainer.expected_value

            vals = np.array(vals)
            top_idx = np.argsort(np.abs(vals))[-10:]

            shap_exp = shap.Explanation(
                values=vals[top_idx],
                base_values=base,
                data=input_array[0][top_idx],
                feature_names=[feature_names[i] for i in top_idx]
            )

            fig = plt.figure()
            shap.plots.waterfall(shap_exp, show=False)
            st.pyplot(fig)

        if auto:
            time.sleep(2)
            st.rerun()

    # ---------------- ADMIN DASHBOARD ----------------
    if menu == "Admin":

        if st.session_state.username != "admin":
            st.error("❌ Admin access only")
        else:
            st.subheader("🛠 Admin Dashboard")

            data = get_all_transactions()

            if data:
                df_admin = pd.DataFrame(
                data,
                columns=["Transaction_ID", "Time", "Probability", "Type"]
                )
                # FIX DATA TYPES
                def safe_float(x):
                  try:
                    if isinstance(x, bytes):
                       return float(x.decode(errors="ignore"))  # ignore bad bytes
                    return float(x)
                  except:
                    return 0.0  # fallback

                df_admin["Probability"] = df_admin["Probability"].apply(safe_float)

                

                col1, col2, col3 = st.columns(3)
                col1.metric("Total", len(df_admin))
                col2.metric("Fraud", (df_admin["Probability"] > 0.8).sum())
                col3.metric("Avg Risk", round(df_admin["Probability"].mean(), 2))

                filter_option = st.selectbox("Filter", ["All", "Fraud", "Normal"])

                if filter_option == "Fraud":
                    df_admin = df_admin[df_admin["Probability"] > 0.8]
                elif filter_option == "Normal":
                    df_admin = df_admin[df_admin["Probability"] <= 0.8]

                st.dataframe(df_admin)

                st.line_chart(df_admin["Probability"])

            else:
                st.info("No transactions yet")

    # ---------------- ALERT PANEL ----------------
    st.sidebar.markdown("### 🔔 Alerts")
    for a in st.session_state.alerts[-5:]:
        st.sidebar.warning(f"Fraud {a:.2f}")