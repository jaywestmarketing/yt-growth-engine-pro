const { app, BrowserWindow, dialog } = require("electron");
const { spawn } = require("child_process");
const path = require("path");
const http = require("http");

const PORT = 8080;
let pyProcess = null;
let mainWindow = null;

function findPython() {
  const candidates = ["python3.11", "python3.10", "python3.9", "python3", "python"];
  for (const cmd of candidates) {
    try {
      require("child_process").execSync(`${cmd} --version`, { stdio: "ignore" });
      return cmd;
    } catch (_) {
      // try next
    }
  }
  return null;
}

function startPython() {
  const pythonCmd = findPython();
  if (!pythonCmd) {
    dialog.showErrorBox(
      "Python Not Found",
      "Python 3 is required but was not found on your system.\n\nInstall from: https://www.python.org/downloads/"
    );
    app.quit();
    return;
  }

  const scriptPath = path.join(__dirname, "..", "web_app.py");
  pyProcess = spawn(pythonCmd, [scriptPath, "--no-browser"], {
    cwd: path.join(__dirname, ".."),
    env: { ...process.env, ELECTRON_MODE: "1" },
  });

  pyProcess.stdout.on("data", (data) => {
    console.log(`[Python] ${data}`);
  });

  pyProcess.stderr.on("data", (data) => {
    console.error(`[Python] ${data}`);
  });

  pyProcess.on("error", (err) => {
    dialog.showErrorBox("Python Error", `Failed to start Python backend:\n${err.message}`);
  });

  pyProcess.on("exit", (code) => {
    console.log(`Python process exited with code ${code}`);
    if (code !== 0 && code !== null) {
      dialog.showErrorBox("Backend Error", `Python backend crashed (exit code ${code}).`);
    }
  });
}

function waitForServer(retries, delay) {
  return new Promise((resolve, reject) => {
    const attempt = (remaining) => {
      const req = http.get(`http://localhost:${PORT}`, (res) => {
        resolve();
      });
      req.on("error", () => {
        if (remaining > 0) {
          setTimeout(() => attempt(remaining - 1), delay);
        } else {
          reject(new Error("Server did not start in time"));
        }
      });
      req.setTimeout(1000, () => {
        req.destroy();
        if (remaining > 0) {
          setTimeout(() => attempt(remaining - 1), delay);
        } else {
          reject(new Error("Server timeout"));
        }
      });
    };
    attempt(retries);
  });
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1000,
    minHeight: 700,
    title: "RealE Tube",
    backgroundColor: "#0D0D0D",
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    },
  });

  mainWindow.loadURL(`http://localhost:${PORT}`);

  mainWindow.on("closed", () => {
    mainWindow = null;
  });
}

app.on("ready", async () => {
  startPython();

  try {
    await waitForServer(30, 500); // Wait up to 15 seconds
    createWindow();
  } catch (err) {
    dialog.showErrorBox(
      "Startup Error",
      "Could not connect to Python backend.\nMake sure Python 3 is installed and dependencies are available."
    );
    app.quit();
  }
});

app.on("window-all-closed", () => {
  app.quit();
});

app.on("will-quit", () => {
  if (pyProcess) {
    pyProcess.kill();
    pyProcess = null;
  }
});
