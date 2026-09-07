import math
import re
import threading
from typing import List, Dict, Tuple, Set, Optional
from backend.app.models.knowledge import DocumentChunk

STOPWORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "can't", "cannot", "could",
    "did", "do", "does", "doing", "down", "during", "each", "few", "for", "from",
    "further", "had", "has", "have", "having", "he", "her", "here", "hers", "herself",
    "him", "himself", "his", "how", "i", "if", "in", "into", "is", "it", "its",
    "itself", "me", "more", "most", "my", "myself", "no", "nor", "not", "of", "off",
    "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out",
    "over", "own", "same", "she", "should", "so", "some", "such", "than", "that",
    "the", "their", "theirs", "them", "themselves", "then", "there", "these", "they",
    "this", "those", "through", "to", "too", "under", "until", "up", "very", "was",
    "we", "were", "what", "when", "where", "which", "while", "who", "whom", "why",
    "with", "would", "you", "your", "yours", "yourself", "yourselves"
}

class BM25Index:
    """
    Genuine Okapi BM25 Lexical Ranking Engine.
    Computes exact IDF and length-normalized term frequencies over indexed document chunks.
    """
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self._lock = threading.Lock()
        self._chunks: Dict[str, DocumentChunk] = {}
        self._doc_lens: Dict[str, int] = {}
        self._avg_doc_len: float = 0.0
        self._inverted_index: Dict[str, Dict[str, int]] = {}  # term -> {chunk_id: tf}
        self._doc_freqs: Dict[str, int] = {}  # term -> df

    def tokenize(self, text: str) -> List[str]:
        tokens = re.findall(r"\b\w+\b", text.lower())
        return [t for t in tokens if t not in STOPWORDS and len(t) > 1]

    def add_chunk(self, chunk: DocumentChunk) -> None:
        with self._lock:
            tokens = self.tokenize(chunk.text)
            chunk_id = chunk.chunk_id
            self._chunks[chunk_id] = chunk
            self._doc_lens[chunk_id] = len(tokens)

            # Compute term frequencies for this chunk
            tf_map: Dict[str, int] = {}
            for t in tokens:
                tf_map[t] = tf_map.get(t, 0) + 1

            for term, tf in tf_map.items():
                if term not in self._inverted_index:
                    self._inverted_index[term] = {}
                    self._doc_freqs[term] = 0
                if chunk_id not in self._inverted_index[term]:
                    self._doc_freqs[term] += 1
                self._inverted_index[term][chunk_id] = tf

            # Recalculate average document length
            total_tokens = sum(self._doc_lens.values())
            self._avg_doc_len = total_tokens / len(self._doc_lens) if self._doc_lens else 0.0

    def add_chunks(self, chunks: List[DocumentChunk]) -> None:
        for c in chunks:
            self.add_chunk(c)

    def search(self, query: str, top_k: int = 5) -> List[Tuple[DocumentChunk, float]]:
        with self._lock:
            q_tokens = self.tokenize(query)
            if not q_tokens or not self._chunks:
                return []

            N = len(self._chunks)
            scores: Dict[str, float] = {}

            for term in q_tokens:
                if term not in self._inverted_index:
                    continue

                df = self._doc_freqs.get(term, 0)
                # Okapi BM25 standard IDF with smoothing
                idf = math.log(1.0 + (N - df + 0.5) / (df + 0.5))

                for chunk_id, tf in self._inverted_index[term].items():
                    doc_len = self._doc_lens.get(chunk_id, 1)
                    denom = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / self._avg_doc_len))
                    term_score = idf * (tf * (self.k1 + 1.0)) / denom if denom > 0 else 0.0
                    scores[chunk_id] = scores.get(chunk_id, 0.0) + term_score

            if not scores:
                return []

            # Softmax or ratio normalization into [0.0, 1.0]
            max_score = max(scores.values())
            normalized_results: List[Tuple[DocumentChunk, float]] = []

            for chunk_id, raw_score in scores.items():
                norm_score = raw_score / (raw_score + 1.0) if max_score > 0 else 0.0
                norm_score = min(1.0, max(0.0, norm_score))
                normalized_results.append((self._chunks[chunk_id], round(norm_score, 4)))

            normalized_results.sort(key=lambda x: x[1], reverse=True)
            return normalized_results[:top_k]
