# server.py
from flask import Flask, request
import requests, os, json

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

@app.route("/")
def home():
    return "🟢 Bot activo y escuchando en Render"

@app.route("/webhook", methods=["POST"])
def webhook():
    # 1) intenta leer JSON
    data = request.get_json(silent=True)
    text = None

    if isinstance(data, dict):
        # acepta "text" o "texto"
        text = data.get("text") or data.get("texto")

    # 2) si no vino JSON, toma el cuerpo crudo (TradingView suele enviar text/plain)
    if not text:
        raw = request.get_data(as_text=True) or ""
        raw = raw.strip()
        if raw:
            # si el cuerpo es JSON en texto, parsea; si no, úsalo como texto tal cual
            if raw.startswith("{") and raw.endswith("}"):
                try:
                    j = json.loads(raw)
                    text = j.get("text") or j.get("texto") or raw
                except Exception:
                    text = raw
            else:
                text = raw

    # 3) fallback
    if not text:
        text = "⚠️ No se recibió texto desde TradingView"

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception:
        pass
    return {"ok": True}, 200
