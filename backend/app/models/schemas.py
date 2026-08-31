from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# ==========================================
# Common & Health Models
# ==========================================
class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "1.0.0"
    model_provider: str
    active_model: str
    nvidia_key_configured: bool

class ApiKeyConfigRequest(BaseModel):
    api_key: str
    model_name: Optional[str] = "meta/llama-3.3-70b-instruct"

# ==========================================
# Level 1: Student Utility Models
# ==========================================
class SummarizeRequest(BaseModel):
    content: str = Field(..., min_length=10, description="Text notes or lecture content to summarize")
    style: str = Field("bullet_points", description="Style: 'bullet_points', 'executive', 'exam_cram', 'key_formulas'")
    target_audience: Optional[str] = "undergraduate"
    api_key: Optional[str] = None

class QuizQuestion(BaseModel):
    id: int
    question: str
    options: List[str]
    correct_option: int
    explanation: str

class Flashcard(BaseModel):
    term: str
    definition: str
    mnemonic: Optional[str] = None

class QuizGenerateRequest(BaseModel):
    content: str = Field(..., min_length=15, description="Source study material")
    num_questions: int = Field(4, ge=1, le=10)
    include_flashcards: bool = True
    difficulty: str = Field("medium", description="'easy', 'medium', 'hard'")
    api_key: Optional[str] = None

class QuizGenerateResponse(BaseModel):
    title: str
    questions: List[QuizQuestion]
    flashcards: List[Flashcard]
    summary_of_material: str
    raw_prompt_used: str
    processing_time_ms: float

class ConceptExplainRequest(BaseModel):
    concept: str = Field(..., min_length=2, description="Concept or topic name")
    depth_level: str = Field("feynman", description="'eli5', 'high_school', 'feynman', 'academic'")
    include_analogy: bool = True
    include_practice_question: bool = True
    api_key: Optional[str] = None

class AnswerImproveRequest(BaseModel):
    question: str = Field(..., min_length=5, description="The original test or exam question")
    student_draft: str = Field(..., min_length=5, description="Student's initial attempt or draft answer")
    rubric_focus: str = Field("rigor_and_clarity", description="'rigor_and_clarity', 'brevity', 'academic_depth'")
    api_key: Optional[str] = None

class StudentUtilityResponse(BaseModel):
    result: str
    structured_data: Optional[Dict[str, Any]] = None
    raw_prompt_used: str
    tokens_estimated: int
    processing_time_ms: float

# ==========================================
# Level 2: Document Q&A Models
# ==========================================
class DocumentChunk(BaseModel):
    chunk_id: int
    doc_name: str
    text: str
    score: float = 0.0
    start_char: int = 0
    end_char: int = 0

class IngestDocResponse(BaseModel):
    doc_id: str
    filename: str
    total_characters: int
    total_chunks: int
    chunk_sample: List[DocumentChunk]
    message: str

class DocQARequest(BaseModel):
    doc_id: str
    query: str = Field(..., min_length=3)
    top_k: int = Field(3, ge=1, le=8)
    strict_grounding: bool = True
    api_key: Optional[str] = None

class DocQAResponse(BaseModel):
    answer: str
    grounded: bool
    retrieved_chunks: List[DocumentChunk]
    confidence_score: float
    hallucination_warning: Optional[str] = None
    execution_time_ms: float

# ==========================================
# Level 3: Production RAG Models
# ==========================================
class RagPipelineRequest(BaseModel):
    query: str = Field(..., min_length=2)
    doc_ids: Optional[List[str]] = None
    top_k: int = Field(4, ge=1, le=10)
    enable_query_rewriting: bool = True
    enable_reranking: bool = True
    enable_guardrails: bool = True
    api_key: Optional[str] = None

class PipelineStepMetric(BaseModel):
    step_name: str
    latency_ms: float
    details: Dict[str, Any]

class RagPipelineResponse(BaseModel):
    query: str
    rewritten_query: Optional[str]
    answer: str
    citations: List[Dict[str, Any]]
    retrieved_chunks: List[DocumentChunk]
    reranked_chunks: List[DocumentChunk]
    faithfulness_score: float  # 0.0 to 1.0
    confidence_score: float    # 0.0 to 1.0
    execution_timeline: List[PipelineStepMetric]
    total_latency_ms: float
