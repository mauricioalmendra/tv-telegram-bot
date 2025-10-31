from flask import Flask, request
import requests
import os

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

@app.route('/')
def home():
    return "✅ Bot activo y escuchando en Render"

@app.route('/send', methods=['GET', 'POST'])
def send_message():
    text = request.args.get('text', 'Sin texto')
    if BOT_TOKEN and CHAT_ID:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
        requests.post(url, data=payload)
        return "✅ Mensaje enviado a Telegram"
    else:
        return "❌ Error: BOT_TOKEN o CHAT_ID no configurado"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
