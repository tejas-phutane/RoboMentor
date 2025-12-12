"""
AI Engine API endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..models import get_db_session
from ..core.ai_engine import GPTClient, ChatHandler, QuizGenerator

# Initialize components
gpt_client = GPTClient()
chat_handler = ChatHandler(gpt_client)
quiz_generator = QuizGenerator(gpt_client)

router = APIRouter(prefix="/api/chat", tags=["AI Engine"])

@router.post("/message")
def send_message(message: str, db: Session = Depends(get_db_session)):
    """Send text message to AI mentor."""
    response = chat_handler.send_message(message)
    return {"response": response}

@router.post("/voice")
def process_voice(audio_data: bytes, db: Session = Depends(get_db_session)):
    """Process voice input (STT)."""
    # Placeholder for voice processing
    text = "Transcribed text from audio"
    response = chat_handler.send_message(text)
    return {"transcribed_text": text, "response": response}

# Quiz endpoints
quiz_router = APIRouter(prefix="/api/quiz", tags=["Quiz"])

@quiz_router.post("/generate")
def generate_quiz(topic: str, difficulty: str = "intermediate", num_questions: int = 5, db: Session = Depends(get_db_session)):
    """Generate quiz from topic."""
    quiz = quiz_generator.generate_quiz(topic, difficulty, num_questions)
    return {"quiz": quiz}

@quiz_router.post("/submit")
def submit_quiz(quiz_data: dict, user_answers: dict, db: Session = Depends(get_db_session)):
    """Submit quiz answers."""
    results = []
    for i, answer in enumerate(user_answers.get("answers", [])):
        if i < len(quiz_data.get("questions", [])):
            question = quiz_data["questions"][i]
            result = quiz_generator.evaluate_answer(question, answer)
            results.append(result)
    return {"results": results}