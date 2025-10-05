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
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    skipTaskbar: true,
    resizable: false,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    }
  });

  mainWindow.loadFile('renderer/index.html');

  if (process.argv.includes('--dev')) {
    mainWindow.webContents.openDevTools({ mode: 'detach' });
  }

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