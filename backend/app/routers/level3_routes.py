import uuid
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.schemas import RagPipelineRequest, RagPipelineResponse, IngestDocResponse
from app.services.doc_processor import doc_processor
from app.services.vector_store import vector_store
from app.services.rag_pipeline import rag_pipeline

router = APIRouter(prefix="/level3", tags=["Level 3: Production RAG"])

@router.post("/upload-multi", response_model=List[IngestDocResponse])
async def upload_multiple_documents(files: List[UploadFile] = File(...)):
    results = []
    for file in files:
        filename = file.filename or f"doc_{uuid.uuid4().hex[:6]}.txt"
        content_bytes = await file.read()
        if not content_bytes:
            continue

        raw_text = doc_processor.extract_text_from_bytes(content_bytes, filename)
        if not raw_text.strip():
            continue

        doc_id = str(uuid.uuid4())[:8]
        chunks = doc_processor.create_chunks(raw_text, filename)
        vector_store.add_document(doc_id, filename, raw_text, chunks)

        results.append(
            IngestDocResponse(
                doc_id=doc_id,
                filename=filename,
                total_characters=len(raw_text),
                total_chunks=len(chunks),
                chunk_sample=chunks[:2],
                message=f"Indexed '{filename}' with {len(chunks)} chunks."
            )
        )

    if not results:
        raise HTTPException(status_code=400, detail="No readable documents could be processed.")
    return results

@router.post("/query-rag", response_model=RagPipelineResponse)
async def execute_rag_pipeline(req: RagPipelineRequest):
    if not req.query or len(req.query.strip()) < 2:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    
    return await rag_pipeline.execute(req)

@router.get("/documents")
async def get_indexed_documents():
    return {
        "documents": vector_store.list_documents(),
        "total_documents": len(vector_store.documents)
    }
