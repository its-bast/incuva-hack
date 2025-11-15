from fastapi import FastAPI, Request
import requests
import os
from dotenv import load_dotenv
from utils.llm import generate_reply

load_dotenv()
app = FastAPI()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

# 1️⃣ Endpoint de verificación (GET)
@app.get("/webhook")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return int(challenge)
    return {"error": "Token inválido"}, 403

# 2️⃣ Endpoint para recibir mensajes (POST)
@app.post("/webhook")
async def handle_message(request: Request):
    body = await request.json()
    
    print("📩 Mensaje recibido:", body)  # Debug

    try:
        entry = body["entry"][0]
        changes = entry["changes"][0]["value"]
        messages = changes.get("messages")

        if messages:
            message = messages[0]
            user_number = message["from"]
            user_text = message["text"]["body"]
            
            print(f"👤 Usuario: {user_number}")  # Debug
            print(f"💬 Texto: {user_text}")     # Debug

            # Generar respuesta con tu modelo IA
            reply = generate_reply(user_text)
            print(f"🤖 Respuesta: {reply}")      # Debug

            # Enviar mensaje de vuelta a WhatsApp Cloud API
            response = send_message(user_number, reply)
            print(f"📤 Respuesta de envío: {response.status_code}")
        else:
            print("⚠️ No hay mensajes en el webhook")

    except Exception as e:
        print("❌ Error procesando mensaje:", e)
        import traceback
        traceback.print_exc()

    return {"status": "ok"}

# Función auxiliar para enviar mensajes
def send_message(to, text):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": text}
    }
    response = requests.post(url, headers=headers, json=payload)
    print(f"📊 Status del envío: {response.status_code}, Respuesta: {response.text}")
    return response