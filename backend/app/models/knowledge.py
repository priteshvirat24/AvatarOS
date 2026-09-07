from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field

class Document(BaseModel):
    """
    Provenance-preserving Document representation in AVATAROS Knowledge Base.
    """
    doc_id: str
    title: str
    source_type: Literal["pdf", "markdown", "text", "benchmark_dataset"] = "text"
    content_hash: str
    language: str = "en"
    version: int = 1
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class DocumentChunk(BaseModel):
    """
    Fine-grained semantic passage with structural provenance (page, section, hash).
    """
    chunk_id: str
    doc_id: str
    chunk_index: int
    text: str
    content_hash: str
    section: Optional[str] = None
    page: Optional[int] = None
    language: str = "en"
    token_count: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)

class RetrievalQuery(BaseModel):
    """
    Query specification for hybrid vector + BM25 retrieval.
    """
    query_text: str
    top_k: int = 5
    language: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None

class RetrievalResult(BaseModel):
    """
    Fused retrieval candidate with separate semantic and lexical scores.
    """
    chunk: DocumentChunk
    semantic_score: float
    lexical_score: float
    hybrid_score: float
    retrieval_methods: List[str] = Field(default_factory=list)

class Evidence(BaseModel):
    """
    Documentary evidence attached to claims with cryptographic checksums.
    Preserves answer to: 'Where did this evidence come from?' without guessing.
    """
    evidence_id: str
    doc_id: str
    chunk_id: str
    title: str
    section: Optional[str] = None
    page: Optional[int] = None
    excerpt: str
    doc_checksum: str
    chunk_checksum: str
    retrieval_score: float
    retrieval_method: str = "hybrid"
