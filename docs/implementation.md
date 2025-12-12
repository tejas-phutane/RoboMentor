# Implementation Guide

This guide provides detailed implementation instructions for building RoboMentor, including code examples, API specifications, and integration steps.

## Project Structure

```
robomentor/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── requirements.txt        # Python dependencies
│   ├── config.py              # Configuration management
│   ├── models/                # SQLAlchemy models
│   │   ├── skill.py
│   │   ├── session.py
│   │   ├── concept.py
│   │   ├── quiz.py
│   │   └── onboarding.py
│   ├── services/              # Business logic
│   │   ├── gpt_engine.py
│   │   ├── voice_module.py
│   │   ├── obsidian_sync.py
│   │   └── roadmap_generator.py
│   ├── api/                   # API endpoints
│   │   ├── chat.py
│   │   ├── skills.py
│   │   ├── quiz.py
│   │   ├── onboarding.py
│   │   └── metrics.py
│   └── db/
│       ├── database.py
│       └── schema.sql
├── electron-app/
│   ├── src/
│   │   ├── main.js            # Electron main process
│   │   ├── preload.js         # IPC bridge
│   │   ├── index.html
│   │   ├── styles/
│   │   │   └── main.css
│   │   └── renderer/
│   │       ├── dashboard.js
│   │       ├── chat.js
│   │       └── onboarding.js
│   ├── package.json
│   └── dist/
├── .env.example               # Environment variables
└── README.md
```

## Backend Setup (FastAPI + SQLAlchemy)

### 1. FastAPI Application

**backend/main.py**
```python
from fastapi import FastAPI, WebSocket
from fastapi.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn
import logging
from dotenv import load_dotenv
import os

from db.database import init_db, get_db
from api import chat, skills, quiz, metrics, goals, onboarding
from services.obsidian_sync import start_vault_watcher

load_dotenv()

app = FastAPI(
    title="RoboMentor Backend",
    description="AI-powered learning system for roboticists",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["localhost:3000", "127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup():
    """Initialize database and start background tasks"""
    init_db()
    logger.info("Database initialized")

    # Start Obsidian vault watcher
    vault_path = os.getenv("OBSIDIAN_VAULT_PATH")
    if vault_path:
        start_vault_watcher(vault_path)
        logger.info("Obsidian vault watcher started")

# API routes
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(skills.router, prefix="/api/skills", tags=["skills"])
app.include_router(quiz.router, prefix="/api/quiz", tags=["quiz"])
app.include_router(metrics.router, prefix="/api/metrics", tags=["metrics"])
app.include_router(goals.router, prefix="/api/goals", tags=["goals"])
app.include_router(onboarding.router, prefix="/api/onboarding", tags=["onboarding"])

@app.get("/")
async def root():
    return {"message": "RoboMentor Backend is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    port = int(os.getenv("BACKEND_PORT", 8000))
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=port,
        log_level="info"
    )
```

### 2. Database Configuration

**backend/db/database.py**
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./robomentor.db"
)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    """Initialize database - create all tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency for getting DB session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 3. Core Models

**backend/models/skill.py**
```python
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base
import uuid
from enum import Enum as PyEnum

class SkillDomain(str, PyEnum):
    COMPUTER_VISION = "Computer Vision"
    ROBOTICS = "Robotics"
    RL_CONTROL = "RL for Control"
    CONTROL_SYSTEMS = "Control Systems"
    SIM2REAL = "Sim2Real Transfer"
    IOT = "IoT & Edge AI"

class Skill(Base):
    __tablename__ = "skills"

    skill_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, unique=True)
    domain = Column(String, nullable=True)
    parent_skill_id = Column(String, ForeignKey("skills.skill_id"), nullable=True)
    proficiency_level = Column(Float, default=0.0)  # 0-100
    last_assessed = Column(DateTime, nullable=True)
    assessment_method = Column(String, nullable=True)
    created_date = Column(DateTime, server_default=func.now())

    parent_skill = relationship("Skill", remote_side=[skill_id])

    def to_dict(self):
        return {
            "skill_id": self.skill_id,
            "name": self.name,
            "domain": self.domain,
            "proficiency_level": self.proficiency_level,
            "last_assessed": self.last_assessed.isoformat() if self.last_assessed else None
        }
```

**backend/models/session.py**
```python
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Enum
from sqlalchemy.sql import func
from db.database import Base
import uuid
from enum import Enum as PyEnum

class SessionType(str, PyEnum):
    READING = "Reading"
    TUTORIAL = "Tutorial"
    PROJECT = "Project"
    QUIZ = "Quiz"
    HANDS_ON_LAB = "Hands-On Lab"
    REFLECTION = "Reflection"

class SessionIntensity(str, PyEnum):
    LIGHT = "Light"
    MEDIUM = "Medium"
    DEEP = "Deep"

class LearningSession(Base):
    __tablename__ = "learning_sessions"

    session_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    date = Column(DateTime, nullable=False, server_default=func.now())
    duration_minutes = Column(Integer, nullable=False)
    session_type = Column(String, nullable=False)
    intensity = Column(String, nullable=True)
    engagement_score = Column(Integer, nullable=True)
    reflection = Column(Text, nullable=True)
    metadata = Column(String, nullable=True)
    created_date = Column(DateTime, server_default=func.now())

    def to_dict(self):
        return {
            "session_id": self.session_id,
            "date": self.date.isoformat(),
            "duration_minutes": self.duration_minutes,
            "session_type": self.session_type,
            "intensity": self.intensity,
            "engagement_score": self.engagement_score,
            "reflection": self.reflection
        }
```

## AI Services

### 4. GPT Engine (OpenRouter Integration)

**backend/services/gpt_engine.py**
```python
import os
import json
import httpx
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

class GPTEngine:
    BASE_URL = "https://openrouter.io/api/v1"
    MODEL = "openai/gpt-4o-2024-11-20"

    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.http_client = httpx.Client()

        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not set in .env")

    def _build_headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "RoboMentor"
        }

    def chat(self, messages: list[dict], temperature: float = 0.7) -> str:
        try:
            response = self.http_client.post(
                f"{self.BASE_URL}/chat/completions",
                headers=self._build_headers(),
                json={
                    "model": self.MODEL,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": 2000
                },
                timeout=30.0
            )
            response.raise_for_status()

            result = response.json()
            return result["choices"][0]["message"]["content"]

        except Exception as e:
            logger.error(f"GPT API error: {e}")
            raise

    def generate_quiz(self, concept_name: str, context: str = "", difficulty: str = "Intermediate") -> dict:
        prompt = f"""
        Generate a 5-question quiz on "{concept_name}" at {difficulty} level.

        Context from user's notes:
        {context}

        Return JSON format:
        {{
            "questions": [
                {{
                    "id": 1,
                    "type": "mcq",
                    "question": "...",
                    "options": ["A", "B", "C", "D"],
                    "correct_answer": "...",
                    "explanation": "..."
                }},
                ...
            ]
        }}
        """

        response_text = self.chat([{"role": "user", "content": prompt}], temperature=0.5)

        try:
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            json_str = response_text[start:end]
            quiz_data = json.loads(json_str)
            return quiz_data
        except Exception as e:
            logger.error(f"Quiz generation parsing error: {e}")
            raise

    def generate_learning_path(self, goal: str, current_skills: dict, available_hours: int) -> dict:
        prompt = f"""
        Create a detailed learning path for the goal: "{goal}"

        Current skill levels:
        {json.dumps(current_skills, indent=2)}

        Available time: {available_hours} hours/week

        Return JSON:
        {{
            "phases": [
                {{
                    "phase": 1,
                    "title": "Fundamentals",
                    "duration_hours": 10,
                    "concepts": ["concept1", "concept2"],
                    "resources": ["tutorial_url", "paper_url"],
                    "milestone": "Take quiz and score 80%"
                }},
                ...
            ],
            "total_hours": 40,
            "estimated_weeks": 7,
            "key_resources": ["url1", "url2"],
            "tips": "Personalized advice"
        }}
        """

        response_text = self.chat([{"role": "user", "content": prompt}], temperature=0.6)

        try:
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            json_str = response_text[start:end]
            path_data = json.loads(json_str)
            return path_data
        except Exception as e:
            logger.error(f"Learning path generation error: {e}")
            raise
```

### 5. Voice Module (Whisper + pyttsx3)

**backend/services/voice_module.py**
```python
import whisper
import pyttsx3
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class VoiceModule:
    def __init__(self, model_size: str = "base"):
        self.whisper_model = whisper.load_model(model_size)
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)
        self.tts_engine.setProperty('volume', 0.9)

    def transcribe_audio(self, audio_file_path: str) -> str:
        try:
            result = self.whisper_model.transcribe(audio_file_path)
            text = result["text"].strip()
            logger.info(f"Transcribed: {text}")
            return text
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            raise

    def text_to_speech(self, text: str, output_file: str = None) -> str:
        try:
            if output_file:
                self.tts_engine.save_to_file(text, output_file)
                self.tts_engine.runAndWait()
                logger.info(f"TTS saved to {output_file}")
                return output_file
            else:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
                return None
        except Exception as e:
            logger.error(f"TTS error: {e}")
            raise
```

## API Endpoints

### 6. Chat API

**backend/api/chat.py**
```python
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from db.database import get_db
from models.session import LearningSession, SessionType
from services.gpt_engine import GPTEngine
from services.voice_module import VoiceModule
from pydantic import BaseModel
from typing import List
import os
import tempfile

router = APIRouter()
gpt_engine = GPTEngine()
voice_module = VoiceModule()

class MessageRequest(BaseModel):
    message: str
    context: str = None

class MessageResponse(BaseModel):
    response: str
    metadata: dict = {}

@router.post("/message", response_model=MessageResponse)
async def send_message(request: MessageRequest, db: Session = Depends(get_db)):
    try:
        system_message = """You are RoboMentor, an AI tutor for roboticists.
        You are knowledgeable about:
        - Computer Vision (YOLO, OpenCV, TensorRT, Deepstream)
        - Robotics (ROS2, motion planning, control)
        - RL for robot control
        - Sim2Real transfer learning
        - Industrial automation and inspection

        Be concise, practical, and hands-on. Reference the user's specific context when available.
        """

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": request.message}
        ]

        response = gpt_engine.chat(messages, temperature=0.7)

        session = LearningSession(
            duration_minutes=5,
            session_type=SessionType.READING.value,
            reflection=request.message[:100]
        )
        db.add(session)
        db.commit()

        return MessageResponse(
            response=response,
            metadata={"session_id": session.session_id}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/voice-message")
async def send_voice_message(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp_path = tmp.name

        user_text = voice_module.transcribe_audio(tmp_path)

        message_request = MessageRequest(message=user_text)
        response = await send_message(message_request, db)

        output_audio_path = tempfile.mktemp(suffix=".wav")
        voice_module.text_to_speech(response.response, output_audio_path)

        return {
            "transcribed_input": user_text,
            "mentor_response": response.response,
            "audio_response_path": output_audio_path
        }

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
```

### 7. Quiz API

**backend/api/quiz.py**
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from models.quiz import QuizAttempt
from services.gpt_engine import GPTEngine
from pydantic import BaseModel
from typing import List

router = APIRouter()
gpt_engine = GPTEngine()

class GenerateQuizRequest(BaseModel):
    concept_name: str
    context: str = None
    difficulty: str = "Intermediate"

class QuizQuestion(BaseModel):
    id: int
    type: str
    question: str
    options: List[str] = None
    correct_answer: str
    explanation: str

class GenerateQuizResponse(BaseModel):
    quiz_id: str
    questions: List[QuizQuestion]
    concept: str
    difficulty: str

@router.post("/generate", response_model=GenerateQuizResponse)
async def generate_quiz(request: GenerateQuizRequest):
    try:
        quiz_data = gpt_engine.generate_quiz(
            concept_name=request.concept_name,
            context=request.context or "",
            difficulty=request.difficulty
        )

        return GenerateQuizResponse(
            quiz_id=f"quiz_{request.concept_name.replace(' ', '_')}",
            questions=quiz_data["questions"],
            concept=request.concept_name,
            difficulty=request.difficulty
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class QuizSubmission(BaseModel):
    quiz_id: str
    concept_id: str
    skill_id: str
    answers: List[str]

class QuizResult(BaseModel):
    score: float
    feedback: str
    next_review_date: str

@router.post("/submit", response_model=QuizResult)
async def submit_quiz(submission: QuizSubmission, db: Session = Depends(get_db)):
    try:
        score = 85.0  # Placeholder grading logic
        feedback = "Great understanding of the concept!"

        attempt = QuizAttempt(
            quiz_id=submission.quiz_id,
            concept_id=submission.concept_id,
            skill_id=submission.skill_id,
            score=score
        )
        db.add(attempt)
        db.commit()

        import datetime
        next_review = datetime.datetime.now() + datetime.timedelta(days=3)

        return QuizResult(
            score=score,
            feedback=feedback,
            next_review_date=next_review.isoformat()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Frontend Setup (Electron)

### 8. Electron Main Process

**electron-app/src/main.js**
```javascript
const { app, BrowserWindow, Menu, ipcMain } = require('electron');
const path = require('path');
const isDev = require('electron-is-dev');

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false
    }
  });

  const startUrl = isDev
    ? 'http://localhost:3000'
    : `file://${path.join(__dirname, '../build/index.html')}`;

  mainWindow.loadURL(startUrl);

  if (isDev) {
    mainWindow.webContents.openDevTools();
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.on('ready', createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});

// IPC handlers
ipcMain.handle('send-message', async (event, message) => {
  const response = await fetch('http://localhost:8000/api/chat/message', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message })
  });
  return response.json();
});

ipcMain.handle('generate-quiz', async (event, concept) => {
  const response = await fetch('http://localhost:8000/api/quiz/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ concept_name: concept })
  });
  return response.json();
});
```

### 9. Preload Script

**electron-app/src/preload.js**
```javascript
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  sendMessage: (message) => ipcRenderer.invoke('send-message', message),
  generateQuiz: (concept) => ipcRenderer.invoke('generate-quiz', concept),
  submitQuiz: (submission) => ipcRenderer.invoke('submit-quiz', submission),
  recordAudio: () => ipcRenderer.invoke('record-audio'),
});
```

## Environment Configuration

### 10. .env File

Create `.env` in project root:

```bash
# Backend
BACKEND_PORT=8000
DATABASE_URL=sqlite:///./robomentor.db

# OpenRouter GPT API
OPENROUTER_API_KEY=your_api_key_here

# Obsidian Vault
OBSIDIAN_VAULT_PATH=/Users/tejas/Library/Mobile\ Documents/com~apple~CloudDocs/Obsidian/Robotics

# Google Calendar (Phase 2)
GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/calendar/oauth2/callback

# Frontend
FRONTEND_URL=http://localhost:3000
```

## Running the Application

### Local Development

```bash
# Terminal 1: Backend
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
python main.py

# Terminal 2: Frontend
cd electron-app
npm install
npm start
```

### Testing APIs

Visit `http://localhost:8000/docs` for interactive Swagger UI to test endpoints.

### Building for Production

```bash
# Backend
cd backend
pyinstaller --onefile --windowed main.py

# Frontend
cd electron-app
npm run build
```

## Integration Checklist

### Backend Integration
- [ ] `backend/models/onboarding.py` created and imported
- [ ] `backend/services/roadmap_generator.py` implemented
- [ ] `backend/api/onboarding.py` added to main FastAPI app
- [ ] Models imported in `backend/models/__init__.py`
- [ ] API router included in `backend/main.py`

### Frontend Integration
- [ ] `electron-app/src/onboarding.html` created
- [ ] `electron-app/src/renderer/onboarding.js` implemented
- [ ] IPC handlers added to `electron-app/src/main.js`
- [ ] API exposures added to `electron-app/src/preload.js`

### Testing
- [ ] Backend APIs accessible at `/docs`
- [ ] Onboarding flow works end-to-end
- [ ] Roadmap generation functional
- [ ] Dashboard displays roadmap correctly

## Key Implementation Notes

### Error Handling
- All API endpoints include try/catch blocks
- User-friendly error messages returned
- Logging implemented for debugging

### Security
- No authentication required for local development
- CORS configured for local development
- Environment variables for sensitive data

### Performance
- SQLite suitable for single-user application
- Local AI processing (Whisper, embeddings)
- Efficient database queries with proper indexing

### Extensibility
- Modular service architecture
- Clean separation of concerns
- Easy to add new AI providers or integrations

This implementation provides a solid foundation for the RoboMentor system, with room for growth and feature additions in future phases.