import PyPDF2
import os
from typing import List


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extrae texto de un PDF"""
    text = ""
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
    return text

def split_text_into_chunks(text: str, chunk_size: int = 500) -> List[str]:
    """Divide el texto en chunks para vectorizar"""
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    
    return chunks

def process_all_pdfs(pdf_folder: str) -> List[str]:
    """Procesa todos los PDFs de una carpeta"""
    all_chunks = []
    
    for filename in os.listdir(pdf_folder):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(pdf_folder, filename)
            print(f"📄 Procesando: {filename}")
            
            text = extract_text_from_pdf(pdf_path)
            chunks = split_text_into_chunks(text)
            all_chunks.extend(chunks)
    
    print(f"✅ Total chunks creados: {len(all_chunks)}")
    return all_chunks
