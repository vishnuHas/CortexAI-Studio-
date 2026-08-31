from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    SummarizeRequest,
    QuizGenerateRequest,
    QuizGenerateResponse,
    ConceptExplainRequest,
    AnswerImproveRequest,
    StudentUtilityResponse
)
from app.services.student_utility import student_service

router = APIRouter(prefix="/level1", tags=["Level 1: Student Utility"])

@router.post("/summarize", response_model=StudentUtilityResponse)
async def summarize(req: SummarizeRequest):
    if not req.content or len(req.content.strip()) < 10:
        raise HTTPException(status_code=400, detail="Content must contain at least 10 characters.")
    return await student_service.summarize_notes(req)

@router.post("/generate-quiz", response_model=QuizGenerateResponse)
async def generate_quiz(req: QuizGenerateRequest):
    if not req.content or len(req.content.strip()) < 15:
        raise HTTPException(status_code=400, detail="Study material must contain at least 15 characters.")
    return await student_service.generate_quiz(req)

@router.post("/explain-concept", response_model=StudentUtilityResponse)
async def explain_concept(req: ConceptExplainRequest):
    if not req.concept or len(req.concept.strip()) < 2:
        raise HTTPException(status_code=400, detail="Concept name cannot be empty.")
    return await student_service.explain_concept(req)

@router.post("/improve-answer", response_model=StudentUtilityResponse)
async def improve_answer(req: AnswerImproveRequest):
    if not req.question.strip() or not req.student_draft.strip():
        raise HTTPException(status_code=400, detail="Question and student draft are both required.")
    return await student_service.improve_answer(req)
