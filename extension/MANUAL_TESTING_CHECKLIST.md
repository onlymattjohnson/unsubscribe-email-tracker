# Manual Testing Checklist for Browser Extension

This checklist should be run before releasing a new version of the extension to ensure UI and core functionality are working as expected.

## Pre-requisites
- [ ] The backend API server is running (`make run`).
- [ ] The extension has been loaded/reloaded in the browser in developer mode.

## Part 1: Options Page
- [ ] **Open Options:** Right-click the extension icon and select "Options". The page should load without errors.
- [ ] **Initial State:** If it's a fresh install, fields should be empty.
- [ ] **Test Connection (Fail):** With empty fields, click "Test Connection". Verify a clear error message appears.
- [ ] **Test Connection (Bad Token):** Enter the correct API URL but an incorrect token. Click "Test Connection". Verify a "401 Authentication failed" message appears.
- [ ] **Test Connection (Success):** Enter the correct API URL and token. Click "Test Connection". Verify a "Connection successful!" message appears.
- [ ] **Save Settings:** Click "Save Settings". Verify a "Settings saved" message appears.
- [ ] **Persistence:** Close and re-open the Options tab. Verify the API URL is still present and the token is masked (e.g., `••••••••xxxx`).

## Part 2: Automated Logic Tests
- [ ] **Open Test Runner:** Open the file `extension/tests/e2e-runner.html` in a new browser tab.
- [ ] **Run Tests:** Click the "Run All Tests" button.
- [ ] **Verify Results:** Confirm that all tests show `[PASS]` and the final summary shows `Failed: 0`.

## Part 3: Popup Workflow
- [ ] **Non-Gmail Page:** Go to any page that is not Gmail (e.g., google.com). Open the popup.
    - [ ] Verify it shows a message like "Open an email in Gmail to auto-fill".
    - [ ] Verify the form fields are empty.
- [ ] **Gmail Inbox View:** Go to the main `mail.google.com` inbox view (not inside an email). Open the popup.
    - [ ] Verify it shows a message like "Could not find sender info. Are you viewing an email?".
- [ ] **Gmail Email View:** Open any email message.
    - [ ] Open the popup. Verify the "Sender Name" and "Sender Email" fields are correctly auto-filled.
    - [ ] Verify a "Form auto-filled" success message appears.
- [ ] **Refresh Functionality:** While in an email view, manually clear the form fields in the popup. Click the refresh button (⟳).
    - [ ] Verify the fields are re-populated from the page.
- [ ] **Submission (Success):** With the form filled (auto or manual), click "Track It".
    - [ ] Verify a loading state appears on the button.
    - [ ] Verify a "Success! Tracked with ID: X" message appears.
    - [ ] Verify the form fields are cleared and the first field is focused.
- [ ] **Data Verification:** Check the main web application UI or the database directly to confirm the new record was saved correctly.
- [ ] **Submission (Validation Fail):** Clear the "Sender Name" field and click "Track It".
    - [ ] Verify a "Please fill out all required fields" error message appears.