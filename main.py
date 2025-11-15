import os
import requests
from fastapi import FastAPI, Request
from dotenv import load_dotenv
from utils.llm import generate_reply

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

app = FastAPI()

# --- Función para enviar mensajes a Telegram ---
def enviar_mensaje(chat_id: int, texto: str):
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {"chat_id": chat_id, "text": texto}
    response = requests.post(url, json=payload)
    print(f"📤 Mensaje enviado: {response.status_code}")

# --- Procesar mensaje con RAG + LLM ---
def procesar_mensaje(texto_usuario: str) -> str:
    return generate_reply(texto_usuario)

# --- Endpoint para verificar webhook (Telegram) ---
@app.get("/webhook")
async def verificar_webhook(request: Request):
    return {"status": "Webhook activo"}

# --- Endpoint Webhook para recibir mensajes ---
@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    print(f"📨 Datos recibidos: {data}")

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        texto = data["message"].get("text", "")
        
        if texto:
            print(f"👤 Usuario {chat_id}: {texto}")
            respuesta = procesar_mensaje(texto)
            enviar_mensaje(chat_id, respuesta)

    return {"ok": True}

# --- Configurar el Webhook con Telegram ---
@app.on_event("startup")
def configurar_webhook():
    if WEBHOOK_URL and TELEGRAM_TOKEN:
        url = f"{TELEGRAM_API}/setWebhook"
        payload = {"url": f"{WEBHOOK_URL}/webhook"}
        r = requests.post(url, json=payload)
        print(f"🔗 Webhook configurado: {r.json()}")
    else:
        print("⚠️ TELEGRAM_TOKEN o WEBHOOK_URL no configurados")

print("🤖 Bot de Telegram con RAG iniciado")