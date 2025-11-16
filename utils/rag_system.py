from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from typing import List, Dict, Any
import os
import pickle
import json

class RAGSystem:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.chunks = []
        self.documents = {}  # Mapeo de documento -> chunks
        self.db_path = "faiss_db"
        
    def load_database(self):
        """Cargar base de datos FAISS si existe"""
        try:
            if os.path.exists(f"{self.db_path}/faiss.index"):
                self.index = faiss.read_index(f"{self.db_path}/faiss.index")
                
            if os.path.exists(f"{self.db_path}/chunks.pkl"):
                with open(f"{self.db_path}/chunks.pkl", "rb") as f:
                    self.chunks = pickle.load(f)
                    
            if os.path.exists(f"{self.db_path}/documents.json"):
                with open(f"{self.db_path}/documents.json", "r", encoding="utf-8") as f:
                    self.documents = json.load(f)
                    
            print(f"✅ Base de datos RAG cargada: {len(self.chunks)} chunks, {len(self.documents)} documentos")
            return True
        except Exception as e:
            print(f"⚠️ Error cargando base de datos RAG: {e}")
            return False
            
    def save_database(self):
        """Guardar base de datos FAISS"""
        try:
            os.makedirs(self.db_path, exist_ok=True)
            
            if self.index is not None:
                faiss.write_index(self.index, f"{self.db_path}/faiss.index")
                
            with open(f"{self.db_path}/chunks.pkl", "wb") as f:
                pickle.dump(self.chunks, f)
                
            with open(f"{self.db_path}/documents.json", "w", encoding="utf-8") as f:
                json.dump(self.documents, f, indent=2, ensure_ascii=False)
                
            print("✅ Base de datos RAG guardada")
            return True
        except Exception as e:
            print(f"❌ Error guardando base de datos RAG: {e}")
            return False
    
    def add_pdf_from_upload(self, file_content: bytes, filename: str) -> bool:
        """Procesar PDF desde upload y agregarlo al sistema"""
        try:
            from PyPDF2 import PdfReader
            import io
            
            # Leer PDF desde bytes
            pdf_reader = PdfReader(io.BytesIO(file_content))
            
            # Extraer texto
            text_content = ""
            for page in pdf_reader.pages:
                text_content += page.extract_text() + "\n"
            
            if not text_content.strip():
                print(f"⚠️ No se pudo extraer texto de {filename}")
                return False
            
            # Dividir en chunks
            chunks = self._split_text(text_content, chunk_size=500)
            
            if not chunks:
                print(f"⚠️ No se generaron chunks para {filename}")
                return False
            
            # Agregar al sistema
            self._add_chunks(chunks, filename)
            
            print(f"✅ PDF procesado: {filename} - {len(chunks)} chunks")
            return True
            
        except Exception as e:
            print(f"❌ Error procesando PDF {filename}: {e}")
            return False
    
    def _split_text(self, text: str, chunk_size: int = 500) -> List[str]:
        """Dividir texto en chunks"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk.strip())
        
        return chunks
    
    def _add_chunks(self, chunks: List[str], document_name: str):
        """Agregar chunks al índice FAISS"""
        try:
            # Generar embeddings
            embeddings = self.model.encode(chunks)
            
            # Crear o extender índice FAISS
            if self.index is None:
                dimension = embeddings.shape[1]
                self.index = faiss.IndexFlatL2(dimension)
            
            # Agregar al índice
            self.index.add(embeddings.astype('float32'))
            
            # Guardar chunks y mapeo de documentos
            start_idx = len(self.chunks)
            self.chunks.extend(chunks)
            
            # Mapear documento -> índices de chunks
            chunk_indices = list(range(start_idx, start_idx + len(chunks)))
            self.documents[document_name] = chunk_indices
            
            # Guardar base de datos
            self.save_database()
            
            print(f"✅ Agregado al índice: {len(chunks)} chunks de {document_name}")
            
        except Exception as e:
            print(f"❌ Error agregando chunks: {e}")
    
    def search_similar(self, query: str, k: int = 3) -> List[str]:
        """Buscar chunks similares a la consulta"""
        if self.index is None or len(self.chunks) == 0:
            return []
        
        try:
            # Generar embedding de la consulta
            query_embedding = self.model.encode([query])
            
            # Buscar en FAISS
            distances, indices = self.index.search(query_embedding.astype('float32'), k)
            
            # Obtener chunks relevantes
            relevant_chunks = []
            for idx in indices[0]:
                if 0 <= idx < len(self.chunks):
                    relevant_chunks.append(self.chunks[idx])
            
            return relevant_chunks
            
        except Exception as e:
            print(f"❌ Error en búsqueda: {e}")
            return []
    
    def delete_document(self, filename: str) -> bool:
        """Eliminar documento del sistema"""
        try:
            if filename not in self.documents:
                return False
            
            # Obtener índices de chunks a eliminar
            chunk_indices = self.documents[filename]
            
            # Eliminar chunks (marcar como vacíos)
            for idx in chunk_indices:
                if 0 <= idx < len(self.chunks):
                    self.chunks[idx] = ""  # Marcar como eliminado
            
            # Eliminar del mapeo
            del self.documents[filename]
            
            # Reconstruir índice (simplificado - en producción sería más eficiente)
            self._rebuild_index()
            
            print(f"✅ Documento eliminado: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Error eliminando documento {filename}: {e}")
            return False
    
    def _rebuild_index(self):
        """Reconstruir índice FAISS sin chunks eliminados"""
        try:
            # Filtrar chunks no vacíos
            valid_chunks = [chunk for chunk in self.chunks if chunk.strip()]
            
            if not valid_chunks:
                self.index = None
                self.chunks = []
                self.documents = {}
                self.save_database()
                return
            
            # Regenerar embeddings e índice
            embeddings = self.model.encode(valid_chunks)
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(embeddings.astype('float32'))
            
            # Actualizar chunks y mapeo
            self.chunks = valid_chunks
            
            # Recalcular mapeo de documentos
            new_documents = {}
            current_idx = 0
            
            for doc_name, old_indices in self.documents.items():
                valid_count = sum(1 for idx in old_indices if 0 <= idx < len(self.chunks) and self.chunks[idx].strip())
                if valid_count > 0:
                    new_documents[doc_name] = list(range(current_idx, current_idx + valid_count))
                    current_idx += valid_count
            
            self.documents = new_documents
            self.save_database()
            
        except Exception as e:
            print(f"❌ Error reconstruyendo índice: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del sistema RAG"""
        return {
            "pdf_count": len(self.documents),
            "chunks_count": len([c for c in self.chunks if c.strip()]),
            "rag_status": self.index is not None,
            "db_status": os.path.exists(f"{self.db_path}/faiss.index")
        }
    
    def list_documents(self) -> List[str]:
        """Listar documentos cargados"""
        return list(self.documents.keys())
    
    def create_vector_database(self, pdf_folder: str):
        """Crear base de datos desde carpeta de PDFs (para compatibilidad)"""
        if not os.path.exists(pdf_folder):
            print(f"⚠️ Carpeta {pdf_folder} no existe")
            return
        
        pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith('.pdf')]
        
        for pdf_file in pdf_files:
            pdf_path = os.path.join(pdf_folder, pdf_file)
            try:
                with open(pdf_path, 'rb') as f:
                    file_content = f.read()
                self.add_pdf_from_upload(file_content, pdf_file)
            except Exception as e:
                print(f"❌ Error procesando {pdf_file}: {e}")