const form = document.getElementById('unsub-form');
const submitBtn = document.getElementById('submit-btn');
const statusMessage = document.getElementById('status-message');
const optionsLink = document.getElementById('options-link');

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

// Check if we are on a Gmail page when the popup opens
document.addEventListener('DOMContentLoaded', async () => {
    try {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        if (tab && tab.url && tab.url.startsWith('https://mail.google.com/')) {
            console.log('On a Gmail page. Ready to extract data.');
            // Placeholder for data extraction logic
            // e.g., chrome.scripting.executeScript(...)
        } else {
            console.log('Not on a Gmail page.');
        }
    } catch (error) {
        console.error('Error checking active tab:', error);
    }
});

// Handle form submission
form.addEventListener('submit', async (event) => {
    event.preventDefault();
    submitBtn.disabled = true;
    submitBtn.textContent = 'Tracking...';
    showStatus(''); // Clear previous status

    const senderName = document.getElementById('sender-name').value;
    const senderEmail = document.getElementById('sender-email').value;
    const unsubMethod = document.querySelector('input[name="unsub-method"]:checked').value;

    console.log('Submitting:', { senderName, senderEmail, unsubMethod });

    // --- Placeholder for API submission logic ---
    try {
        // 1. Get API URL and Token from chrome.storage.local
        // const { apiUrl, apiToken } = await chrome.storage.local.get(['apiUrl', 'apiToken']);
        
        // 2. Make a fetch() call to the API endpoint
        // const response = await fetch(`${apiUrl}/api/v1/unsubscribed_emails/`, { ... });
        
        // 3. Handle response
        // if (response.ok) {
        //     const data = await response.json();
        //     showStatus(`Success! Tracked with ID: ${data.id}`);
        //     form.reset();
        // } else {
        //     showStatus(`Error: ${response.status} ${response.statusText}`, true);
        // }
        
        // Using a timeout to simulate API call for now
        setTimeout(() => {
             showStatus(`Success! (Simulated)`);
             form.reset();
             submitBtn.disabled = false;
             submitBtn.textContent = 'Track It';
        }, 1000);

    } catch (error) {
        console.error('Submission error:', error);
        showStatus('An unexpected error occurred.', true);
        submitBtn.disabled = false;
        submitBtn.textContent = 'Track It';
    }
});

// Handle options link
optionsLink.addEventListener('click', (e) => {
    e.preventDefault();
    chrome.runtime.openOptionsPage();
});