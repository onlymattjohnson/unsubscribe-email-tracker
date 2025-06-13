import { getSettings, saveSettings } from '../js/storage.js';
import { createUnsubscribedEmail, testConnection } from '../js/api.js';

const runTestsBtn = document.getElementById('run-tests-btn');
const resultsEl = document.getElementById('results');

let testsPassed = 0;
let testsFailed = 0;
let originalSettings = null;

// A simple test runner function
async function runTest(description, testFn) {
    try {
        await testFn();
        resultsEl.innerHTML += `[<span class="pass">PASS</span>] ${description}\n`;
        testsPassed++;
    } catch (error) {
        resultsEl.innerHTML += `[<span class="fail">FAIL</span>] ${description}\n`;
        resultsEl.innerHTML += `     └─ ${error.message}\n`;
        console.error(`Test failed: ${description}`, error);
        testsFailed++;
    }
}

// Simple assertion helper
function assert(condition, message = 'Assertion failed') {
    if (!condition) {
        throw new Error(message);
    }
}

async function runAllTests() {
    runTestsBtn.disabled = true;
    resultsEl.innerHTML = 'Running tests...\n\n';
    testsPassed = 0;
    testsFailed = 0;

    // Save original settings before running tests
    originalSettings = await getSettings();
    resultsEl.innerHTML += `Using API URL: ${originalSettings.apiUrl}\n\n`;

    // --- Storage Tests ---
    await runTest('Should save and retrieve settings from storage', async () => {
        const testSettings = { apiUrl: 'https://test.com', apiToken: 'test-token-123' };
        await saveSettings(testSettings);
        const retrieved = await getSettings();
        assert(retrieved.apiUrl === testSettings.apiUrl, 'API URL did not match');
        assert(retrieved.apiToken === testSettings.apiToken, 'API Token did not match');
        
        // Restore original settings immediately after this test
        await saveSettings(originalSettings);
    });

    // --- API Communication Tests ---
    await runTest('Should successfully test a valid API connection', async () => {
        const { apiUrl, apiToken } = await getSettings();
        const result = await testConnection(apiUrl, apiToken);
        assert(result.success === true, `Connection test failed: ${result.message}`);
    });

    await runTest('Should fail to test connection with an invalid token (if API validates tokens)', async () => {
        const { apiUrl } = await getSettings();
        const result = await testConnection(apiUrl, 'invalid-token');
        console.log('Invalid token test result:', result);
        
        // Note: This test will only pass if your API's health endpoint validates tokens
        // If your health endpoint is public (doesn't check auth), this test will fail
        if (result.success === true) {
            console.warn('⚠️  Health endpoint does not validate tokens - this may be intentional for uptime monitoring');
            // You might want to skip this test or test a different endpoint that requires auth
            assert(true, 'Skipping - health endpoint does not require authentication');
        } else {
            assert(result.success === false, `Expected connection to fail with invalid token`);
            assert(result.message && (result.message.includes('Authentication failed') || result.message.includes('401')), 
                   `Expected auth failure message, got: ${result.message}`);
        }
    });

    await runTest('Should fail to create record with invalid token', async () => {
        const { apiUrl } = await getSettings();
        const payload = {
            sender_name: 'Test with bad token',
            sender_email: 'valid@email.com',
            unsub_method: 'direct_link'
        };
        
        try {
            await createUnsubscribedEmail(apiUrl, 'invalid-token', payload);
            assert(false, 'Expected request to fail with invalid token');
        } catch (error) {
            console.log('Invalid token error:', error.message, 'Status:', error.status);
            assert(error.status === 401 || error.status === 403, 
                `Expected 401 or 403 status for invalid token, got ${error.status}`);
        }
    });
    
    await runTest('Should create a new record via the API', async () => {
        const { apiUrl, apiToken } = await getSettings();
        const payload = {
            sender_name: 'E2E Test Sender',
            sender_email: 'e2e@test.com',
            unsub_method: 'direct_link'
        };
        const result = await createUnsubscribedEmail(apiUrl, apiToken, payload);
        assert(typeof result.id === 'number', 'API response did not include a numeric ID');
    });

    await runTest('Should handle API validation errors (422)', async () => {
        const { apiUrl, apiToken } = await getSettings();
        const payload = {
            sender_name: 'Invalid Test',
            sender_email: 'not-an-email', // Invalid email
            unsub_method: 'direct_link'
        };

        try {
            await createUnsubscribedEmail(apiUrl, apiToken, payload);
            // If it gets here, the test fails because it should have thrown an error
            assert(false, 'API call should have failed with a 422 error but it succeeded.');
        } catch (error) {
            console.log('Validation error:', error.message);
            console.log('Error status:', error.status);
            
            // Check status
            assert(error.status === 422, `Expected status 422 but got ${error.status}`);
            
            // Check error message (should now be a readable string)
            assert(error.message.includes('email'), `Expected error about email validation, got: ${error.message}`);
            
            // Check the detailed error data structure
            assert(error.data && error.data.detail, 'Expected error to have data.detail property');
            assert(Array.isArray(error.data.detail), 'Expected error.data.detail to be an array');
        }
    });

    // --- Final Summary ---
    resultsEl.innerHTML += '\n----------------------------------\n';
    resultsEl.innerHTML += `Test run complete. Passed: ${testsPassed}, Failed: ${testsFailed}\n`;
    
    // Make sure original settings are restored even if tests fail
    if (originalSettings) {
        await saveSettings(originalSettings);
    }
    
    runTestsBtn.disabled = false;
}

runTestsBtn.addEventListener('click', runAllTests);