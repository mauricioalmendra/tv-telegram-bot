# server.py
from flask import Flask, request
import requests, os, json, re

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
CHAT_ID   = os.environ.get("CHAT_ID", "")

@app.route("/")
def home():
    return "✅ Bot activo y escuchando en Render"

@app.route("/webhook", methods=["POST"])
def webhook():
    # 1) Intento principal: JSON nativo
    data = request.get_json(silent=True)
    text = None

    if isinstance(data, dict):
        # Acepta varias claves por compatibilidad
        text = data.get("texto") or data.get("text") or data.get("message")
    elif isinstance(data, str):
        # Algunos clientes mandan un string JSON o texto plano
        text = data

    # 2) Fallback leyendo el cuerpo crudo
    if not text:
        raw = request.data.decode("utf-8") if request.data else ""

        # 2a) Si es JSON válido, lo cargo
        try:
            j = json.loads(raw)
            if isinstance(j, dict):
                text = j.get("texto") or j.get("text") or j.get("message")
            elif isinstance(j, str):
                text = j
        except Exception:
            # 2b) Si llega como texto plano con forma {"texto":"..."}
            m = re.match(r'^\s*\{\s*"texto"\s*:\s*"(.*)"\s*\}\s*$', raw, re.S)
            if m:
                # Decodifica secuencias escapadas (\n, \") si las hubiera
                text = m.group(1).encode("utf-8").decode("unicode_escape")
            else:
                text = raw

    if not text:
        text = "⚠️ No se recibió texto desde TradingView"

    # 3) Envío a Telegram
    if BOT_TOKEN and CHAT_ID:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
        try:
            requests.post(url, json=payload, timeout=10)
        except Exception:
            pass  # No tumbar el servidor por errores de red

    return ("ok", 200)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)
