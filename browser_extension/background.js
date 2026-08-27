// ==========================================
// NeuroShield AI
// Background Service Worker
// ==========================================

console.log("NeuroShield AI: Background service worker loaded.");


/* =========================================
   OPEN SETTINGS
========================================= */

chrome.runtime.onMessage.addListener(
    (message, sender, sendResponse) => {

        if (!message) {
            return;
        }


        if (message.type === "OPEN_NEUROSHIELD_SETTINGS") {

            chrome.runtime.openOptionsPage();

            return;
        }

    }
);