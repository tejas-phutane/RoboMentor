# RoboMentor Application

[![CI](https://github.com/your-username/robomentor_app/actions/workflows/ci.yml/badge.svg)](https://github.com/your-username/robomentor_app/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

An AI-powered learning platform designed specifically for robotics engineers, providing personalized learning paths, adaptive scheduling, and real-time upgrade recommendations in a local-first architecture.

## Table of Contents

- [Project Description](#project-description)
- [Key Features](#key-features)
- [Architecture Overview](#architecture-overview)
- [Installation and Setup](#installation-and-setup)
- [Usage Examples](#usage-examples)
- [API Documentation](#api-documentation)
- [Screenshots](#screenshots)
- [Contributing](#contributing)
- [License](#license)

## Project Description

RoboMentor is a comprehensive AI-guided learning system built for robotics engineers. It combines advanced AI mentoring, personalized learning path generation, adaptive scheduling, and real-time trend integration to accelerate professional development in robotics. The system operates locally-first, ensuring data privacy while leveraging cloud integrations for calendar management and trend analysis.

The platform addresses the unique challenges of robotics engineering by providing:
- AI-powered mentorship for complex technical concepts
- Automated learning path generation based on skill gaps
- Calendar integration for structured learning sessions
- Real-time insights from academic and industry trends
- Performance analytics and upgrade recommendations

## Key Features

### 🤖 AI-Powered Mentoring
- Interactive chat with AI mentor for robotics-specific guidance
- Voice input processing (speech-to-text integration)
- Context-aware responses based on user's skill level and goals

### 📚 Personalized Learning Paths
- Automated path generation using AI analysis of user skills and goals
- Phase-based progression with adaptive difficulty
- Integration with Obsidian vaults for concept synchronization
- Skill proficiency tracking and gap analysis

### 📅 Adaptive Scheduling
- Google Calendar integration for seamless session scheduling
- Smart scheduling algorithms that adapt to user availability
- Conflict resolution and optimal time slot recommendations

### 📊 Real-Time Analytics
- Learning velocity tracking and visualization
- Gap analysis reports for skill improvement
- Dashboard with comprehensive metrics and insights

### 🌐 Trend Integration
- ArXiv integration for latest robotics research papers
- GitHub trending repositories monitoring
- Automated content recommendations based on industry trends

### 🧠 Quiz and Assessment
- AI-generated quizzes with adaptive difficulty
- Real-time answer evaluation and feedback
- Progress tracking through assessment results

## Architecture Overview

The RoboMentor application follows a desktop application architecture with an Electron frontend and a Python FastAPI backend, providing a complete local-first learning platform.

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Electron      │    │  RoboMentor API │    │   Integrations  │
│   Frontend      │◄──►│   (FastAPI)     │◄──►│   (Google,      │
│   (HTML/CSS/JS) │    │   (Bundled)     │    │   ArXiv, GitHub)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                      │
                                                      ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AI Engine     │    │ Learning Tracker│    │ Adaptive        │
│   (GPT, Quiz)   │    │ (Paths, Skills) │    │ Scheduler       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                      │
                                                      ▼
┌─────────────────┐    ┌─────────────────┐
│   Database      │    │   File System   │
│   (SQLAlchemy)  │    │   (Obsidian)    │
└─────────────────┘    └─────────────────┘
```

### Core Components

- **AI Engine**: Handles GPT integration, chat processing, and quiz generation
- **Learning Tracker**: Manages learning paths, skill profiles, and goal tracking
- **Adaptive Scheduler**: Coordinates calendar integration and session scheduling
- **Upgrade Recommendations**: Provides analytics and gap analysis
- **Integrations**: Manages external API connections (Google Calendar, ArXiv, GitHub)

For detailed architecture diagrams, see the images below.

## Installation and Setup

### Prerequisites

- Python 3.9 or higher
- pip package manager
- Google Cloud Console account (for Calendar integration)
- GitHub Personal Access Token (for trend monitoring)

### Backend Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/robomentor_app.git
   cd robomentor_app
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   Create a `.env` file in the `backend/` directory:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   GOOGLE_CALENDAR_CREDENTIALS_PATH=path/to/credentials.json
   GITHUB_TOKEN=your_github_token
   DATABASE_URL=sqlite:///./robomentor.db
   HOST=localhost
   PORT=8000
   ```

5. **Run database migrations:**
   ```bash
   alembic upgrade head
   ```

6. **Start the server:**
    ```bash
    python main.py
    ```

The API will be available at `http://localhost:8000`.

### Frontend Setup

1. **Install Node.js dependencies:**
    ```bash
    cd frontend
    npm install
    ```

2. **Run the Electron application:**
    ```bash
    npm start
    ```

The RoboMentor desktop application will launch with the bundled backend.

### Running Tests

```bash
cd backend
python -m pytest tests/ -v
```

## Deployment

For building and deploying the complete RoboMentor application, see the [BUILD_DEPLOYMENT.md](BUILD_DEPLOYMENT.md) guide, which covers:

- Building the Python backend into a standalone executable
- Packaging the Electron application for Windows, macOS, and Linux
- Code signing and distribution options
- CI/CD integration examples

## Usage Examples

### Application Usage

Once the RoboMentor desktop application is running, you can:

1. **Dashboard**: View your learning progress, active goals, and recent activity
2. **AI Chat**: Interact with the AI mentor for robotics guidance and questions
3. **Learning Planner**: Set learning goals and view your personalized learning paths
4. **Settings**: Configure your preferences, including theme and notifications

The application provides a complete local-first experience with all features accessible through the intuitive desktop interface.

### API Usage (for Development/Integration)

If you need to interact with the RoboMentor API directly:

### Basic AI Chat Interaction

```python
import requests

# Send a message to the AI mentor
response = requests.post("http://localhost:8000/api/chat/message",
                        json={"message": "Explain PID controllers in robotics"})
print(response.json())
```

### Generate a Learning Path

```python
# Create a personalized learning path
path_data = {
    "user_skills": {"python": 0.8, "ros": 0.6, "computer_vision": 0.4},
    "user_goals": ["Master ROS2", "Learn SLAM algorithms"],
    "hours_per_week": 15
}

response = requests.post("http://localhost:8000/api/paths/create", json=path_data)
print(response.json())
```

### Schedule a Learning Session

```python
# Schedule a session in Google Calendar
session_data = {
    "title": "ROS2 Navigation Stack Study",
    "duration": 90,
    "preferred_time": "2024-01-15T14:00:00Z"
}

response = requests.post("http://localhost:8000/api/calendar/schedule-session",
                        json=session_data)
print(response.json())
```

### Generate and Take a Quiz

```python
# Generate a quiz on robotics topics
quiz_request = {
    "topic": "Computer Vision in Robotics",
    "difficulty": "intermediate",
    "num_questions": 5
}

response = requests.post("http://localhost:8000/api/quiz/generate", json=quiz_request)
quiz = response.json()["quiz"]

# Submit answers
answers = {"answers": ["Answer 1", "Answer 2", "Answer 3", "Answer 4", "Answer 5"]}
results = requests.post("http://localhost:8000/api/quiz/submit",
                       json={"quiz_data": quiz, "user_answers": answers})
print(results.json())
```

## API Documentation

The RoboMentor API is built with FastAPI and provides comprehensive OpenAPI documentation.

### Available Endpoints

#### AI Engine (`/api/chat`, `/api/quiz`)
- `POST /api/chat/message` - Send text message to AI mentor
- `POST /api/chat/voice` - Process voice input (STT)
- `POST /api/quiz/generate` - Generate AI-powered quiz
- `POST /api/quiz/submit` - Submit quiz answers for evaluation

#### Learning Tracker (`/api`)
- `GET /api/paths/active` - Retrieve active learning paths
- `POST /api/paths/create` - Generate new learning path
- `PUT /api/paths/{path_id}/next-phase` - Advance to next learning phase
- `GET /api/paths/{path_id}/recommendations` - Get AI recommendations
- `GET /api/skills/profile` - Get user skills snapshot
- `PUT /api/skills/{skill_id}/proficiency` - Update skill proficiency
- `GET /api/concepts/search` - Search learning concepts
- `POST /api/concepts/from-obsidian` - Sync concepts from Obsidian vault
- `GET /api/goals/active` - Get active learning goals
- `POST /api/goals/create` - Create new learning goal
- `PUT /api/goals/{goal_id}/progress` - Update goal progress

#### Adaptive Scheduler (`/api/calendar`)
- `POST /api/calendar/sync` - Sync with external calendar
- `POST /api/calendar/schedule-session` - Schedule learning session

#### Upgrade Recommendations (`/api/metrics`)
- `GET /api/metrics/dashboard` - Get dashboard analytics
- `GET /api/metrics/gap-analysis` - Generate skill gap analysis
- `GET /api/metrics/learning-velocity` - Get learning velocity data

#### Integrations (`/api/calendar`, `/api/trends`)
- `POST /api/calendar/sync` - Sync Google Calendar
- `POST /api/calendar/schedule-session` - Schedule in Google Calendar
- `GET /api/trends/arxiv` - Get ArXiv robotics trends
- `GET /api/trends/github` - Get GitHub trending repos

### Interactive API Documentation

Once the server is running, visit `http://localhost:8000/docs` for interactive Swagger UI documentation, or `http://localhost:8000/redoc` for ReDoc documentation.

## Screenshots

### System Architecture Overview
![RoboMentor Architecture](../robomentor/robomentor_architecture.png)

*High-level system architecture showing component interactions and data flow.*

### Learning Dashboard
![RoboMentor Overview](../robomentor/robomentor_overview.png)

*Main dashboard displaying learning progress, active goals, and upcoming sessions.*

### Development Roadmap
![RoboMentor Roadmap](../robomentor/robomentor_roadmap.png)

*Product roadmap showing planned features and milestones.*

### Transformation Journey
![RoboMentor Transformation](../robomentor/robomentor_transformation.png)

*Visualization of the learning transformation process from novice to expert.*

## Contributing

We welcome contributions to RoboMentor! Please follow these guidelines:

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Set up the development environment as described in [Installation](#installation-and-setup)
4. Make your changes
5. Run tests: `python -m pytest tests/ -v`
6. Commit your changes: `git commit -am 'Add some feature'`
7. Push to the branch: `git push origin feature/your-feature-name`
8. Submit a pull request

### Code Style

- Follow PEP 8 Python style guidelines
- Use type hints for function parameters and return values
- Write comprehensive docstrings for all functions and classes
- Ensure all tests pass before submitting

### Testing

- Write unit tests for new functionality
- Maintain test coverage above 80%
- Test both happy path and error scenarios
- Use descriptive test names that explain the expected behavior

### Documentation

- Update this README for any new features
- Add docstrings to all new functions
- Update API documentation for endpoint changes

### Reporting Issues

- Use GitHub Issues to report bugs or request features
- Provide detailed steps to reproduce bugs
- Include relevant error messages and stack traces
- Specify your environment (OS, Python version, etc.)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2024 The RoboMentor Authors

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.