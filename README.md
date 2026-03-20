🚀 Real-time AI-powered fraud detection with explainable insights and live monitoring dashboard.

FinSecure AI Fraud Detection is an end-to-end machine learning system designed to detect fraudulent financial transactions in real time. It combines AI, backend APIs, and an interactive dashboard to provide accurate predictions and explainable insights.

 🚀 Features
- 🔍 Real-time fraud detection using XGBoost  
- 🌐 FastAPI backend with REST & WebSocket support  
- 📊 Streamlit dashboard with premium UI  
- 🧠 SHAP explainability (feature importance & waterfall)  
- 📂 Supports multiple datasets (auto preprocessing)  
- 📱 Mobile-friendly responsive UI  
- 🛠 Admin dashboard with transaction monitoring  
- 📈 Live prediction history & alerts  

🧠 Tech Stack
- **Frontend:** Streamlit  
- **Backend:** FastAPI  
- **Machine Learning:** XGBoost  
- **Explainability:** SHAP  
- **Database:** SQLite  
- **Communication:** REST API + WebSockets  

📂 Project Structure
fraud-detection/ │ ├── app.py              # Streamlit frontend ├── api.py              # FastAPI backend ├── db.py               # Database handling ├── train_model.py      # Model training ├── utils/              # Helper functions ├── requirements.txt    # Dependencies └── README.md

⚙️ Installation & Setup

1. Install dependencies  
pip install -r requirements.txt

2. Run backend  
uvicorn api:app --reload

3. Run frontend  
streamlit run app.py

🔐 Login Credentials
Username: admin Password: admin

📊 How It Works

1. User inputs transaction data (manual or auto simulation)  
2. Data is sent to backend via API/WebSocket  
3. ML model predicts fraud probability  
4. SHAP explains feature importance  
5. Results displayed in dashboard and stored in database  

🌍 Real-World Impact

- Helps detect fraudulent transactions instantly  
- Provides explainable AI insights for better decisions  
- Useful in banking, fintech, and payment systems
  

 ⚠️ Note

Large files like dataset (`creditcard.csv`) and model (`xgb_model.pkl`) are not included due to GitHub size limits.

💡 What Makes It Special

- Real-time prediction using WebSockets  
- Explainable AI using SHAP  
- End-to-end system (UI + API + ML + DB)  
- Works with multiple datasets


