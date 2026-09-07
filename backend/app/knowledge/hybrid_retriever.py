from typing import List, Dict, Any, Optional
from backend.app.config import settings
from backend.app.logging import app_logger
from backend.app.models.knowledge import DocumentChunk, RetrievalResult
from backend.app.knowledge.embeddings import BaseEmbeddingProvider, get_embedding_provider
from backend.app.knowledge.vector_store import VectorStore
from backend.app.knowledge.bm25 import BM25Index

class HybridRetriever:
    """
    Hybrid Retrieval Service combining Semantic Vector Search + Okapi BM25 Lexical Ranking.
    Normalizes scores, deduplicates chunks, tags retrieval methods, and preserves provenance.
    """
    def __init__(
        self,
        vector_store: VectorStore,
        bm25_index: BM25Index,
        embedding_provider: Optional[BaseEmbeddingProvider] = None,
        vector_weight: Optional[float] = None,
        lexical_weight: Optional[float] = None
    ):
        self.vector_store = vector_store
        self.bm25_index = bm25_index
        self.embedding_provider = embedding_provider or get_embedding_provider()
        self.vector_weight = vector_weight if vector_weight is not None else settings.VECTOR_WEIGHT
        self.lexical_weight = lexical_weight if lexical_weight is not None else settings.LEXICAL_WEIGHT

    def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
        trace_id: str = "system"
    ) -> List[RetrievalResult]:
        actual_k = top_k or settings.HYBRID_TOP_K
        if not query or not query.strip():
            return []

        # 1. Semantic Vector Search
        q_vec = self.embedding_provider.embed_text(query)
        vector_hits = self.vector_store.search(q_vec, top_k=actual_k * 2, filters=filters)
        vec_map: Dict[str, Tuple[DocumentChunk, float]] = {c.chunk_id: (c, score) for c, score in vector_hits}

        # 2. BM25 Lexical Search
        lexical_hits = self.bm25_index.search(query, top_k=actual_k * 2)
        lex_map: Dict[str, Tuple[DocumentChunk, float]] = {c.chunk_id: (c, score) for c, score in lexical_hits}

        # 3. Score Fusion & Deduplication
        all_chunk_ids = set(vec_map.keys()).union(set(lex_map.keys()))
        fused_candidates: List[RetrievalResult] = []

        for cid in all_chunk_ids:
            chunk: Optional[DocumentChunk] = None
            sem_score = 0.0
            lex_score = 0.0
            methods: List[str] = []

            if cid in vec_map:
                chunk, sem_score = vec_map[cid]
                methods.append("semantic")

            if cid in lex_map:
                c_lex, lex_score = lex_map[cid]
                if chunk is None:
                    chunk = c_lex
                methods.append("lexical")

            if chunk is None:
                continue

            hybrid_score = (self.vector_weight * sem_score) + (self.lexical_weight * lex_score)
            fused_candidates.append(RetrievalResult(
                chunk=chunk,
                semantic_score=round(sem_score, 4),
                lexical_score=round(lex_score, 4),
                hybrid_score=round(hybrid_score, 4),
                retrieval_methods=methods
            ))

        # Sort descending by fused hybrid score
        fused_candidates.sort(key=lambda x: x.hybrid_score, reverse=True)
        final_results = fused_candidates[:actual_k]

        app_logger.log_operation(
            trace_id=trace_id,
            operation="hybrid_retrieval",
            status="SUCCESS",
            agent_task="retrieval_service",
            details={
                "query": query[:60],
                "vector_hits": len(vector_hits),
                "lexical_hits": len(lexical_hits),
                "fused_results": len(final_results)
            }
        )

        return final_results
