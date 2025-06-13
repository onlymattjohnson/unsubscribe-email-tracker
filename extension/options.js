import { getSettings, saveSettings } from './js/storage.js';
import { testConnection } from './js/api.js';

// DOM Elements
const form = document.getElementById('options-form');
const apiUrlInput = document.getElementById('api-url');
const apiTokenInput = document.getElementById('api-token');
const tokenDisplay = document.getElementById('token-display');
const saveBtn = document.getElementById('save-btn');
const statusMessage = document.getElementById('status-message');
const testConnBtn = document.getElementById('test-conn-btn');
const connStatus = document.getElementById('conn-status');

// Helper to mask the token for display
function maskToken(token) {
    if (!token || token.length < 8) {
        return 'Token is too short to be masked.';
    }
    return `••••••••${token.slice(-4)}`;
}

// Show a general status message
function showStatus(message, isError = false) {
    statusMessage.textContent = message;
    statusMessage.className = `status-message ${isError ? 'status-error' : 'status-success'}`;
    statusMessage.style.display = 'block';
    setTimeout(() => { statusMessage.style.display = 'none'; }, 3000);
}

// Show the connection test status
function showConnStatus(message, isError = false) {
    connStatus.innerHTML = message; // Use innerHTML to render spinner
    connStatus.className = `conn-status ${isError ? 'conn-error' : 'conn-success'}`;
    connStatus.style.display = 'block';
}

// Load saved options
async function restoreOptions() {
    const settings = await getSettings();
    apiUrlInput.value = settings.apiUrl || '';
    apiTokenInput.value = settings.apiToken || '';
    if (settings.apiToken) {
        tokenDisplay.textContent = `Current token: ${maskToken(settings.apiToken)}`;
    }
}

// Save options
async function handleSave(e) {
    e.preventDefault();
    saveBtn.disabled = true;
    saveBtn.textContent = 'Saving...';
    try {
        await saveSettings({
            apiUrl: apiUrlInput.value.trim(),
            apiToken: apiTokenInput.value.trim()
        });
        showStatus('Settings saved successfully!');
        await restoreOptions(); // Refresh display
    } catch (error) {
        showStatus(`Error saving settings: ${error.message}`, true);
    } finally {
        saveBtn.disabled = false;
        saveBtn.textContent = 'Save Settings';
    }
}

// Test connection
async function handleTestConnection() {
    testConnBtn.disabled = true;
    showConnStatus('<span class="spinner"></span> Testing...');

    const apiUrl = apiUrlInput.value.trim();
    const apiToken = apiTokenInput.value.trim();
    
    const result = await testConnection(apiUrl, apiToken);
    
    showConnStatus(result.message, !result.success);
    testConnBtn.disabled = false;
}

// Event Listeners
document.addEventListener('DOMContentLoaded', restoreOptions);
form.addEventListener('submit', handleSave);
testConnBtn.addEventListener('click', handleTestConnection);