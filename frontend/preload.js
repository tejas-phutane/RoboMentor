const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // Chat functionality
  sendChatMessage: (message) => ipcRenderer.invoke('send-chat-message', message),

  // Quiz functionality
  generateQuiz: (params) => ipcRenderer.invoke('generate-quiz', params),

  // Learning paths
  getLearningPaths: () => ipcRenderer.invoke('get-learning-paths'),
  createLearningPath: (params) => ipcRenderer.invoke('create-learning-path', params),

  // Skills and goals
  getSkillsProfile: () => ipcRenderer.invoke('get-skills-profile'),
  getActiveGoals: () => ipcRenderer.invoke('get-active-goals'),
  createGoal: (params) => ipcRenderer.invoke('create-goal', params),
});