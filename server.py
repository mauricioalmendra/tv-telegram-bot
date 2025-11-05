from flask import Flask, request
import requests
import os

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID   = os.environ.get("CHAT_ID")
TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

@app.route("/", methods=["GET"])
def home():
    return "✅ Bot activo y escuchando en Render", 200

# Acepta ambas rutas para evitar confusiones en TradingView
@app.route("/webhook", methods=["POST"])
@app.route("/send",    methods=["POST"])
def send_message():
    data = request.get_json(silent=True) or {}
    text = (
        data.get("texto")
        or data.get("text")
        or request.args.get("texto")
        or request.args.get("text")
    )

    if not text:
        text = "⚠️ No se recibió texto desde TradingView"

    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
    }
    try:
        r = requests.post(TELEGRAM_URL, json=payload, timeout=10)
        status = r.status_code
    except Exception as e:
        return {"ok": False, "error": str(e)}, 500

    return {"ok": True, "echo": text, "tg_status": status}, 200


# ==== PUNTO DE ENTRADA PARA RENDER ====
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render define PORT
    app.run(host="0.0.0.0", port=port)
