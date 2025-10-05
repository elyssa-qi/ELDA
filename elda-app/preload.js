const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  // Existing functions
  nextStep: () => ipcRenderer.send('next-step'),
  needHelp: () => ipcRenderer.send('need-help'),
  closePopup: () => ipcRenderer.send('close-popup'),
  
  // Notify when step changes
  notifyStepChanged: (step) => {
    console.log('Step changed to:', step);
    // You can add ipcRenderer.send here if needed
  },
  
  // Listen for step advancement
  onAdvanceStep: (callback) => {
    ipcRenderer.on('advance-step', callback);
  },
  
  // Listen for tutorial data
  onSetTutorial: (callback) => {
    ipcRenderer.on('set-tutorial', (event, data) => callback(data));
  },
  
  // NEW: Listen for tutorial requests from WebSocket
  onTutorialRequest: (callback) => {
    ipcRenderer.on('new-tutorial-request', (event, data) => {
      callback(data);
    });
  },
  
  // Listen for state changes
  onSetState: (callback) => {
    ipcRenderer.on('set-state', (event, data) => {
      callback(data);
    });
  },

  // Send commands to main process
  sendCommand: (command) => {
    ipcRenderer.send('renderer-command', command);
  }
});