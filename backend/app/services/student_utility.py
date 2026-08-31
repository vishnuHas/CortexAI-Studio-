import time
import json
from typing import Dict, Any, List
from app.services.nvidia_client import nvidia_client
from app.models.schemas import (
    SummarizeRequest,
    QuizGenerateRequest,
    QuizGenerateResponse,
    QuizQuestion,
    Flashcard,
    ConceptExplainRequest,
    AnswerImproveRequest,
    StudentUtilityResponse
)

class StudentUtilityService:

    async def summarize_notes(self, request: SummarizeRequest) -> StudentUtilityResponse:
        start_time = time.time()
        
        style_instructions = {
            "bullet_points": "Format the output as clear, structured bullet points with high-yield key takeaways and bolded terms.",
            "executive": "Format as an executive overview with Problem, Key Findings, Strategic Takeaways, and Recommendations.",
            "exam_cram": "Format as an ultra-condensed exam cram sheet with mnemonics, critical formulas, and high-frequency exam points.",
            "key_formulas": "Extract all definitions, key terms, equations, and algorithmic steps into a reference glossary."
        }.get(request.style, "Format as structured bullet points.")

        prompt = f"""You are an elite academic tutor and learning specialist.
Task: Summarize the following lecture notes/study text for a {request.target_audience} student.

Style Guidance:
{style_instructions}

Source Text:
\"\"\"
{request.content}
\"\"\"

Requirements:
- Preserve factual accuracy.
- Highlight core definitions and cause-and-effect relationships.
- Use clear markdown headings and callouts."""

        messages = [
            {"role": "system", "content": "You are a master academic study assistant that outputs clear, pedagogical markdown summaries."},
            {"role": "user", "content": prompt}
        ]

        result = await nvidia_client.generate_completion(messages, api_key=request.api_key)
        elapsed_ms = (time.time() - start_time) * 1000

        return StudentUtilityResponse(
            result=result,
            raw_prompt_used=prompt,
            tokens_estimated=int(len(prompt.split()) * 1.3),
            processing_time_ms=round(elapsed_ms, 2)
        )

    async def generate_quiz(self, request: QuizGenerateRequest) -> QuizGenerateResponse:
        start_time = time.time()

        prompt = f"""You are an expert exam creator. Analyze the provided study material and generate a high-yield study assessment.

Difficulty: {request.difficulty}
Number of Multiple Choice Questions: {request.num_questions}
Include Flashcards: {request.include_flashcards}

Source Material:
\"\"\"
{request.content}
\"\"\"

CRITICAL: Return ONLY a valid, parseable JSON object with this exact structure:
{{
  "title": "Topic or Subject Title",
  "summary_of_material": "2-sentence high-level overview",
  "questions": [
    {{
      "id": 1,
      "question": "Question text here?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_option": 0,
      "explanation": "Detailed explanation of why this option is correct."
    }}
  ],
  "flashcards": [
    {{
      "term": "Key Concept Name",
      "definition": "Clear, concise definition",
      "mnemonic": "Helpful memory cue or mnemonic"
    }}
  ]
}}"""

        messages = [
            {"role": "system", "content": "You are a JSON-only assessment generation engine. You always output valid JSON without preamble or code blocks."},
            {"role": "user", "content": prompt}
        ]

        raw_output = await nvidia_client.generate_completion(messages, api_key=request.api_key)
        
        # Parse JSON
        parsed_data = None
        try:
            # Clean possible markdown ticks
            cleaned_json = raw_output.strip()
            if cleaned_json.startswith("```json"):
                cleaned_json = cleaned_json[7:]
            if cleaned_json.startswith("```"):
                cleaned_json = cleaned_json[3:]
            if cleaned_json.endswith("```"):
                cleaned_json = cleaned_json[:-3]
            parsed_data = json.loads(cleaned_json.strip())
        except Exception:
            # Fallback parsing
            parsed_data = {
                "title": "Study Assessment",
                "summary_of_material": "Key conceptual review generated from study notes.",
                "questions": [
                    {
                        "id": 1,
                        "question": "What is the primary concept discussed in the text?",
                        "options": ["Core foundational principles", "Unrelated topics", "Syntax error handling", "Peripheral metadata"],
                        "correct_option": 0,
                        "explanation": "The text directly focuses on establishing foundational understanding."
                    }
                ],
                "flashcards": [
                    {
                        "term": "Foundational Concept",
                        "definition": "The primary building block of the subject matter.",
                        "mnemonic": "Base first"
                    }
                ]
            }

        elapsed_ms = (time.time() - start_time) * 1000

        return QuizGenerateResponse(
            title=parsed_data.get("title", "Study Assessment"),
            questions=[QuizQuestion(**q) for q in parsed_data.get("questions", [])],
            flashcards=[Flashcard(**f) for f in parsed_data.get("flashcards", [])],
            summary_of_material=parsed_data.get("summary_of_material", ""),
            raw_prompt_used=prompt,
            processing_time_ms=round(elapsed_ms, 2)
        )

    async def explain_concept(self, request: ConceptExplainRequest) -> StudentUtilityResponse:
        start_time = time.time()

        depth_instructions = {
            "eli5": "Explain Like I'm 5: Use simple, delightful everyday metaphors and zero jargon.",
            "high_school": "High School Level: Clear, engaging explanation with real-world examples and basic technical terms.",
            "feynman": "The Feynman Technique: Break down complex mechanisms intuitively, eliminate false assumptions, and verify understanding.",
            "academic": "Rigorous Academic Level: Formal definitions, mathematical or architectural formulation, edge cases, and theoretical foundations."
        }.get(request.depth_level, "Feynman technique explanation.")

        prompt = f"""Explain the following concept: "{request.concept}"

Approach:
{depth_instructions}

Include Analogy: {request.include_analogy}
Include Practice Check Question: {request.include_practice_question}

Structure your response with:
1. 💡 Core Intuition / Hook
2. 🔬 Step-by-Step Breakdown
3. 🌐 Real-World Analogy
4. ⚠️ Common Misconceptions to Avoid
5. 🎯 Self-Assessment Question & Answer"""

        messages = [
            {"role": "system", "content": "You are a world-class educator who explains complex technical concepts with unparalleled clarity."},
            {"role": "user", "content": prompt}
        ]

        result = await nvidia_client.generate_completion(messages, api_key=request.api_key)
        elapsed_ms = (time.time() - start_time) * 1000

        return StudentUtilityResponse(
            result=result,
            raw_prompt_used=prompt,
            tokens_estimated=int(len(prompt.split()) * 1.3),
            processing_time_ms=round(elapsed_ms, 2)
        )

    async def improve_answer(self, request: AnswerImproveRequest) -> StudentUtilityResponse:
        start_time = time.time()

        prompt = f"""You are a senior academic grading evaluator and coach.

Original Question:
\"{request.question}\"

Student's Draft Answer:
\"{request.student_draft}\"

Evaluation Focus: {request.rubric_focus}

Please provide:
1. 🌟 **Enhanced Version**: A high-scoring, rigorous model answer that preserves the student's authentic voice.
2. 📊 **Score & Diagnostic Feedback**:
   - Accuracy (1-10)
   - Structure & Clarity (1-10)
   - Technical Depth (1-10)
3. 🔍 **What Was Missing / Weak**: Key missed points or ambiguous statements.
4. 💡 **Actionable Advice**: How to tackle similar exam questions effectively."""

        messages = [
            {"role": "system", "content": "You are an encouraging but rigorous academic evaluator."},
            {"role": "user", "content": prompt}
        ]

        result = await nvidia_client.generate_completion(messages, api_key=request.api_key)
        elapsed_ms = (time.time() - start_time) * 1000

        return StudentUtilityResponse(
            result=result,
            raw_prompt_used=prompt,
            tokens_estimated=int(len(prompt.split()) * 1.3),
            processing_time_ms=round(elapsed_ms, 2)
        )

student_service = StudentUtilityService()
