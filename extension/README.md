# Unsubscribed Tracker - Browser Extension

This directory contains the source code for the browser extension.

## Development Setup

The extension is built with vanilla JavaScript, HTML, and CSS. No build step is required for development.

### Loading the Extension in Your Browser

You can load the extension directly from this directory for testing.

#### Google Chrome (and other Chromium-based browsers)

1.  Open Chrome and navigate to `chrome://extensions`.
2.  Enable "Developer mode" using the toggle in the top-right corner.
3.  Click the "Load unpacked" button.
4.  Select the `extension` folder from this project directory.
5.  The extension should now appear in your list and in your browser toolbar.

After making changes to the code, you will need to click the "Reload" button (a circular arrow icon) on the extension's card in the `chrome://extensions` page.

#### Mozilla Firefox

1.  Open Firefox and navigate to `about:debugging`.
2.  Click "This Firefox" in the sidebar.
3.  Click the "Load Temporary Add-on..." button.
4.  Select the `manifest.json` file from inside the `extension` folder.
5.  The extension will now be loaded for your current browser session.

Unlike Chrome, changes to the code in Firefox are often reflected automatically. If not, you can use the "Reload" button on the add-on's page in `about:debugging`. Note that temporary add-ons are removed when you close Firefox.

## Configuration

Before the extension can be used, you must configure it via the **Options** page:

1.  Right-click the extension icon in your toolbar and select "Options".
2.  Enter the URL of your API (e.g., `https://your-api.com`).
3.  Enter the API Bearer Token you have configured.
4.  Click "Save".