# Architecture

## Overview

RoboMentor is an intelligent, measurement-driven learning system that combines AI-powered personalization with comprehensive progress tracking. Built on the principle **"You can only change what you can measure"**, it provides robotics engineers with adaptive learning paths, voice-powered AI mentorship, and data-driven optimization.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    RoboMentor Desktop App                   │
│                     (Electron.js)                           │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Voice    │  │ Learning │  │ Dashboard│  │ Settings │   │
│  │ Chat     │  │ Planner  │  │ & Metrics│  │ & Integr.│   │
│  │ (STT)    │  │          │  │ (Charts) │  │          │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
├─────────────────────────────────────────────────────────────┤
│              Local Backend (Python/FastAPI)                 │
├─────────────┬────────────────┬──────────────┬─────────────┤
│  Vector DB  │  Quiz Engine   │  Path        │  Voice/     │
│  (Obsidian  │  (GPT +        │  Recommender │  Integr.    │
│  Content)   │  Context)      │              │  Module     │
├─────────────┴────────────────┴──────────────┴─────────────┤
│                   Data Layer (SQLite)                       │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Schema: Skills | Concepts | Learning Sessions       │  │
│  │         Quiz Attempts | Calendar Events             │  │
│  │         Project Milestones | Trend Feed             │  │
│  └──────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│              External Integrations (APIs)                   │
├─────────────┬────────────────┬──────────────┬─────────────┤
│  Obsidian   │  Google        │  OpenRouter  │  arXiv +    │
│  File Sync  │  Calendar      │  (GPT-4o)    │  GitHub     │
│  (via REST) │  (OAuth2)      │              │  Trends     │
└─────────────┴────────────────┴──────────────┴─────────────┘
```

## Core Components

### Frontend (Electron)

The desktop application interface providing a native-like experience:

- **Electron Framework**: Cross-platform desktop runtime
- **HTML/CSS/JavaScript**: Modern web technologies for responsive UI
- **Main Process**: Node.js process managing application lifecycle and IPC
- **Renderer Process**: Chromium browser instance for UI rendering
- **Preload Scripts**: Secure context bridge between main and renderer processes
- **Voice Integration**: Web Audio API for recording and playback

### Backend (Python/FastAPI)

The AI and business logic engine running locally:

- **API Layer**: FastAPI-based REST API with automatic OpenAPI/Swagger documentation
- **Core Services**:
  - **AI Engine**: GPT-4o integration via OpenRouter for chat and quiz generation
  - **Voice Module**: Whisper (STT) and pyttsx3 (TTS) for voice interactions
  - **Learning Tracker**: Skill analysis, path generation, progress tracking
  - **Obsidian Sync**: File watching and content parsing for knowledge integration
  - **Metrics Engine**: Learning velocity, retention analysis, gap identification
- **Integrations**:
  - **Calendar Integration**: Google Calendar OAuth2 for scheduling
  - **Trend Monitoring**: ArXiv and GitHub APIs for robotics research updates
- **Data Layer**: SQLAlchemy ORM with SQLite for local data persistence
- **Background Tasks**: File watching, scheduled reviews, trend updates

### Data Model

#### Core Entities

**Skills Taxonomy** (Hierarchical proficiency tracking):
```python
class Skill(Base):
    skill_id: UUID (primary key)
    name: str (e.g., "Computer Vision")
    domain: str (e.g., "Core", "Advanced")
    parent_skill_id: UUID (foreign key for hierarchy)
    proficiency_level: float (0-100%)
    last_assessed: datetime
    assessment_method: str ("quiz", "project", "hands-on")
```

**Concepts Registry** (Knowledge base with mastery tracking):
```python
class Concept(Base):
    concept_id: UUID
    title: str (e.g., "Transformer Architecture")
    domain: str (e.g., "AI/ML", "Robotics")
    difficulty: str ("Beginner", "Intermediate", "Advanced")
    mastery_level: float (0-100%)
    obsidian_file_path: str
    date_first_encountered: datetime
    date_last_reviewed: datetime
```

**Learning Sessions** (Activity logging with metadata):
```python
class LearningSession(Base):
    session_id: UUID
    date: datetime
    duration_minutes: int
    type: str ("Reading", "Tutorial", "Project", "Quiz", "Hands-On Lab")
    intensity: str ("Light", "Medium", "Deep")
    engagement_score: int (1-10)
    reflection: text
    metadata: json (tutorial_name, tool_used, etc.)
```

**Adaptive Roadmaps** (AI-generated personalized learning paths):
```python
class AdaptiveRoadmap(Base):
    roadmap_id: UUID
    user_id: UUID
    title: str
    roadmap_structure: json (phases, milestones, resources)
    current_phase: int
    overall_progress: float (0-100%)
    is_active: bool
```

**Quiz Attempts** (Knowledge assessment with retention tracking):
```python
class QuizAttempt(Base):
    quiz_id: UUID
    attempt_id: UUID
    concept_id: UUID
    skill_id: UUID
    score: float (0-100%)
    time_spent_minutes: int
    date_attempted: datetime
    retention_predicted: float
    next_review_date: datetime
```

### Data Flow Architecture

1. **User Interaction**: Electron frontend captures input (text, voice, form data)
2. **IPC Communication**: Secure inter-process communication between Electron processes
3. **API Requests**: Frontend makes HTTP requests to local FastAPI backend
4. **Business Logic**: Backend processes requests using AI services and database
5. **External Integration**: Backend communicates with APIs (OpenRouter, Google Calendar, etc.)
6. **Data Persistence**: All user data stored locally in SQLite database
7. **Response Rendering**: Results returned to frontend for display and interaction

### Key Design Principles

- **Local-First**: All user data stored locally for privacy and offline capability
- **AI-Powered**: GPT-4o integration for intelligent personalization and content generation
- **Measurement-Driven**: Comprehensive tracking enables data-driven learning optimization
- **Modular Architecture**: Clean separation of concerns for maintainability and extensibility
- **Cross-Platform**: Works on Windows, macOS, and Linux through Electron
- **Privacy-Focused**: No user data sent to external servers except for AI API calls
- **Extensible**: Plugin architecture for adding new AI providers and integrations
- **Testable**: Comprehensive test coverage with unit, integration, and functional tests

## User Interface Architecture

### Dashboard (Main Landing)
- **Weekly Metrics**: Hours, engagement, streak tracking
- **Skill Heatmap**: Proficiency levels across domains
- **Knowledge Gaps**: Priority-ranked learning opportunities
- **Today's Schedule**: Calendar-integrated learning blocks

### Voice Chat Interface
- **Conversational AI**: GPT-powered mentor specialized in robotics
- **Voice I/O**: Whisper STT and pyttsx3 TTS for hands-free interaction
- **Context Awareness**: Draws from user's Obsidian vault and learning history
- **Resource Generation**: AI-curated tutorials, papers, and hands-on exercises

### Learning Planner
- **Adaptive Roadmaps**: Multi-phase personalized learning paths
- **Progress Tracking**: Milestone completion and phase advancement
- **Resource Integration**: Curated content from user's knowledge base
- **Adaptation Logic**: Automatic path adjustment based on progress and interests

### Metrics & Analytics
- **Learning Velocity**: Time-series charts of learning activity
- **Skill Progression**: Historical proficiency tracking
- **Retention Analysis**: Quiz performance and spaced repetition scheduling
- **ROI Tracking**: Learning investment vs. business/project outcomes

## Deployment & Distribution

### Development Environment
- **Local Setup**: Python venv + Node.js for development
- **Hot Reload**: Fast iteration with Electron dev tools
- **API Testing**: Swagger UI at `http://localhost:8000/docs`
- **Database Inspection**: SQLite browser for data debugging

### Production Build
- **Backend Bundling**: PyInstaller creates standalone executable
- **Frontend Packaging**: Electron Builder creates platform-specific installers
- **Single Binary**: Self-contained application with all dependencies
- **Auto-Updates**: Optional update mechanism for future releases

### Platform Support
- **Windows**: .exe installer with Windows-specific optimizations
- **macOS**: .dmg installer with code signing
- **Linux**: .deb/.rpm packages with system integration

## Security & Privacy

### Data Protection
- **Local Storage**: All user data remains on device
- **No Telemetry**: No tracking or data collection without explicit consent
- **Encryption**: Sensitive data encrypted at rest
- **API Security**: Secure API key management for external services

### Network Security
- **Local APIs**: Backend only accessible from localhost
- **CORS Configuration**: Strict origin policies for development
- **Certificate Pinning**: For external API communications
- **Rate Limiting**: Built-in protection against API abuse

## Performance Considerations

### Optimization Strategies
- **Lazy Loading**: Components loaded on demand
- **Caching**: Frequent queries cached in memory
- **Background Processing**: Heavy operations run asynchronously
- **Database Indexing**: Optimized queries for large datasets
- **Memory Management**: Efficient handling of large Obsidian vaults

### Scalability Limits
- **Local Processing**: Bounded by device hardware capabilities
- **Database Size**: SQLite suitable for individual users (no multi-user scaling needed)
- **API Limits**: External API rate limits managed through queuing and caching
- **File Watching**: Efficient monitoring of Obsidian vaults without performance impact

## Integration Points

### Obsidian Vault Integration
- **File Watching**: Real-time monitoring of markdown files
- **Content Parsing**: Extract concepts, links, and code blocks
- **Vector Embeddings**: Semantic search using sentence-transformers
- **Context Injection**: Personal notes used in AI responses and quiz generation

### Calendar Integration
- **OAuth2 Flow**: Secure Google Calendar authentication
- **Event Creation**: Automatic scheduling of learning sessions
- **Conflict Resolution**: Smart scheduling around existing commitments
- **Progress Sync**: Learning completion updates calendar events

### Trend Monitoring
- **ArXiv Integration**: Daily robotics paper summaries
- **GitHub Monitoring**: Trending repository tracking
- **Content Filtering**: Relevance-based notifications
- **Learning Path Updates**: New research integrated into roadmaps

This architecture provides a solid foundation for an intelligent, measurement-driven learning system that can grow with user needs and technological advancements.