const fs = require('fs');
const path = require('path');

let lastExecutedButton = null;
let shouldClearConsole = true;

document.addEventListener("DOMContentLoaded", () => {

    const clearConsoleCheckbox = document.getElementById("clearConsoleToggle");
    clearConsoleCheckbox.addEventListener("change", (e) => {
        shouldClearConsole = e.target.checked;
    });


    // Load config.json dynamically
    const configPath = path.join(__dirname, "config.json");
    fs.readFile(configPath, "utf8", (err, data) => {
        if (err) {
            console.error("Error loading config.json:", err);
            return;
        }

        const config = JSON.parse(data);
        loadTasks(config)
    });
});


function updateConsoleOutput(message, type = "info") {
    const consoleOutput = document.getElementById("consoleOutput");

    // Generate timestamp
    const timestamp = new Date().toLocaleTimeString();
    const formattedMessage = `[${timestamp}] ${message}`;

    // Create a log entry
    const logElement = document.createElement("div");
    logElement.textContent = formattedMessage;

    // Apply different colors based on log type
    if (type === "error") {
        // logElement.style.color = "#F44336";  Red for errors 
        logElement.style.color = "#43f601"; // Light green for standard output
    } else {
        logElement.style.color = "#43f601"; // Light green for standard output
    }

    // Append log entry to console panel
    consoleOutput.appendChild(logElement);
    
    // Ensure the console auto-scrolls to the latest message
    consoleOutput.scrollTop = consoleOutput.scrollHeight;
}

// Function to execute task command via Electron's child_process
function executeTask(task, activeButton) {
    
    // Clear only if setting is enabled
    if (shouldClearConsole) {
        const consoleOutput = document.getElementById("consoleOutput");
        consoleOutput.innerHTML = "";
    }

    // Highlight the current task button
    activeButton.classList.add("active-task");
    lastExecutedButton = activeButton;

    // Show running state
    activeButton.disabled = true;
    activeButton.textContent = `${task.name} (Running...)`;

    updateConsoleOutput(`Executing: ${task.command}`, "info");
    const process = require("child_process").exec(task.command);

    process.stdout.on("data", (data) => updateConsoleOutput(data, "info"));
    process.stderr.on("data", (data) => updateConsoleOutput(data, "error"));

    process.on("exit", (code) => {
        if (code === 0 || code === 15) {
            updateConsoleOutput(`Process exited successfully with code ${code}`, "info");
        } else {
            updateConsoleOutput(`Error: Task execution failed with code ${code}`, "error");
        }

        // Task No Longer Active
        activeButton.disabled = false;
        activeButton.textContent = `${task.name}`;
        activeButton.classList.remove("active-task");

        // Reset previous task button style
        if (lastExecutedButton) {
            lastExecutedButton.classList.remove("active-task");
        }
    });
}

/// Modify createTaskButton to pass button reference to executeTask
function createTaskButton(container, task) {
    const button = document.createElement("button");
    button.textContent = task.name;
    button.title = task.description;
    button.className = "task-button";

    // Pass button reference to executeTask for status updates
    button.addEventListener("click", () => {
        executeTask(task, button);
    });

    container.appendChild(button);
}


function loadTasks(config) {
    const backendContainer = document.getElementById("backendTasks");
    const frontendContainer = document.getElementById("frontendTasks");

    config.backend_tasks.forEach(task => {
        createTaskButton(backendContainer, task);
    });

    config.frontend_tasks.forEach(task => {
        createTaskButton(frontendContainer, task);
    });
}

// Helper function to set active tab
function setActiveTab(tabId) {
    document.querySelectorAll('#sidebar button').forEach(btn => btn.classList.remove('active'));
    document.getElementById(tabId).classList.add('active');
}

// Helper function to show the correct section
function showSection(sectionId) {
    document.querySelectorAll(".task-section").forEach(section => section.style.display = "none");
    document.getElementById(sectionId).style.display = "block";
}

document.getElementById("backendTab").addEventListener("click", () => {
    setActiveTab("backendTab");
    showSection("backendTasks");
    lastExecutedButton = null;
});

document.getElementById("frontendTab").addEventListener("click", () => {
    setActiveTab("frontendTab");
    showSection("frontendTasks");
    lastExecutedButton = null;
});

document.getElementById("settingsTab").addEventListener("click", () => {
    setActiveTab("settingsTab");
    showSection("settingsContainer");
});

