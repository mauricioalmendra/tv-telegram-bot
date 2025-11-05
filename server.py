# server.py
from flask import Flask, request
import requests, os, json

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

@app.route("/")
def home():
    return "🟢 Bot activo y escuchando en Render"

@app.route("/health")
def health():
    return {"ok": True}, 200

@app.route("/webhook", methods=["POST"])
def webhook():
    # 1) intenta leer JSON
    data = request.get_json(silent=True)
    text = None
    if isinstance(data, dict):
        text = data.get("text") or data.get("texto")

    # 2) si no hay JSON, usa el cuerpo crudo (TradingView puede enviar text/plain)
    if not text:
        raw = request.get_data(as_text=True) or ""
        raw = raw.strip()
        if raw:
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

    # 4) envía a Telegram
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
        requests.post(url, json=payload, timeout=10)
    except Exception:
        # evita que un error externo derribe el webhook
        pass

    return {"ok": True}, 200


if __name__ == "__main__":
    # Render asigna el puerto por variable de entorno PORT
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)
