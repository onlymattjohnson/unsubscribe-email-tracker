/**
 * Tests the connection to the API using the provided credentials.
 * @param {string} apiUrl - The base URL of the API.
 * @param {string} apiToken - The API bearer token.
 * @returns {Promise<{success: boolean, message: string}>} Result object.
 */
export async function testConnection(apiUrl, apiToken) {
    if (!apiUrl || !apiToken) {
        return { success: false, message: 'API URL and Token are required.' };
    }

    try {
        const response = await fetch(`${apiUrl}/api/v1/health`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${apiToken}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            return { success: true, message: 'Connection successful!' };
        } else if (response.status === 401) {
            return { success: false, message: 'Authentication failed. Please check your API Token.' };
        } else {
            return { success: false, message: `Server returned an error: ${response.status} ${response.statusText}` };
        }
    } catch (error) {
        console.error('Connection test error:', error);
        return { success: false, message: 'Failed to connect. Check the API URL and your network.' };
    }
}

/**
 * Creates a new unsubscribed email record via the API.
 * @param {string} apiUrl - The base URL of the API.
 * @param {string} apiToken - The API bearer token.
 * @param {{sender_name: string, sender_email: string, unsub_method: string}} payload - The data to submit.
 * @returns {Promise<object>} The parsed JSON response from the API.
 */
export async function createUnsubscribedEmail(apiUrl, apiToken, payload) {
    const response = await fetch(`${apiUrl}/api/v1/unsubscribed_emails/`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${apiToken}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    });

    if (!response.ok) {
        // If the response is not ok, create a structured error object
        const errorData = await response.json().catch(() => ({ detail: 'Failed to parse error response.' }));
        const error = new Error(errorData.detail || `HTTP Error: ${response.status}`);
        error.status = response.status;
        error.data = errorData;
        throw error;
    }

    return response.json();
}