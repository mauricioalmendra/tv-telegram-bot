from flask import Flask, request
import requests
import os
import json

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

@app.route("/")
def home():
    return "✅ Bot activo y escuchando en Render"

@app.route("/webhook", methods=["POST", "GET"])
def webhook():
    # Logs mínimos para depurar
    try:
        raw = request.get_data(as_text=True) or ""
        print("== Headers ==", dict(request.headers))
        print("== Raw body ==", raw[:500])
    except Exception as e:
        print("No se pudo leer raw body:", e)
        raw = ""

    # 1) Intento JSON directo
    data = request.get_json(silent=True)
    if not data and raw:
        # 2) A veces llega como str JSON
        try:
            data = json.loads(raw)
        except Exception:
            data = {}

    # 3) Extrae texto desde múltiples claves conocidas
    text = None
    if isinstance(data, dict):
        text = (
            data.get("text")
            or data.get("texto")
            or data.get("message")
            or data.get("alert_message")
            or data.get("comentario")
            or data.get("comment")
        )

    # 4) Si vino por querystring (?texto=...), úsalo
    if not text and request.args:
        text = request.args.get("text") or request.args.get("texto")

    # 5) Último recurso: usa el raw body tal cual
    if not text and raw:
        text = raw

    if not text or not str(text).strip():
        text = "⚠️ No se recibió texto desde TradingView"

    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        # Quita parse_mode para evitar problemas con guiones bajos, asteriscos, etc.
        # "parse_mode": "Markdown"
    }
    r = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json=payload, timeout=10
    )
    print("Telegram status:", r.status_code, r.text[:200])
    return "ok", 200
    
