from flask import Flask, request
import requests
import os

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

@app.route('/')
def home():
    return "✅ Bot activo y escuchando alertas desde TradingView"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json(silent=True) or {}
    text = data.get('texto')

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
        return {'status': 'ok', 'msg': 'Mensaje enviado a Telegram'}
    else:
        return {'status': 'error', 'msg': r.text}, 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
