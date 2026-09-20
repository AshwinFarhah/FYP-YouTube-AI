// ==========================================
// NeuroShield AI
// Background Service Worker
// ==========================================

console.log(
    "NeuroShield AI: Background service worker loaded."
);


// ==========================================
// BACKEND CONFIGURATION
// ==========================================

const BACKEND_URL =
    "http://127.0.0.1:8000";


// ==========================================
// POLLING CONFIGURATION
// ==========================================

// Check the backend every 5 seconds.
// Each individual HTTP request is short-lived.

const POLL_INTERVAL_MS = 5000;


// Maximum total polling time.
//
// 15 minutes gives the backend plenty of time for:
// download + visual + audio + Whisper + RF.
//
// This is NOT one 15-minute HTTP request.
// It is a sequence of short requests.

const MAX_POLL_ATTEMPTS = 180;


// ==========================================
// MESSAGE HANDLER
// ==========================================

chrome.runtime.onMessage.addListener(
    function(message, sender, sendResponse) {

        if (!message) {
            return;
        }


        // ======================================
        // OPEN SETTINGS
        // ======================================

        if (
            message.action ===
            "OPEN_SETTINGS"
        ) {

            chrome.runtime.openOptionsPage();

            sendResponse({
                success: true
            });

            return false;
        }


        // ======================================
        // CHECK BACKEND STATUS
        // ======================================

        if (
            message.action ===
            "CHECK_BACKEND"
        ) {

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
                        error:
                            error.message
                    });

                });

            return true;
        }


        // ======================================
        // ANALYZE YOUTUBE VIDEO
        // ======================================

        if (
            message.action ===
            "ANALYZE_VIDEO"
        ) {

            const tabId =
                sender.tab &&
                sender.tab.id;


            // ==================================
            // IDENTIFY REQUESTING TAB
            // ==================================

            if (!tabId) {

                sendResponse({
                    started: false,
                    error:
                        "Could not identify YouTube tab."
                });

                return false;
            }


            // ==================================
            // RESPOND TO CONTENT SCRIPT
            // IMMEDIATELY
            // ==================================

            sendResponse({
                started: true
            });


            console.log(
                "NeuroShield AI: Analysis request accepted for tab:",
                tabId
            );


            // ==================================
            // START BACKEND JOB + POLLING
            // ==================================

            startAndMonitorAnalysis(
                message.youtubeUrl,
                tabId
            )
                .catch(function(error) {

                    console.error(
                        "NeuroShield AI: Analysis process failed:",
                        error
                    );


                    sendAnalysisError(
                        tabId,
                        error.message
                    );

                });


            // ==================================
            // IMPORTANT:
            // Original Chrome message response
            // has already been sent.
            // ==================================

            return false;
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
                data.model_type ||
                data.model ||
                "Unknown",

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

            error:
                error.message

        };

    }

}


// ==========================================
// START AND MONITOR ANALYSIS
// ==========================================

async function startAndMonitorAnalysis(
    youtubeUrl,
    tabId
) {

    // ======================================
    // 1. START ANALYSIS JOB
    // ======================================

    const job =
        await startAnalysisJob(
            youtubeUrl
        );


    if (
        !job ||
        !job.job_id
    ) {

        throw new Error(
            "Backend did not return an analysis job ID."
        );

    }


    const jobId =
        job.job_id;


    console.log(
        "NeuroShield AI: Analysis job started:",
        jobId
    );


    // ======================================
    // 2. POLL UNTIL FINISHED
    // ======================================

    const result =
        await pollAnalysisJob(
            jobId
        );


    console.log(
        "NeuroShield AI: Analysis completed:",
        result
    );


    // ======================================
    // 3. SEND FINAL RESULT TO CONTENT.JS
    // ======================================

    console.log(
        "NeuroShield AI: Sending completed analysis to tab:",
        tabId
    );


    await chrome.tabs.sendMessage(
        tabId,
        {
            type:
                "NEUROSHIELD_ANALYSIS_UPDATE",

            data:
                result
        }
    );


    console.log(
        "NeuroShield AI: Analysis result delivered to content script."
    );

}


// ==========================================
// START ANALYSIS JOB
// ==========================================

async function startAnalysisJob(
    youtubeUrl
) {

    console.log(
        "NeuroShield AI: Starting backend analysis job:",
        youtubeUrl
    );


    const response =
        await fetch(
            `${BACKEND_URL}/analyze-video`,
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    youtube_url:
                        youtubeUrl
                })
            }
        );


    if (!response.ok) {

        const errorMessage =
            await getBackendError(
                response
            );


        throw new Error(
            errorMessage
        );

    }


    const data =
        await response.json();


    console.log(
        "NeuroShield AI: Backend job response:",
        data
    );


    if (!data.job_id) {

        throw new Error(
            "Backend response did not contain a job ID."
        );

    }


    return data;

}


// ==========================================
// POLL ANALYSIS JOB
// ==========================================

async function pollAnalysisJob(
    jobId
) {

    for (
        let attempt = 1;
        attempt <= MAX_POLL_ATTEMPTS;
        attempt++
    ) {

        // ==================================
        // WAIT BEFORE STATUS CHECK
        // ==================================

        await sleep(
            POLL_INTERVAL_MS
        );


        console.log(
            `NeuroShield AI: Checking analysis status (${attempt}/${MAX_POLL_ATTEMPTS})...`
        );


        // ==================================
        // GET JOB STATUS
        // ==================================

        const response =
            await fetch(
                `${BACKEND_URL}/analysis-status/${encodeURIComponent(jobId)}`
            );


        if (!response.ok) {

            const errorMessage =
                await getBackendError(
                    response
                );


            throw new Error(
                errorMessage
            );

        }


        const data =
            await response.json();


        console.log(
            "NeuroShield AI: Analysis status:",
            data.status
        );


        // ==================================
        // COMPLETE
        // ==================================

        if (
            data.status ===
            "complete"
        ) {

            if (!data.result) {

                throw new Error(
                    "Analysis completed but backend returned no result."
                );

            }


            return data.result;

        }


        // ==================================
        // FAILED
        // ==================================

        if (
            data.status ===
            "failed"
        ) {

            throw new Error(
                data.error ||
                "Video analysis failed."
            );

        }


        // ==================================
        // OTHERWISE:
        // queued / processing
        //
        // Continue polling.
        // ==================================

        console.log(
            "NeuroShield AI: Analysis still processing..."
        );

    }


    // ======================================
    // MAXIMUM WAIT REACHED
    // ======================================

    throw new Error(
        "Video analysis timed out while waiting for the backend."
    );

}


// ==========================================
// SEND ANALYSIS ERROR TO CONTENT SCRIPT
// ==========================================

async function sendAnalysisError(
    tabId,
    errorMessage
) {

    try {

        await chrome.tabs.sendMessage(
            tabId,
            {
                type:
                    "NEUROSHIELD_ANALYSIS_ERROR",

                error:
                    errorMessage
            }
        );


        console.log(
            "NeuroShield AI: Analysis error delivered to content script."
        );


    } catch (sendError) {

        console.error(
            "NeuroShield AI: Could not deliver analysis error:",
            sendError
        );

    }

}


// ==========================================
// READ BACKEND ERROR
// ==========================================

async function getBackendError(
    response
) {

    let errorMessage =
        `Backend returned HTTP ${response.status}`;


    try {

        const errorData =
            await response.json();


        if (errorData.detail) {

            if (
                typeof errorData.detail ===
                "string"
            ) {

                errorMessage =
                    errorData.detail;

            } else {

                errorMessage =
                    JSON.stringify(
                        errorData.detail
                    );

            }

        }


    } catch (jsonError) {

        // Keep the original HTTP error.

    }


    return errorMessage;

}


// ==========================================
// SLEEP
// ==========================================

function sleep(
    milliseconds
) {

    return new Promise(
        function(resolve) {

            setTimeout(
                resolve,
                milliseconds
            );

        }
    );

}