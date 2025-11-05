# server.py
from flask import Flask, request
import requests, os, json

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID   = os.environ.get("CHAT_ID")

@app.route("/")
def home():
    return "✅ Bot activo y escuchando en Render"

@app.route("/webhook", methods=["POST"])
def webhook():
    # 1) intenta parsear JSON normalmente
    data = request.get_json(silent=True)
    # 2) si falla, intenta parsear el raw body
    if data is None:
        raw = request.data.decode("utf-8") if request.data else ""
        try:
            data = json.loads(raw) if raw else {}
        except Exception:
            # si no es JSON, trátalo como texto plano
            data = {"texto": raw}

    text = data.get("texto") or data.get("text")
    if not text:
        text = "⚠️ No se recibió texto desde TradingView"

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    requests.post(url, json=payload, timeout=10)
    return ("ok", 200)
