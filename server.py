from flask import Flask, request
import requests
import os

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

@app.route('/')
def home():
    return "✅ Bot activo y escuchando en Render"

@app.route('/send', methods=['POST'])
def send_message():
    data = request.get_json(force=True, silent=True) or {}
    text = data.get('text') # <-- ahora busca correctamente el campo "text"

    if not text:
        text = "⚠️ No se recibió texto desde TradingView"

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': text,
        'parse_mode': 'Markdown'
    }
    r = requests.post(url, json=payload)

    if r.status_code == 200:
        return "✅ Mensaje enviado a Telegram"
    else:
        return f"❌ Error al enviar mensaje ({r.status_code})"
