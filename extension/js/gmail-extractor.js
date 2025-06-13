/**
 * This function is NOT executed in the extension's context.
 * It is injected into the active Gmail tab and executed there.
 * Therefore, it must be entirely self-contained.
 *
 * It attempts to find the sender's name and email from an open email thread in Gmail.
 */
function extractEmailData() {
    // Check if we are in an email view (and not the main inbox)
    // The .hP class is typically on the element containing the email subject.
    const emailSubjectEl = document.querySelector('.hP');
    if (!emailSubjectEl) {
        return null; // Not in an email view
    }

    let senderName, senderEmail;

    // Strategy 1: Find the element with a 'name' and 'email' attribute. This is common.
    const senderEl = document.querySelector('.gD[email]');
    if (senderEl) {
        senderName = senderEl.getAttribute('name');
        senderEmail = senderEl.getAttribute('email');
    } else {
        // Fallback Strategy 2: Look for elements with specific roles or structures
        // This is more brittle and may need adjustment if Gmail's DOM changes.
        const nameEl = document.querySelector('h3 .gD');
        const emailEl = document.querySelector('h3 .go');

        if (nameEl) senderName = nameEl.textContent.trim();
        if (emailEl) {
             // Email is often in the format "<user@example.com>"
            const emailMatch = emailEl.textContent.match(/<(.+?)>/);
            if (emailMatch && emailMatch[1]) {
                senderEmail = emailMatch[1];
            }
        }
    }
    
    if (senderName && senderEmail) {
        return { senderName, senderEmail };
    }
    
    return null; // Return null if data couldn't be found
}

// NOTE: We don't export this function directly. We will read this file's content
// as a string or use the function object itself in executeScript.