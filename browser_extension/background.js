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
// MESSAGE HANDLER
// ==========================================

chrome.runtime.onMessage.addListener(
    function (message, sender, sendResponse) {

        if (!message) {
            return false;
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
                .then(function (result) {

                    sendResponse(
                        result
                    );

                })
                .catch(function (error) {

                    console.error(
                        "NeuroShield AI: Backend check failed:",
                        error
                    );

                    sendResponse({
                        connected: false,
                        modelLoaded: false,
                        error: error.message
                    });

                });

            return true;
        }


        // ======================================
        // START YOUTUBE VIDEO ANALYSIS
        // ======================================

        if (
            message.action ===
            "ANALYZE_VIDEO"
        ) {

            startAnalysisJob(
                message.youtubeUrl,
                message.force_reanalyse === true
            )
                .then(function (data) {

                    sendResponse({
                        started: true,
                        job_id: data.job_id
                    });

                })
                .catch(function (error) {

                    console.error(
                        "NeuroShield AI: Could not start analysis:",
                        error
                    );

                    sendResponse({
                        started: false,
                        error: error.message
                    });

                });

            return true;
        }


        // ======================================
        // CHECK ANALYSIS JOB STATUS
        // ======================================

        if (
            message.action ===
            "CHECK_ANALYSIS_STATUS"
        ) {

            getAnalysisJobStatus(
                message.jobId
            )
                .then(function (data) {

                    sendResponse({
                        success: true,
                        data: data
                    });

                })
                .catch(function (error) {

                    console.error(
                        "NeuroShield AI: Could not check analysis status:",
                        error
                    );

                    sendResponse({
                        success: false,
                        error: error.message
                    });

                });

            return true;
        }


        // ======================================
        // UNKNOWN MESSAGE
        // ======================================

        return false;

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
// START ANALYSIS JOB
// ==========================================

async function startAnalysisJob(
    youtubeUrl,
    forceReanalyse = false
) {

    if (!youtubeUrl) {

        throw new Error(
            "YouTube URL is missing."
        );

    }


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
                    youtube_url: youtubeUrl,
                    force: forceReanalyse
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
// GET ANALYSIS JOB STATUS
// ==========================================

async function getAnalysisJobStatus(
    jobId
) {

    if (!jobId) {

        throw new Error(
            "Analysis job ID is missing."
        );

    }


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


    return data;

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