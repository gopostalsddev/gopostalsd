// Import required Electron modules
const { app, BrowserWindow } = require('electron');
const path = require('path');

let mainWindow;

// Initialize the app when Electron is ready
app.whenReady().then(() => {
    // Create the main application window
    mainWindow = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            //preload: path.join(__dirname, "preload.js"),
            nodeIntegration: true,  // Enable Node.js integration in renderer process
            contextIsolation: false  // Ensures compatibility
        }
    });

    // Load the main HTML file
    mainWindow.loadFile('index.html');

    // Handle macOS app activation
    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) createWindow();
    });
});

// Quit the app when all windows are closed (except on macOS)
app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit();
});