from typing import Dict, List, Optional
from pydantic import BaseModel

class DocumentPassage(BaseModel):
    doc_id: str
    title: str
    section: str
    page: int
    text: str
    retrieval_score: float = 0.95

class ClaimVerification(BaseModel):
    claim_id: str
    claim_text: str
    status: str  # "verified", "partial", "unsupported"
    confidence: float
    supporting_docs: List[dict]
    reasoning: str
    is_blocked: bool

DOCUMENTS: Dict[str, List[DocumentPassage]] = {
    "product_benchmark.pdf": [
        DocumentPassage(
            doc_id="product_benchmark.pdf",
            title="Titan AI Laptop Benchmarks 2026",
            section="Inference Latency",
            page=12,
            text="Independent benchmarks conducted with MLPerf Dev Suite demonstrate 40% faster inference on local LLM code completion and debugging workloads compared to previous generation chips."
        ),
        DocumentPassage(
            doc_id="product_benchmark.pdf",
            title="Titan AI Laptop Benchmarks 2026",
            section="Battery Endurance",
            page=15,
            text="Lab testing under continuous developer workflows (Docker, IDE, local test runner, WiFi active) confirms 18 hours of sustained battery life."
        ),
        DocumentPassage(
            doc_id="product_benchmark.pdf",
            title="Titan AI Laptop Benchmarks 2026",
            section="NPU Architecture",
            page=19,
            text="The integrated 45 TOPS Neural Processing Unit executes transformer-based code models locally with sub-15ms time-to-first-token, requiring zero cloud telemetry."
        )
    ],
    "brand_guidelines.md": [
        DocumentPassage(
            doc_id="brand_guidelines.md",
            title="ExampleCo Engineering Brand Kit v9",
            section="Tone & Phrasing",
            page=1,
            text="Speak engineer-to-engineer. Never use hyperbolic marketing adjectives like 'revolutionary' or 'unrivaled'. Lead with reproducible benchmarks and verifiable engineering data."
        )
    ]
}

def get_seed_claims() -> Dict[str, ClaimVerification]:
    return {
        "claim_0231": ClaimVerification(
            claim_id="claim_0231",
            claim_text="40% faster inference for local code completion",
            status="verified",
            confidence=0.94,
            supporting_docs=[{"doc_id": "product_benchmark.pdf", "page": 12, "excerpt": "40% faster inference on local LLM code completion"}],
            reasoning="Directly supported by MLPerf benchmark data in product_benchmark.pdf page 12.",
            is_blocked=False
        ),
        "claim_0198": ClaimVerification(
            claim_id="claim_0198",
            claim_text="18 hours of battery life during intensive build cycles",
            status="verified",
            confidence=0.92,
            supporting_docs=[{"doc_id": "product_benchmark.pdf", "page": 15, "excerpt": "confirms 18 hours of sustained battery life"}],
            reasoning="Verified against continuous developer workload lab tests.",
            is_blocked=False
        ),
        "claim_0310": ClaimVerification(
            claim_id="claim_0310",
            claim_text="45 TOPS on-device NPU for instant code assistance",
            status="verified",
            confidence=0.95,
            supporting_docs=[{"doc_id": "product_benchmark.pdf", "page": 19, "excerpt": "integrated 45 TOPS Neural Processing Unit"}],
            reasoning="Verified against hardware specifications sheet.",
            is_blocked=False
        ),
        "claim_fail_3x": ClaimVerification(
            claim_id="claim_fail_3x",
            claim_text="This laptop is 3x faster than all competitor machines",
            status="unsupported",
            confidence=0.21,
            supporting_docs=[],
            reasoning="Research Agent found zero comparative data supporting '3x faster than all competitors'. Automatic block enforced (confidence 0.21 < threshold 0.60).",
            is_blocked=True
        )
    }

SEED_CLAIMS: Dict[str, ClaimVerification] = get_seed_claims()
