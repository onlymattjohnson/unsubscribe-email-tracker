// Get all relevant DOM elements once
const elements = {
    form: document.getElementById('unsub-form'),
    submitBtn: document.getElementById('submit-btn'),
    statusMessage: document.getElementById('status-message'),
    senderNameInput: document.getElementById('sender-name')
};

/**
 * Displays a status message in the designated area.
 * @param {string} message - The message to display. Can include HTML.
 * @param {'success' | 'error' | 'info'} type - The type of message.
 */
export function showMessage(message, type = 'info') {
    elements.statusMessage.innerHTML = message;
    elements.statusMessage.className = `status-message status-${type}`;
    elements.statusMessage.style.display = 'block';
}

/**
 * Shows the loading state on the submit button.
 */
export function showLoading() {
    elements.submitBtn.disabled = true;
    elements.submitBtn.innerHTML = '<span class="spinner"></span> Tracking...';
}

/**
 * Hides the loading state and re-enables the submit button.
 */
export function hideLoading() {
    elements.submitBtn.disabled = false;
    elements.submitBtn.innerHTML = 'Track It';
}

/**
 * Clears the form inputs.
 */
export function clearForm() {
    elements.form.reset();
    elements.senderNameInput.focus(); // Re-focus the first field
}

/**
 * Auto-focuses the first form field.
 */
export function autoFocus() {
    elements.senderNameInput.focus();
}