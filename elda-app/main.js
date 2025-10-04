const { app, BrowserWindow, ipcMain, screen } = require('electron');
const path = require('path');
const WebSocket = require('ws');

let mainWindow;
let wss;

function createWindow() {
  // Get primary display dimensions
  const primaryDisplay = screen.getPrimaryDisplay();
  const { width, height } = primaryDisplay.workAreaSize;

  mainWindow = new BrowserWindow({
    width: 580,
    height: 450,
    x: width - 600, // Position 20px from right edge
    y: 20, // Position 20px from top
    frame: false, // Frameless window
    transparent: true, // Transparent background for rounded corners
    alwaysOnTop: true, // Always stay on top
    skipTaskbar: true, // Don't show in taskbar
    resizable: false,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    }
  });

  mainWindow.loadFile('renderer/index.html');

  // Optional: Open DevTools in development
  if (process.argv.includes('--dev')) {
    mainWindow.webContents.openDevTools({ mode: 'detach' });
  }

  // Prevent window from being closed, just hide it instead
  mainWindow.on('close', (event) => {
    if (!app.isQuitting) {
      event.preventDefault();
      mainWindow.hide();
    }
  });
}

// WebSocket server for Python communication
function startWebSocketServer() {
  wss = new WebSocket.Server({ port: 8765 });

  wss.on('connection', (ws) => {
    console.log('Python client connected');

    ws.on('message', (message) => {
      const data = JSON.parse(message);
      console.log('Received from Python:', data);

      // Handle different commands from Python
      switch (data.command) {
        case 'show':
          mainWindow.show();
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

// IPC handlers
ipcMain.on('next-step', () => {
  mainWindow.webContents.send('advance-step');
});

ipcMain.on('need-help', () => {
  console.log('User needs more help');
  // You can send this back to Python or handle it here
  broadcastToPython({ event: 'need-help' });
});

ipcMain.on('close-popup', () => {
  mainWindow.hide();
});

ipcMain.on('minimize-popup', () => {
  mainWindow.minimize();
});

// Broadcast messages to all connected Python clients
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