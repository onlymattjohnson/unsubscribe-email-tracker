const form = document.getElementById('options-form');
const apiUrlInput = document.getElementById('api-url');
const apiTokenInput = document.getElementById('api-token');
const statusMessage = document.getElementById('status-message');

// Function to display status messages
function showStatus(message, isError = false) {
    statusMessage.textContent = message;
    statusMessage.className = 'status-message'; // Reset classes
    if (isError) {
        statusMessage.classList.add('status-error');
    } else {
        statusMessage.classList.add('status-success');
    }
    statusMessage.style.display = 'block';
}

// Save options to chrome.storage.local
function saveOptions(e) {
    e.preventDefault();
    const apiUrl = apiUrlInput.value.trim();
    const apiToken = apiTokenInput.value.trim();

    if (!apiUrl || !apiToken) {
        showStatus('Both API URL and Token are required.', true);
        return;
    }

    chrome.storage.local.set({
        apiUrl: apiUrl,
        apiToken: apiToken
    }, () => {
        showStatus('Settings saved successfully!');
        setTimeout(() => { statusMessage.style.display = 'none'; }, 2000);
    });
}

// Load saved options when the page loads
function restoreOptions() {
    chrome.storage.local.get(['apiUrl', 'apiToken'], (result) => {
        apiUrlInput.value = result.apiUrl || '';
        apiTokenInput.value = result.apiToken || '';
    });
}

document.addEventListener('DOMContentLoaded', restoreOptions);
form.addEventListener('submit', saveOptions);