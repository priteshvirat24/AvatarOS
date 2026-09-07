import hashlib
import re
from typing import List, Optional, Dict, Any
from backend.app.models.knowledge import DocumentChunk

class SemanticChunker:
    """
    Structure-aware document chunker.
    Respects Markdown headings, paragraph boundaries, and page numbers.
    Maintains cryptographic SHA-256 provenance for each chunk.
    """
    def __init__(self, target_chunk_words: int = 150, max_chunk_words: int = 250, overlap_words: int = 20):
        self.target_chunk_words = target_chunk_words
        self.max_chunk_words = max_chunk_words
        self.overlap_words = overlap_words

    def compute_sha256(self, text: str) -> str:
        return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()

    def chunk_text(
        self,
        text: str,
        doc_id: str,
        page: Optional[int] = None,
        default_section: Optional[str] = None,
        language: str = "en",
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[DocumentChunk]:
        chunks: List[DocumentChunk] = []
        if not text or not text.strip():
            return chunks

        # Split into blocks by double newlines or markdown headings
        raw_lines = text.split("\n")
        current_section = default_section or "Introduction"
        current_block: List[str] = []
        blocks: List[Dict[str, Any]] = []

        for line in raw_lines:
            stripped = line.strip()
            # Check for Markdown heading
            heading_match = re.match(r"^(#{1,6})\s+(.*)$", stripped)
            if heading_match:
                if current_block:
                    block_text = "\n".join(current_block).strip()
                    if block_text:
                        blocks.append({"section": current_section, "text": block_text})
                    current_block = []
                current_section = heading_match.group(2).strip()
            elif not stripped and current_block:
                block_text = "\n".join(current_block).strip()
                if block_text:
                    blocks.append({"section": current_section, "text": block_text})
                current_block = []
            else:
                if stripped:
                    current_block.append(line)

        if current_block:
            block_text = "\n".join(current_block).strip()
            if block_text:
                blocks.append({"section": current_section, "text": block_text})

        # Assemble blocks into bounded chunks with section awareness and small overlap
        chunk_idx = 0
        current_words: List[str] = []
        chunk_section = default_section or "Overview"

        for b in blocks:
            b_words = b["text"].split()
            if not b_words:
                continue

            # If section changed and we already have words for previous section, emit chunk
            if current_words and b["section"] != chunk_section:
                chunk_str = " ".join(current_words)
                c_hash = self.compute_sha256(chunk_str)
                chunks.append(DocumentChunk(
                    chunk_id=f"{doc_id}#c{chunk_idx:03d}",
                    doc_id=doc_id,
                    chunk_index=chunk_idx,
                    text=chunk_str,
                    content_hash=c_hash,
                    section=chunk_section,
                    page=page,
                    language=language,
                    token_count=len(current_words),
                    metadata=dict(metadata or {})
                ))
                chunk_idx += 1
                current_words = []

            chunk_section = b["section"]

            # If block itself exceeds max_chunk_words, break it down
            if len(b_words) > self.max_chunk_words:
                start = 0
                while start < len(b_words):
                    slice_words = b_words[start : start + self.max_chunk_words]
                    chunk_str = " ".join(slice_words)
                    c_hash = self.compute_sha256(chunk_str)
                    chunks.append(DocumentChunk(
                        chunk_id=f"{doc_id}#c{chunk_idx:03d}",
                        doc_id=doc_id,
                        chunk_index=chunk_idx,
                        text=chunk_str,
                        content_hash=c_hash,
                        section=chunk_section,
                        page=page,
                        language=language,
                        token_count=len(slice_words),
                        metadata=dict(metadata or {})
                    ))
                    chunk_idx += 1
                    start += (self.max_chunk_words - self.overlap_words) if self.max_chunk_words > self.overlap_words else self.max_chunk_words
                continue

            if len(current_words) + len(b_words) <= self.max_chunk_words:
                current_words.extend(b_words)
            else:
                if current_words:
                    chunk_str = " ".join(current_words)
                    c_hash = self.compute_sha256(chunk_str)
                    chunks.append(DocumentChunk(
                        chunk_id=f"{doc_id}#c{chunk_idx:03d}",
                        doc_id=doc_id,
                        chunk_index=chunk_idx,
                        text=chunk_str,
                        content_hash=c_hash,
                        section=chunk_section,
                        page=page,
                        language=language,
                        token_count=len(current_words),
                        metadata=dict(metadata or {})
                    ))
                    chunk_idx += 1
                    current_words = current_words[-self.overlap_words:] if len(current_words) >= self.overlap_words else []

                current_words.extend(b_words)

        if current_words:
            chunk_str = " ".join(current_words)
            c_hash = self.compute_sha256(chunk_str)
            chunks.append(DocumentChunk(
                chunk_id=f"{doc_id}#c{chunk_idx:03d}",
                doc_id=doc_id,
                chunk_index=chunk_idx,
                text=chunk_str,
                content_hash=c_hash,
                section=chunk_section,
                page=page,
                language=language,
                token_count=len(current_words),
                metadata=dict(metadata or {})
            ))

        return chunks
