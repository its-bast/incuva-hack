from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle
import os
from typing import List
from .pdf_processor import process_all_pdfs

class RAGSystem:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.chunks = []
        
    def create_vector_database(self, pdf_folder: str):
        """Crea la base de datos vectorial desde PDFs"""
        print("🔄 Procesando PDFs...")
        self.chunks = process_all_pdfs(pdf_folder)
        
        print("🔄 Creando embeddings...")
        embeddings = self.model.encode(self.chunks)
        
        # Crear índice FAISS
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Producto interno
        self.index.add(embeddings.astype('float32'))
        
        # Guardar todo
        self.save_database()
        print("✅ Base de datos vectorial creada!")
        
    def save_database(self):
        """Guarda la base de datos"""
        faiss.write_index(self.index, "data/vectors/faiss_index.index")
        with open("data/vectors/chunks.pkl", "wb") as f:
            pickle.dump(self.chunks, f)
            
    def load_database(self):
        """Carga la base de datos"""
        if os.path.exists("data/vectors/faiss_index.index"):
            self.index = faiss.read_index("data/vectors/faiss_index.index")
            with open("data/vectors/chunks.pkl", "rb") as f:
                self.chunks = pickle.load(f)
            return True
        return False
        
    def search_similar(self, query: str, k: int = 3) -> List[str]:
        """Busca chunks similares a la consulta"""
        if not self.index:
            return []
            
        query_embedding = self.model.encode([query])
        scores, indices = self.index.search(query_embedding.astype('float32'), k)
        
        results = []
        for i in indices[0]:
            if i < len(self.chunks):
                results.append(self.chunks[i])
        
        return results