// Default settings
const DEFAULTS = {
    apiUrl: '',
    apiToken: ''
};

/**
 * Gets settings from chrome.storage.local.
 * @returns {Promise<object>} A promise that resolves to the settings object.
 */
export async function getSettings() {
    return new Promise((resolve) => {
        chrome.storage.local.get(DEFAULTS, (items) => {
            resolve(items);
        });
    });
}

/**
 * Saves settings to chrome.storage.local.
 * @param {object} settingsToSave - The settings object to save.
 * @returns {Promise<void>} A promise that resolves when saving is complete.
 */
export async function saveSettings(settingsToSave) {
    return new Promise((resolve, reject) => {
        chrome.storage.local.set(settingsToSave, () => {
            if (chrome.runtime.lastError) {
                return reject(chrome.runtime.lastError);
            }
            resolve();
        });
    });
}