# API Reference

The RoboMentor backend provides a REST API built with FastAPI. When the application is running, you can access interactive API documentation at `http://localhost:8000/docs` (Swagger UI) or `http://localhost:8000/redoc` (ReDoc).

## Base URL
```
http://localhost:8000
```

## Authentication
Currently, the API does not require authentication for local development. In production deployments, consider adding API key authentication.

## Endpoints

### AI Engine (`/api`)

#### Chat Endpoints
- `POST /api/chat/message`
  - Send a text message to the AI mentor
  - **Request Body**:
    ```json
    {
      "message": "Explain PID controllers in robotics",
      "context": "intermediate"
    }
    ```
  - **Response**: AI-generated response with guidance

- `POST /api/chat/voice`
  - Process voice input (speech-to-text)
  - **Request Body**: Audio file (multipart/form-data)
  - **Response**: Transcribed text and AI response

#### Quiz Endpoints
- `POST /api/quiz/generate`
  - Generate an AI-powered quiz
  - **Request Body**:
    ```json
    {
      "topic": "Computer Vision in Robotics",
      "difficulty": "intermediate",
      "num_questions": 5
    }
    ```
  - **Response**: Generated quiz with questions and options

- `POST /api/quiz/submit`
  - Submit quiz answers for evaluation
  - **Request Body**:
    ```json
    {
      "quiz_id": "uuid",
      "answers": ["Answer 1", "Answer 2", "Answer 3", "Answer 4", "Answer 5"]
    }
    ```
  - **Response**: Score, feedback, and explanations

### Learning Tracker (`/api`)

#### Learning Paths
- `GET /api/paths/active`
  - Retrieve user's active learning paths
  - **Response**: List of current learning paths with progress

- `POST /api/paths/create`
  - Generate a new personalized learning path
  - **Request Body**:
    ```json
    {
      "user_skills": {"python": 0.8, "ros": 0.6},
      "user_goals": ["Master ROS2", "Learn SLAM"],
      "hours_per_week": 15
    }
    ```
  - **Response**: Generated learning path with phases and milestones

- `PUT /api/paths/{path_id}/next-phase`
  - Advance to the next learning phase
  - **Response**: Updated path status

- `GET /api/paths/{path_id}/recommendations`
  - Get AI recommendations for the current path
  - **Response**: Personalized learning suggestions

#### Skills and Goals
- `GET /api/skills/profile`
  - Get user's current skill profile
  - **Response**: Skill levels and proficiency data

- `PUT /api/skills/{skill_id}/proficiency`
  - Update skill proficiency level
  - **Request Body**: `{"proficiency": 0.85}`

- `GET /api/goals/active`
  - Retrieve active learning goals
  - **Response**: List of current goals with progress

- `POST /api/goals/create`
  - Create a new learning goal
  - **Request Body**:
    ```json
    {
      "title": "Master ROS2 Navigation",
      "description": "Complete ROS2 navigation stack tutorials",
      "target_date": "2024-06-01",
      "skill_requirements": ["ros", "python"]
    }
    ```

- `PUT /api/goals/{goal_id}/progress`
  - Update goal progress
  - **Request Body**: `{"progress": 0.75, "notes": "Completed basic tutorials"}`

#### Concepts
- `GET /api/concepts/search`
  - Search learning concepts
  - **Query Parameters**: `q=robotics`, `category=ai`
  - **Response**: Matching concepts with metadata

- `POST /api/concepts/from-obsidian`
  - Sync concepts from Obsidian vault
  - **Request Body**: Obsidian vault data
  - **Response**: Sync status and new concepts added

### Adaptive Scheduler (`/api/calendar`)

- `POST /api/calendar/sync`
  - Sync with external calendar (Google Calendar)
  - **Response**: Sync status and events imported

- `POST /api/calendar/schedule-session`
  - Schedule a new learning session
  - **Request Body**:
    ```json
    {
      "title": "ROS2 Navigation Study",
      "duration": 90,
      "preferred_time": "2024-01-15T14:00:00Z",
      "description": "Study ROS2 navigation stack"
    }
    ```
  - **Response**: Scheduled event details

### Upgrade Recommendations (`/api/metrics`)

- `GET /api/metrics/dashboard`
  - Get comprehensive dashboard analytics
  - **Response**: Learning velocity, skill gaps, progress metrics

- `GET /api/metrics/gap-analysis`
  - Generate detailed skill gap analysis
  - **Response**: Identified gaps with recommendations

- `GET /api/metrics/learning-velocity`
  - Get learning velocity data and trends
  - **Response**: Progress over time metrics

### Trend Integrations (`/api/trends`)

- `GET /api/trends/arxiv`
  - Get latest robotics papers from ArXiv
  - **Query Parameters**: `days=7`, `category=robotics`
  - **Response**: Recent papers with abstracts and links

- `GET /api/trends/github`
  - Get trending robotics repositories on GitHub
  - **Query Parameters**: `language=python`, `days=30`
  - **Response**: Trending repos with stats and descriptions

## Response Format

All API responses follow a consistent format:

**Success Response**:
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully"
}
```

**Error Response**:
```json
{
  "success": false,
  "error": "Error description",
  "details": { ... }
}
```

## Rate Limiting

- No rate limiting is currently implemented for local development
- Consider implementing rate limiting for production deployments

## Error Codes

- `400` - Bad Request: Invalid input parameters
- `404` - Not Found: Resource not found
- `422` - Validation Error: Input validation failed
- `500` - Internal Server Error: Server-side error

## WebSocket Support

The API includes WebSocket endpoints for real-time features (planned):
- `ws://localhost:8000/ws/chat` - Real-time chat
- `ws://localhost:8000/ws/notifications` - Live notifications

## SDKs and Libraries

Currently, no official SDKs are available. You can interact with the API using:
- `requests` library in Python
- `fetch` API in JavaScript
- `curl` for command-line testing
- Postman or similar API testing tools

For more details, visit the interactive API documentation at `http://localhost:8000/docs` when the server is running.