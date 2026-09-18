// ==========================================
// NeuroShield AI
// Background Service Worker
// ==========================================

console.log("NeuroShield AI: Background service worker loaded.");


// ==========================================
// BACKEND CONFIGURATION
// ==========================================

const BACKEND_URL = "http://127.0.0.1:8000";


// ==========================================
// MESSAGE HANDLER
// ==========================================

chrome.runtime.onMessage.addListener(
    function(message, sender, sendResponse) {

        if (!message) {
            return;
        }


        // ==========================================
        // OPEN SETTINGS
        // ==========================================

        if (message.action === "OPEN_SETTINGS") {

            chrome.runtime.openOptionsPage();

            sendResponse({
                success: true
            });

            return true;
        }


        // ==========================================
        // CHECK BACKEND STATUS
        // ==========================================

        if (message.action === "CHECK_BACKEND") {

            checkBackendStatus()
                .then(function(result) {

                    sendResponse(result);

                })
                .catch(function(error) {

                    console.error(
                        "NeuroShield AI: Backend check failed:",
                        error
                    );

                    sendResponse({
                        connected: false,
                        error: error.message
                    });

                });

            return true;
        }

    }
);


// ==========================================
// CHECK BACKEND STATUS
// ==========================================

async function checkBackendStatus() {

    try {

        const response =
            await fetch(
                `${BACKEND_URL}/model-status`
            );


        if (!response.ok) {

            throw new Error(
                `Backend returned HTTP ${response.status}`
            );

        }


        const data =
            await response.json();


        console.log(
            "NeuroShield AI: Backend status:",
            data
        );


        return {

            connected: true,

            modelLoaded:
                data.model_loaded === true,

            model:
                data.model || "Unknown",

            featureCount:
                data.feature_count || 0

        };

    } catch (error) {

        console.error(
            "NeuroShield AI: Could not connect to backend:",
            error
        );


        return {

            connected: false,

            modelLoaded: false,

            model: null,

            featureCount: 0,

            error: error.message

        };

    }

}