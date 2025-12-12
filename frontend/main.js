const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const http = require('http');
const https = require('https');
const { spawn } = require('child_process');

let mainWindow;
let backendProcess = null;

function checkBackendHealth() {
  return new Promise((resolve) => {
    const req = http.get(`${BACKEND_URL}/health`, (res) => {
      if (res.statusCode === 200) {
        resolve(true);
      } else {
        resolve(false);
      }
    });

    req.on('error', () => {
      resolve(false);
    });

    req.setTimeout(5000, () => {
      req.destroy();
      resolve(false);
    });
  });
}

function startBackend() {
  const isPackaged = app.isPackaged;
  const backendPath = isPackaged
    ? path.join(process.resourcesPath, 'robomentor-backend')
    : path.join(__dirname, '..', 'backend', 'dist', 'robomentor-backend');

  console.log('Starting backend from:', backendPath);

  backendProcess = spawn(backendPath, [], {
    stdio: ['ignore', 'pipe', 'pipe'],
    detached: false,
    env: { ...process.env, PYTHONUNBUFFERED: '1' }
  });

  backendProcess.stdout.on('data', (data) => {
    console.log('Backend stdout:', data.toString());
  });

  backendProcess.stderr.on('data', (data) => {
    console.error('Backend stderr:', data.toString());
  });

  backendProcess.on('close', (code) => {
    console.log(`Backend process exited with code ${code}`);
    backendProcess = null;
  });

  backendProcess.on('error', (err) => {
    console.error('Failed to start backend:', err);
  });

  // Wait for backend to be healthy
  return new Promise(async (resolve) => {
    let attempts = 0;
    const maxAttempts = 30; // 30 seconds max

    const checkHealth = async () => {
      attempts++;
      const isHealthy = await checkBackendHealth();

      if (isHealthy) {
        console.log('Backend is healthy and ready');
        resolve();
      } else if (attempts >= maxAttempts) {
        console.error('Backend failed to start within timeout');
        resolve(); // Continue anyway, let the app handle errors
      } else {
        setTimeout(checkHealth, 1000);
      }
    };

    // Initial delay before first check
    setTimeout(checkHealth, 2000);
  });
}

function stopBackend() {
  if (backendProcess) {
    console.log('Stopping backend process...');
    backendProcess.kill('SIGTERM');

    // Give it time to shut down gracefully
    setTimeout(() => {
      if (backendProcess) {
        backendProcess.kill('SIGKILL');
      }
    }, 5000);
  }
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
    },
  });

  // Load the built React app
  if (process.env.NODE_ENV === 'development') {
    mainWindow.loadURL('http://localhost:3000');
  } else {
    mainWindow.loadFile(path.join(__dirname, 'index.html'));
  }

  // Open DevTools in development
  if (process.env.NODE_ENV === 'development') {
    mainWindow.webContents.openDevTools();
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.whenReady().then(async () => {
  await startBackend();
  createWindow();
});

app.on('window-all-closed', () => {
  stopBackend();
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

app.on('before-quit', () => {
  stopBackend();
});

// Backend API configuration
const BACKEND_HOST = 'localhost';
const BACKEND_PORT = 8000;
const BACKEND_URL = `http://${BACKEND_HOST}:${BACKEND_PORT}`;

// Helper function to make HTTP requests to backend
async function makeBackendRequest(endpoint, method = 'GET', data = null) {
  return new Promise((resolve, reject) => {
    const url = `${BACKEND_URL}${endpoint}`;
    const options = {
      method: method,
      headers: {
        'Content-Type': 'application/json',
      },
    };

    const req = http.request(url, options, (res) => {
      let body = '';
      res.on('data', (chunk) => {
        body += chunk;
      });
      res.on('end', () => {
        try {
          const response = JSON.parse(body);
          if (res.statusCode >= 200 && res.statusCode < 300) {
            resolve(response);
          } else {
            reject(new Error(`HTTP ${res.statusCode}: ${response.detail || response.message || 'Unknown error'}`));
          }
        } catch (e) {
          reject(new Error('Invalid JSON response from backend'));
        }
      });
    });

    req.on('error', (err) => {
      reject(new Error(`Backend connection failed: ${err.message}`));
    });

    if (data) {
      req.write(JSON.stringify(data));
    }
    req.end();
  });
}

// IPC handlers for communication with backend
ipcMain.handle('send-chat-message', async (event, message) => {
  try {
    const response = await makeBackendRequest('/api/chat/message', 'POST', message);
    return response;
  } catch (error) {
    console.error('Backend chat error:', error);
    throw error;
  }
});

ipcMain.handle('generate-quiz', async (event, { topic, difficulty, numQuestions }) => {
  try {
    const response = await makeBackendRequest('/api/quiz/generate', 'POST', {
      topic,
      difficulty: difficulty || 'intermediate',
      num_questions: numQuestions || 5
    });
    return response;
  } catch (error) {
    console.error('Backend quiz generation error:', error);
    throw error;
  }
});

ipcMain.handle('get-learning-paths', async () => {
  try {
    const response = await makeBackendRequest('/api/paths/active');
    return response;
  } catch (error) {
    console.error('Backend learning paths error:', error);
    throw error;
  }
});

ipcMain.handle('create-learning-path', async (event, { skills, goals, hoursPerWeek }) => {
  try {
    const response = await makeBackendRequest('/api/paths/create', 'POST', {
      user_skills: skills,
      user_goals: goals,
      hours_per_week: hoursPerWeek || 10
    });
    return response;
  } catch (error) {
    console.error('Backend create path error:', error);
    throw error;
  }
});

ipcMain.handle('get-skills-profile', async () => {
  try {
    const response = await makeBackendRequest('/api/skills/profile');
    return response;
  } catch (error) {
    console.error('Backend skills profile error:', error);
    throw error;
  }
});

ipcMain.handle('get-active-goals', async () => {
  try {
    const response = await makeBackendRequest('/api/goals/active');
    return response;
  } catch (error) {
    console.error('Backend active goals error:', error);
    throw error;
  }
});

ipcMain.handle('create-goal', async (event, { title, description, domain, timeframeWeeks }) => {
  try {
    const response = await makeBackendRequest('/api/goals/create', 'POST', {
      title,
      description,
      domain,
      timeframe_weeks: timeframeWeeks || 12
    });
    return response;
  } catch (error) {
    console.error('Backend create goal error:', error);
    throw error;
  }
});