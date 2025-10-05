const { app, BrowserWindow, ipcMain, screen } = require('electron');
const path = require('path');
const WebSocket = require('ws');

let mainWindow;
let wss;

function createWindow() {
  const primaryDisplay = screen.getPrimaryDisplay();
  const { width, height } = primaryDisplay.workAreaSize;

  mainWindow = new BrowserWindow({
    width: 580,
    height: 450,
    x: width - 600,
    y: 20,
    frame: true,
    transparent: false,
    alwaysOnTop: true,
    skipTaskbar: false,
    resizable: false,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    }
  });

  mainWindow.loadFile('renderer/index.html');

  // Always open dev tools for debugging
  mainWindow.webContents.openDevTools({ mode: 'detach' });

  mainWindow.on('close', (event) => {
    if (!app.isQuitting) {
      event.preventDefault();
      mainWindow.hide();
    }
  });
}

function startWebSocketServer() {
  wss = new WebSocket.Server({ port: 8765 });

  wss.on('connection', (ws) => {
    console.log('Python client connected');

    ws.on('message', (message) => {
      const data = JSON.parse(message);
      console.log('Received from Python:', data);

      switch (data.command) {
        case 'show':
          console.log('Showing window...');
          mainWindow.show();
          mainWindow.focus();
          break;
        case 'showListening':
          console.log('Showing listening state...');
          mainWindow.show();
          mainWindow.focus();
          mainWindow.webContents.send('set-state', { state: 'listening' });
          break;
        case 'hide':
          mainWindow.hide();
          break;
        case 'nextStep':
          mainWindow.webContents.send('next-step');
          break;
        case 'setTutorial':
          mainWindow.webContents.send('set-tutorial', data.tutorial);
          break;
        case 'showHowTo':
          // New: Handle how-to tutorial requests
          console.log('Showing how-to window with transcription:', data.transcription);
          mainWindow.show();
          mainWindow.focus();
          mainWindow.webContents.send('new-tutorial-request', { 
            transcription: data.transcription 
          });
          break;
        case 'showTutorial':
          // Switch to full tutorial mode
          console.log('Switching to full tutorial mode...');
          mainWindow.webContents.send('set-state', { state: 'tutorial' });
          break;
        default:
          console.log('Unknown command:', data.command);
      }
    });

    ws.on('close', () => {
      console.log('Python client disconnected');
    });
  });

  console.log('WebSocket server running on ws://localhost:8765');
}

ipcMain.on('next-step', () => {
  mainWindow.webContents.send('advance-step');
});

ipcMain.on('need-help', () => {
  console.log('User needs more help');
  broadcastToPython({ event: 'need-help' });
});

ipcMain.on('close-popup', () => {
  mainWindow.hide();
});

ipcMain.on('renderer-command', (event, command) => {
  console.log('Received command from renderer:', command);
  // Handle the command as if it came from WebSocket
  const mockData = { command };
  switch (command) {
    case 'showTutorial':
      mainWindow.webContents.send('set-state', { state: 'tutorial' });
      break;
    default:
      console.log('Unknown renderer command:', command);
  }
});

function broadcastToPython(data) {
  wss.clients.forEach((client) => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(JSON.stringify(data));
    }
  });
}

app.whenReady().then(() => {
  createWindow();
  startWebSocketServer();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  app.isQuitting = true;
  if (wss) {
    wss.close();
  }
});