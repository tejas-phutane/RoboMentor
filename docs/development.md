# Development Guide

## Development Roadmap Overview

RoboMentor follows a **5-phase development approach** over 20 weeks, from MVP to full-featured AI-powered learning system:

- **Phase 1: MVP (Weeks 1-4)** - Core learning loop with voice chat, session logging, and basic quizzes
- **Phase 2: Context Integration (Weeks 5-8)** - Obsidian sync, spaced repetition, calendar integration
- **Phase 3: Adaptive Paths (Weeks 9-12)** - AI-generated learning paths, multi-phase roadmaps
- **Phase 4: Advanced Analytics (Weeks 13-16)** - Learning velocity tracking, skill heatmaps, retention metrics
- **Phase 5: Robotics Expertise (Weeks 17-20)** - Domain-specific templates, trend integration

**Current Status**: Phase 1 MVP implementation (Dec 9 - Jan 8, 2026)

## Setting Up Development Environment

1. Follow the [Getting Started](getting-started.md) guide for basic setup.

2. **Backend development dependencies**:
    ```bash
    cd backend
    pip install -r requirements-dev.txt  # if exists, otherwise install pytest manually
    pip install pytest pytest-cov black isort mypy
    ```

3. **Frontend development dependencies**:
    ```bash
    cd ../frontend
    npm install --save-dev electron-devtools-installer concurrently
    ```

## Development Workflow

### Backend Development

#### Running Tests
```bash
cd backend
pytest tests/ -v --cov=.
```

#### Code Quality
- **Formatting**: `black .`
- **Import sorting**: `isort .`
- **Type checking**: `mypy .`
- **Linting**: `flake8 .`

#### Database Operations
```bash
cd backend
# Initialize database
python -c "from db.database import init_db; init_db()"

# Inspect database
sqlite3 robomentor.db ".tables"
sqlite3 robomentor.db ".schema skills"
```

### Frontend Development

#### Development Mode
```bash
cd frontend
npm run dev  # Runs Electron in development mode
```

#### Hot Reloading
For faster development, you can modify the frontend files and reload manually, or set up a development server.

#### Building for Testing
```bash
cd frontend
npm run build-backend  # Build Python backend first
npm run build-electron  # Build Electron app
```

### Full Stack Development

#### Running Both Services
Use separate terminals:

**Terminal 1 - Backend:**
```bash
cd backend
python main.py
# Visit http://localhost:8000/docs for API documentation
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Or use a process manager like `concurrently` in package.json scripts.

## Project Structure

### Backend Structure
```
backend/
├── api/                 # FastAPI route handlers
│   ├── __init__.py
│   ├── chat.py          # AI chat and voice endpoints
│   ├── skills.py        # Skill tracking endpoints
│   ├── quiz.py          # Quiz generation and grading
│   ├── onboarding.py    # User onboarding and roadmaps
│   └── metrics.py       # Analytics and reporting
├── services/            # Business logic
│   ├── gpt_engine.py    # OpenRouter GPT integration
│   ├── voice_module.py  # Whisper STT + pyttsx3 TTS
│   ├── obsidian_sync.py # Vault file watching
│   ├── roadmap_generator.py # AI-powered path creation
│   └── metrics.py       # Learning analytics
├── models/              # SQLAlchemy models
│   ├── skill.py         # Skill proficiency tracking
│   ├── session.py       # Learning session logging
│   ├── concept.py       # Knowledge base concepts
│   ├── quiz.py          # Quiz attempts and results
│   └── onboarding.py    # User profiles and roadmaps
├── db/                  # Database layer
│   ├── database.py      # SQLAlchemy setup
│   └── schema.sql       # SQLite schema
├── tests/               # Test suites
│   ├── unit/
│   ├── integration/
│   └── functional/
├── config.py            # Configuration management
├── main.py              # FastAPI application entry point
└── requirements.txt     # Python dependencies
```

### Frontend Structure
```
electron-app/
├── src/
│   ├── main.js          # Electron main process
│   ├── preload.js       # IPC bridge for security
│   ├── index.html       # Main UI layout
│   ├── styles/
│   │   └── main.css     # Application styling
│   └── renderer/
│       ├── dashboard.js # Main dashboard logic
│       ├── chat.js      # Voice/text chat interface
│       ├── onboarding.js # User onboarding flow
│       └── planner.js   # Learning path management
├── package.json         # Node.js configuration
└── dist/                # Build output
```

## Code Style Guidelines

### Backend (Python)
- **PEP 8** compliance
- **Type hints** for all function parameters and return values
- **Docstrings** for all public functions and classes
- **Black** formatting with 88 character line length
- **Descriptive variable names** and clear logic flow

### Frontend (JavaScript)
- **ES6+** features
- **Consistent indentation** (2 spaces)
- **Descriptive function names**
- **Comments** for complex logic
- **Modular code** with clear separation of concerns

## Testing Strategy

### Backend Tests
- **Unit tests** for individual functions and classes
- **Integration tests** for API endpoints
- **Functional tests** for complete workflows
- **Mock external dependencies** (OpenRouter, Google Calendar)

### Frontend Tests
- **Unit tests** for JavaScript functions
- **Integration tests** for UI interactions
- **End-to-end tests** for complete user workflows

## Phase 1 MVP Development (Current Focus)

### Week 1-2: Foundation Setup
**Goal**: Working backend + frontend skeleton

**Tasks**:
- [ ] Create project structure with proper directories
- [ ] Set up FastAPI backend with basic endpoints
- [ ] Configure Electron frontend with IPC communication
- [ ] Initialize SQLite database with core tables
- [ ] Implement basic GPT chat integration
- [ ] Test end-to-end communication

**Success Criteria**:
- Backend serves API at localhost:8000
- Frontend can send/receive data from backend
- Database stores and retrieves basic records
- GPT API responds to test messages

### Week 3-4: Core Features
**Goal**: Functional MVP with chat, sessions, quizzes

**Tasks**:
- [ ] Implement voice I/O (Whisper + pyttsx3)
- [ ] Build learning session logging system
- [ ] Create skill proficiency tracking
- [ ] Develop quiz generation from GPT
- [ ] Design dashboard with metrics display
- [ ] Integrate Obsidian vault watching
- [ ] Package for standalone execution

**Success Criteria**:
- Voice chat works end-to-end
- Session logging captures all metadata
- Quiz generation uses GPT with good results
- Dashboard shows accurate weekly metrics
- Application runs without external dependencies

## Contributing

### Development Process
1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/your-feature-name`
3. **Develop** with tests: Write code and comprehensive tests
4. **Test** thoroughly: Run all test suites
5. **Format** code: Apply Black and isort
6. **Commit** changes: `git commit -am 'Add feature description'`
7. **Push** branch: `git push origin feature/your-feature-name`
8. **Submit** pull request with detailed description

### Code Review Checklist
- [ ] Tests pass and coverage maintained
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] No breaking changes without migration
- [ ] Security considerations addressed
- [ ] Performance impact assessed

## Debugging

### Backend Debugging
- Use `uvicorn main:app --reload` for auto-restart on changes
- Check logs in terminal or configure logging to file
- Use `pdb` or `ipdb` for interactive debugging
- Test API endpoints with `curl` or Postman
- Visit `http://localhost:8000/docs` for Swagger UI

### Frontend Debugging
- Use Electron DevTools: `Ctrl+Shift+I` (or `Cmd+Option+I` on Mac)
- Check console for JavaScript errors
- Use browser developer tools for UI debugging
- Monitor network requests to backend

### Database Debugging
```bash
# Inspect database
sqlite3 robomentor.db ".tables"
sqlite3 robomentor.db ".schema skills"
sqlite3 robomentor.db "SELECT * FROM learning_sessions LIMIT 5;"

# Reset database
rm robomentor.db
python -c "from db.database import init_db; init_db()"
```

### Common Issues
- **Port conflicts**: Ensure backend port 8000 is available
- **CORS errors**: Check CORS configuration in FastAPI
- **Database issues**: Verify SQLite file permissions
- **Build failures**: Clear node_modules and rebuild
- **API key errors**: Verify OpenRouter key in .env file

## Documentation

### Building Docs Locally
```bash
pip install mkdocs mkdocs-material mkdocstrings
mkdocs serve
```
Visit `http://localhost:8000` to view the documentation.

### Updating Documentation
- Keep README.md, docs, and code comments in sync
- Update API docs when endpoints change
- Add examples for new features
- Test documentation builds successfully

## Deployment

For production builds and deployment, see [BUILD_DEPLOYMENT.md](../BUILD_DEPLOYMENT.md).

### Development vs Production
- **Development**: Hot reloading, debug logging, local database
- **Production**: Optimized builds, bundled backend, production config

## Weekly Progress Tracking

Use this template for weekly development updates:

```
Week [X] Progress Report ([Start Date])

✅ Completed This Week:
- [ ] Task 1
- [ ] Task 2
- [ ] Task 3

⏳ In Progress:
- [ ] Task 4
- [ ] Task 5

📊 Metrics:
- Hours invested: __
- Lines of code: __
- Features completed: __
- Bugs fixed: __

🎯 Next Week Focus:
- [ ] Priority task
- [ ] Secondary task

📋 Blockers & Solutions:
- Blocker: __________
- Solution: __________

🏆 Wins:
- Accomplishment 1
- Accomplishment 2
```

## Phase Completion Milestones

### Phase 1 MVP (Week 4)
- [ ] Voice chat working end-to-end
- [ ] Session logging with metadata
- [ ] Skill tracking (0-100% proficiency)
- [ ] Quiz generation and completion
- [ ] Dashboard with weekly metrics
- [ ] Obsidian integration
- [ ] Standalone executable
- [ ] Documentation complete
- [ ] No critical bugs

### Phase 2 Context (Week 8)
- [ ] Obsidian deep parsing
- [ ] Vector embeddings for search
- [ ] Spaced repetition algorithm
- [ ] Calendar integration
- [ ] Retention tracking

### Phase 3 Paths (Week 12)
- [ ] AI path generation
- [ ] Multi-phase roadmaps
- [ ] Progress tracking
- [ ] Adaptation logic

### Phase 4 Analytics (Week 16)
- [ ] Learning velocity charts
- [ ] Skill heatmaps
- [ ] Retention prediction
- [ ] Automated insights

### Phase 5 Robotics (Week 20)
- [ ] Domain templates
- [ ] Trend monitoring
- [ ] Paper integration
- [ ] Hardware paths