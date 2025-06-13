import { getSettings } from './js/storage.js';
import { createUnsubscribedEmail } from './js/api.js';
import * as ui from './js/ui.js';

// We need to reference the function to inject it.
// The bundler (or in our case, the browser) won't use this import path,
// but it's good for code organization and potential future build steps.
// For now, we'll have to copy the function text or reference it carefully.
// Let's redefine it here for simplicity in a non-build setup.

// --- Start of Injected Function ---
// This function must be self-contained
function extractEmailData() {
    // Check if we're in an email view
    const emailSubjectEl = document.querySelector('.hP');
    if (!emailSubjectEl) {
        console.log('Not in email view - no subject element found');
        return null;
    }

    let senderName = null;
    let senderEmail = null;

    // Strategy 1: Most reliable - look for elements with email attribute
    const senderElements = document.querySelectorAll('[email]:not([aria-label])');
    console.log(`Found ${senderElements.length} elements with email attribute`);
    
    if (senderElements.length > 0) {
        // Get the first sender (original sender in conversation)
        const senderEl = senderElements[0];
        senderName = senderEl.getAttribute('name') || senderEl.textContent.trim();
        senderEmail = senderEl.getAttribute('email');
        console.log('Strategy 1 success:', { senderName, senderEmail });
    }

    // Strategy 2: Look for sender info in the header area
    if (!senderEmail) {
        // Try to find the sender info in the email header
        const headerContainer = document.querySelector('.iw, .gE');
        if (headerContainer) {
            // Look for email patterns in the header
            const headerText = headerContainer.textContent;
            const emailMatch = headerText.match(/([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/);
            if (emailMatch) {
                senderEmail = emailMatch[1];
                // Try to extract name from nearby text
                const nameMatch = headerText.match(/^([^<\n]+)/);
                if (nameMatch) {
                    senderName = nameMatch[1].trim();
                }
                console.log('Strategy 2 success:', { senderName, senderEmail });
            }
        }
    }

    // Strategy 3: Look for specific Gmail classes
    if (!senderEmail) {
        // Try the go/gD combination
        const nameEl = document.querySelector('.gD');
        const emailEl = document.querySelector('.go, .gD[email]');
        
        if (nameEl) {
            senderName = nameEl.textContent.trim();
        }
        
        if (emailEl) {
            const emailText = emailEl.textContent.trim();
            // Extract email from various formats
            const patterns = [
                /<([^>]+)>/, // <email@example.com>
                /\(([^)]+@[^)]+)\)/, // (email@example.com)
                /([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/ // plain email
            ];
            
            for (const pattern of patterns) {
                const match = emailText.match(pattern);
                if (match) {
                    senderEmail = match[1];
                    break;
                }
            }
        }
        console.log('Strategy 3 result:', { senderName, senderEmail });
    }

    // Strategy 4: Look in the message header area
    if (!senderEmail) {
        const messageHeaders = document.querySelectorAll('.g3, .gE, .a3s');
        for (const header of messageHeaders) {
            const text = header.textContent;
            if (text.includes('@')) {
                const emailMatch = text.match(/([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/);
                if (emailMatch) {
                    senderEmail = emailMatch[1];
                    console.log('Strategy 4 found email:', senderEmail);
                    break;
                }
            }
        }
    }

    // Clean up the data
    if (senderName) {
        // Remove extra whitespace and common suffixes
        senderName = senderName
            .replace(/\s+/g, ' ')
            .replace(/\s*<.*>/, '')
            .replace(/\s*\(.*\)/, '')
            .trim();
    }

    if (senderEmail) {
        senderEmail = senderEmail.toLowerCase().trim();
    }

    // Only return if we have at least an email
    if (senderEmail) {
        return { 
            senderName: senderName || 'Unknown Sender',
            senderEmail 
        };
    }

    console.log('No sender data found');
    return null;
}


const form = document.getElementById('unsub-form');
const optionsLink = document.getElementById('options-link');
const refreshBtn = document.getElementById('refresh-btn');
const senderNameInput = document.getElementById('sender-name');
const senderEmailInput = document.getElementById('sender-email');

/**
 * Injects the extractor script into the active tab and fills the form.
 */
async function injectAndExtractData() {
    console.log('Starting extraction...');
    ui.showMessage('Scanning page...', 'info');
    try {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

        if (!tab || !tab.url || !tab.url.startsWith('https://mail.google.com/')) {
            ui.showMessage('Open an email in Gmail to auto-fill.', 'info');
            return;
        }

        const results = await chrome.scripting.executeScript({
            target: { tabId: tab.id },
            func: extractEmailData, // Pass the function to be executed
        });

        // The result is an array, get the result from the first (and only) frame
        const extractedData = results[0].result;

        if (extractedData) {
            senderNameInput.value = extractedData.senderName;
            senderEmailInput.value = extractedData.senderEmail;
            ui.showMessage('Form auto-filled from Gmail!', 'success');
        } else {
            ui.showMessage('Could not find sender info. Are you viewing an email?', 'info');
        }
    } catch (error) {
        console.error('Script injection failed:', error);
        // This can happen if the extension doesn't have permission for the page
        ui.showMessage('Could not access this page. Try reloading the tab.', 'error');
    }
}


/**
 * Handles the main form submission logic.
 */
async function handleSubmit(event) {
    event.preventDefault();
    
    // Find the selected radio button
    const unsubMethodElement = document.querySelector('input[name="unsub-method"]:checked');

    // --- THIS IS THE FIX ---
    if (!unsubMethodElement) {
        ui.showMessage('Please select an unsubscribe method.', 'error');
        return; // Stop execution if no method is selected
    }
    // --- END FIX ---

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
            // Now we can safely access .value because we know the element exists
            unsub_method: unsubMethodElement.value,
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

/**
 * Initializes the popup.
 */
async function initPopup() {
    ui.autoFocus();
    await injectAndExtractData();
}

// --- Initialize ---
document.addEventListener('DOMContentLoaded', initPopup);
refreshBtn.addEventListener('click', injectAndExtractData);
form.addEventListener('submit', handleSubmit);
optionsLink.addEventListener('click', openOptions);