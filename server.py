# server.py
from flask import Flask, request
import requests, os, json

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
CHAT_ID   = os.environ.get("CHAT_ID", "")

@app.route("/")
def home():
    return "✅ Bot activo y escuchando en Render"

@app.route("/webhook", methods=["POST"])
def webhook():
    # Intento normal: JSON
    data = request.get_json(silent=True)
    # Fallback: raw body
    if data is None:
        raw = request.data.decode("utf-8") if request.data else ""
        try:
            data = json.loads(raw) if raw else {}
        except Exception:
            data = {"texto": raw}

    # Acepta "texto" (tu Pine) o "text"
    text = data.get("texto") or data.get("text")
    if not text:
        text = "⚠️ No se recibió texto desde TradingView"

    # Envío a Telegram
    if BOT_TOKEN and CHAT_ID:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
        try:
            requests.post(url, json=payload, timeout=10)
        except Exception:
            pass  # no detenemos el servidor por errores de red

    return ("ok", 200)

# ¡IMPORTANTE! Mantener el servidor corriendo en Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)
