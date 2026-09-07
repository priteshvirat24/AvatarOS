import threading
from typing import Dict, List, Any, Optional

from backend.app.models.knowledge import Document, DocumentChunk, RetrievalResult
from backend.app.knowledge.chunker import SemanticChunker
from backend.app.knowledge.ingest import DocumentIngestionEngine
from backend.app.knowledge.embeddings import get_embedding_provider, BaseEmbeddingProvider
from backend.app.knowledge.vector_store import VectorStore
from backend.app.knowledge.bm25 import BM25Index
from backend.app.knowledge.hybrid_retriever import HybridRetriever
from backend.app.logging import app_logger

class KnowledgeBase:
    """
    Central Grounded Knowledge Base repository for AVATAROS.
    Manages document lifecycle, cryptographic checksum versioning, vector index, and BM25 index.
    """
    def __init__(self, embedding_provider: Optional[BaseEmbeddingProvider] = None):
        self._lock = threading.Lock()
        self.embedding_provider = embedding_provider or get_embedding_provider()
        self.chunker = SemanticChunker()
        self.ingestion = DocumentIngestionEngine(self.chunker)
        self.vector_store = VectorStore()
        self.bm25_index = BM25Index()
        self.retriever = HybridRetriever(
            vector_store=self.vector_store,
            bm25_index=self.bm25_index,
            embedding_provider=self.embedding_provider
        )
        self.documents: Dict[str, Document] = {}
        self.chunks: Dict[str, DocumentChunk] = {}
        self._seed_canonical_benchmark_knowledge()

    def ingest_text_document(
        self,
        text: str,
        doc_id: str,
        title: str,
        source_type: str = "text",
        language: str = "en",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Document:
        doc, chunks = self.ingestion.ingest_text(
            text=text,
            doc_id=doc_id,
            title=title,
            source_type=source_type,
            language=language,
            metadata=metadata
        )

        with self._lock:
            # Check for exact duplicate content
            if doc_id in self.documents and self.documents[doc_id].content_hash == doc.content_hash:
                return self.documents[doc_id]

            # If document exists but content changed, increment version
            if doc_id in self.documents:
                doc.version = self.documents[doc_id].version + 1

            self.documents[doc_id] = doc

            # Generate vectors
            texts = [c.text for c in chunks]
            vectors = self.embedding_provider.embed_batch(texts)

            # Index into vector store and BM25
            for c, vec in zip(chunks, vectors):
                self.chunks[c.chunk_id] = c
                self.vector_store.add_chunk(c, vec)
                self.bm25_index.add_chunk(c)

        app_logger.log_operation(
            trace_id="system",
            operation="document_ingested",
            status="SUCCESS",
            agent_task="knowledge_base",
            details={
                "doc_id": doc_id,
                "title": title,
                "source_type": source_type,
                "chunks_indexed": len(chunks),
                "version": doc.version
            }
        )
        return doc

    def _seed_canonical_benchmark_knowledge(self) -> None:
        """
        Seeds canonical benchmark knowledge from AVATAROS specification:
        - product_benchmark.pdf (Inference Latency, Battery Endurance, NPU Architecture)
        - brand_guidelines.md (Tone & Phrasing)
        - titan_laptop_specs.pdf (Hardware architecture)
        """
        # 1. Product Benchmark Document
        benchmark_doc_text = """
# Titan AI Laptop Benchmarks 2026

## Inference Latency
Independent benchmarks conducted with MLPerf Dev Suite demonstrate 40% faster inference on local LLM code completion and debugging workloads compared to previous generation chips.
Developers observe sub-15ms time-to-first-token running 7B parameter models on silicon with zero cloud latency.

## Battery Endurance
Lab testing under continuous developer workflows (Docker, IDE, local test runner, WiFi active) confirms 18 hours of sustained battery life.
The optimized power profile maintains 100% compute performance even when unplugged on transatlantic developer flights.

## NPU Architecture
The integrated 45 TOPS Neural Processing Unit executes transformer-based code models locally with sub-15ms time-to-first-token, requiring zero cloud telemetry.
Hardware matrix multiplication units enable simultaneous local code indexing, syntax verification, and test generation without GPU throttling.
"""
        self.ingest_text_document(
            text=benchmark_doc_text,
            doc_id="product_benchmark.pdf",
            title="Titan AI Laptop Benchmarks 2026",
            source_type="pdf",
            language="en",
            metadata={"pages": 24, "type": "pdf_technical", "lab": "MLPerf Lab"}
        )

        # 2. Brand Guidelines Document
        brand_doc_text = """
# ExampleCo Engineering Brand Kit v9

## Tone & Phrasing
Speak engineer-to-engineer. Never use hyperbolic marketing adjectives like 'revolutionary' or 'unrivaled'.
Lead with reproducible benchmarks and verifiable engineering data.
Always cite independent lab verification and hardware specifications.
Never claim subjective or comparative superiority (such as '3x faster than all competitor machines') without verified comparative benchmark datasets.
"""
        self.ingest_text_document(
            text=brand_doc_text,
            doc_id="brand_guidelines.md",
            title="ExampleCo Engineering Brand Kit v9",
            source_type="markdown",
            language="en",
            metadata={"pages": 8, "type": "markdown"}
        )

        # 3. Hardware Specification Sheet
        specs_doc_text = """
# Titan AI Laptop Hardware Specifications

## Hardware Architecture
Titan AI Studio Laptop specs: Integrated 45 TOPS on-device NPU running transformer models directly on silicon.
Includes 32GB LPDDR5X unified memory with 18 hours of continuous build endurance.
MLPerf verified 40% faster inference on local developer completions.
"""
        self.ingest_text_document(
            text=specs_doc_text,
            doc_id="titan_laptop_specs.pdf",
            title="Titan AI Laptop Specifications",
            source_type="pdf",
            language="en",
            metadata={"pages": 12, "type": "spec_sheet"}
        )

    def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
        trace_id: str = "system"
    ) -> List[RetrievalResult]:
        return self.retriever.search(query=query, top_k=top_k, filters=filters, trace_id=trace_id)

    def list_documents(self) -> List[Dict[str, Any]]:
        with self._lock:
            docs = []
            for d in self.documents.values():
                chunk_count = sum(1 for c in self.chunks.values() if c.doc_id == d.doc_id)
                docs.append({
                    "doc_id": d.doc_id,
                    "title": d.title,
                    "source_type": d.source_type,
                    "content_hash": d.content_hash,
                    "language": d.language,
                    "version": d.version,
                    "chunks": chunk_count,
                    "created_at": d.created_at,
                    "metadata": d.metadata
                })
            return docs

# Global facade
knowledge_base = KnowledgeBase()
