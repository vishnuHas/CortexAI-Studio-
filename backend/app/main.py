import os
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import settings
from app.models.schemas import HealthResponse, ApiKeyConfigRequest
from app.routers import level1_routes, level2_routes, level3_routes
from app.services.vector_store import vector_store
from app.services.doc_processor import doc_processor

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="CortexAI Multi-Tier Evaluation Platform"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register level routers
app.include_router(level1_routes.router, prefix=settings.API_PREFIX)
app.include_router(level2_routes.router, prefix=settings.API_PREFIX)
app.include_router(level3_routes.router, prefix=settings.API_PREFIX)

# System Health & Info
@app.get(f"{settings.API_PREFIX}/health", response_model=HealthResponse)
async def health_check():
    has_key = bool(settings.NVIDIA_API_KEY and settings.NVIDIA_API_KEY.strip())
    return HealthResponse(
        status="ok",
        version=settings.VERSION,
        model_provider="NVIDIA NIM (meta/llama-3.3-70b-instruct) with Intelligent Engine fallback",
        active_model=settings.DEFAULT_CHAT_MODEL,
        nvidia_key_configured=has_key
    )

@app.post(f"{settings.API_PREFIX}/config/api-key")
async def update_api_key(req: ApiKeyConfigRequest):
    settings.NVIDIA_API_KEY = req.api_key.strip()
    if req.model_name:
        settings.DEFAULT_CHAT_MODEL = req.model_name
    return {
        "status": "success",
        "message": "NVIDIA API key updated successfully.",
        "active_model": settings.DEFAULT_CHAT_MODEL
    }

# Pre-populate sample benchmark knowledge base for instant out-of-the-box testing
@app.on_event("startup")
async def preload_sample_kb():
    sample_doc_content = """--- AI ENGINEERING ARCHITECTURE HANDBOOK ---

SECTION 1: RETRIEVAL-AUGMENTED GENERATION (RAG) PARADIGMS
Retrieval-Augmented Generation (RAG) combines dense semantic retrieval mechanisms with high-capacity generative large language models. In a production setting, traditional vector lookups alone can suffer from semantic drift, vocabulary mismatch, and noisy context insertion.

To overcome this, modern RAG systems adopt a multi-stage agentic workflow:
1. Query Rewriting & Expansion: Transforming imprecise human prompts into high-density semantic search vectors.
2. Hierarchical Chunking: Dividing long-form documents into recursive chunks with sliding-window overlap (e.g. 400 characters with 50-character overlap) to prevent loss of boundary concepts.
3. Hybrid Similarity Ranking: Merging cosine similarity of high-dimensional embeddings with lexical BM25 keyword matching.
4. Cross-Encoder Reranking: Applying cross-attention scoring to select only the top-K highest-yield context excerpts.
5. Faithfulness Verification: Evaluating whether generated claims match source context before delivering the final response.

SECTION 2: PROMPT ENGINEERING & GUARDRAILS
Structured prompt engineering enforces consistent JSON outputs, prevents prompt injection, and constrains model generation strictly to retrieved context. Hallucination guardrails compute token overlap and semantic entailment ratios between source chunks and generated statements.

SECTION 3: PRODUCTION DEPLOYMENT & PERFORMANCE
Deploying AI workflows at scale requires containerization with Docker, asynchronous request queues in FastAPI, and typed validation schemas via Pydantic v2. Observability metrics such as step-by-step latency, token counts, and confidence scores ensure full operational transparency."""

    doc_id = "sample_arch_guide"
    chunks = doc_processor.create_chunks(sample_doc_content, "AI_Architecture_Handbook.pdf")
    vector_store.add_document(doc_id, "AI_Architecture_Handbook.pdf", sample_doc_content, chunks)
    print(f"[*] Preloaded sample knowledge base with {len(chunks)} chunks for instant demo testing.")

# Mount frontend static directory if present
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend"))
if os.path.exists(frontend_dir):
    js_dir = os.path.join(frontend_dir, "js")
    css_dir = os.path.join(frontend_dir, "css")
    if os.path.exists(js_dir):
        app.mount("/js", StaticFiles(directory=js_dir), name="js")
    if os.path.exists(css_dir):
        app.mount("/css", StaticFiles(directory=css_dir), name="css")
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/favicon.ico")
    async def favicon():
        return Response(status_code=204)

    @app.get("/")
    async def serve_index():
        return FileResponse(os.path.join(frontend_dir, "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
