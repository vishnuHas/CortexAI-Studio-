import uuid
import time
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from app.models.schemas import IngestDocResponse, DocQARequest, DocQAResponse
from app.services.doc_processor import doc_processor
from app.services.vector_store import vector_store
from app.services.nvidia_client import nvidia_client

router = APIRouter(prefix="/level2", tags=["Level 2: Document Q&A"])

@router.post("/upload", response_model=IngestDocResponse)
async def upload_document(file: UploadFile = File(...)):
    filename = file.filename or "uploaded_document.txt"
    content_bytes = await file.read()
    
    if not content_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    raw_text = doc_processor.extract_text_from_bytes(content_bytes, filename)
    if not raw_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract readable text from document.")

    doc_id = str(uuid.uuid4())[:8]
    chunks = doc_processor.create_chunks(raw_text, filename)
    vector_store.add_document(doc_id, filename, raw_text, chunks)

    return IngestDocResponse(
        doc_id=doc_id,
        filename=filename,
        total_characters=len(raw_text),
        total_chunks=len(chunks),
        chunk_sample=chunks[:3],
        message=f"Document '{filename}' successfully ingested and indexed into vector memory."
    )

@router.post("/query", response_model=DocQAResponse)
async def query_document(req: DocQARequest):
    start_time = time.time()
    doc_data = vector_store.get_document(req.doc_id)
    if not doc_data:
        raise HTTPException(status_code=404, detail="Document ID not found in vector memory.")

    # Retrieve matching chunks
    matched_chunks = vector_store.similarity_search(req.query, doc_id=req.doc_id, top_k=req.top_k)

    if not matched_chunks:
        return DocQAResponse(
            answer="No relevant content matching your question was found in this document.",
            grounded=False,
            retrieved_chunks=[],
            confidence_score=0.0,
            hallucination_warning="No matching chunks retrieved.",
            execution_time_ms=round((time.time() - start_time) * 1000, 2)
        )

    # Format grounded context
    context_blocks = [f"[Chunk {c.chunk_id}]: {c.text}" for c in matched_chunks]
    context_str = "\n\n".join(context_blocks)

    prompt = f"""You are a precise Document Q&A Assistant.
Answer the following question STRICTLY based on the provided document excerpts.
If the excerpts do not contain the answer, say "The provided document does not contain information to answer this question."

Document Excerpts:
\"\"\"
{context_str}
\"\"\"

Question: {req.query}

Answer:"""

    messages = [
        {"role": "system", "content": "You answer questions strictly using provided document context."},
        {"role": "user", "content": prompt}
    ]

    answer = await nvidia_client.generate_completion(messages, api_key=req.api_key)
    elapsed_ms = (time.time() - start_time) * 1000

    avg_score = sum(c.score for c in matched_chunks) / len(matched_chunks)

    return DocQAResponse(
        answer=answer,
        grounded=True,
        retrieved_chunks=matched_chunks,
        confidence_score=round(avg_score, 2),
        execution_time_ms=round(elapsed_ms, 2)
    )
