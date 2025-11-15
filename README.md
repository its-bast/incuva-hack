# 🤖 WhatsApp Bot con RAG (Retrieval-Augmented Generation)

Bot de WhatsApp inteligente que combina un LLM (Groq) con un sistema RAG para responder preguntas técnicas basadas en PDFs de manuales y documentación.

## ⚡ Características

- 🚀 **LLM integrado** con Groq API (Llama 3.1)
- 📚 **Sistema RAG** para consultar documentos técnicos
- 📱 **Integración WhatsApp** Business API
- 🔍 **Búsqueda semántica** en PDFs
- ⚡ **Respuestas rápidas** y contextualizadas

## 🛠️ Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/sebastianromero07/incuva-hack.git
cd incuva-hack
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Crear archivo `.env`
```env
# WhatsApp Business API
TELEGRAM_TOKEN=tu_verify_token
WEBHOOK_URL=tu_access_token

# Groq API (gratis en https://groq.com/)
GROQ_API_KEY=tu_groq_api_key
```

## 📚 Configuración del RAG

### 1. Agregar documentos técnicos
Coloca tus PDFs (manuales, FAQ, documentación) en:
```
data/pdfs/
├── manual_producto.pdf
├── faq_soporte.pdf
└── documentacion_tecnica.pdf
```

### 2. Procesar PDFs (ejecutar una sola vez)
```bash
python
```
```python
from utils.llm import setup_rag
setup_rag()
exit()
```

## 🚀 Ejecutar el Bot

### Modo desarrollo
```bash
uvicorn main:app --reload
```

### Modo producción
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 📖 Cómo funciona

### Flujo del RAG
1. **Usuario envía mensaje** → WhatsApp webhook
2. **Sistema busca** contexto relevante en PDFs procesados
3. **LLM genera respuesta** combinando pregunta + contexto técnico
4. **Respuesta enviada** de vuelta a WhatsApp

### Arquitectura del sistema
```
Usuario → WhatsApp → Webhook → RAG Search → Groq LLM → Respuesta
                                   ↓
                            Base de datos vectorial
                            (PDFs procesados)
```

## 🧩 Estructura del proyecto

```
incuva-hack/
├── main.py                 # FastAPI app principal
├── requirements.txt        # Dependencias
├── .env                   # Variables de entorno
├── utils/
│   ├── __init__.py
│   ├── llm.py            # Integración Groq + RAG
│   ├── pdf_processor.py  # Procesamiento de PDFs
│   └── rag_system.py     # Sistema de vectores
└── data/
    ├── pdfs/             # PDFs fuente
    └── vectors/          # Base de datos vectorial
```

## 🧪 Ejemplos de preguntas

**Usuario:** "¿Cómo resetear el dispositivo?"
**Bot:** Busca en manuales técnicos y responde con pasos específicos

**Usuario:** "Error 404 en la pantalla"
**Bot:** Consulta FAQ y proporciona solución detallada

**Usuario:** "Especificaciones técnicas del modelo X"
**Bot:** Extrae información de documentación técnica



**¡Listo!** 🎉 Tu bot inteligente con RAG está funcionando.
