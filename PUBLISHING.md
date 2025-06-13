# Browser Extension Publishing Guide

This guide outlines the steps to package and publish the extension to the Chrome Web Store and Firefox Browser Add-ons.

## 1. Version Management

Before publishing, always update the version number in `extension/manifest.json`. Follow [Semantic Versioning](https://semver.org/) (e.g., `1.0.1` for a patch, `1.1.0` for a new feature).

## 2. Packaging the Extension

Create a ZIP file containing only the necessary files from the `extension/` directory.

**Do NOT include test files or documentation.**

Your ZIP file should contain:
- `manifest.json`
- `popup.html`
- `popup.js`
- `options.html`
- `options.js`
- `styles.css`
- The `icons/` directory
- The `js/` directory (`storage.js`, `api.js`, etc.)

**Example command to create the package:**
```bash
# From the project root directory
cd extension
zip -r ../unsubscribed-tracker-v1.0.0.zip . -x "tests/*" "*.md"
cd ..
``` 