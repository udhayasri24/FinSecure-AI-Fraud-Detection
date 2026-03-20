from fastapi import FastAPI, WebSocket
import asyncio
import json
import joblib
import numpy as np

app = FastAPI()

model = joblib.load("xgb_model.pkl")

@app.get("/")
def home():
    return {"status": "API running"}
@app.post("/login")
def login(data: dict):
    username = data.get("username")
    password = data.get("password")

    print("LOGIN DATA:", username, password)  # debug

    if username == "admin" and password == "admin":
        return {"token": "secure_token"}

    return {"error": "Invalid"}

@app.post("/predict")
def predict(data: dict):
    features = np.array(data["features"]).reshape(1, -1)
    prob = model.predict_proba(features)[0][1]
    return {"probability": float(prob)}

# 🔥 REAL-TIME STREAMING
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    while True:
        data = await ws.receive_json()
        features = np.array(data["features"]).reshape(1, -1)
        prob = model.predict_proba(features)[0][1]
        await ws.send_json({"probability": float(prob)})
        # ---------------- WEBSOCKET REAL-TIME ----------------
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    while True:
        try:
            # receive data from client
            data = await websocket.receive_text()
            data = json.loads(data)

            features = np.array(data["features"]).reshape(1, -1)
            prob = model.predict_proba(features)[0][1]

            # send result back
            await websocket.send_text(json.dumps({
                "probability": float(prob)
            }))

        except Exception as e:
            await websocket.close()
            break