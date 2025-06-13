import { getSettings } from './js/storage.js';
import { createUnsubscribedEmail } from './js/api.js';
import * as ui from './js/ui.js';

const form = document.getElementById('unsub-form');
const optionsLink = document.getElementById('options-link');

/**
 * Handles the main form submission logic.
 */
async function handleSubmit(event) {
    event.preventDefault();
    if (!form.checkValidity()) {
        ui.showMessage('Please fill out all required fields.', 'error');
        return;
    }

    ui.showLoading();

    try {
        const { apiUrl, apiToken } = await getSettings();
        if (!apiUrl || !apiToken) {
            throw new Error('API settings are not configured. Please go to the options page.');
        }

        const payload = {
            sender_name: document.getElementById('sender-name').value,
            sender_email: document.getElementById('sender-email').value,
            unsub_method: document.querySelector('input[name="unsub-method"]:checked').value,
        };

        const data = await createUnsubscribedEmail(apiUrl, apiToken, payload);
        ui.showMessage(`Success! Tracked with ID: ${data.id}`, 'success');
        ui.clearForm();

    } catch (error) {
        console.error('Submission failed:', error);
        handleApiError(error);
    } finally {
        ui.hideLoading();
    }
}

/**
 * Handles different types of API errors and displays appropriate messages.
 * @param {Error} error - The error object from the API call.
 */
function handleApiError(error) {
    if (error.status === 401) {
        ui.showMessage('Authentication failed. Your API Token may be invalid. <a href="#" id="error-options-link">Go to Options</a>', 'error');
        // Add a listener to the new link
        document.getElementById('error-options-link')?.addEventListener('click', openOptions);
    } else if (error.status === 429) {
        ui.showMessage('Rate limit exceeded. Please try again later.', 'error');
    } else if (error.status === 422) {
        // Handle validation errors from the API
        const details = error.data?.detail?.[0]?.msg || 'Invalid data.';
        ui.showMessage(`Validation Error: ${details}`, 'error');
    } else {
        ui.showMessage(error.message || 'An unknown error occurred.', 'error');
    }
}

function openOptions(e) {
    if(e) e.preventDefault();
    chrome.runtime.openOptionsPage();
}

// --- Initialize ---
document.addEventListener('DOMContentLoaded', ui.autoFocus);
form.addEventListener('submit', handleSubmit);
optionsLink.addEventListener('click', openOptions);