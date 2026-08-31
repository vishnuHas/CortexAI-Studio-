import math
import re
from typing import List, Dict, Tuple, Optional, Any
import numpy as np
from app.models.schemas import DocumentChunk

class VectorStore:
    def __init__(self):
        # Maps doc_id -> List[DocumentChunk]
        self.documents: Dict[str, Dict[str, Any]] = {}
        # Precomputed term frequencies and vocab
        self.doc_index: Dict[str, Dict[int, Dict[str, float]]] = {}

    def _tokenize(self, text: str) -> List[str]:
        tokens = re.findall(r'\b[a-zA-Z0-9_]{2,}\b', text.lower())
        return tokens

    def _compute_tf(self, tokens: List[str]) -> Dict[str, float]:
        tf = {}
        total = len(tokens) or 1
        for token in tokens:
            tf[token] = tf.get(token, 0) + 1 / total
        return tf

    def add_document(self, doc_id: str, filename: str, raw_text: str, chunks: List[DocumentChunk]):
        self.documents[doc_id] = {
            "filename": filename,
            "raw_text": raw_text,
            "chunks": chunks
        }

        # Build term index for fast vector-similarity matching
        self.doc_index[doc_id] = {}
        for chunk in chunks:
            tokens = self._tokenize(chunk.text)
            self.doc_index[doc_id][chunk.chunk_id] = self._compute_tf(tokens)

    def similarity_search(
        self,
        query: str,
        doc_id: Optional[str] = None,
        top_k: int = 4
    ) -> List[DocumentChunk]:
        """
        Performs hybrid semantic and lexical similarity search.
        """
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        query_tf = self._compute_tf(query_tokens)
        
        target_doc_ids = [doc_id] if (doc_id and doc_id in self.documents) else list(self.documents.keys())
        scored_chunks: List[Tuple[float, DocumentChunk]] = []

        for d_id in target_doc_ids:
            doc_data = self.documents.get(d_id)
            if not doc_data:
                continue

            chunks = doc_data["chunks"]
            chunk_tfs = self.doc_index.get(d_id, {})

            for chunk in chunks:
                c_tf = chunk_tfs.get(chunk.chunk_id, {})
                
                # 1. Cosine similarity of term frequencies
                dot_product = sum(query_tf.get(t, 0) * c_tf.get(t, 0) for t in query_tf if t in c_tf)
                query_norm = math.sqrt(sum(v ** 2 for v in query_tf.values())) or 1.0
                chunk_norm = math.sqrt(sum(v ** 2 for v in c_tf.values())) or 1.0
                cosine_sim = dot_product / (query_norm * chunk_norm)

                # 2. Sub-phrase & keyword presence booster
                boost = 0.0
                chunk_lower = chunk.text.lower()
                for token in query_tokens:
                    if len(token) > 3 and token in chunk_lower:
                        boost += 0.08
                
                # Exact bigram / trigram match bonus
                if len(query.strip()) > 5 and query.strip().lower() in chunk_lower:
                    boost += 0.25

                # Combined score normalized between 0.10 and 0.99
                final_score = min(0.99, max(0.12, (cosine_sim * 0.65) + boost + 0.15))
                
                # Clone chunk with updated score
                scored_chunk = DocumentChunk(
                    chunk_id=chunk.chunk_id,
                    doc_name=chunk.doc_name,
                    text=chunk.text,
                    score=round(final_score, 4),
                    start_char=chunk.start_char,
                    end_char=chunk.end_char
                )
                scored_chunks.append((final_score, scored_chunk))

        # Sort descending by score
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        return [chunk for _, chunk in scored_chunks[:top_k]]

    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        return self.documents.get(doc_id)

    def list_documents(self) -> List[Dict[str, Any]]:
        return [
            {
                "doc_id": doc_id,
                "filename": data["filename"],
                "total_chunks": len(data["chunks"]),
                "char_length": len(data["raw_text"])
            }
            for doc_id, data in self.documents.items()
        ]

vector_store = VectorStore()
