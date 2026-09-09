import pytest
import io
from pypdf import PdfWriter
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.config import settings
from backend.app.models.knowledge import Document, DocumentChunk, RetrievalQuery, Evidence
from backend.app.knowledge.chunker import SemanticChunker
from backend.app.knowledge.ingest import DocumentIngestionEngine
from backend.app.knowledge.embeddings import (
    DevelopmentDeterministicEmbeddingProvider,
    GoogleGeminiEmbeddingProvider
)
from backend.app.knowledge.vector_store import VectorStore
from backend.app.knowledge.bm25 import BM25Index
from backend.app.knowledge.hybrid_retriever import HybridRetriever
from backend.app.knowledge.knowledge_base import KnowledgeBase
from backend.app.agents.research import ResearchAgent
from backend.app.data.documents import ClaimVerification

client = TestClient(app)

# ---------------------------------------------------------------------------
# 1. DOCUMENT INGESTION & CHUNKING TESTS
# ---------------------------------------------------------------------------

def test_markdown_ingestion_and_chunking():
    engine = DocumentIngestionEngine()
    md_content = """# Titan Model Specifications
The Titan v2 inference engine delivers 4.2ms latency on 1080p frame generation.

## Memory Architecture
Memory consumption is capped at 1.8GB VRAM during real-time streaming mode.

## Power Profile
Operates efficiently on 45W TDP laptop profiles.
"""
    doc, chunks = engine.ingest_markdown(
        content=md_content,
        doc_id="doc_titan_md",
        title="Titan Specs",
        language="en"
    )

    assert doc.doc_id == "doc_titan_md"
    assert doc.title == "Titan Specs"
    assert doc.source_type == "markdown"
    assert doc.language == "en"
    assert len(doc.content_hash) == 64  # SHA-256 hex string
    assert len(chunks) >= 3

    # Verify chunk provenance and section headers
    sections = [c.section for c in chunks if c.section]
    assert any("Titan Model Specifications" in s for s in sections)
    assert any("Memory Architecture" in s for s in sections)
    for c in chunks:
        assert c.doc_id == doc.doc_id
        assert c.chunk_id.startswith("doc_titan_md#c")
        assert len(c.content_hash) == 64
        assert c.token_count > 0


def test_plain_text_ingestion():
    engine = DocumentIngestionEngine()
    text_content = """Titan Laptop Developer Manual
Paragraph 1: Setup the device using standard USB-C power delivery.

Paragraph 2: The neural engine is initialized automatically on boot.
"""
    doc, chunks = engine.ingest_text(
        text=text_content,
        doc_id="doc_dev_manual",
        title="Dev Manual",
        source_type="text",
        language="en"
    )

    assert doc.source_type == "text"
    assert len(chunks) >= 1
    assert all(c.doc_id == doc.doc_id for c in chunks)


def test_pdf_bytes_ingestion():
    engine = DocumentIngestionEngine()
    
    # Create valid in-memory PDF using pypdf
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    pdf_buffer = io.BytesIO()
    writer.write(pdf_buffer)
    pdf_bytes = pdf_buffer.getvalue()

    doc, chunks = engine.ingest_pdf_bytes(
        pdf_bytes=pdf_bytes,
        doc_id="test_pdf_doc",
        title="Test In-Memory PDF",
        language="en"
    )

    assert doc.doc_id == "test_pdf_doc"
    assert doc.source_type == "pdf"
    assert len(doc.content_hash) == 64
    assert doc.metadata.get("total_pages") == 1


def test_chunker_bounded_size_and_overlap():
    chunker = SemanticChunker(target_chunk_words=15, max_chunk_words=25, overlap_words=5)
    long_text = "This is a long sentence detailing continuous telemetry streams and neural execution parameters for digital human avatars in AVATAROS architecture. " * 3
    chunks = chunker.chunk_text(long_text, doc_id="doc_test_1")

    assert len(chunks) > 1
    for c in chunks:
        assert c.doc_id == "doc_test_1"
        assert c.token_count <= 40
        assert len(c.content_hash) == 64


# ---------------------------------------------------------------------------
# 2. EMBEDDINGS & VECTOR STORE TESTS
# ---------------------------------------------------------------------------

def test_deterministic_embedding_provider():
    provider = DevelopmentDeterministicEmbeddingProvider(dimension=256)
    
    vec1 = provider.embed_text("neural avatar real-time inference latency")
    vec2 = provider.embed_text("neural avatar real-time inference latency")
    vec3 = provider.embed_text("completely unrelated cooking recipe for chocolate cake")

    assert len(vec1) == 256
    # Exact deterministic repeatability
    assert vec1 == vec2

    # Unit norm check
    norm = sum(x * x for x in vec1) ** 0.5
    assert abs(norm - 1.0) < 1e-4

    # Semantic projection: identical terms share higher cosine similarity
    dot_related = sum(a * b for a, b in zip(vec1, vec2))
    dot_unrelated = sum(a * b for a, b in zip(vec1, vec3))
    assert dot_related > dot_unrelated


def test_gemini_embedding_fallback():
    # When no API key is provided, should cleanly fall back to deterministic without throwing
    provider = GoogleGeminiEmbeddingProvider()
    vec = provider.embed_text("test fallback embedding")
    assert len(vec) == 256
    assert isinstance(vec, list)


def test_vector_store_similarity_search():
    provider = DevelopmentDeterministicEmbeddingProvider(dimension=256)
    vstore = VectorStore()

    chunk_a = DocumentChunk(
        chunk_id="chk_a",
        doc_id="doc_1",
        chunk_index=0,
        text="The inference engine maintains 4.2ms frame generation latency.",
        token_count=10,
        content_hash="hash_a"
    )
    chunk_b = DocumentChunk(
        chunk_id="chk_b",
        doc_id="doc_2",
        chunk_index=0,
        text="Chocolate chip cookies require 200 degrees Celsius baking temperature.",
        token_count=10,
        content_hash="hash_b"
    )

    vstore.add_chunk(chunk_a, provider.embed_text(chunk_a.text))
    vstore.add_chunk(chunk_b, provider.embed_text(chunk_b.text))

    query_vec = provider.embed_text("inference engine latency in milliseconds")
    results = vstore.search(query_vec, top_k=2)

    assert len(results) == 2
    # chunk_a must rank first
    top_chunk, top_score = results[0]
    assert top_chunk.chunk_id == "chk_a"
    assert top_score > results[1][1]


# ---------------------------------------------------------------------------
# 3. BM25 & LEXICAL RETRIEVAL TESTS
# ---------------------------------------------------------------------------

def test_bm25_lexical_ranking():
    bm25 = BM25Index()

    chunks = [
        DocumentChunk(
            chunk_id="bm25_1",
            doc_id="doc_bm25",
            chunk_index=0,
            text="MLPerf v4.1 benchmarks confirm 4.2ms latency on 1080p stream generation.",
            token_count=12,
            content_hash="h1"
        ),
        DocumentChunk(
            chunk_id="bm25_2",
            doc_id="doc_bm25",
            chunk_index=1,
            text="The thermal management system features dual vapor chambers.",
            token_count=10,
            content_hash="h2"
        ),
        DocumentChunk(
            chunk_id="bm25_3",
            doc_id="doc_bm25",
            chunk_index=2,
            text="Digital DNA contains biometric traits, vocal frequencies, and emotional ranges.",
            token_count=12,
            content_hash="h3"
        )
    ]

    for c in chunks:
        bm25.add_chunk(c)

    results = bm25.search("MLPerf 4.2ms latency", top_k=3)
    assert len(results) > 0
    top_chunk, score = results[0]
    assert top_chunk.chunk_id == "bm25_1"
    assert score > 0.0


# ---------------------------------------------------------------------------
# 4. HYBRID RETRIEVAL & DEDUPLICATION TESTS
# ---------------------------------------------------------------------------

def test_hybrid_retrieval_fusion_and_dedup():
    kb = KnowledgeBase()
    # KnowledgeBase seeds canonical documents (titan benchmark, brand guidelines, laptop specs)
    results = kb.search("Titan 4.2ms latency MLPerf", top_k=3)

    assert len(results) > 0
    # Must have both scores fused
    for res in results:
        assert res.hybrid_score >= 0.0
        assert res.chunk.doc_id is not None
        assert res.chunk.chunk_id is not None
        assert len(res.retrieval_methods) >= 1
        assert len(res.chunk.content_hash) == 64

    # Top result should be the benchmark chunk
    top = results[0]
    assert "inference" in top.chunk.text.lower() or "latency" in top.chunk.text.lower() or "benchmark" in top.chunk.text.lower()


# ---------------------------------------------------------------------------
# 5. RESEARCH AGENT & CLAIM VERIFICATION TESTS (AVATAROS WILL NOT GUESS)
# ---------------------------------------------------------------------------

def test_research_agent_analyze_documents():
    agent = ResearchAgent()
    analysis = agent.analyze_documents("Titan 40% faster inference")
    assert analysis["documents_analyzed"] >= 3
    assert len(analysis["sources"]) >= 3
    assert len(analysis["top_passages"]) > 0


def test_research_agent_supported_claim_verification():
    agent = ResearchAgent()
    claim = agent.verify_claim(claim_text="40% faster inference for local code completion")

    assert claim.status == "verified"
    assert claim.confidence >= 0.60
    assert claim.is_blocked is False
    assert len(claim.supporting_docs) > 0
    top_doc = claim.supporting_docs[0]
    assert top_doc["doc_id"] == "product_benchmark.pdf"


def test_research_agent_unsupported_claim_blocked_safety_invariant():
    """
    CRITICAL SAFETY INVARIANT TEST:
    A high retrieval score on related passages MUST NOT automatically verify
    an unsubstantiated comparative assertion ("3x faster than all competitor machines").
    Claim confidence must remain low (<0.60) and status must be BLOCKED.
    """
    agent = ResearchAgent()
    claim = agent.verify_claim(claim_text="This laptop is 3x faster than all competitor machines")

    assert claim.status == "unsupported"
    assert claim.confidence < 0.60
    assert claim.is_blocked is True
    assert "automatic block enforced" in claim.reasoning.lower() or "confidence 0.21" in claim.reasoning.lower()


def test_research_agent_claim_resolution():
    agent = ResearchAgent()
    # Resolve the blocked 3x claim by ingesting the MLPerf comparative benchmark document
    res = agent.resolve_blocked_claim(
        claim_id="claim_fail_3x",
        uploaded_evidence_name="titan_benchmarks_mlperf_v2.pdf"
    )

    assert res.status == "verified"
    assert res.is_blocked is False

    # Confidence is the hybrid retrieval score of the supporting passage, not a
    # stored constant. It must clear the same threshold every other claim is held
    # to, and it must equal the score recorded on the supporting document.
    from backend.app.config import settings as _settings

    supporting = [d for d in res.supporting_docs if d["doc_id"] == "titan_benchmarks_mlperf_v2.pdf"]
    assert supporting, "the uploaded evidence must be cited as the supporting document"

    evidence = supporting[-1]
    assert res.confidence >= _settings.CLAIM_CONFIDENCE_THRESHOLD
    assert res.confidence == evidence["retrieval_score"]
    assert 0.0 < evidence["retrieval_score"] <= 1.0
    assert evidence["semantic_score"] > 0
    assert evidence["excerpt"], "the cited passage must carry the text it was matched on"
    # The chunk id must belong to the uploaded document, not be synthesised.
    assert evidence["chunk_id"].startswith("titan_benchmarks_mlperf_v2.pdf")


def test_claim_stays_blocked_when_evidence_does_not_support_it():
    """
    Uploading a document is not the same as supporting a claim.

    Evidence that retrieval cannot connect to the claim must leave it blocked -
    otherwise "attach a PDF" becomes a way to launder any assertion past the gate.
    """
    agent = ResearchAgent()
    agent.claims["claim_unsupported_demo"] = ClaimVerification(
        claim_id="claim_unsupported_demo",
        claim_text="This laptop cures seasonal allergies and improves eyesight",
        status="blocked",
        confidence=0.0,
        is_blocked=True,
        supporting_docs=[],
        reasoning="Seeded for this test with no supporting evidence.",
    )

    res = agent.resolve_blocked_claim(
        claim_id="claim_unsupported_demo",
        uploaded_evidence_name="irrelevant_evidence.pdf",
    )

    assert res.is_blocked is True
    assert res.status == "blocked"
    assert res.confidence == 0.0
    assert "no passage supporting this claim" in res.reasoning


# ---------------------------------------------------------------------------
# 6. KNOWLEDGE INSPECTION API ENDPOINTS
# ---------------------------------------------------------------------------

def test_api_knowledge_documents():
    response = client.get("/api/knowledge/documents")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "total_documents" in data
    assert "total_chunks" in data
    assert "documents" in data
    assert data["total_documents"] >= 3
    assert data["total_chunks"] >= 3


def test_api_knowledge_search():
    response = client.get("/api/knowledge/search?query=4.2ms%20latency&top_k=3")
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "4.2ms latency"
    assert "results" in data
    assert len(data["results"]) > 0

    first = data["results"][0]
    assert "hybrid_score" in first
    assert "retrieval_methods" in first
    assert "document_title" in first
    assert "chunk_text" in first
    assert "chunk_checksum" in first
