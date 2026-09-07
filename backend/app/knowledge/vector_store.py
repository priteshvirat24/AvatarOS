import math
import threading
from typing import List, Tuple, Dict, Any, Optional
from backend.app.models.knowledge import DocumentChunk

class VectorStore:
    """
    In-memory vector similarity index for semantic nearest-neighbor retrieval.
    Computes exact cosine similarity and returns ranked DocumentChunks.
    """
    def __init__(self):
        self._lock = threading.Lock()
        self._chunks: List[DocumentChunk] = []
        self._vectors: List[List[float]] = []
        self._chunk_map: Dict[str, DocumentChunk] = {}

    def add_chunk(self, chunk: DocumentChunk, vector: List[float]) -> None:
        with self._lock:
            if chunk.chunk_id in self._chunk_map:
                # Update existing chunk
                idx = next(i for i, c in enumerate(self._chunks) if c.chunk_id == chunk.chunk_id)
                self._chunks[idx] = chunk
                self._vectors[idx] = vector
            else:
                self._chunks.append(chunk)
                self._vectors.append(vector)
            self._chunk_map[chunk.chunk_id] = chunk

    def add_chunks(self, chunks: List[DocumentChunk], vectors: List[List[float]]) -> None:
        for c, v in zip(chunks, vectors):
            self.add_chunk(c, v)

    def total_chunks(self) -> int:
        with self._lock:
            return len(self._chunks)

    def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[DocumentChunk, float]]:
        with self._lock:
            if not self._vectors:
                return []

            q_norm = math.sqrt(sum(x * x for x in query_vector))
            if q_norm == 0:
                return []

            results: List[Tuple[DocumentChunk, float]] = []

            for chunk, vec in zip(self._chunks, self._vectors):
                # Apply metadata filters
                if filters:
                    match = True
                    for k, v in filters.items():
                        if getattr(chunk, k, None) != v and chunk.metadata.get(k) != v:
                            match = False
                            break
                    if not match:
                        continue

                # Cosine similarity
                dot_prod = sum(q * v for q, v in zip(query_vector, vec))
                v_norm = math.sqrt(sum(v * v for v in vec))
                if v_norm > 0:
                    cos_sim = dot_prod / (q_norm * v_norm)
                else:
                    cos_sim = 0.0

                # Bound to [0.0, 1.0]
                normalized_score = max(0.0, min(1.0, (cos_sim + 1.0) / 2.0))
                results.append((chunk, round(normalized_score, 4)))

            results.sort(key=lambda x: x[1], reverse=True)
            return results[:top_k]
