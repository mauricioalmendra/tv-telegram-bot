from flask import Flask, request
import requests
import os

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

@app.route('/')
def home():
    return "✅ Bot activo y escuchando en Render"

@app.route('/send', methods=['POST', 'GET'])
def send_message():
    data = request.get_json(silent=True) or request.args
    text = data.get('text')

    if not text:
        text = "⚠️ No se recibió texto desde TradingView"

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': text,
        'parse_mode': 'Markdown'
    }

    try:
        r = requests.post(url, json=payload)
        if r.status_code == 200:
            return "✅ Mensaje enviado a Telegram"
        else:
            return f"❌ Error al enviar mensaje ({r.status_code})"
    except Exception as e:
        return f"⚠️ Error en el servidor: {e}"

# 🔥 Render requiere capturar el puerto asignado dinámicamente
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
