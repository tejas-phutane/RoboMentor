// Renderer process JavaScript for RoboMentor Electron App

// Screen management
function showScreen(screenId) {
  // Hide all screens
  const screens = document.querySelectorAll('.screen');
  screens.forEach(screen => screen.classList.remove('active'));

  // Show selected screen
  const targetScreen = document.getElementById(screenId);
  if (targetScreen) {
    targetScreen.classList.add('active');
  }
}

// Error handling
function showErrorMessage(message) {
  // Create or update error message element
  let errorDiv = document.getElementById('error-message');
  if (!errorDiv) {
    errorDiv = document.createElement('div');
    errorDiv.id = 'error-message';
    errorDiv.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: #ff4444;
      color: white;
      padding: 10px 15px;
      border-radius: 5px;
      z-index: 1000;
      max-width: 300px;
    `;
    document.body.appendChild(errorDiv);
  }
  errorDiv.textContent = message;
  errorDiv.style.display = 'block';

  // Auto-hide after 5 seconds
  setTimeout(() => {
    errorDiv.style.display = 'none';
  }, 5000);
}

// Initialize app
document.addEventListener('DOMContentLoaded', async () => {
  // Load user data on startup
  try {
    const [skillsProfile, activeGoals, learningPaths] = await Promise.all([
      window.electronAPI.getSkillsProfile(),
      window.electronAPI.getActiveGoals(),
      window.electronAPI.getLearningPaths()
    ]);
    updateDashboard(skillsProfile, activeGoals, learningPaths);
  } catch (error) {
    console.error('Failed to load user data:', error);
    // Show error message to user
    showErrorMessage('Failed to load dashboard data. Please check if the backend is running.');
  }

  // Show dashboard by default
  showScreen('dashboard');
});

// Update dashboard with user data
function updateDashboard(skillsProfile, activeGoals, learningPaths) {
  // Update skills count
  const skillsCount = skillsProfile.profile ? Object.keys(skillsProfile.profile).length : 0;
  document.getElementById('skills-count').textContent = skillsCount;

  // Update goals count
  document.getElementById('goals-count').textContent = activeGoals.goals.length;

  // Update learning paths count
  document.getElementById('paths-count').textContent = learningPaths.paths.length;

  // Update activity list based on real data
  const activityList = document.getElementById('activity-list');
  const activities = [];

  if (activeGoals.goals.length > 0) {
    activities.push(`Active goals: ${activeGoals.goals.length}`);
  }
  if (learningPaths.paths.length > 0) {
    activities.push(`Learning paths: ${learningPaths.paths.length}`);
  }
  if (skillsCount > 0) {
    activities.push(`Skills tracked: ${skillsCount}`);
  }

  if (activities.length === 0) {
    activities.push('No activity yet - start by creating a goal or learning path!');
  }

  activityList.innerHTML = activities.map(activity => `<li>${activity}</li>`).join('');
}

// Chat functionality
async function sendMessage() {
  const input = document.getElementById('message-input');
  const message = input.value.trim();

  if (!message) return;

  // Add user message to chat
  addMessageToChat(message, 'user');
  input.value = '';

  try {
    // Send to backend via IPC
    const response = await window.electronAPI.sendChatMessage(message);

    // Add bot response to chat
    addMessageToChat(response.response, 'bot');
  } catch (error) {
    console.error('Failed to send message:', error);
    addMessageToChat('Sorry, I encountered an error communicating with the backend. Please check if the server is running.', 'bot');
  }
}

function addMessageToChat(message, sender) {
  const chatMessages = document.getElementById('chat-messages');
  const messageElement = document.createElement('div');
  messageElement.className = `message ${sender}`;
  messageElement.textContent = message;
  chatMessages.appendChild(messageElement);

  // Scroll to bottom
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Handle Enter key in chat input
document.getElementById('message-input').addEventListener('keypress', (e) => {
  if (e.key === 'Enter') {
    sendMessage();
  }
});

// Learning planner functionality
async function loadGoals() {
  try {
    const goalsData = await window.electronAPI.getActiveGoals();
    const goalsList = document.getElementById('goals-list');
    if (goalsData.goals && goalsData.goals.length > 0) {
      goalsList.innerHTML = goalsData.goals.map(goal =>
        `<li>${goal.title}: ${goal.description}</li>`
      ).join('');
    } else {
      goalsList.innerHTML = '<li>No active goals yet. Create your first goal!</li>';
    }
  } catch (error) {
    console.error('Failed to load goals:', error);
    showErrorMessage('Failed to load goals from backend.');
  }
}

// Create new goal
async function createNewGoal() {
  const title = prompt('Enter goal title:');
  if (!title) return;

  const description = prompt('Enter goal description:');
  if (!description) return;

  const domain = prompt('Enter domain (e.g., Python, Robotics, AI):');
  if (!domain) return;

  try {
    await window.electronAPI.createGoal({
      title,
      description,
      domain,
      timeframeWeeks: 12
    });
    showErrorMessage('Goal created successfully!');
    loadGoals(); // Refresh goals list
  } catch (error) {
    console.error('Failed to create goal:', error);
    showErrorMessage('Failed to create goal.');
  }
}

// Create learning path
async function createLearningPath() {
  const skills = prompt('Enter your current skills (comma-separated):');
  if (!skills) return;

  const goals = prompt('Enter your learning goals (comma-separated):');
  if (!goals) return;

  const hoursPerWeek = parseInt(prompt('Hours per week for learning:', '10')) || 10;

  try {
    const skillsArray = skills.split(',').map(s => s.trim());
    const goalsArray = goals.split(',').map(g => g.trim());

    await window.electronAPI.createLearningPath({
      skills: skillsArray,
      goals: goalsArray,
      hoursPerWeek
    });
    showErrorMessage('Learning path created successfully!');
    // Refresh dashboard data
    location.reload();
  } catch (error) {
    console.error('Failed to create learning path:', error);
    showErrorMessage('Failed to create learning path.');
  }
}

// Generate quiz
async function generateQuiz() {
  const topic = prompt('Enter quiz topic:');
  if (!topic) return;

  const difficulty = prompt('Enter difficulty (beginner/intermediate/advanced):', 'intermediate');
  const numQuestions = parseInt(prompt('Number of questions:', '5')) || 5;

  try {
    const quizData = await window.electronAPI.generateQuiz({
      topic,
      difficulty,
      numQuestions
    });
    console.log('Generated quiz:', quizData);
    showErrorMessage('Quiz generated! Check console for details.');
  } catch (error) {
    console.error('Failed to generate quiz:', error);
    showErrorMessage('Failed to generate quiz.');
  }
}

// Add event listeners for learning planner actions
document.addEventListener('DOMContentLoaded', () => {
  // Add buttons for creating goals and paths if they don't exist
  const plannerContent = document.querySelector('.planner-content');
  if (plannerContent) {
    const actionsDiv = document.createElement('div');
    actionsDiv.innerHTML = `
      <div style="margin-bottom: 20px;">
        <button onclick="createNewGoal()" style="margin-right: 10px;">Create New Goal</button>
        <button onclick="createLearningPath()" style="margin-right: 10px;">Create Learning Path</button>
        <button onclick="generateQuiz()">Generate Quiz</button>
      </div>
    `;
    plannerContent.insertBefore(actionsDiv, plannerContent.firstChild);
  }
});

// Load goals when learning planner screen is shown
document.addEventListener('click', (e) => {
  if (e.target.textContent === 'Learning Planner') {
    loadGoals();
  }
});

// Settings functionality
document.querySelector('form').addEventListener('submit', (e) => {
  e.preventDefault();

  const username = document.getElementById('username').value;
  const theme = document.getElementById('theme').value;
  const notifications = document.getElementById('notifications').checked;

  // Save settings (mock implementation)
  console.log('Settings saved:', { username, theme, notifications });
  alert('Settings saved successfully!');
});

// Theme switching (basic implementation)
document.getElementById('theme').addEventListener('change', (e) => {
  const theme = e.target.value;
  document.body.className = theme === 'dark' ? 'dark-theme' : '';
});