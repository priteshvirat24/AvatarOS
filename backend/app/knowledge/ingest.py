import os
import hashlib
import re
from datetime import datetime, timezone
from typing import List, Tuple, Optional, Dict, Any

from backend.app.models.knowledge import Document, DocumentChunk
from backend.app.knowledge.chunker import SemanticChunker

class DocumentIngestionEngine:
    """
    Multimodal Document Ingestion Pipeline.
    Supports Plain Text, Markdown, and PDF formats with page/section preservation.
    """
    def __init__(self, chunker: Optional[SemanticChunker] = None):
        self.chunker = chunker or SemanticChunker()

    def compute_sha256(self, content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()

    def ingest_text(
        self,
        text: str,
        doc_id: str,
        title: str,
        source_type: str = "text",
        language: str = "en",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[Document, List[DocumentChunk]]:
        raw_bytes = text.strip().encode("utf-8")
        doc_hash = self.compute_sha256(raw_bytes)

        doc = Document(
            doc_id=doc_id,
            title=title,
            source_type=source_type,  # type: ignore
            content_hash=doc_hash,
            language=language,
            version=1,
            metadata=dict(metadata or {}),
            created_at=datetime.now(timezone.utc).isoformat()
        )

        chunks = self.chunker.chunk_text(
            text=text,
            doc_id=doc_id,
            page=1,
            default_section="Overview",
            language=language,
            metadata={"doc_title": title, **(metadata or {})}
        )

        return doc, chunks

    def ingest_markdown(
        self,
        content: str,
        doc_id: str,
        title: str,
        language: str = "en",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[Document, List[DocumentChunk]]:
        return self.ingest_text(
            text=content,
            doc_id=doc_id,
            title=title,
            source_type="markdown",
            language=language,
            metadata=metadata
        )

    def ingest_pdf_bytes(
        self,
        pdf_bytes: bytes,
        doc_id: str,
        title: str,
        language: str = "en",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[Document, List[DocumentChunk]]:
        from pypdf import PdfReader
        import io

        doc_hash = self.compute_sha256(pdf_bytes)
        reader = PdfReader(io.BytesIO(pdf_bytes))
        
        doc = Document(
            doc_id=doc_id,
            title=title,
            source_type="pdf",
            content_hash=doc_hash,
            language=language,
            version=1,
            metadata={"total_pages": len(reader.pages), **(metadata or {})},
            created_at=datetime.now(timezone.utc).isoformat()
        )

        all_chunks: List[DocumentChunk] = []
        chunk_counter = 0

        for page_idx, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            if not page_text.strip():
                continue

            page_num = page_idx + 1
            page_chunks = self.chunker.chunk_text(
                text=page_text,
                doc_id=doc_id,
                page=page_num,
                default_section=f"Page {page_num}",
                language=language,
                metadata={"doc_title": title, "page": page_num, **(metadata or {})}
            )
            for c in page_chunks:
                c.chunk_id = f"{doc_id}#c{chunk_counter:03d}"
                c.chunk_index = chunk_counter
                chunk_counter += 1
                all_chunks.append(c)

        return doc, all_chunks

    def ingest_file(
        self,
        file_path: str,
        doc_id: Optional[str] = None,
        title: Optional[str] = None,
        language: str = "en",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[Document, List[DocumentChunk]]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Document file not found: {file_path}")

        base_name = os.path.basename(file_path)
        actual_doc_id = doc_id or base_name
        actual_title = title or os.path.splitext(base_name)[0].replace("_", " ").title()

        with open(file_path, "rb") as f:
            content_bytes = f.read()

        if file_path.lower().endswith(".pdf"):
            return self.ingest_pdf_bytes(
                pdf_bytes=content_bytes,
                doc_id=actual_doc_id,
                title=actual_title,
                language=language,
                metadata=metadata
            )
        else:
            text = content_bytes.decode("utf-8", errors="replace")
            source_type = "markdown" if file_path.lower().endswith((".md", ".markdown")) else "text"
            return self.ingest_text(
                text=text,
                doc_id=actual_doc_id,
                title=actual_title,
                source_type=source_type,
                language=language,
                metadata=metadata
            )
