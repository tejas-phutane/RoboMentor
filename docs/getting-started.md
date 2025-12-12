# Getting Started

This guide will help you set up and run the RoboMentor desktop application on your local machine.

## Prerequisites

- **Python 3.9 or higher** - Required for the backend API
- **Node.js 16 or higher** - Required for the Electron frontend
- **npm or yarn** - Package manager for Node.js
- **Git** - For cloning the repository

### Optional Prerequisites (for full functionality)
- **Google Cloud Console account** - For Calendar integration
- **GitHub Personal Access Token** - For trend monitoring

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/robomentor_app.git
cd robomentor_app
```

### 2. Backend Setup

Install Python dependencies:

```bash
cd backend
pip install -r requirements.txt
```

Configure environment variables (create `.env` file in `backend/` directory):

```env
OPENAI_API_KEY=your_openai_api_key
GOOGLE_CALENDAR_CREDENTIALS_PATH=path/to/credentials.json
GITHUB_TOKEN=your_github_token
DATABASE_URL=sqlite:///./robomentor.db
HOST=localhost
PORT=8000
```

### 3. Frontend Setup

Install Node.js dependencies:

```bash
cd ../frontend
npm install
```

## Running the Application

### Development Mode

1. **Start the backend server** (in one terminal):
    ```bash
    cd backend
    python main.py
    ```

2. **Start the Electron app** (in another terminal):
    ```bash
    cd frontend
    npm run dev
    ```

### Production Mode

For the complete bundled application:

```bash
cd frontend
npm start
```

This will launch the RoboMentor desktop application with the backend automatically bundled and started.

## First Time Setup

When you first run RoboMentor, you'll go through an intelligent onboarding process:

### Onboarding Flow (15-20 minutes)

1. **Welcome Screen**: Introduction to RoboMentor's measurement-driven approach
2. **Personal Information**: Basic details and technology background
3. **Robotics Background**: Experience level and project history
4. **Goals & Interests**: Learning objectives and target domains
5. **Learning Style**: Preferred approach (hands-on, theory-first, or mixed)
6. **Skill Assessment**: Rate proficiency in 20+ robotics skills (0-100%)
7. **Roadmap Generation**: AI creates your personalized learning path
8. **Success Screen**: Welcome with your custom roadmap preview

### Post-Onboarding Experience

After onboarding completes:
- **Dashboard**: Shows your current phase, weekly metrics, and skill progress
- **Learning Paths**: Access your personalized roadmap with milestones
- **AI Mentor**: Chat with voice/text for robotics guidance
- **Session Logging**: Track all learning activities
- **Quiz Generation**: Test knowledge with AI-generated assessments

## Basic Usage

### Dashboard
- View your learning progress and statistics
- See active goals and upcoming sessions
- Monitor recent activity

### AI Chat
- Ask questions about robotics concepts
- Get personalized guidance
- Request code examples or explanations

### Learning Planner
- Set new learning goals
- View generated learning paths
- Schedule study sessions

### Settings
- Customize your profile
- Configure notification preferences
- Manage integrations

## Troubleshooting

### Backend Won't Start
- Ensure Python 3.9+ is installed: `python --version`
- Check that all dependencies are installed: `pip list`
- Verify environment variables are set correctly

### Frontend Won't Launch
- Ensure Node.js 16+ is installed: `node --version`
- Check npm installation: `npm --version`
- Try clearing node_modules: `rm -rf node_modules && npm install`

### Application Crashes
- Check the console for error messages
- Ensure the backend is running on the correct port
- Verify database file permissions

## Next Steps

- Explore the [Architecture](architecture.md) to understand the system design
- Check the [API Reference](api-reference.md) for programmatic access
- Learn about [Development](development.md) if you want to contribute

For more detailed information, see the main [README](../README.md).