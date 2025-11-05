# server.py
from flask import Flask, request
import requests
import os
import json

app = Flask(__name__)

# Variables de entorno en Render: BOT_TOKEN y CHAT_ID
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID   = os.environ.get("CHAT_ID")

def send_to_telegram(text: str) -> None:
    """
    Envía el mensaje 'text' al chat indicado por CHAT_ID usando el bot BOT_TOKEN.
    Mantiene compatibilidad con Markdown y caracteres Unicode.
    """
    if not BOT_TOKEN or not CHAT_ID:
        # Si faltan variables, no lanzar excepción para no tumbar el proceso.
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",          # Mantiene negritas con *texto*
        "disable_web_page_preview": True,  # Evita previews accidentales
        "allow_sending_without_reply": True
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception:
        # Evita que un fallo de red derribe el contenedor
        pass


@app.route("/", methods=["GET"])
def home():
    return "✅ Bot activo y escuchando en Render"


@app.route("/ping", methods=["GET", "POST"])
def ping():
    # Comprobación manual desde navegador o Web Shell de Render
    send_to_telegram("✅ Ping desde Render (post-fix)")
    return "pong", 200


@app.route("/health", methods=["GET"])
def health():
    # Endpoint simple para health checks
    return {"ok": True}, 200


@app.route("/webhook", methods=["POST"])
def webhook():
    """
    Endpoint que recibe el POST de TradingView.
    Acepta estos formatos:
      1) JSON con clave "texto"   -> {"texto": "..."}
      2) JSON con clave "text"    -> {"text": "..."}
      3) JSON con clave "message" -> {"message": "..."}  (formato por defecto de TV)
      4) Cuerpo como texto plano  -> '{"texto":"..."}' o el mensaje directo

    Si 'message' trae un JSON en string, intenta extraer "texto"/"message" interno.
    """
    try:
        data = request.get_json(silent=True) or request.form.to_dict() or {}
        raw  = request.get_data(as_text=True) or ""

        # Preferencias de claves habituales
        text = data.get("texto") or data.get("text") or data.get("message")

        # Si llegó en bruto, úsalo
        if not text and raw:
            text = raw.strip()

        # Si 'text' es un JSON serializado, intenta decodificar y extraer
        if text:
            try:
                obj = json.loads(text)
                if isinstance(obj, dict):
                    text = obj.get("texto") or obj.get("message") or text
            except Exception:
                # No era JSON, seguir con el string original
                pass

        if not text:
            text = "⚠️ No se recibió texto desde TradingView"

        # Envío a Telegram
        send_to_telegram(text)

        return {"ok": True}, 200

    except Exception as e:
        # Respuesta controlada ante errores inesperados
        send_to_telegram(f"⚠️ Error en webhook: {e}")
        return {"ok": False, "error": str(e)}, 500


if __name__ == "__main__":
    # Render asigna PORT; por compatibilidad dejamos 10000 por defecto
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)
