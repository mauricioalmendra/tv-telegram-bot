from flask import Flask, request
import requests, os, json

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
CHAT_ID = os.environ.get("CHAT_ID", "")

@app.route("/")
def home():
    return "✅ Bot activo y escuchando en Render"

@app.route("/webhook", methods=["POST", "GET"])
def webhook():
    # — Logs de entrada para depurar —
    try:
        raw = request.get_data(as_text=True) or ""
        print("== Headers ==", dict(request.headers))
        print("== Raw body ==", raw[:800])
    except Exception as e:
        print("No se pudo leer el body:", e)
        raw = ""

    # 1) Intentar JSON nativo
    data = request.get_json(silent=True)
    # 2) Intentar parsear texto crudo como JSON
    if not data and raw:
        try:
            data = json.loads(raw)
        except Exception:
            data = {}

    # 3) Buscar el mensaje en varias claves típicas
    text = None
    if isinstance(data, dict):
        for k in ("text", "texto", "message", "alert_message", "comentario", "comment", "mensaje"):
            v = data.get(k)
            if v and str(v).strip():
                text = str(v)
                break

    # 4) Fallback: querystring (?text=... o ?texto=...)
    if not text:
        text = request.args.get("text") or request.args.get("texto")

    # 5) Último recurso: el body crudo entero
    if not text:
        text = raw if raw.strip() else "⚠️ No se recibió texto desde TradingView"

    payload = {"chat_id": CHAT_ID, "text": text}
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json=payload, timeout=10
        )
        print("Telegram resp:", r.status_code, r.text[:200])
    except Exception as e:
        print("Error enviando a Telegram:", e)

    return "ok", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)
