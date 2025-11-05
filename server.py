# server.py
from flask import Flask, request
import requests, os, json
from urllib.parse import parse_qs

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID   = os.environ.get("CHAT_ID")

def extract_text(req):
    # 1) JSON bien formado
    data = request.get_json(silent=True)
    if isinstance(data, dict):
        for k in ("texto", "text", "message", "alert", "payload"):
            v = data.get(k)
            if v:
                return str(v)

    # 2) Cuerpo crudo: puede ser JSON como texto o formulario
    raw = request.get_data(as_text=True) or ""
    if raw:
        # 2a) Intentar JSON en crudo
        try:
            obj = json.loads(raw)
            if isinstance(obj, dict):
                for k in ("texto", "text", "message", "alert", "payload"):
                    v = obj.get(k)
                    if v:
                        return str(v)
        except Exception:
            pass
        # 2b) Intentar parseo estilo formulario
        qs = parse_qs(raw)
        for k in ("texto", "text", "message", "alert", "payload"):
            if k in qs and qs[k]:
                return str(qs[k][0])
        # 2c) Último recurso: devolver el crudo
        return raw

    # 3) Querystring
    for k in ("texto", "text", "message"):
        v = request.args.get(k)
        if v:
            return v

    return None

@app.route("/")
def home():
    return "✅ Bot activo y escuchando en Render"

@app.route("/webhook", methods=["POST"])
def webhook():
    text = extract_text(request)
    if not text:
        text = "⚠️ No se recibió texto desde TradingView"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": text}, timeout=10)
    return {"ok": True}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "10000")))
