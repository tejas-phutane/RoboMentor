# Onboarding System

RoboMentor features an intelligent onboarding system that captures user context and generates personalized learning roadmaps using AI.

## Overview

The onboarding system is designed to solve the problem of one-size-fits-all learning approaches in robotics. Instead of generic curricula, RoboMentor creates personalized learning paths based on:

- User's background and experience level
- Specific learning goals and target domains
- Available time commitment
- Preferred learning style
- Current skill assessment

## Onboarding Flow

The onboarding process takes approximately 15-20 minutes and consists of 6 steps:

### Step 1: Personal Information
Captures foundational information:
- Name and email
- Years in technology/engineering
- Education background (Mechanical Engineering, Computer Science, Self-taught, etc.)

### Step 2: Robotics Background
Assesses robotics experience level:
- Experience type (hobby, academic, industry, startup, research)
- Years of robotics experience
- Number of completed projects
- Previous project descriptions
- Current role

### Step 3: Goals & Interests
Defines learning objectives:
- Primary learning goal (e.g., "Become full-stack roboticist")
- Target robotics domains (Computer Vision, Motion Control, Manipulation, RL, etc.)
- Timeline (1-24 months)
- Hours per week available

### Step 4: Learning Style
Personal learning preference:
- **Hands-on Projects**: Learn by building
- **Theory First**: Understand concepts before implementation
- **Mixed**: Balance of theory and practice

### Step 5: Skill Assessment
Self-assessment in 20+ robotics skills rated 0-100%:
- Programming: Python, C/C++, ROS/ROS2
- Computer Vision: YOLO, OpenCV, 3D Vision
- Control Systems: Motion Planning, PID Control
- Simulation: Gazebo, Isaac Sim
- AI/ML: Reinforcement Learning, Deep Learning
- And more...

### Step 6: Review & Generate
- Summary of profile information
- AI-powered roadmap generation
- Preview of personalized learning path

## AI-Powered Roadmap Generation

Once onboarding completes, RoboMentor uses GPT-4o to generate a customized learning roadmap that adapts to:

### Background Adaptation
- **Industry experience (5+ years)**: Less fundamentals, more advanced topics
- **Self-taught background**: More handholding and foundational concepts
- **Academic focus**: Emphasis on research and theory

### Time-Based Customization
- **10 hours/week**: 6-month comprehensive path
- **30 hours/week**: 2-month intensive program

### Goal-Driven Focus
- **"Waste management automation"**: Focus on mobile robotics, vision, grasping
- **"Research in RL"**: Deep focus on simulation and reinforcement learning

### Skill Gap Integration
- Identifies current proficiency levels
- Creates realistic progression paths
- Includes review modules for weak areas

## Roadmap Structure

Generated roadmaps include:

### Multi-Phase Structure
- **4-6 phases** with clear progression
- **Weekly milestones** and deliverables
- **Estimated time** per phase
- **Success criteria** for completion

### Resources & Projects
- **Curated resources**: Tutorials, documentation, papers
- **Hands-on projects**: Real robotics implementations
- **Skill development tracking**: Measurable proficiency gains

### Example Roadmap: "Full-Stack Robotics for Waste Management"

```
Phase 1: Foundations & Robotics Fundamentals (4 weeks, 40 hours)
├── Skills: ROS2 Basics, Python for Robotics, Linux
├── Milestone: ROS2 "Hello World" node
├── Project: Simple mobile robot simulator
└── Resources: Official ROS2 tutorials

Phase 2: Computer Vision Integration (5 weeks, 50 hours)
├── Skills: YOLO, OpenCV, 3D Vision
├── Milestone: Object detection on live camera feed
├── Project: Waste classification system
└── Resources: YOLOv11 docs, NVIDIA Deepstream guide

Phase 3: Motion Control & Planning (5 weeks, 50 hours)
├── Skills: Kinematics, Motion Planning, ROS2 Control
├── Milestone: Autonomous navigation
├── Project: Path planning algorithm implementation
└── Resources: MoveIt tutorials, control systems courses
```

## Adaptive Learning System

Roadmaps are not static—they evolve based on actual progress:

### Progress-Based Adaptation
- **Ahead of schedule (+20%)**: Compress timeline, add stretch goals
- **Behind schedule (-20%)**: Extend timeline, add review modules
- **Interest changes**: Re-generate roadmap with new context

### Continuous Tracking
- Session logging with engagement scores
- Skill proficiency updates
- Milestone completion tracking
- Automatic adaptation triggers

## Data Model

### UserProfile
```python
{
    "user_id": "uuid",
    "personal_info": {...},
    "robotics_background": {...},
    "goals": {...},
    "learning_style": "Hands-on" | "Theory-first" | "Mixed",
    "skill_assessment": {
        "YOLO": {"level": 75, "confidence": 85, "projects": 3},
        "ROS2": {"level": 40, "confidence": 60, "projects": 1},
        # ... 18+ more skills
    },
    "onboarding_complete": true
}
```

### AdaptiveRoadmap
```python
{
    "roadmap_id": "uuid",
    "user_id": "uuid",
    "title": "Personalized Robotics Learning Path",
    "phases": [
        {
            "phase_number": 1,
            "title": "Foundations",
            "duration_weeks": 4,
            "estimated_hours": 40,
            "skills_to_develop": [...],
            "milestones": [...],
            "resources": [...],
            "projects": [...]
        }
    ],
    "current_phase": 1,
    "overall_progress": 0.0,
    "adaptations": [...]
}
```

## Integration with Learning System

### Dashboard Integration
After onboarding, the dashboard displays:
- Current phase progress
- Roadmap timeline visualization
- Weekly milestones
- Recommended resources
- Skill development heatmap

### Session Tracking
Learning sessions automatically link to roadmap phases:
- Progress updates trigger roadmap advancement
- Engagement scores inform adaptation decisions
- Completed milestones unlock next phases

## API Endpoints

### Onboarding APIs
- `POST /api/onboarding/start-onboarding` - Create user profile
- `POST /api/onboarding/complete-onboarding/{user_id}` - Generate roadmap
- `GET /api/onboarding/roadmap/{user_id}` - Retrieve active roadmap
- `PUT /api/onboarding/roadmap/{roadmap_id}/update-progress` - Update progress

## Success Metrics

### Onboarding Effectiveness
- Completion rate (% of users finishing all 6 steps)
- Time to complete (target: <20 minutes)
- Roadmap clarity (user satisfaction surveys)

### Learning Outcomes
- Goal achievement rate (% of users hitting timeline targets)
- Skill growth (pre/post proficiency improvements)
- Project completion rates

## Implementation

The onboarding system is implemented across multiple components:

### Backend Components
- `models/onboarding.py` - UserProfile and AdaptiveRoadmap models
- `services/roadmap_generator.py` - AI-powered roadmap generation
- `api/onboarding.py` - REST API endpoints

### Frontend Components
- `onboarding.html` - 6-step form interface
- `onboarding.js` - Form logic and API integration

### Integration Points
- IPC handlers in Electron main process
- Context bridge for secure API access
- Database models and relationships

## Philosophy

> **"Every learner is different. We measure, personalize, and adapt."**

RoboMentor's onboarding embodies the 2026 learning paradigm:
- **Personalized** to background and goals
- **Adaptive** to actual progress
- **Measurable** at every step
- **Domain-aware** for robotics expertise

This creates learning infrastructure that compounds knowledge rather than just consuming content.