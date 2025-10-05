const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  nextStep: () => ipcRenderer.send('next-step'),
  needHelp: () => ipcRenderer.send('need-help'),
  closePopup: () => ipcRenderer.send('close-popup'),
  onAdvanceStep: (callback) => ipcRenderer.on('advance-step', callback),
  onSetTutorial: (callback) => ipcRenderer.on('set-tutorial', (event, data) => callback(data))
});