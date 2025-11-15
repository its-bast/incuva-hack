import os
import requests
from .rag_system import RAGSystem

# Inicializar RAG globalmente
rag = RAGSystem()
rag.load_database()  # Cargar si ya existe

def generate_reply(user_text: str) -> str:
    """Genera respuesta usando Groq + RAG"""
    
    print(f"🤖 Procesando con Groq + RAG: '{user_text}'")
    
    # Buscar en documentos técnicos
    context = ""
    if rag.index is not None:
        similar_chunks = rag.search_similar(user_text, k=2)
        if similar_chunks:
            context = "\n\nContexto de manuales técnicos:\n" + "\n".join(similar_chunks)
            print(f"📚 Contexto encontrado: {len(similar_chunks)} chunks")
    
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        return "❌ Error: No se encontró GROQ_API_KEY. Regístrate en https://groq.com/ para obtener tu API key gratuita."
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Prompt mejorado con contexto
    system_prompt = """Eres un asistente de soporte técnico especializado. 
    Responde en español de manera profesional y útil.
    Si tienes contexto de manuales técnicos, úsalo para dar respuestas más precisas.
    Si no tienes información técnica específica, responde de manera general pero útil."""
    
    user_message = user_text + context
    
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
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

def setup_rag(pdf_folder: str = "data/pdfs"):
    """Función para configurar RAG - ejecutar una vez"""
    global rag
    if os.path.exists(pdf_folder) and os.listdir(pdf_folder):
        rag.create_vector_database(pdf_folder)
        print("✅ RAG configurado correctamente")
    else:
        print(f"⚠️ No se encontraron PDFs en {pdf_folder}")

print("🚀 Sistema usando Groq API + RAG")