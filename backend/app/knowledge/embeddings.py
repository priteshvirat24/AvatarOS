import math
import hashlib
import re
from abc import ABC, abstractmethod
from typing import List, Optional

from backend.app.config import settings
from backend.app.logging import app_logger

class BaseEmbeddingProvider(ABC):
    """
    Abstract embedding provider for semantic vector search.
    Enables swapping between offline deterministic development provider and Google Gemini embeddings.
    """
    @property
    @abstractmethod
    def dimension(self) -> int:
        pass

    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        pass

    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        pass


class DevelopmentDeterministicEmbeddingProvider(BaseEmbeddingProvider):
    """
    High-entropy, deterministic semantic vector provider for local development and offline testing.
    Uses n-gram semantic projection and L2 normalization to produce 256-dimensional unit vectors.
    Texts sharing key terms have high cosine similarity; unrelated texts have low similarity.
    Zero external network or ML dependency.
    """
    def __init__(self, dimension: int = 256):
        self._dim = dimension

    @property
    def dimension(self) -> int:
        return self._dim

    def _project_token(self, token: str, weight: float, vec: List[float]) -> None:
        # Generate 4 bucket indices per token for dimensional density
        h_bytes = hashlib.sha256(token.encode("utf-8")).digest()
        for i in range(4):
            idx = int.from_bytes(h_bytes[i*4 : i*4+2], byteorder="big") % self._dim
            sign = 1.0 if (h_bytes[i*4+2] % 2 == 0) else -1.0
            vec[idx] += sign * weight

    def embed_text(self, text: str) -> List[float]:
        if not text:
            return [0.0] * self._dim

        vec = [0.0] * self._dim
        clean = text.lower().strip()
        tokens = re.findall(r"\b\w+\b", clean)

        # Word-level projection
        for token in tokens:
            weight = 1.0 + min(len(token), 10) * 0.1
            self._project_token(token, weight, vec)

        # Character n-gram projection for subword/morphological similarity
        for i in range(len(clean) - 2):
            trigram = clean[i : i+3]
            self._project_token(trigram, 0.4, vec)

        # L2 normalize
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            return [round(x / norm, 6) for x in vec]
        return [0.0] * self._dim

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_text(t) for t in texts]


class GoogleGeminiEmbeddingProvider(BaseEmbeddingProvider):
    """
    Production embedding provider using Google Gemini text-embedding models.
    Requires GEMINI_API_KEY. Falls back gracefully to development provider if key is absent.
    """
    def __init__(self, fallback: Optional[BaseEmbeddingProvider] = None):
        self._dim = 768
        self.fallback = fallback or DevelopmentDeterministicEmbeddingProvider()

    @property
    def dimension(self) -> int:
        if settings.GEMINI_API_KEY:
            return self._dim
        return self.fallback.dimension

    def embed_text(self, text: str) -> List[float]:
        if not settings.GEMINI_API_KEY:
            return self.fallback.embed_text(text)

        try:
            import httpx
            api_key = settings.GEMINI_API_KEY.get_secret_value()
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.EMBEDDING_MODEL}:embedContent?key={api_key}"
            
            payload = {
                "model": f"models/{settings.EMBEDDING_MODEL}",
                "content": {"parts": [{"text": text}]}
            }
            with httpx.Client(timeout=4.0) as client:
                res = client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    values = data.get("embedding", {}).get("values", [])
                    if values:
                        return values

            app_logger.log_operation(
                trace_id="system",
                operation="gemini_embed",
                status="FALLBACK",
                agent_task="embeddings",
                details={"reason": f"Gemini API returned status {res.status_code}"}
            )
            return self.fallback.embed_text(text)
        except Exception as e:
            app_logger.log_operation(
                trace_id="system",
                operation="gemini_embed",
                status="FALLBACK",
                agent_task="embeddings",
                details={"error": str(e)}
            )
            return self.fallback.embed_text(text)

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_text(t) for t in texts]


def get_embedding_provider() -> BaseEmbeddingProvider:
    if settings.EMBEDDING_PROVIDER == "gemini" and settings.GEMINI_API_KEY:
        return GoogleGeminiEmbeddingProvider()
    return DevelopmentDeterministicEmbeddingProvider()
