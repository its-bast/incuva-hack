import os
import requests

def generate_reply(user_text: str) -> str:
    """Genera respuesta usando SOLO Groq API"""
    
    print(f"🤖 Procesando con Groq: '{user_text}'")
    
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        return "❌ Error: No se encontró GROQ_API_KEY. Regístrate en https://groq.com/ para obtener tu API key gratuita."
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama-3.1-8b-instant",  # Modelo gratuito de Groq
        "messages": [
            {"role": "system", "content": "Eres un asistente útil y amigable que responde en español de manera natural y conversacional."},
            {"role": "user", "content": user_text}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"🔍 Groq - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if "choices" in data and len(data["choices"]) > 0:
                reply = data["choices"][0]["message"]["content"].strip()
                print(f"✅ Respuesta de Groq: {reply}")
                return reply
        else:
            print(f"❌ Groq error: {response.text}")
            return f"Error de Groq: {response.status_code}. Verifica tu API key."
            
    except Exception as e:
        print(f"❌ Groq exception: {e}")
        return f"Error de conexión con Groq: {str(e)}"
    
    return "🤖 No pude generar una respuesta en este momento."

print("🚀 Sistema usando SOLO Groq API")