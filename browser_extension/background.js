// ==========================================
// NeuroShield AI
// Background Service Worker
// ==========================================

console.log("NeuroShield AI: Background service worker loaded.");


/* =========================================
   OPEN SETTINGS
========================================= */

chrome.runtime.onMessage.addListener(
    function(message, sender, sendResponse) {

        if (!message) {
            return;
        }


        if (message.action === "OPEN_SETTINGS") {

            chrome.runtime.openOptionsPage();

            sendResponse({
                success: true
            });

            return true;

        }


        // your other existing actions...
    }
);