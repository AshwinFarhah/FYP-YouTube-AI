// ============================================================
// NeuroShield AI
// YouTube Content Script
// ============================================================

console.log("NeuroShield AI: Content script loaded.");


// ============================================================
// STATE
// ============================================================

let protectionEnabled = false;
let currentVideoId = null;
let overlay = null;

let isDragging = false;
let dragOffsetX = 0;
let dragOffsetY = 0;

let notificationsEnabled = true;
let lastAlertedVideoId = null;

let activeAnalysisJobId = null;
let analysisPolling = false;
let analysisSessionId = 0;
let reanalysisStarting = false;
let manualReanalysisSessionId = null;

const ANALYSIS_POLL_INTERVAL_MS = 5000;
const MAX_ANALYSIS_POLL_ATTEMPTS = 180;

// ============================================================
// INITIALISE
// ============================================================

async function initialise() {

    try {

        const result = await chrome.storage.local.get([
            "protectionEnabled",
            "neuroshieldNotificationsEnabled"
        ]);

        protectionEnabled =
            result.protectionEnabled === true;

        notificationsEnabled =
            result.neuroshieldNotificationsEnabled !== false;

        checkCurrentPage();

    } catch (error) {

        console.error(
            "NeuroShield AI: Initialisation failed:",
            error
        );

    }

}


// ============================================================
// CHECK CURRENT YOUTUBE PAGE
// ============================================================

function checkCurrentPage() {

    if (!protectionEnabled) {

        removeOverlay();

        return;

    }

    const videoId = getCurrentVideoId();

    // --------------------------------------------------------
    // YOUTUBE HOME / NO VIDEO
    // --------------------------------------------------------

    if (!videoId) {

        currentVideoId = null;

        removeOverlay();

        return;

    }

    // --------------------------------------------------------
    // NEW VIDEO
    // --------------------------------------------------------

    if (videoId !== currentVideoId) {
        manualReanalysisSessionId = null;
        currentVideoId = videoId;

        lastAlertedVideoId = null;

        showAnalysisTemplate();

        return;

    }

    // --------------------------------------------------------
    // OVERLAY DISAPPEARED
    // --------------------------------------------------------

    if (!document.getElementById("neuroshield-overlay")) {

        showAnalysisTemplate();

    }

}


// ============================================================
// GET CURRENT VIDEO ID
// ============================================================

function getCurrentVideoId() {

    try {

        const url =
            new URL(window.location.href);

        if (
            url.hostname.includes("youtube.com") &&
            url.pathname === "/watch"
        ) {

            return url.searchParams.get("v");

        }

    } catch (error) {

        console.log(
            "NeuroShield AI: Could not read YouTube URL."
        );

    }

    return null;

}


// ============================================================
// CREATE OVERLAY
// ============================================================

async function showAnalysisTemplate() {

    removeOverlay();

    overlay =
        document.createElement("div");

    overlay.id =
        "neuroshield-overlay";

    const logoURL =
        chrome.runtime.getURL("icons/logo.png");

    console.log(
        "NeuroShield AI: Logo URL =",
        logoURL
    );

    try {

        const templateURL =
            chrome.runtime.getURL(
                "content/overlay.html"
            );

        const templateResponse =
            await fetch(templateURL);

        if (!templateResponse.ok) {

            throw new Error(
                `Could not load overlay template: HTTP ${templateResponse.status}`
            );

        }

        overlay.innerHTML =
            await templateResponse.text();

        const logoImage =
            overlay.querySelector(
                "#neuroshield-logo-image"
            );

        if (logoImage) {

            logoImage.src =
                logoURL;

            logoImage.addEventListener(
                "error",
                function () {

                    logoImage.style.display =
                        "none";

                    console.error(
                        "NeuroShield AI: Logo failed to load:",
                        logoImage.src
                    );

                }
            );

        }

        // Set extension icon URLs after loading external HTML.
        // JavaScript template expressions do not execute inside overlay.html.
        const overlayIconPaths = {
            cognitiveIcon: "icons/cognitive.png",
            behaviouralIcon: "icons/behavioural.png",
            emotionalIcon: "icons/emotional.png",
            overallIcon: "icons/overall.png",
            explainabilityIcon: "icons/explainability.png",
            visualIcon: "icons/visual.png",
            audioIcon: "icons/audio.png",
            textualIcon: "icons/textual.png",
            engagementIcon: "icons/engagement.png",
            emotionFeatureIcon: "icons/emotion-feature.png",
            metadataIcon: "icons/metadata.png"
        };

        Object.entries(
            overlayIconPaths
        ).forEach(
            ([elementId, iconPath]) => {

                const iconElement =
                    overlay.querySelector(
                        `#${elementId}`
                    );

                if (iconElement) {

                    iconElement.src =
                        chrome.runtime.getURL(
                            iconPath
                        );

                }

            }
        );

    } catch (error) {

        console.error(
            "NeuroShield AI: Could not load overlay template:",
            error
        );

        return;

    }


    document.body.appendChild(
        overlay
    );


// Load the embedded Settings interface.
    try {

        const settingsResponse =
            await fetch(
                chrome.runtime.getURL(
                    "settings/settings.html"
                )
            );

        if (!settingsResponse.ok) {

            throw new Error(
                `Settings HTTP ${settingsResponse.status}`
            );

        }

        const settingsView =
            overlay.querySelector(
                "#neuroshield-settings-view"
            );

        if (settingsView) {

            settingsView.innerHTML =
                await settingsResponse.text();

        }

    } catch (error) {

        console.error(
            "NeuroShield AI: Could not load Settings:",
            error
        );

    }


    initialiseOverlayControls();

    // ========================================================
    // RESTORE MULTIMEDIA VISIBILITY
    // ========================================================

    chrome.storage.local.get(
        "neuroshieldMultimediaEnabled"
    ).then(function (result) {

        updateMultimediaVisibility(
            result.neuroshieldMultimediaEnabled !== false
        );

    });

    // Apply saved Explainability preference.

    chrome.storage.local.get(
        "explainabilityEnabled"
    ).then(function (result) {

        updateExplainabilityVisibility(
            result.explainabilityEnabled !== false
        );

    });

    // Restore saved Multimedia Features preference.

    chrome.storage.local.get(
        "neuroshieldMultimediaEnabled"
    ).then(function (result) {

        updateMultimediaVisibility(
            result.neuroshieldMultimediaEnabled !== false
        );

    });


// ========================================================
// INITIALISE EMBEDDED SETTINGS
// ========================================================


    const settingsContainer =
        document.getElementById("neuroshield-settings-view");

    if (
        settingsContainer &&
        typeof NeuroShieldSettings !== "undefined"
    ) {
        await NeuroShieldSettings.initialise(
            settingsContainer,
            function () {
                const analysisView =
                    document.getElementById("neuroshield-content");

                const settingsView =
                    document.getElementById("neuroshield-settings-view");

                if (analysisView && settingsView) {
                    settingsView.style.display = "none";
                    analysisView.style.display = "";
                }
            }
        );

        // Register button AFTER settings have initialised.
        const reanalyseButton =
            settingsContainer.querySelector("#ns-reanalyse-video");

        const reanalyseMessage =
            settingsContainer.querySelector("#ns-reanalyse-message");

        if (reanalyseButton) {
            console.log(
                "NeuroShield AI: Reanalyse button initialised."
            );

            reanalyseButton.addEventListener(
                "click",
                async function (event) {
                    event.preventDefault();

                    if (reanalysisStarting) {
                        return;
                    }

                    reanalyseButton.disabled = true;

                    if (reanalyseMessage) {
                        reanalyseMessage.textContent =
                            "Starting fresh analysis...";
                    }

                    try {
                        await reanalyseCurrentVideo();

                        if (reanalyseMessage) {
                            reanalyseMessage.textContent =
                                "Fresh analysis started. Results will update when complete.";
                        }
                    } catch (error) {
                        console.error(
                            "NeuroShield AI: Reanalysis failed:",
                            error
                        );

                        if (reanalyseMessage) {
                            reanalyseMessage.textContent =
                                error.message || "Unable to start reanalysis.";
                        }
                    } finally {
                        reanalyseButton.disabled = false;
                    }
                }
            );
        } else {
            console.warn(
                "NeuroShield AI: Reanalyse button not found."
            );
        }
    }


    loadOverlayPosition();


    setMonitoringStatus(
        false
    );


    checkBackendConnection()
        .then(
            function (isReady) {

                if (isReady) {

                    requestVideoAnalysis();

                }

            }
        );

}

const hybridWhyButton =
    document.getElementById(
        "hybridWhyButton"
    );

const hybridWhyContent =
    document.getElementById(
        "hybridWhyContent"
    );

if (
    hybridWhyButton &&
    hybridWhyContent
) {

    hybridWhyButton.addEventListener(
        "click",
        function () {

            const isOpen =
                hybridWhyButton.getAttribute(
                    "aria-expanded"
                ) === "true";

            hybridWhyButton.setAttribute(
                "aria-expanded",
                String(!isOpen)
            );

            hybridWhyContent.style.display =
                isOpen
                    ? "none"
                    : "block";

            const arrow =
                hybridWhyButton.querySelector(
                    ".hybrid-accordion-arrow"
                );

            if (arrow) {

                arrow.textContent =
                    isOpen
                        ? "▸"
                        : "▾";

            }

        }
    );

}

// ============================================================
// OVERLAY CONTROLS
// ============================================================

function initialiseOverlayControls() {

    const windowElement =
        document.querySelector(
            ".neuroshield-window"
        );


    const dragHandle =
        document.getElementById(
            "neuroshield-drag-handle"
        );


    const closeButton =
        document.getElementById(
            "neuroshield-close"
        );


    const minimizeButton =
        document.getElementById(
            "neuroshield-minimize"
        );


    const notificationButton =
        document.getElementById(
            "neuroshield-notification"
        );


    const settingsButton =
        document.getElementById(
            "neuroshield-settings"
        );


    if (
        !windowElement ||
        !dragHandle
    ) {

        console.error(
            "NeuroShield AI: Overlay controls could not initialise."
        );

        return;

    }


    // ========================================================
    // NOTIFICATIONS
    // ========================================================

    if (notificationButton) {

        updateNotificationButton(
            notificationButton
        );


        notificationButton.addEventListener(
            "click",
            async function (event) {

                event.preventDefault();

                event.stopPropagation();


                await toggleNotifications();

            }
        );

    }


    // ========================================================
    // SETTINGS - EMBEDDED OVERLAY NAVIGATION
    // ========================================================

    if (settingsButton) {

        settingsButton.addEventListener(
            "click",
            function (event) {

                event.preventDefault();
                event.stopPropagation();

                const analysisView =
                    document.getElementById(
                        "neuroshield-content"
                    );

                const settingsView =
                    document.getElementById(
                        "neuroshield-settings-view"
                    );

                if (!analysisView || !settingsView) {
                    return;
                }

                analysisView.style.display =
                    "none";

                settingsView.style.display =
                    "block";

            }
        );

    }

    // ========================================================
    // CLOSE
    // ========================================================

    if (closeButton) {

        closeButton.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                event.stopPropagation();


                removeOverlay();

            }
        );

    }


    // ========================================================
    // MINIMIZE
    // ========================================================

    if (minimizeButton) {

        minimizeButton.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                event.stopPropagation();


                windowElement.classList.toggle(
                    "minimized"
                );


                if (
                    windowElement.classList.contains(
                        "minimized"
                    )
                ) {

                    minimizeButton.textContent =
                        "+";

                } else {

                    minimizeButton.textContent =
                        "−";

                }

            }
        );

    }


    // ========================================================
    // DRAG
    // ========================================================

    dragHandle.addEventListener(
        "mousedown",
        function (event) {

            if (
                event.target.closest(
                    ".neuroshield-action"
                )
            ) {

                return;

            }


            isDragging = true;


            const rect =
                windowElement.getBoundingClientRect();


            dragOffsetX =
                event.clientX -
                rect.left;


            dragOffsetY =
                event.clientY -
                rect.top;


            windowElement.classList.add(
                "dragging"
            );


            event.preventDefault();

        }
    );


    // ========================================================
    // SAVE SIZE WHEN RESIZED
    // ========================================================

    if (window.ResizeObserver) {

        const resizeObserver =
            new ResizeObserver(
                function () {

                    if (
                        !windowElement.classList.contains(
                            "minimized"
                        )
                    ) {

                        saveOverlayPosition();

                    }

                }
            );


        resizeObserver.observe(
            windowElement
        );

    }

}


// ============================================================
// NOTIFICATION TOGGLE
// ============================================================

async function toggleNotifications() {

    notificationsEnabled =
        !notificationsEnabled;


    try {

        await chrome.storage.local.set({

            neuroshieldNotificationsEnabled:
            notificationsEnabled

        });

    } catch (error) {

        console.error(
            "NeuroShield AI: Could not save notification setting:",
            error
        );

    }


    const button =
        document.getElementById(
            "neuroshield-notification"
        );


    if (button) {

        updateNotificationButton(
            button
        );

    }

}


// ============================================================
// UPDATE NOTIFICATION BUTTON
// ============================================================

function updateNotificationButton(
    button
) {

    if (!button) {

        return;

    }


    if (notificationsEnabled) {

        button.textContent =
            "🔔";


        button.title =
            "Mute high-risk alerts";


        button.setAttribute(
            "aria-label",
            "Mute high-risk alerts"
        );


        button.classList.remove(
            "muted"
        );

    } else {

        button.textContent =
            "🔕";


        button.title =
            "Unmute high-risk alerts";


        button.setAttribute(
            "aria-label",
            "Unmute high-risk alerts"
        );


        button.classList.add(
            "muted"
        );

    }

}


// ============================================================
// HANDLE DRAG
// ============================================================

function handleDrag(
    event
) {

    if (
        !isDragging ||
        !overlay
    ) {

        return;

    }


    const windowElement =
        document.querySelector(
            ".neuroshield-window"
        );


    if (!windowElement) {

        return;

    }


    let x =
        event.clientX -
        dragOffsetX;


    let y =
        event.clientY -
        dragOffsetY;


    const width =
        windowElement.offsetWidth;


    const height =
        windowElement.offsetHeight;


    const maxX =
        Math.max(
            0,
            window.innerWidth -
            width
        );


    const maxY =
        Math.max(
            0,
            window.innerHeight -
            height
        );


    x =
        Math.max(
            0,
            Math.min(
                x,
                maxX
            )
        );


    y =
        Math.max(
            0,
            Math.min(
                y,
                maxY
            )
        );


    windowElement.style.left =
        `${x}px`;


    windowElement.style.top =
        `${y}px`;


    windowElement.style.right =
        "auto";

}


// ============================================================
// STOP DRAG
// ============================================================

function stopDrag() {

    if (!isDragging) {

        return;

    }


    isDragging =
        false;


    const windowElement =
        document.querySelector(
            ".neuroshield-window"
        );


    if (windowElement) {

        windowElement.classList.remove(
            "dragging"
        );

    }


    saveOverlayPosition();

}


// ============================================================
// SAVE POSITION + SIZE
// ============================================================

function saveOverlayPosition() {

    const windowElement =
        document.querySelector(
            ".neuroshield-window"
        );


    if (!windowElement) {

        return;

    }


    const rect =
        windowElement.getBoundingClientRect();


    chrome.storage.local.set({

        neuroshieldWindowPosition: {

            left:
            rect.left,

            top:
            rect.top,

            width:
            rect.width,

            height:
            rect.height

        }

    });

}


// ============================================================
// LOAD POSITION + SIZE
// ============================================================

async function loadOverlayPosition() {

    const windowElement =
        document.querySelector(
            ".neuroshield-window"
        );


    if (!windowElement) {

        return;

    }


    try {

        const result =
            await chrome.storage.local.get(
                "neuroshieldWindowPosition"
            );


        const position =
            result.neuroshieldWindowPosition;


        if (!position) {

            return;

        }


        if (
            typeof position.width ===
            "number"
        ) {

            windowElement.style.width =
                `${position.width}px`;

        }


        if (
            typeof position.height ===
            "number"
        ) {

            windowElement.style.height =
                `${position.height}px`;

        }


        if (
            typeof position.left ===
            "number"
        ) {

            const maxLeft =
                Math.max(
                    0,
                    window.innerWidth -
                    120
                );


            windowElement.style.left =
                `${Math.max(
                    0,
                    Math.min(
                        position.left,
                        maxLeft
                    )
                )}px`;


            windowElement.style.right =
                "auto";

        }


        if (
            typeof position.top ===
            "number"
        ) {

            const maxTop =
                Math.max(
                    0,
                    window.innerHeight -
                    120
                );


            windowElement.style.top =
                `${Math.max(
                    0,
                    Math.min(
                        position.top,
                        maxTop
                    )
                )}px`;

        }

    } catch (error) {

        console.log(
            "NeuroShield AI: Could not restore window settings."
        );

    }

}


// ============================================================
// REMOVE OVERLAY
// ============================================================

function removeOverlay() {

    const existing =
        document.getElementById(
            "neuroshield-overlay"
        );


    if (existing) {

        existing.remove();

    }


    overlay =
        null;

}


// ============================================================
// MESSAGE HANDLING
// ============================================================

chrome.runtime.onMessage.addListener(
    function (
        message,
        sender,
        sendResponse
    ) {

        if (!message) {

            return;

        }


        // ====================================================
        // START
        // ====================================================

        if (
            message.action ===
            "START_ANALYSIS"
        ) {

            protectionEnabled =
                true;


            chrome.storage.local.set({

                protectionEnabled:
                    true

            });


            checkCurrentPage();


            sendResponse({

                success:
                    true

            });


            return true;

        }


        // ====================================================
        // STOP
        // ====================================================

        if (
            message.action ===
            "STOP_ANALYSIS"
        ) {

            protectionEnabled =
                false;


            chrome.storage.local.set({

                protectionEnabled:
                    false

            });


            removeOverlay();


            sendResponse({

                success:
                    true

            });


            return true;

        }


        // ====================================================
        // REAL BACKEND RESULT
        // ====================================================

        if (
            message.type ===
            "NEUROSHIELD_ANALYSIS_UPDATE"
        ) {

            console.log(
                "NeuroShield AI: Backend analysis received."
            );


            console.log(
                "NeuroShield AI: REAL ANALYSIS RESULT:",
                message.data
            );


            updateRealRiskResult(
                message.data
            );


            sendResponse({

                success:
                    true

            });


            return true;

        }

    }
);


// ============================================================
// CHECK BACKEND CONNECTION
// ============================================================

async function checkBackendConnection() {

    console.log(
        "NeuroShield AI: Checking backend connection..."
    );


    try {

        const response =
            await chrome.runtime.sendMessage({

                action:
                    "CHECK_BACKEND"

            });


        if (
            response &&
            response.connected === true &&
            response.modelLoaded === true
        ) {

            console.log(
                "NeuroShield AI: Backend connected.",
                response
            );


            setMonitoringStatus(
                true
            );


            return true;

        }


        console.warn(
            "NeuroShield AI: Backend is not ready."
        );


        setMonitoringStatus(
            false
        );


        return false;

    } catch (error) {

        console.error(
            "NeuroShield AI: Backend connection check failed:",
            error
        );


        setMonitoringStatus(
            false
        );


        return false;

    }

}

// ============================================================
// REANALYSE CURRENT VIDEO
// ============================================================


async function reanalyseCurrentVideo() {

    if (reanalysisStarting) {
        throw new Error("Reanalysis is already starting.");
    }

    const videoId = getCurrentVideoId();

    if (!protectionEnabled || !videoId) {
        throw new Error(
            "Enable protection and open a YouTube video first."
        );
    }

    const backendReady = await checkBackendConnection();

    if (!backendReady) {
        throw new Error(
            "Backend is not connected or the model is unavailable."
        );
    }

    reanalysisStarting = true;

    try {
        currentVideoId = videoId;

        // Invalidate previous polling sessions.
        analysisSessionId++;

        activeAnalysisJobId = null;
        analysisPolling = false;
        lastAlertedVideoId = null;

        manualReanalysisSessionId = analysisSessionId + 1;

        const started = await requestVideoAnalysis(true);

        if (!started) {
            throw new Error(
                "Backend did not accept the fresh analysis request."
            );
        }

        console.log(
            "NeuroShield AI: Fresh reanalysis job started."
        );

        return true;

    } finally {
        reanalysisStarting = false;
    }
}


// ============================================================
// REQUEST VIDEO ANALYSIS
// ============================================================


async function requestVideoAnalysis(forceReanalyse = false) {

    const sessionId = ++analysisSessionId;

    const requestedVideoId = currentVideoId;

    if (!requestedVideoId) {
        console.warn(
            "NeuroShield AI: No YouTube video ID available."
        );
        return false;
    }

    const youtubeUrl =
        `https://www.youtube.com/watch?v=${requestedVideoId}`;

    console.log(
        "NeuroShield AI: Requesting analysis:",
        youtubeUrl,
        "Force:",
        forceReanalyse
    );

    try {
        const response = await chrome.runtime.sendMessage({
            action: "ANALYZE_VIDEO",
            youtubeUrl: youtubeUrl,
            force_reanalyse: forceReanalyse
        });

        if (
            !response ||
            response.started !== true ||
            !response.job_id
        ) {
            console.error(
                "NeuroShield AI: Analysis could not start:",
                response
            );

            return false;
        }

        if (
            sessionId !== analysisSessionId ||
            currentVideoId !== requestedVideoId
        ) {
            return false;
        }

        activeAnalysisJobId = response.job_id;

        console.log(
            "NeuroShield AI: Analysis started successfully.",
            "Job ID:",
            activeAnalysisJobId
        );

        if (forceReanalyse) {
            setMonitoringStatus(true);
        }

        void pollAnalysisFromContentScript(
            activeAnalysisJobId,
            requestedVideoId,
            sessionId
        );

        return true;

    } catch (error) {
        console.error(
            "NeuroShield AI: Could not request analysis:",
            error
        );

        return false;
    }
}


// ============================================================
// POLL ANALYSIS FROM CONTENT SCRIPT
// ============================================================

async function pollAnalysisFromContentScript(
    jobId,
    requestedVideoId,
    sessionId
) {

    if (!jobId) {

        console.error(
            "NeuroShield AI: Cannot poll without a job ID."
        );

        return;
    }

    analysisPolling = true;

    for (
        let attempt = 1;
        attempt <= MAX_ANALYSIS_POLL_ATTEMPTS;
        attempt++
    ) {

        // --------------------------------------------------------
        // STOP IF USER NAVIGATED TO ANOTHER VIDEO
        // --------------------------------------------------------

        if (
            currentVideoId !== requestedVideoId ||
            sessionId !== analysisSessionId
        ) {

            console.log(
                "NeuroShield AI: Video changed. Stopping old analysis polling."
            );

            return;
        }

        // --------------------------------------------------------
        // WAIT 5 SECONDS
        // --------------------------------------------------------

        await sleepInContentScript(
            ANALYSIS_POLL_INTERVAL_MS
        );

        if (
            sessionId !== analysisSessionId ||
            currentVideoId !== requestedVideoId
        ) {
            return;
        }

        try {

            console.log(
                `NeuroShield AI: Checking analysis status (${attempt}/${MAX_ANALYSIS_POLL_ATTEMPTS})...`
            );

            const response =
                await chrome.runtime.sendMessage({

                    action: "CHECK_ANALYSIS_STATUS",

                    jobId: jobId

                });

            // Ignore responses from older sessions.
            if (
                sessionId !== analysisSessionId ||
                currentVideoId !== requestedVideoId
            ) {
                return;
            }

            if (
                !response ||
                response.success !== true ||
                !response.data
            ) {

                console.warn(
                    "NeuroShield AI: Status check failed:",
                    response
                );

                continue;
            }

            const data = response.data;

            console.log(
                "NeuroShield AI: Analysis status:",
                data.status
            );

            // ----------------------------------------------------
            // ANALYSIS COMPLETE
            // ----------------------------------------------------

            if (data.status === "complete") {

                if (!data.result) {

                    console.error(
                        "NeuroShield AI: Analysis completed but no result was returned."
                    );

                    analysisPolling = false;
                    activeAnalysisJobId = null;

                    return;
                }

                // Ensure the video has not changed.
                if (
                    currentVideoId !== requestedVideoId ||
                    sessionId !== analysisSessionId
                ) {

                    console.log(
                        "NeuroShield AI: Ignoring result because the video changed."
                    );

                    analysisPolling = false;

                    return;
                }

                console.log(
                    "NeuroShield AI: Backend analysis received."
                );

                console.log(
                    "NeuroShield AI: REAL ANALYSIS RESULT:",
                    data.result
                );

                // Update the analysis results.
                updateRealRiskResult(
                    data.result
                );

                // ============================================================
                // SHOW SUCCESS ONLY FOR MANUAL REANALYSIS
                // ============================================================

                if (manualReanalysisSessionId === sessionId) {

                    const reanalyseMessage =
                        document.querySelector("#ns-reanalyse-message");

                    if (reanalyseMessage) {

                        reanalyseMessage.textContent =
                            "Video reanalysed successfully!";

                        reanalyseMessage.style.color = "#16a34a";

                    }

                    manualReanalysisSessionId = null;
                }

                // ----------------------------------------------------
                // CLEAN UP COMPLETED JOB
                // ----------------------------------------------------

                activeAnalysisJobId = null;

                analysisPolling = false;

                console.log(
                    "NeuroShield AI: UI updated successfully."
                );

                return;
            }

            // ----------------------------------------------------
            // ANALYSIS FAILED
            // ----------------------------------------------------

            if (data.status === "failed") {

                console.error(
                    "NeuroShield AI: Analysis failed:",
                    data.error || "Unknown backend error."
                );

                activeAnalysisJobId = null;

                analysisPolling = false;

                // ====================================================
                // SHOW FAILURE ONLY FOR MANUAL REANALYSIS
                // ====================================================

                if (manualReanalysisSessionId === sessionId) {

                    const reanalyseMessage =
                        document.querySelector(
                            "#ns-reanalyse-message"
                        );

                    if (reanalyseMessage) {

                        reanalyseMessage.textContent =
                            "Video reanalysis failed. Please try again.";

                        reanalyseMessage.style.color =
                            "#dc2626";

                    }

                    manualReanalysisSessionId = null;
                }

                return;
            }

            // ----------------------------------------------------
            // ANALYSIS STILL PROCESSING
            // ----------------------------------------------------

            console.log(
                "NeuroShield AI: Analysis still processing..."
            );

        } catch (error) {

            console.warn(
                "NeuroShield AI: Analysis status request failed:",
                error
            );

            // Continue polling after temporary errors.

        }

    }

    // --------------------------------------------------------
    // ANALYSIS POLLING TIMED OUT
    // --------------------------------------------------------

    if (
        sessionId !== analysisSessionId ||
        currentVideoId !== requestedVideoId
    ) {
        return;
    }

    activeAnalysisJobId = null;

    analysisPolling = false;

    console.error(
        "NeuroShield AI: Analysis polling timed out."
    );

    if (manualReanalysisSessionId === sessionId) {

        const reanalyseMessage =
            document.querySelector(
                "#ns-reanalyse-message"
            );

        if (reanalyseMessage) {

            reanalyseMessage.textContent =
                "Reanalysis timed out. Please try again.";

            reanalyseMessage.style.color =
                "#dc2626";
        }

        manualReanalysisSessionId = null;
    }

}


// ============================================================
// CONTENT SCRIPT SLEEP
// ============================================================

function sleepInContentScript(
    milliseconds
) {

    return new Promise(
        function (resolve) {

            setTimeout(
                resolve,
                milliseconds
            );

        }
    );

}

// ============================================================
// UPDATE REAL RISK RESULT
// ============================================================

function updateRealRiskResult(
    data
) {

    if (!data) {

        console.warn(
            "NeuroShield AI: No analysis data received."
        );


        return;

    }


    const riskLevel =
        data.risk_level ||
        "Unknown Risk";


    const confidence =
        typeof data.confidence ===
        "number"
            ? Math.round(
                data.confidence *
                100
            )
            : 0;


    console.log(
        "NeuroShield AI: Updating UI with real result:",
        riskLevel,
        confidence + "%"
    );

    // ========================================================
    // HYBRID DEVELOPMENTAL ASSESSMENT
    // ========================================================


    // ========================================================
    // GET MAIN RESULT ELEMENTS
    // ========================================================

    const mainCard =
        document.getElementById(
            "mainScoreCard"
        );


    const overallScore =
        document.getElementById(
            "overallScore"
        );


    const overallScoreLabel =
        document.getElementById(
            "overallScoreLabel"
        );


    const statusText =
        document.getElementById(
            "analysisStatusText"
        );


    const liveBadge =
        document.getElementById(
            "analysisLiveBadge"
        );


    const description =
        document.getElementById(
            "mainScoreDescription"
        );


    // ========================================================
    // DISPLAY REAL MODEL CONFIDENCE
    // ========================================================

    if (overallScore) {

        overallScore.textContent =
            confidence + "%";

    }


    // ========================================================
    // DISPLAY REAL RISK LEVEL
    // ========================================================

    if (overallScoreLabel) {

        overallScoreLabel.textContent =
            riskLevel;

    }

    // ========================================================
    // UPDATE AI RISK CARD FROM MODEL CLASS
    // ========================================================

    if (mainCard) {

        // Remove any colour left from a previous video.
        mainCard.classList.remove(
            "low",
            "moderate",
            "high"
        );

    }


    if (riskLevel === "High Risk") {

        if (overallScoreLabel) {

            overallScoreLabel.textContent =
                "High Developmental Impact";

        }

        if (mainCard) {

            mainCard.classList.add(
                "high"
            );

        }

    } else if (riskLevel === "Medium Risk") {

        if (overallScoreLabel) {

            overallScoreLabel.textContent =
                "Moderate Developmental Impact";

        }

        if (mainCard) {

            mainCard.classList.add(
                "moderate"
            );

        }

    } else if (riskLevel === "Low Risk") {

        if (overallScoreLabel) {

            overallScoreLabel.textContent =
                "Low Developmental Impact";

        }

        if (mainCard) {

            mainCard.classList.add(
                "low"
            );

        }

    } else {

        if (overallScoreLabel) {

            overallScoreLabel.textContent =
                "Developmental Impact Unavailable";

        }

    }

    // ========================================================
    // ANALYSIS STATUS
    // ========================================================

    if (statusText) {

        statusText.textContent =
            "Analysis complete";

    }


    if (liveBadge) {

        liveBadge.textContent =
            "MODEL PREDICTION";

    }


    // ========================================================
    // RESULT DESCRIPTION
    // ========================================================

    if (description) {

        description.textContent =
            `Model confidence: ${confidence}%. ` +
            `Analysis completed using ${data.feature_count || 42} ` +
            `multimodal features from the first ` +
            `${Math.round(
                data.analysis_duration_seconds ||
                300
            )} seconds of this video.`;

    }


    // ========================================================
    // DEVELOPMENTAL IMPACT SCORES
    // ========================================================

    const developmentalScores =
        data.developmental_scores;


    if (developmentalScores) {

        updateScoreBar(
            developmentalScores.cognitive,
            "cognitiveScore",
            "cognitiveBar"
        );


        updateScoreBar(
            developmentalScores.behavioural,
            "behaviouralScore",
            "behaviouralBar"
        );


        updateScoreBar(
            developmentalScores.emotional,
            "emotionalScore",
            "emotionalBar"
        );

        updateOverallDevelopmentalDonut(
            developmentalScores.overall
        );

        console.log(
            "NeuroShield AI: Developmental scores updated:",
            developmentalScores
        );

    }

    // ========================================================
    // PARENT GUIDANCE
    // ========================================================

    if (
        data.hybrid_assessment &&
        developmentalScores
    ) {

        updateParentGuidance(
            data.hybrid_assessment,
            developmentalScores
        );

    }


    // ========================================================
    // EXPLAINABLE AI - SHAP
    // ========================================================
    //
    // IMPORTANT:
    // The old file rendered this section twice.
    // The duplicate has now been removed.
    // ========================================================

    const explainability =
        data.explainability;

    const featureInterpretations =
        data.feature_interpretations || {};

    // ========================================================
    // HYBRID DEVELOPMENTAL ASSESSMENT
    // ========================================================

    updateHybridAssessment(
        data.hybrid_assessment,
        developmentalScores,
        explainability,
        featureInterpretations
    );


    if (explainability) {

        renderExplainability(
            explainability
        );


        console.log(
            "NeuroShield AI: SHAP explanation updated:",
            explainability
        );

    }


    // ========================================================
    // SHAP-BASED DETECTED MULTIMEDIA FEATURES
    // ========================================================

    if (
        explainability &&
        Array.isArray(
            explainability.feature_contributions
        )
    ) {

        renderContributingFeatures(
            explainability.feature_contributions,
            featureInterpretations
        );


        console.log(
            "NeuroShield AI: SHAP-based multimedia features updated:",
            explainability.feature_contributions
        );

    }


    // ========================================================
    // HIGH RISK NOTIFICATION
    // ========================================================

    const hybridCategory =
        data.hybrid_assessment &&
        data.hybrid_assessment.category;


    if (
        riskLevel === "High Risk" ||
        hybridCategory === "High"
    ) {

        triggerHighRiskAlert(
            riskLevel === "High Risk",
            hybridCategory === "High"
        );

    }

}

/// ============================================================
// HYBRID DEVELOPMENTAL ASSESSMENT
// ============================================================

function updateHybridAssessment(
    hybridAssessment,
    developmentalScores = null,
    explainability = null,
    featureInterpretations = {}
) {

    const card =
        document.getElementById(
            "hybridAssessmentCard"
        );

    const scoreElement =
        document.getElementById(
            "hybridAssessmentScore"
        );

    const categoryElement =
        document.getElementById(
            "hybridAssessmentCategory"
        );

    const badge =
        document.getElementById(
            "hybridAssessmentBadge"
        );

    const description =
        document.getElementById(
            "hybridAssessmentDescription"
        );

    const explanationContainer =
        document.getElementById(
            "hybridExplanation"
        );


    // ========================================================
    // SAFETY CHECK
    // ========================================================

    if (
        !hybridAssessment ||
        typeof hybridAssessment.score !== "number"
    ) {

        console.warn(
            "NeuroShield AI: Hybrid assessment unavailable."
        );

        if (scoreElement) {
            scoreElement.textContent = "—";
        }

        if (categoryElement) {
            categoryElement.textContent =
                "Assessment unavailable";
        }

        if (badge) {
            badge.textContent =
                "UNAVAILABLE";
        }

        if (explanationContainer) {
            explanationContainer.style.display =
                "none";
        }

        return;
    }


    // ========================================================
    // READ BACKEND VALUES
    // ========================================================

    const safeScore =
        Math.max(
            0,
            Math.min(
                100,
                hybridAssessment.score
            )
        );

    const category =
        hybridAssessment.category ||
        "Unknown";

    const rfEvidence =
        typeof hybridAssessment.rf_risk_evidence === "number"
            ? Math.max(
                0,
                Math.min(
                    100,
                    hybridAssessment.rf_risk_evidence
                )
            )
            : null;

    const developmentalImpact =
        typeof hybridAssessment.developmental_impact === "number"
            ? Math.max(
                0,
                Math.min(
                    100,
                    hybridAssessment.developmental_impact
                )
            )
            : null;


    // ========================================================
    // MAIN SCORE
    // ========================================================

    if (scoreElement) {

        scoreElement.textContent =
            `${Math.round(safeScore)} / 100`;

    }


    if (categoryElement) {

        categoryElement.textContent =
            "Overall Developmental Assessment";

    }


    if (badge) {

        badge.textContent =
            "HYBRID RESULT (RF & DS)";

    }


    if (description) {

        description.textContent =
            "Combined assessment using Random Forest " +
            "risk evidence and developmental scoring.";

    }


    // ========================================================
    // CARD COLOUR
    // ========================================================

    if (card) {

        card.classList.remove(
            "low",
            "moderate",
            "high"
        );

        if (category === "High") {

            card.classList.add("high");

        } else if (category === "Medium") {

            card.classList.add("moderate");

        } else if (category === "Low") {

            card.classList.add("low");

        }

    }


    // ========================================================
    // CALCULATION BREAKDOWN
    // ========================================================

    const rfValueElement =
        document.getElementById(
            "hybridRfEvidence"
        );

    const rfBar =
        document.getElementById(
            "hybridRfEvidenceBar"
        );

    const developmentalValueElement =
        document.getElementById(
            "hybridDevelopmentalImpact"
        );

    const developmentalBar =
        document.getElementById(
            "hybridDevelopmentalImpactBar"
        );

    const combinedResult =
        document.getElementById(
            "hybridCombinedResult"
        );


    if (rfEvidence !== null) {

        if (rfValueElement) {

            rfValueElement.textContent =
                `${Math.round(rfEvidence)} / 100`;

        }

        if (rfBar) {

            rfBar.style.width =
                `${rfEvidence}%`;

        }

    }


    if (developmentalImpact !== null) {

        if (developmentalValueElement) {

            developmentalValueElement.textContent =
                `${Math.round(developmentalImpact)} / 100`;

        }

        if (developmentalBar) {

            developmentalBar.style.width =
                `${developmentalImpact}%`;

        }

    }


    if (combinedResult) {

        combinedResult.textContent =
            `${Math.round(safeScore)} / 100`;

    }


    // ========================================================
    // WHY THIS RESULT?
    // ========================================================

    const summaryElement =
        document.getElementById(
            "hybridWhySummary"
        );

    const developmentalExplanation =
        document.getElementById(
            "hybridDevelopmentalExplanation"
        );

    const rfExplanation =
        document.getElementById(
            "hybridRfExplanation"
        );


    // --------------------------------------------------------
    // HYBRID COMPONENT EXPLANATION
    // --------------------------------------------------------

    if (
        summaryElement &&
        rfEvidence !== null &&
        developmentalImpact !== null
    ) {

        const difference =
            rfEvidence -
            developmentalImpact;

        if (
            rfEvidence >= 68.5 &&
            developmentalImpact >= 68.5
        ) {

            summaryElement.textContent =
                "The combined assessment is higher because " +
                "both the Random Forest risk evidence and " +
                "developmental impact produced relatively " +
                "higher scores.";

        } else if (difference >= 15) {

            summaryElement.textContent =
                "The Random Forest risk evidence was higher " +
                "than the developmental impact score and " +
                "contributed more strongly to the combined result.";

        } else if (difference <= -15) {

            summaryElement.textContent =
                "The developmental impact score was higher " +
                "than the Random Forest risk evidence and " +
                "contributed more strongly to the combined result.";

        } else if (
            rfEvidence < 28 &&
            developmentalImpact < 28
        ) {

            summaryElement.textContent =
                "The combined assessment is lower because " +
                "both components produced relatively lower scores.";

        } else {

            summaryElement.textContent =
                "The Random Forest risk evidence and " +
                "developmental impact produced similar scores, " +
                "so both contributed comparably to the " +
                "combined assessment.";

        }

    }


    // --------------------------------------------------------
    // DEVELOPMENTAL EXPLANATION
    // --------------------------------------------------------

    if (
        developmentalExplanation &&
        developmentalScores
    ) {

        const dimensions = [
            {
                name: "Cognitive",
                value: Number(
                    developmentalScores.cognitive
                )
            },
            {
                name: "Behavioural",
                value: Number(
                    developmentalScores.behavioural
                )
            },
            {
                name: "Emotional",
                value: Number(
                    developmentalScores.emotional
                )
            }
        ].filter(
            item => Number.isFinite(item.value)
        );


        if (dimensions.length > 0) {

            dimensions.sort(
                (a, b) =>
                    b.value - a.value
            );

            const strongest =
                dimensions[0];

            developmentalExplanation.textContent =
                `${strongest.name} was the strongest ` +
                `measured developmental dimension ` +
                `(${Math.round(strongest.value)} / 100).`;

        } else {

            developmentalExplanation.textContent =
                "Developmental dimension details " +
                "were unavailable.";

        }

    }


    // --------------------------------------------------------
    // RANDOM FOREST / SHAP FEATURE EXPLANATION
    // --------------------------------------------------------

    const supportingContainer =
        document.getElementById(
            "hybridSupportingFeatures"
        );

    const opposingContainer =
        document.getElementById(
            "hybridOpposingFeatures"
        );


    const contributions =
        explainability &&
        Array.isArray(
            explainability.feature_contributions
        )
            ? explainability.feature_contributions
            : [];


    // --------------------------------------------------------
    // FEATURE INTERPRETATION LOOKUP
    // --------------------------------------------------------

    function getFeatureInterpretation(
        featureName
    ) {

        if (
            !featureInterpretations ||
            !featureName
        ) {
            return "";
        }


        const interpretation =
            featureInterpretations[
                featureName
                ];


        if (!interpretation) {
            return "";
        }


        if (
            typeof interpretation.reference_label ===
            "string"
        ) {

            return interpretation.reference_label;

        }


        return "";

    }


    // --------------------------------------------------------
    // CREATE PARENT-FRIENDLY FEATURE ROW
    // --------------------------------------------------------

    function createHybridFeatureRow(
        item,
        direction
    ) {

        const row =
            document.createElement("div");

        row.className =
            "hybrid-feature-row";


        const name =
            document.createElement("div");

        name.className =
            "hybrid-feature-name";

        name.textContent =
            item.friendly_name ||
            formatHybridFeatureName(
                item.feature
            );


        const interpretation =
            document.createElement("div");

        interpretation.className =
            "hybrid-feature-interpretation";


        const interpretationText =
            getFeatureInterpretation(
                item.feature
            );


        interpretation.textContent =
            interpretationText ||
            "Reference range unavailable";


        const influence =
            document.createElement("div");

        influence.className =
            "hybrid-feature-influence";


        if (direction === "supporting") {

            influence.textContent =
                "Supported the Random Forest prediction";

        } else {

            influence.textContent =
                "Opposed the Random Forest prediction";

        }


        row.appendChild(name);
        row.appendChild(interpretation);
        row.appendChild(influence);

        return row;

    }


    // --------------------------------------------------------
    // SUPPORTING FEATURES
    // --------------------------------------------------------

    const supporting =
        explainability &&
        Array.isArray(
            explainability.supporting_factors
        )
            ? explainability.supporting_factors
            : [];


    if (supportingContainer) {

        supportingContainer.innerHTML = "";

        if (supporting.length > 0) {

            supporting.forEach(
                item => {

                    supportingContainer.appendChild(
                        createHybridFeatureRow(
                            item,
                            "supporting"
                        )
                    );

                }
            );

        } else {

            const empty =
                document.createElement("div");

            empty.className =
                "hybrid-feature-empty";

            empty.textContent =
                "No supporting feature details available.";

            supportingContainer.appendChild(
                empty
            );

        }

    }


    // --------------------------------------------------------
    // OPPOSING FEATURES
    // --------------------------------------------------------

    const opposing =
        explainability &&
        Array.isArray(
            explainability.opposing_factors
        )
            ? explainability.opposing_factors
            : [];


    if (opposingContainer) {

        opposingContainer.innerHTML = "";

        if (opposing.length > 0) {

            opposing.forEach(
                item => {

                    opposingContainer.appendChild(
                        createHybridFeatureRow(
                            item,
                            "opposing"
                        )
                    );

                }
            );

        } else {

            const empty =
                document.createElement("div");

            empty.className =
                "hybrid-feature-empty";

            empty.textContent =
                "No opposing feature details available.";

            opposingContainer.appendChild(
                empty
            );

        }

    }

    const supportingCount =
        document.getElementById(
            "hybridSupportingCount"
        );

    const opposingCount =
        document.getElementById(
            "hybridOpposingCount"
        );


    if (supportingCount) {

        supportingCount.textContent =
            `${supporting.length} ${
                supporting.length === 1
                    ? "feature"
                    : "features"
            }`;

    }


    if (opposingCount) {

        opposingCount.textContent =
            `${opposing.length} ${
                opposing.length === 1
                    ? "feature"
                    : "features"
            }`;

    }


    // ========================================================
    // SHOW EXPLANATION
    // ========================================================

    if (explanationContainer) {

        explanationContainer.style.display =
            "block";

        initialiseHybridAccordions();
        initialiseHybridDetailAccordions();
        initialiseMultimediaSection();
        initialiseParentalGuidance();
        initialiseExplainabilitySection();

    }


    console.log(
        "NeuroShield AI: Hybrid assessment updated:",
        `${safeScore.toFixed(2)} / 100`,
        category
    );

}

// ============================================================
// HYBRID EXPLANATION ACCORDIONS
// ============================================================

function initialiseHybridAccordions() {

    const buttons =
        document.querySelectorAll(
            ".hybrid-accordion-button"
        );


    buttons.forEach(button => {

        if (
            button.dataset.hybridAccordionReady === "true"
        ) {
            return;
        }


        button.dataset.hybridAccordionReady =
            "true";


        button.addEventListener(
            "click",
            () => {

                const targetId =
                    button.dataset.hybridTarget;

                const content =
                    document.getElementById(
                        targetId
                    );

                const arrow =
                    button.querySelector(
                        ".hybrid-accordion-arrow"
                    );


                if (!content) {
                    return;
                }


                const isOpen =
                    content.classList.contains(
                        "open"
                    );


                // CLOSE
                if (isOpen) {

                    content.classList.remove(
                        "open"
                    );

                    button.classList.remove(
                        "open"
                    );

                    button.setAttribute(
                        "aria-expanded",
                        "false"
                    );

                    if (arrow) {
                        arrow.textContent = "▸";
                    }

                }

                // OPEN
                else {

                    content.classList.add(
                        "open"
                    );

                    button.classList.add(
                        "open"
                    );

                    button.setAttribute(
                        "aria-expanded",
                        "true"
                    );

                    if (arrow) {
                        arrow.textContent = "⌄";
                    }

                }

            }
        );

    });

}

// ============================================================
// HYBRID DETAIL ACCORDIONS
// ============================================================

function initialiseHybridDetailAccordions() {

    const buttons =
        document.querySelectorAll(
            ".hybrid-detail-toggle"
        );


    buttons.forEach(button => {

        if (
            button.dataset.ready === "true"
        ) {
            return;
        }


        button.dataset.ready = "true";


        button.addEventListener(
            "click",
            function () {

                const targetId =
                    button.dataset.hybridDetailTarget;


                const content =
                    document.getElementById(
                        targetId
                    );


                const arrow =
                    button.querySelector(
                        ".hybrid-detail-arrow"
                    );


                if (!content) {
                    return;
                }


                const isOpen =
                    content.classList.toggle(
                        "open"
                    );


                button.setAttribute(
                    "aria-expanded",
                    isOpen
                        ? "true"
                        : "false"
                );


                if (arrow) {

                    arrow.textContent =
                        isOpen
                            ? "⌃"
                            : "⌄";

                }

            }
        );

    });

}

// ============================================================
// MULTIMEDIA SECTION ACCORDION
// ============================================================

function initialiseMultimediaSection() {

    const toggle =
        document.getElementById(
            "multimediaSectionToggle"
        );

    const content =
        document.getElementById(
            "multimediaSectionContent"
        );

    const arrow =
        document.getElementById(
            "multimediaSectionArrow"
        );


    if (
        !toggle ||
        !content ||
        !arrow
    ) {
        return;
    }


    if (
        toggle.dataset.ready === "true"
    ) {
        return;
    }


    toggle.dataset.ready = "true";


    toggle.addEventListener(
        "click",
        function () {

            const isOpen =
                content.classList.toggle(
                    "open"
                );

            toggle.setAttribute(
                "aria-expanded",
                isOpen
                    ? "true"
                    : "false"
            );

            arrow.textContent =
                isOpen
                    ? "⌃"
                    : "⌄";

        }
    );

}

// ============================================================
// PARENTAL GUIDANCE ACCORDION
// ============================================================

function initialiseParentalGuidance() {

    const toggle =
        document.getElementById(
            "parentalGuidanceToggle"
        );

    const content =
        document.getElementById(
            "parentalGuidanceContent"
        );

    const arrow =
        document.getElementById(
            "parentalGuidanceArrow"
        );


    if (
        !toggle ||
        !content ||
        !arrow
    ) {
        return;
    }


    if (
        toggle.dataset.ready === "true"
    ) {
        return;
    }


    toggle.dataset.ready = "true";


    toggle.addEventListener(
        "click",
        function () {

            const isOpen =
                content.classList.toggle(
                    "open"
                );


            toggle.setAttribute(
                "aria-expanded",
                isOpen
                    ? "true"
                    : "false"
            );


            arrow.textContent =
                isOpen
                    ? "⌃"
                    : "⌄";

        }
    );

}

// ============================================================
// HYBRID FEATURE NAME FORMATTER
// ============================================================

function formatHybridFeatureName(
    featureName
) {

    const readableNames = {

        attention_score:
            "Attention score",

        attention_reset_rate:
            "Attention reset rate",

        reward_cue_frequency:
            "Reward cue frequency",

        motion_spike_rate:
            "Motion spike rate",

        motion_mean:
            "Average motion",

        motion_std:
            "Motion variation",

        scene_rate:
            "Scene change rate",

        flicker_rate:
            "Visual flicker rate",

        avg_saturation:
            "Colour saturation",

        avg_brightness:
            "Visual brightness",

        loudness:
            "Audio loudness",

        sound_density:
            "Sound density",

        audio_variation:
            "Audio variation",

        avg_pitch:
            "Average pitch",

        pitch_variation:
            "Pitch variation",

        emotion_arousal:
            "Emotional arousal",

        emotion_valence:
            "Emotional valence",

        emotion_stability:
            "Emotional stability",

        loop_detection_score:
            "Repetitive content patterns",

        phrase_repetition:
            "Phrase repetition",

        vocabulary_diversity:
            "Vocabulary diversity",

        sentence_complexity:
            "Sentence complexity"

    };


    if (readableNames[featureName]) {

        return readableNames[
            featureName
            ];

    }


    return String(featureName || "")
        .replaceAll("_", " ")
        .replace(
            /\b\w/g,
            letter =>
                letter.toUpperCase()
        );

}

// ============================================================
// PARENTAL GUIDANCE
// ============================================================

function updateParentGuidance(
    hybridAssessment,
    developmentalScores
) {

    const container =
        document.getElementById("recommendation");

    const intro =
        document.getElementById("parentalGuidanceIntro");


    if (!container) {
        return;
    }


    // --------------------------------------------------------
    // READ CURRENT ASSESSMENT
    // --------------------------------------------------------

    const hybridCategory =
        String(
            hybridAssessment?.hybrid_category ||
            hybridAssessment?.category ||
            ""
        ).toLowerCase();


    const cognitive =
        Number(
            developmentalScores?.cognitive?.score ??
            developmentalScores?.cognitive_score ??
            0
        );


    const behavioural =
        Number(
            developmentalScores?.behavioural?.score ??
            developmentalScores?.behavioural_score ??
            0
        );


    const emotional =
        Number(
            developmentalScores?.emotional?.score ??
            developmentalScores?.emotional_score ??
            0
        );


    // --------------------------------------------------------
    // INTRODUCTION
    // --------------------------------------------------------

    if (intro) {

        intro.textContent =
            "Based on this video's assessment, parents may consider the following guidance.";

    }


    // --------------------------------------------------------
    // BUILD RECOMMENDATION LIST
    // --------------------------------------------------------

    const recommendations = [];


    function addRecommendation(
        id,
        icon,
        title,
        action,
        reason
    ) {

        if (
            recommendations.some(
                item => item.id === id
            )
        ) {
            return;
        }


        recommendations.push({
            id,
            icon,
            title,
            action,
            reason
        });

    }


    // --------------------------------------------------------
    // HIGH HYBRID RESULT
    // --------------------------------------------------------

    if (hybridCategory.includes("high")) {

        addRecommendation(
            "watch-together",
            "👨‍👩‍👧",
            "Watch Together & Discuss",
            "Consider watching the video together and talking with your child about what they are seeing and hearing.",
            "The overall NeuroShield assessment identified a high level of combined machine-learning risk evidence and developmental stimulation."
        );


        addRecommendation(
            "viewing-break",
            "⏸",
            "Take a Viewing Break",
            "Consider taking a break before continuing to another video and encourage an offline activity such as play, reading or physical activity.",
            "The overall assessment suggests that a pause between videos may be appropriate before continuing viewing."
        );


        addRecommendation(
            "autoplay",
            "▶",
            "Consider Turning Off Autoplay",
            "Consider disabling autoplay so that another video does not begin automatically after the current video finishes.",
            "The video received a high overall assessment, so allowing the child or parent to make an intentional choice before the next video may be helpful."
        );

    }


    // --------------------------------------------------------
    // BEHAVIOURAL PRIORITY
    // --------------------------------------------------------

    if (behavioural >= 60) {

        addRecommendation(
            "behavioural-break",
            "⏸",
            "Pause Between Videos",
            "Consider creating a natural stopping point after this video before another video begins.",
            `Behavioural stimulation was elevated in this analysis (${formatGuidanceScore(behavioural)}/100).`
        );


        addRecommendation(
            "autoplay",
            "▶",
            "Consider Turning Off Autoplay",
            "Consider disabling autoplay so that viewing does not automatically continue into another video.",
            `Behavioural stimulation was elevated in this analysis (${formatGuidanceScore(behavioural)}/100).`
        );

    }


    // --------------------------------------------------------
    // COGNITIVE PRIORITY
    // --------------------------------------------------------

    if (cognitive >= 60) {

        addRecommendation(
            "watch-discuss",
            "💬",
            "Watch & Discuss",
            "Ask simple questions about what happened in the video, what your child noticed, and what they understood.",
            `Cognitive stimulation was elevated in this analysis (${formatGuidanceScore(cognitive)}/100).`
        );


        addRecommendation(
            "offline-connection",
            "📚",
            "Connect Viewing to the Real World",
            "Consider following the video with an offline activity such as reading, drawing, play or discussing a related real-world example.",
            `Cognitive stimulation was elevated in this analysis (${formatGuidanceScore(cognitive)}/100).`
        );

    }


    // --------------------------------------------------------
    // EMOTIONAL PRIORITY
    // --------------------------------------------------------

    if (emotional >= 60) {

        addRecommendation(
            "emotional-discussion",
            "💬",
            "Talk About the Video",
            "Consider asking your child how the video made them feel and discussing any intense or confusing moments together.",
            `Emotional stimulation was elevated in this analysis (${formatGuidanceScore(emotional)}/100).`
        );

    }


    // --------------------------------------------------------
    // MEDIUM HYBRID RESULT
    // --------------------------------------------------------

    if (hybridCategory.includes("medium")) {

        addRecommendation(
            "watch-together",
            "👨‍👩‍👧",
            "Watch Together When Possible",
            "Consider watching alongside your child when practical and discussing parts of the video that attract their attention.",
            "The overall NeuroShield assessment identified a moderate level of combined machine-learning risk evidence and developmental stimulation."
        );


        addRecommendation(
            "balanced-viewing",
            "⚖",
            "Balance Viewing with Offline Activities",
            "Consider balancing screen viewing with activities such as play, reading, conversation or physical activity.",
            "The overall assessment suggests that maintaining balanced media habits may be appropriate."
        );

    }


    // --------------------------------------------------------
    // LOW HYBRID RESULT
    // --------------------------------------------------------

    if (hybridCategory.includes("low")) {

        addRecommendation(
            "balanced-media",
            "⚖",
            "Maintain Balanced Media Habits",
            "Continue balancing video viewing with sleep, physical activity, family interaction, reading and other offline activities.",
            "The video received a lower overall NeuroShield assessment, but balanced media habits remain useful regardless of an individual video's result."
        );


        addRecommendation(
            "co-viewing",
            "👨‍👩‍👧",
            "Watch & Talk Together",
            "When possible, watching and discussing media together can help make viewing a more active experience.",
            "This is general parental guidance and is not an indication that NeuroShield detected a specific problem."
        );

    }


    // --------------------------------------------------------
    // GENERAL BEDTIME GUIDANCE
    // --------------------------------------------------------

    addRecommendation(
        "bedtime",
        "🌙",
        "Protect Bedtime",
        "Consider keeping media use from interfering with the child's regular bedtime and sleep routine.",
        "This is general media-use guidance rather than a recommendation triggered by one specific NeuroShield feature."
    );


    // --------------------------------------------------------
    // FALLBACK
    // --------------------------------------------------------

    if (recommendations.length === 0) {

        addRecommendation(
            "general-guidance",
            "👨‍👩‍👧",
            "Stay Involved in Viewing",
            "Consider watching and discussing digital media together and balancing viewing with offline activities.",
            "NeuroShield could not determine a specific guidance priority from the current assessment."
        );

    }


    // --------------------------------------------------------
    // RENDER
    // --------------------------------------------------------

    container.innerHTML =
        recommendations
            .map(
                (item, index) => {

                    const contentId =
                        `parentGuidanceItem-${index}`;

                    return `
                        <div class="parent-guidance-item">

                            <button
                                type="button"
                                class="parent-guidance-item-toggle"
                                data-guidance-target="${contentId}"
                                aria-expanded="false"
                            >

                                <span class="parent-guidance-item-heading">

                                    <span class="parent-guidance-item-icon">
                                        ${escapeHTML(item.icon)}
                                    </span>

                                    <span>
                                        ${escapeHTML(item.title)}
                                    </span>

                                </span>

                                <span class="parent-guidance-item-arrow">
                                    ⌄
                                </span>

                            </button>


                            <div
                                class="parent-guidance-item-content"
                                id="${contentId}"
                            >

                                <p class="parent-guidance-action">
                                    ${escapeHTML(item.action)}
                                </p>


                                <div class="parent-guidance-reason">

                                    <strong>
                                        Why this is recommended
                                    </strong>

                                    <p>
                                        ${escapeHTML(item.reason)}
                                    </p>

                                </div>

                            </div>

                        </div>
                    `;

                }
            )
            .join("");


    initialiseParentGuidanceItems();

}

// ============================================================
// FORMAT PARENTAL GUIDANCE SCORE
// ============================================================

function formatGuidanceScore(value) {

    const number = Number(value);

    if (!Number.isFinite(number)) {
        return "—";
    }

    return number.toFixed(1);

}


// ============================================================
// PARENTAL GUIDANCE ITEM ACCORDIONS
// ============================================================

function initialiseParentGuidanceItems() {

    const buttons =
        document.querySelectorAll(
            ".parent-guidance-item-toggle"
        );


    buttons.forEach(button => {

        if (
            button.dataset.ready === "true"
        ) {
            return;
        }


        button.dataset.ready = "true";


        button.addEventListener(
            "click",
            function () {

                const targetId =
                    button.dataset.guidanceTarget;

                const content =
                    document.getElementById(
                        targetId
                    );

                const arrow =
                    button.querySelector(
                        ".parent-guidance-item-arrow"
                    );


                if (!content) {
                    return;
                }


                const isOpen =
                    content.classList.toggle(
                        "open"
                    );


                button.setAttribute(
                    "aria-expanded",
                    isOpen
                        ? "true"
                        : "false"
                );


                if (arrow) {

                    arrow.textContent =
                        isOpen
                            ? "⌃"
                            : "⌄";

                }

            }
        );

    });

}

// ============================================================
// EXPLAINABILITY SECTION ACCORDION
// ============================================================

function initialiseExplainabilitySection() {

    const toggle =
        document.getElementById(
            "explainabilitySectionToggle"
        );

    const content =
        document.getElementById(
            "explainabilitySectionContent"
        );

    const arrow =
        document.getElementById(
            "explainabilitySectionArrow"
        );


    if (
        !toggle ||
        !content ||
        !arrow
    ) {
        return;
    }


    if (
        toggle.dataset.ready === "true"
    ) {
        return;
    }


    toggle.dataset.ready = "true";


    toggle.addEventListener(
        "click",
        function () {

            const isOpen =
                content.classList.toggle(
                    "open"
                );


            toggle.setAttribute(
                "aria-expanded",
                isOpen
                    ? "true"
                    : "false"
            );


            arrow.textContent =
                isOpen
                    ? "⌃"
                    : "⌄";

        }
    );

}

// ============================================================
// MONITORING STATUS
// ============================================================

function setMonitoringStatus(
    isReady
) {

    const card =
        document.getElementById(
            "monitoringStatusCard"
        );


    const dot =
        document.getElementById(
            "monitoringStatusDot"
        );


    const badge =
        document.getElementById(
            "monitoringStatusBadge"
        );


    const text =
        document.getElementById(
            "analysisStatusText"
        );


    const liveBadge =
        document.getElementById(
            "analysisLiveBadge"
        );


    if (
        !card ||
        !dot ||
        !badge ||
        !text
    ) {

        console.warn(
            "NeuroShield AI: Monitoring status elements not found."
        );


        return;

    }


    // ========================================================
    // REMOVE OLD STATES
    // ========================================================

    card.classList.remove(
        "waiting",
        "active"
    );


    dot.classList.remove(
        "waiting",
        "active"
    );


    badge.classList.remove(
        "waiting",
        "active"
    );


    // ========================================================
    // BACKEND READY
    // ========================================================

    if (isReady) {

        card.classList.add(
            "active"
        );


        dot.classList.add(
            "active"
        );


        badge.classList.add(
            "active"
        );


        badge.textContent =
            "Active";


        // Backend is connected, but analysis is
        // still running / waiting for a result.
        text.textContent =
            "Analysis in progress";


        // Keep AI Risk Assessment waiting until
        // the real backend result is received.
        if (liveBadge) {

            liveBadge.textContent =
                "ANALYSING";

        }

    }


        // ========================================================
        // WAITING FOR BACKEND
    // ========================================================

    else {

        card.classList.add(
            "waiting"
        );


        dot.classList.add(
            "waiting"
        );


        badge.classList.add(
            "waiting"
        );


        badge.textContent =
            "Waiting";


        text.textContent =
            "Waiting for backend analysis";


        // ====================================================
        // RESET MAIN SCORE CARD
        // ====================================================

        const mainCard =
            document.getElementById(
                "mainScoreCard"
            );


        const overallScore =
            document.getElementById(
                "overallScore"
            );


        const overallScoreLabel =
            document.getElementById(
                "overallScoreLabel"
            );


        if (mainCard) {

            mainCard.classList.remove(
                "low",
                "moderate",
                "high"
            );

        }


        if (overallScore) {

            overallScore.textContent =
                "—";

        }


        if (overallScoreLabel) {

            overallScoreLabel.textContent =
                "Awaiting analysis";

        }


        if (liveBadge) {

            liveBadge.textContent =
                "WAITING";

        }

    }

}


// ============================================================
// APPLY REAL BACKEND RESULTS
// ============================================================

function applyBackendResults(
    data
) {

    if (!data) {

        return;

    }


    console.log(
        "NeuroShield AI: Applying verified backend data:",
        data
    );


    // Backend has successfully returned analysis

    if (
        typeof data.overall ===
        "number"
    ) {

        setMonitoringStatus(
            true
        );

    }


    // ========================================================
    // OVERALL
    // ========================================================

    if (
        typeof data.overall ===
        "number"
    ) {

        updateScore(
            data.overall,
            "overallScore",
            "overallScoreLabel"
        );


        updateMainCardLevel(
            data.overall
        );

    }


    // ========================================================
    // DEVELOPMENTAL
    // ========================================================

    updateScoreBar(
        data.cognitive,
        "cognitiveScore",
        "cognitiveBar"
    );


    updateScoreBar(
        data.behavioural,
        "behaviouralScore",
        "behaviouralBar"
    );


    updateScoreBar(
        data.emotional,
        "emotionalScore",
        "emotionalBar"
    );


    // ========================================================
    // MULTIMEDIA
    // ========================================================

    updateFeatureScore(
        data.visual,
        "visualBar",
        "visualLevel"
    );


    updateFeatureScore(
        data.audio,
        "audioBar",
        "audioLevel"
    );


    updateFeatureScore(
        data.text,
        "textBar",
        "textLevel"
    );


    updateFeatureScore(
        data.engagement,
        "engagementBar",
        "engagementLevel"
    );


    // ========================================================
    // STATUS
    // ========================================================

    const status =
        document.getElementById(
            "analysisStatusText"
        );


    if (status) {

        status.textContent =
            "Analysis complete";

    }


    // ========================================================
    // RECOMMENDATION
    // ========================================================

    if (
        typeof data.recommendation ===
        "string" &&
        data.recommendation.trim() !==
        ""
    ) {

        const recommendation =
            document.getElementById(
                "recommendation"
            );


        if (recommendation) {

            recommendation.innerHTML = `

                <span>
                    💡
                </span>

                <p>
                    ${escapeHTML(
                data.recommendation
            )}
                </p>

            `;

        }

    }


    // ========================================================
    // INSIGHTS
    // ========================================================

    if (
        Array.isArray(
            data.insights
        ) &&
        data.insights.length >
        0
    ) {

        renderInsights(
            data.insights
        );

    }


    // ========================================================
    // HIGH ALERT
    // ========================================================

    if (
        typeof data.overall ===
        "number" &&
        data.overall >
        75
    ) {

        triggerHighRiskAlert();

    }

}

// ============================================================
// OVERALL DEVELOPMENTAL IMPACT DONUT
// ============================================================

function updateOverallDevelopmentalDonut(
    value
) {

    if (
        typeof value !== "number" ||
        !Number.isFinite(value)
    ) {

        return;

    }


    const safeValue =
        Math.max(
            0,
            Math.min(
                100,
                value
            )
        );


    const scoreElement =
        document.getElementById(
            "overallDevelopmentalScore"
        );


    const donut =
        document.getElementById(
            "overallDevelopmentalDonut"
        );


    if (scoreElement) {

        scoreElement.textContent =
            Math.round(
                safeValue
            );

    }


    if (donut) {

        const degrees =
            (
                safeValue /
                100
            ) * 360;


        donut.style.setProperty(
            "--developmental-angle",
            `${degrees}deg`
        );

    }

}

// ============================================================
// UPDATE MAIN SCORE
// ============================================================

function updateScore(
    value,
    valueId,
    labelId
) {

    if (
        typeof value !==
        "number"
    ) {

        return;

    }


    const valueElement =
        document.getElementById(
            valueId
        );


    const labelElement =
        document.getElementById(
            labelId
        );


    const safeValue =
        Math.max(
            0,
            Math.min(
                100,
                value
            )
        );


    if (valueElement) {

        valueElement.textContent =
            `${Math.round(
                safeValue
            )}%`;

    }


    if (labelElement) {

        if (
            safeValue >
            75
        ) {

            labelElement.textContent =
                "High Stimulation";

        } else if (
            safeValue <
            40
        ) {

            labelElement.textContent =
                "Low Stimulation";

        } else {

            labelElement.textContent =
                "Moderate Stimulation";

        }

    }

}


// ============================================================
// MAIN CARD COLOUR
// ============================================================

function updateMainCardLevel(
    score
) {

    const card =
        document.getElementById(
            "mainScoreCard"
        );


    if (!card) {

        return;

    }


    card.classList.remove(
        "low",
        "moderate",
        "high"
    );


    if (
        score >
        75
    ) {

        card.classList.add(
            "high"
        );

    } else if (
        score <
        40
    ) {

        card.classList.add(
            "low"
        );

    } else {

        card.classList.add(
            "moderate"
        );

    }

}


// ============================================================
// SCORE BAR
// ============================================================

function updateScoreBar(
    value,
    valueId,
    barId
) {

    if (
        typeof value !==
        "number"
    ) {

        return;

    }


    const safeValue =
        Math.max(
            0,
            Math.min(
                100,
                value
            )
        );


    const valueElement =
        document.getElementById(
            valueId
        );


    const barElement =
        document.getElementById(
            barId
        );


    if (valueElement) {

        valueElement.textContent =
            `${Math.round(
                safeValue
            )} / 100`;

    }


    if (barElement) {

        barElement.style.width =
            `${safeValue}%`;

    }

}


// ============================================================
// FEATURE SCORE
// ============================================================

function updateFeatureScore(
    value,
    barId,
    levelId
) {

    if (
        typeof value !==
        "number"
    ) {

        return;

    }


    const safeValue =
        Math.max(
            0,
            Math.min(
                100,
                value
            )
        );


    const bar =
        document.getElementById(
            barId
        );


    const level =
        document.getElementById(
            levelId
        );


    if (bar) {

        bar.style.width =
            `${safeValue}%`;

    }


    if (level) {

        if (
            safeValue >
            75
        ) {

            level.textContent =
                "High";

        } else if (
            safeValue <
            40
        ) {

            level.textContent =
                "Low";

        } else {

            level.textContent =
                "Moderate";

        }

    }

}


// ============================================================
// LIVE SHAP EXPLAINABILITY
// ============================================================

// ============================================================
// RENDER EXPLAINABILITY
// ============================================================

function renderExplainability(explainability) {

    const container =
        document.getElementById("insightContainer");


    if (!container) {
        return;
    }


    const contributions =
        explainability &&
        Array.isArray(
            explainability.feature_contributions
        )
            ? explainability.feature_contributions
            : [];


    // --------------------------------------------------------
    // NO EXPLANATION AVAILABLE
    // --------------------------------------------------------

    if (contributions.length === 0) {

        container.innerHTML = `
            <div class="empty-insight-icon">
                <img
                    src="${escapeHTML(
            chrome.runtime.getURL(
                "icons/explainability.png"
            )
        )}"
                    alt=""
                >
            </div>

            <div>
                <strong>
                    No explanation available
                </strong>

                <p>
                    Explainable AI information was not
                    available for this analysis.
                </p>
            </div>
        `;

        return;
    }


    // --------------------------------------------------------
    // FIND MOST INFLUENTIAL FEATURE
    // --------------------------------------------------------

    const strongest =
        contributions.reduce(
            (currentStrongest, item) => {

                const currentValue =
                    Math.abs(
                        Number(
                            currentStrongest?.absolute_shap ??
                            currentStrongest?.shap_value ??
                            0
                        )
                    );

                const itemValue =
                    Math.abs(
                        Number(
                            item?.absolute_shap ??
                            item?.shap_value ??
                            0
                        )
                    );


                return itemValue > currentValue
                    ? item
                    : currentStrongest;

            },
            contributions[0]
        );


    const featureName =
        strongest?.friendly_name ||
        formatHybridFeatureName(
            strongest?.feature
        );


    const shapValue =
        Number(
            strongest?.shap_value ?? 0
        );


    const supportsPrediction =
        shapValue >= 0;


    const directionText =
        supportsPrediction
            ? "Supports the Random Forest result"
            : "Opposes the Random Forest result";


    const directionClass =
        supportsPrediction
            ? "supports"
            : "opposes";


    const directionArrow =
        supportsPrediction
            ? "↑"
            : "↓";


    // --------------------------------------------------------
    // RENDER
    // --------------------------------------------------------

    container.innerHTML = `

        <div class="explainability-overview">

            <div class="explainability-overview-icon">

                <img
                    src="${escapeHTML(
        chrome.runtime.getURL(
            "icons/explainability.png"
        )
    )}"
                    alt=""
                >

            </div>


            <div class="explainability-overview-text">

                <strong>
                    What influenced the Random Forest result?
                </strong>

                <p>
                    The Random Forest evaluated the extracted
                    multimedia features to produce this
                    classification.
                </p>

            </div>

        </div>


        <div class="explainability-feature-card">

            <div class="explainability-feature-label">
                MOST INFLUENTIAL FEATURE
            </div>


            <div class="explainability-feature-name">
                ${escapeHTML(featureName)}
            </div>


            <div
                class="
                    explainability-direction
                    ${directionClass}
                "
            >

                <span class="explainability-direction-arrow">
                    ${directionArrow}
                </span>

                <span>
                    ${escapeHTML(directionText)}
                </span>

            </div>

        </div>


        <div class="explainability-method">

            <button
                type="button"
                class="explainability-method-toggle"
                id="explainabilityMethodToggle"
                aria-expanded="false"
            >

                <span>
                    How this explanation works
                </span>

                <span
                    class="explainability-method-arrow"
                    id="explainabilityMethodArrow"
                >
                    ⌄
                </span>

            </button>


            <div
                class="explainability-method-content"
                id="explainabilityMethodContent"
            >

                <p>
                    SHAP estimates how each feature contributed
                    to the Random Forest prediction. A feature
                    may support or oppose the predicted class.
                    These influences explain the model's
                    prediction and do not establish causation.
                </p>

            </div>

        </div>
    `;


    initialiseExplainabilityMethod();

}

// ============================================================
// EXPLAINABILITY METHOD ACCORDION
// ============================================================

function initialiseExplainabilityMethod() {

    const toggle =
        document.getElementById(
            "explainabilityMethodToggle"
        );

    const content =
        document.getElementById(
            "explainabilityMethodContent"
        );

    const arrow =
        document.getElementById(
            "explainabilityMethodArrow"
        );


    if (
        !toggle ||
        !content ||
        !arrow
    ) {
        return;
    }


    if (
        toggle.dataset.ready === "true"
    ) {
        return;
    }


    toggle.dataset.ready = "true";


    toggle.addEventListener(
        "click",
        function () {

            const isOpen =
                content.classList.toggle(
                    "open"
                );


            toggle.setAttribute(
                "aria-expanded",
                isOpen
                    ? "true"
                    : "false"
            );


            arrow.textContent =
                isOpen
                    ? "⌃"
                    : "⌄";

        }
    );

}

// ============================================================
// SHAP-BASED DETECTED MULTIMEDIA FEATURES
// ============================================================

function renderContributingFeatures(
    featureContributions,
    featureInterpretations = {}
) {

    if (
        !Array.isArray(
            featureContributions
        ) ||
        featureContributions.length === 0
    ) {

        return;

    }


    // ========================================================
    // SORT ALL FEATURES BY ABSOLUTE SHAP CONTRIBUTION
    // ========================================================
    //
    // The backend normally already sends these in descending
    // order, but sorting again here makes the frontend robust.
    //
    // All 42 model features remain candidates.
    // ========================================================

    const sortedContributions =
        [...featureContributions]
            .filter(
                function (feature) {

                    return (
                        feature &&
                        typeof feature.absolute_shap ===
                        "number" &&
                        Number.isFinite(
                            feature.absolute_shap
                        )
                    );

                }
            )
            .sort(
                function (a, b) {

                    return (
                        b.absolute_shap -
                        a.absolute_shap
                    );

                }
            );


    if (
        sortedContributions.length === 0
    ) {

        return;

    }


    // ========================================================
    // STRONGEST CONTRIBUTION
    // ========================================================

    const strongestContribution =
        sortedContributions[0]
            .absolute_shap;


    if (
        typeof strongestContribution !==
        "number" ||
        strongestContribution <= 0
    ) {

        return;

    }


    // ========================================================
    // DISPLAY THRESHOLD
    // ========================================================
    //
    // Individual feature bubbles are displayed when their
    // absolute SHAP contribution is at least 20% as strong
    // as the strongest feature for this prediction.
    //
    // This is only a UI display heuristic.
    //
    // It is NOT:
    // - a statistical significance threshold
    // - a developmental-risk threshold
    // - a probability threshold
    // ========================================================

    const contributionThreshold =
        strongestContribution *
        0.20;


    // ========================================================
    // SELECT MAJOR INDIVIDUAL CONTRIBUTORS
    // ========================================================

    const selectedFeatures =
        sortedContributions
            .filter(
                function (feature) {

                    return (
                        feature.absolute_shap >=
                        contributionThreshold
                    );

                }
            )
            .slice(
                0,
                12
            );


    // ========================================================
    // CREATE GROUPS
    // ========================================================
    //
    // allGroups:
    // Contains every one of the 42 RF features.
    //
    // selectedGroups:
    // Contains only features that passed the UI display
    // threshold above.
    // ========================================================

    const allGroups =
        createEmptyFeatureGroups();


    const selectedGroups =
        createEmptyFeatureGroups();


    // ========================================================
    // GROUP ALL 42 FEATURES
    // ========================================================

    sortedContributions.forEach(
        function (feature) {

            const group =
                getFeatureGroup(
                    feature.feature
                );


            allGroups[group].push(
                feature
            );

        }
    );


    // ========================================================
    // GROUP SELECTED FEATURES
    // ========================================================

    selectedFeatures.forEach(
        function (feature) {

            const group =
                getFeatureGroup(
                    feature.feature
                );


            selectedGroups[group].push(
                feature
            );

        }
    );


    // ========================================================
    // TOTAL ABSOLUTE SHAP CONTRIBUTION
    // ========================================================
    //
    // This value is used to calculate how much each modality
    // contributes to the current Random Forest prediction.
    //
    // Example:
    //
    // Visual absolute SHAP total
    // --------------------------
    // All 42 absolute SHAP total
    //
    // gives the Visual contribution share.
    //
    // These percentages are NOT model confidence and are NOT
    // developmental impact scores.
    // ========================================================

    const totalAbsoluteShap =
        sortedContributions.reduce(
            function (
                total,
                feature
            ) {

                return (
                    total +
                    feature.absolute_shap
                );

            },
            0
        );


    // ========================================================
    // VISUAL
    // ========================================================

    renderLiveContributionGroup(
        "visualFeatures",
        "visualBar",
        "visualLevel",
        allGroups.visual,
        allGroups.visual,
        totalAbsoluteShap,
        featureInterpretations
    );


    // ========================================================
    // AUDIO
    // ========================================================

    renderLiveContributionGroup(
        "audioFeatures",
        "audioBar",
        "audioLevel",
        allGroups.audio,
        allGroups.audio,
        totalAbsoluteShap,
        featureInterpretations
    );


    // ========================================================
    // TEXT
    // ========================================================

    renderLiveContributionGroup(
        "textFeatures",
        "textBar",
        "textLevel",
        allGroups.text,
        allGroups.text,
        totalAbsoluteShap,
        featureInterpretations
    );


    // ========================================================
    // ENGAGEMENT
    // ========================================================

    renderLiveContributionGroup(
        "engagementFeatures",
        "engagementBar",
        "engagementLevel",
        allGroups.engagement,
        allGroups.engagement,
        totalAbsoluteShap,
        featureInterpretations
    );


    // ========================================================
    // EMOTIONAL
    // ========================================================

    renderLiveContributionGroup(
        "emotionalFeatures",
        "emotionalFeatureBar",
        "emotionalFeatureLevel",
        allGroups.emotional,
        allGroups.emotional,
        totalAbsoluteShap,
        featureInterpretations
    );


    // ========================================================
    // VIDEO CONTEXT / METADATA
    // ========================================================

    renderLiveContributionGroup(
        "metadataFeatures",
        "metadataBar",
        "metadataLevel",
        allGroups.metadata,
        allGroups.metadata,
        totalAbsoluteShap,
        featureInterpretations
    );
    // ========================================================
    // SORT FEATURE CARDS BY LIVE SHAP CONTRIBUTION
    // ========================================================
    //
    // Highest contribution appears first.
    //
    // The percentage for each group is calculated from:
    //
    // group absolute SHAP
    // -------------------  × 100
    // total absolute SHAP
    //
    // This only changes the DISPLAY ORDER of the six cards.
    // It does not change the model, SHAP values, or prediction.
    // ========================================================

    sortFeatureCardsByContribution(
        allGroups,
        totalAbsoluteShap
    );
    // ============================================================
    // SORT MULTIMEDIA CARDS BY LIVE SHAP CONTRIBUTION
    // ============================================================

    function sortFeatureCardsByContribution(
        allGroups,
        totalAbsoluteShap
    ) {

        if (
            !allGroups ||
            typeof totalAbsoluteShap !== "number" ||
            totalAbsoluteShap <= 0
        ) {

            return;

        }


        // ========================================================
        // GET FEATURE STACK
        // ========================================================

        const featureStack =
            document.querySelector(
                ".feature-stack"
            );


        if (!featureStack) {

            return;

        }


        // ========================================================
        // MAP EACH GROUP TO ONE OF THE SIX CARDS
        // ========================================================

        const groups = [

            {
                name: "visual",
                containerId: "visualFeatures"
            },

            {
                name: "audio",
                containerId: "audioFeatures"
            },

            {
                name: "text",
                containerId: "textFeatures"
            },

            {
                name: "engagement",
                containerId: "engagementFeatures"
            },

            {
                name: "emotional",
                containerId: "emotionalFeatures"
            },

            {
                name: "metadata",
                containerId: "metadataFeatures"
            }

        ];


        // ========================================================
        // CALCULATE EACH GROUP'S LIVE CONTRIBUTION
        // ========================================================

        const rankedGroups =
            groups.map(
                function (group) {

                    const features =
                        Array.isArray(
                            allGroups[group.name]
                        )
                            ? allGroups[group.name]
                            : [];


                    const groupAbsoluteShap =
                        features.reduce(
                            function (
                                total,
                                feature
                            ) {

                                if (
                                    feature &&
                                    typeof feature.absolute_shap ===
                                    "number" &&
                                    Number.isFinite(
                                        feature.absolute_shap
                                    )
                                ) {

                                    return (
                                        total +
                                        feature.absolute_shap
                                    );

                                }


                                return total;

                            },
                            0
                        );


                    const contributionShare =
                        (
                            groupAbsoluteShap /
                            totalAbsoluteShap
                        ) * 100;


                    const container =
                        document.getElementById(
                            group.containerId
                        );


                    const card =
                        container
                            ? container.closest(
                                ".feature-card"
                            )
                            : null;


                    return {

                        name:
                        group.name,

                        contribution:
                        contributionShare,

                        card:
                        card

                    };

                }
            );


        // ========================================================
        // SORT HIGHEST → LOWEST
        // ========================================================

        rankedGroups.sort(
            function (a, b) {

                return (
                    b.contribution -
                    a.contribution
                );

            }
        );


        // ========================================================
        // MOVE CARDS INTO THEIR NEW DISPLAY ORDER
        // ========================================================
        //
        // appendChild() moves an existing DOM element.
        // It does NOT duplicate the card.
        // ========================================================

        rankedGroups.forEach(
            function (group) {

                if (group.card) {

                    featureStack.appendChild(
                        group.card
                    );

                }

            }
        );


        console.log(
            "NeuroShield AI: Feature cards ranked by SHAP contribution:",
            rankedGroups.map(
                function (group) {

                    return {

                        group:
                        group.name,

                        contribution:
                            group.contribution.toFixed(1) +
                            "%"

                    };

                }
            )
        );

    }


    console.log(
        "NeuroShield AI: Meaningful SHAP features:",
        selectedFeatures
    );


    console.log(
        "NeuroShield AI: SHAP feature groups:",
        allGroups
    );


    console.log(
        "NeuroShield AI: Total absolute SHAP:",
        totalAbsoluteShap
    );

}


// ============================================================
// CREATE EMPTY FEATURE GROUPS
// ============================================================

function createEmptyFeatureGroups() {

    return {

        visual: [],

        audio: [],

        text: [],

        engagement: [],

        emotional: [],

        metadata: []

    };

}


// ============================================================
// FEATURE → MODALITY GROUP
// ============================================================
//
// IMPORTANT:
//
// These groups cover all 42 Random Forest input features.
//
// The grouping is used only for presenting the model's
// SHAP contributions in the parent-facing interface.
//
// The Random Forest itself still receives all 42 features
// independently.
// ============================================================

function getFeatureGroup(
    featureName
) {


    // ========================================================
    // VISUAL FEATURES
    // 7 FEATURES
    // ========================================================

    const visualFeatures =
        new Set([

            "avg_saturation",

            "avg_brightness",

            "motion_mean",

            "motion_std",

            "scene_rate",

            "flicker_rate",

            "motion_spike_rate"

        ]);


    // ========================================================
    // AUDIO FEATURES
    // 13 FEATURES
    // ========================================================

    const audioFeatures =
        new Set([

            "loudness",

            "sound_density",

            "audio_variation",

            "avg_pitch",

            "pitch_variation",

            "spectral_centroid",

            "spectral_bandwidth",

            "spectral_rolloff",

            "spectral_contrast",

            "zero_crossing_rate",

            "harmonic_ratio",

            "percussive_ratio",

            "tempo"

        ]);


    // ========================================================
    // TEXT FEATURES
    // 14 FEATURES
    // ========================================================

    const textFeatures =
        new Set([

            "transcript_length",

            "sentence_complexity",

            "average_sentence_length",

            "vocabulary_diversity",

            "phrase_repetition",

            "educational_word_ratio",

            "reward_keyword_frequency",

            "transcript_word_count",

            "unique_word_ratio",

            "repeated_word_ratio",

            "hallucination_score",

            "english_ratio",

            "nonsense_ratio",

            "transcript_length_normalized"

        ]);


    // ========================================================
    // ENGAGEMENT FEATURES
    // 4 FEATURES
    // ========================================================

    const engagementFeatures =
        new Set([

            "attention_score",

            "loop_detection_score",

            "reward_cue_frequency",

            "attention_reset_rate"

        ]);


    // ========================================================
    // EMOTIONAL FEATURES
    // 3 FEATURES
    // ========================================================

    const emotionalFeatures =
        new Set([

            "emotion_arousal",

            "emotion_valence",

            "emotion_stability"

        ]);


    // ========================================================
    // VIDEO CONTEXT / METADATA
    // 1 FEATURE
    // ========================================================

    const metadataFeatures =
        new Set([

            "video_duration_seconds"

        ]);


    // ========================================================
    // RETURN MATCHING GROUP
    // ========================================================

    if (
        visualFeatures.has(
            featureName
        )
    ) {

        return "visual";

    }


    if (
        audioFeatures.has(
            featureName
        )
    ) {

        return "audio";

    }


    if (
        textFeatures.has(
            featureName
        )
    ) {

        return "text";

    }


    if (
        engagementFeatures.has(
            featureName
        )
    ) {

        return "engagement";

    }


    if (
        emotionalFeatures.has(
            featureName
        )
    ) {

        return "emotional";

    }


    if (
        metadataFeatures.has(
            featureName
        )
    ) {

        return "metadata";

    }


    // ========================================================
    // SAFETY FALLBACK
    // ========================================================
    //
    // With the current NeuroShield model this should never
    // happen because all 42 features are explicitly assigned.
    // ========================================================

    console.warn(
        "NeuroShield AI: Unknown SHAP feature group:",
        featureName
    );


    return "metadata";

}


// ============================================================
// RENDER LIVE CONTRIBUTION GROUP
// ============================================================
//
// This function does TWO separate things:
//
// 1. Calculates the LIVE contribution percentage/bar using
//    ALL features belonging to the category.
//
// 2. Displays individual feature bubbles only for features
//    that passed the 20%-of-strongest display threshold.
//
// Therefore a category can correctly show:
//
//     Audio Features
//     5.2% contribution
//     [small progress bar]
//
//     No feature above display threshold
//
// That does NOT mean audio contributed nothing.
//
// It means the combined audio features contributed 5.2% of
// total absolute SHAP, but no single audio feature was large
// enough to qualify as a major individual contributor.
// ============================================================

function renderLiveContributionGroup(
    containerId,
    barId,
    levelId,
    selectedFeatures,
    allGroupFeatures,
    totalAbsoluteShap,
    featureInterpretations = {}
) {


    const container =
        document.getElementById(
            containerId
        );


    const bar =
        document.getElementById(
            barId
        );


    const level =
        document.getElementById(
            levelId
        );


    // ========================================================
    // SUM ABSOLUTE SHAP FOR THIS GROUP
    // ========================================================

    const groupAbsoluteShap =
        Array.isArray(
            allGroupFeatures
        )
            ? allGroupFeatures.reduce(
                function (
                    total,
                    feature
                ) {

                    if (
                        typeof feature.absolute_shap ===
                        "number" &&
                        Number.isFinite(
                            feature.absolute_shap
                        )
                    ) {

                        return (
                            total +
                            feature.absolute_shap
                        );

                    }


                    return total;

                },
                0
            )
            : 0;


    // ========================================================
    // CALCULATE LIVE CONTRIBUTION SHARE
    // ========================================================

    const contributionShare =
        totalAbsoluteShap > 0
            ? (
            groupAbsoluteShap /
            totalAbsoluteShap
        ) * 100
            : 0;


    const safeShare =
        Math.max(
            0,
            Math.min(
                100,
                contributionShare
            )
        );


    // ========================================================
    // UPDATE LIVE CONTRIBUTION LABEL
    // ========================================================

    if (level) {

        level.textContent =
            `${safeShare.toFixed(
                1
            )}% contribution`;


        level.title =
            "Share of total absolute SHAP contribution across all 42 model features.";


        level.setAttribute(
            "aria-label",
            `${safeShare.toFixed(
                1
            )}% contribution to the current model prediction`
        );

    }


    // ========================================================
    // UPDATE LIVE PROGRESS BAR
    // ========================================================

    if (bar) {

        bar.style.width =
            `${safeShare}%`;


        bar.setAttribute(
            "aria-valuemin",
            "0"
        );


        bar.setAttribute(
            "aria-valuemax",
            "100"
        );


        bar.setAttribute(
            "aria-valuenow",
            safeShare.toFixed(
                1
            )
        );


        bar.title =
            `${safeShare.toFixed(
                1
            )}% of total absolute SHAP contribution`;

    }


    // ========================================================
    // NO CONTAINER
    // ========================================================

    if (!container) {

        return;

    }


    // ========================================================
    // NO INDIVIDUAL FEATURE ABOVE DISPLAY THRESHOLD
    // ========================================================
    //
    // The progress bar and percentage above remain live.
    //
    // We therefore no longer say:
    //
    // "No major contributors"
    //
    // because the category may still have a genuine combined
    // contribution to the model prediction.
    // ========================================================

    if (
        !Array.isArray(
            selectedFeatures
        ) ||
        selectedFeatures.length === 0
    ) {

        container.innerHTML = `

            <span class="feature-not-significant">
                No feature above display threshold
            </span>

        `;


        return;

    }


    // ========================================================
    // DISPLAY SELECTED INDIVIDUAL FEATURES
    // ========================================================


    // ========================================================
    // SORT FEATURES BY REFERENCE LEVEL
    // Higher → Typical → Lower → No reference
    // ========================================================

    const referenceOrder = {
        "Higher than typical": 0,
        "Typical range": 1,
        "Lower than typical": 2
    };


    const sortedFeatures =
        [...selectedFeatures].sort(
            function (a, b) {

                const aInterpretation =
                    featureInterpretations &&
                    featureInterpretations[a.feature];

                const bInterpretation =
                    featureInterpretations &&
                    featureInterpretations[b.feature];


                const aLabel =
                    aInterpretation &&
                    aInterpretation.reference_label
                        ? aInterpretation.reference_label
                        : "";

                const bLabel =
                    bInterpretation &&
                    bInterpretation.reference_label
                        ? bInterpretation.reference_label
                        : "";


                const aOrder =
                    referenceOrder[aLabel] !== undefined
                        ? referenceOrder[aLabel]
                        : 3;

                const bOrder =
                    referenceOrder[bLabel] !== undefined
                        ? referenceOrder[bLabel]
                        : 3;


                return aOrder - bOrder;
            }
        );


    // ========================================================
    // RENDER FEATURES
    // ========================================================

    container.innerHTML =
        sortedFeatures
            .map(
                function (feature) {

                    const interpretation =
                        featureInterpretations &&
                        featureInterpretations[
                            feature.feature
                            ]
                            ? featureInterpretations[
                                feature.feature
                                ]
                            : null;


                    const featureName =
                        interpretation &&
                        interpretation.display_name
                            ? interpretation.display_name
                            : (
                                feature.friendly_name ||
                                formatHybridFeatureName(
                                    feature.feature
                                )
                            );


                    const rawValue =
                        interpretation &&
                        typeof interpretation.value ===
                        "number"
                            ? interpretation.value
                            : feature.feature_value;


                    const value =
                        formatFeatureValue(
                            rawValue
                        );


                    const referenceLabel =
                        interpretation &&
                        typeof interpretation.reference_label ===
                        "string"
                            ? interpretation.reference_label
                            : "";


                    let referenceClass =
                        "reference-unknown";


                    if (
                        referenceLabel ===
                        "Higher than typical"
                    ) {

                        referenceClass =
                            "reference-higher";

                    } else if (
                        referenceLabel ===
                        "Typical range"
                    ) {

                        referenceClass =
                            "reference-typical";

                    } else if (
                        referenceLabel ===
                        "Lower than typical"
                    ) {

                        referenceClass =
                            "reference-lower";

                    }


                    return `
        
                            <div class="detected-feature detailed ${referenceClass}">
        
                                <div class="detected-feature-name">
                                    ${escapeHTML(
                        featureName
                    )}
                                </div>
        
                                <div class="detected-feature-value">
                                    ${escapeHTML(
                        value
                    )}
                                </div>
        
                            </div>
        
                        `;

                }
            )
            .join("");


// ========================================================
// COLLAPSIBLE DETECTED FEATURES
// ========================================================

    container.classList.add(
        "detected-features-collapsible"
    );

    container.classList.remove(
        "detected-features-open"
    );


// Avoid creating the button more than once

    let toggle =
        container.previousElementSibling;

    if (
        !toggle ||
        !toggle.classList.contains(
            "detected-features-toggle"
        )
    ) {

        toggle =
            document.createElement(
                "button"
            );

        toggle.type = "button";

        toggle.className =
            "detected-features-toggle";

        container.parentNode.insertBefore(
            toggle,
            container
        );

    }


    const featureCount =
        selectedFeatures.length;


    function updateToggleText(
        isOpen
    ) {

        toggle.innerHTML = `
    
            <span>
                ${featureCount}
                extracted
                ${featureCount === 1
            ? "feature"
            : "features"}
            </span>
    
            <span class="detected-features-toggle-arrow">
                ${isOpen ? "⌃" : "⌄"}
            </span>
    
        `;

    }


    updateToggleText(false);


    toggle.onclick =
        function () {

            const isOpen =
                container.classList.toggle(
                    "detected-features-open"
                );

            toggle.classList.toggle(
                "open",
                isOpen
            );

            toggle.setAttribute(
                "aria-expanded",
                isOpen
                    ? "true"
                    : "false"
            );

            updateToggleText(
                isOpen
            );

        };

    // ========================================================
    // MAKE THE WHOLE FEATURE CARD CLICKABLE
    // ========================================================

    const featureCard =
        container.closest(
            ".feature-card"
        );


    if (featureCard) {

        featureCard.classList.add(
            "feature-card-clickable"
        );


        featureCard.onclick =
            function (event) {

                // The existing View / Hide button already
                // handles its own click.
                if (
                    event.target.closest(
                        ".detected-features-toggle"
                    )
                ) {
                    return;
                }


                // Do not close the card when the user clicks
                // one of the individual feature tiles.
                if (
                    event.target.closest(
                        ".detected-feature"
                    )
                ) {
                    return;
                }


                toggle.click();

            };

    }


    toggle.setAttribute(
        "aria-expanded",
        "false"
    );
}

// ============================================================
// FORMAT FEATURE VALUE
// ============================================================

function formatFeatureValue(
    value
) {

    if (
        typeof value !==
        "number" ||
        !Number.isFinite(
            value
        )
    ) {

        return "—";

    }


    const absoluteValue =
        Math.abs(
            value
        );


    if (
        absoluteValue >=
        100
    ) {

        return value.toFixed(
            1
        );

    }


    if (
        absoluteValue >=
        10
    ) {

        return value.toFixed(
            2
        );

    }


    if (
        absoluteValue >=
        1
    ) {

        return value.toFixed(
            2
        );

    }


    return value.toFixed(
        3
    );

}

// ============================================================
// INSIGHTS
// ============================================================

function renderInsights(
    insights
) {

    const container =
        document.getElementById(
            "insightContainer"
        );


    if (!container) {

        return;

    }


    container.innerHTML =
        "";


    insights.forEach(
        function (insight) {

            const box =
                document.createElement(
                    "div"
                );


            box.className =
                "empty-insight";


            box.innerHTML = `

                <div class="empty-insight-icon">
                    <img
                        src="${chrome.runtime.getURL('icons/explainability.png')}"
                        alt=""
                    >
                </div>

                <div>

                    <strong>
                        Explainability Insight
                    </strong>

                    <p>
                        ${escapeHTML(
                insight
            )}
                    </p>

                </div>

            `;


            container.appendChild(
                box
            );

        }
    );

}


// ============================================================
// HIGH RISK ALERT
// ============================================================

function triggerHighRiskAlert(
    pulseAiCard = true,
    pulseHybridCard = false
) {

    if (!notificationsEnabled) {

        return;

    }


    if (
        !currentVideoId ||
        lastAlertedVideoId ===
        currentVideoId
    ) {

        return;

    }


    lastAlertedVideoId =
        currentVideoId;


    playAlertSound();


    const mainCard =
        document.getElementById(
            "mainScoreCard"
        );


    const hybridCard =
        document.getElementById(
            "hybridAssessmentCard"
        );


    if (
        pulseAiCard &&
        mainCard
    ) {

        mainCard.classList.add(
            "alert-pulse"
        );


        setTimeout(
            function () {

                mainCard.classList.remove(
                    "alert-pulse"
                );

            },
            2500
        );

    }


    if (
        pulseHybridCard &&
        hybridCard
    ) {

        hybridCard.classList.add(
            "alert-pulse"
        );


        setTimeout(
            function () {

                hybridCard.classList.remove(
                    "alert-pulse"
                );

            },
            2500
        );

    }

}


// ============================================================
// ALERT SOUND
// ============================================================

function playAlertSound() {

    try {

        const AudioContext =
            window.AudioContext ||
            window.webkitAudioContext;


        if (!AudioContext) {

            return;

        }


        const audioContext =
            new AudioContext();


        const oscillator =
            audioContext.createOscillator();


        const gain =
            audioContext.createGain();


        oscillator.type =
            "sine";


        oscillator.frequency.setValueAtTime(
            660,
            audioContext.currentTime
        );


        oscillator.frequency.setValueAtTime(
            880,
            audioContext.currentTime +
            0.15
        );


        gain.gain.setValueAtTime(
            0.0001,
            audioContext.currentTime
        );


        gain.gain.exponentialRampToValueAtTime(
            0.18,
            audioContext.currentTime +
            0.03
        );


        gain.gain.exponentialRampToValueAtTime(
            0.0001,
            audioContext.currentTime +
            0.35
        );


        oscillator.connect(
            gain
        );


        gain.connect(
            audioContext.destination
        );


        oscillator.start();


        oscillator.stop(
            audioContext.currentTime +
            0.4
        );

    } catch (error) {

        console.log(
            "NeuroShield AI: Alert sound unavailable."
        );

    }

}


// ============================================================
// ESCAPE HTML
// ============================================================

function escapeHTML(
    value
) {

    const div =
        document.createElement(
            "div"
        );


    div.textContent =
        String(
            value
        );


    return div.innerHTML;

}


// ============================================================
// YOUTUBE SPA NAVIGATION
// ============================================================

let lastUrl =
    window.location.href;


setInterval(
    function () {

        const currentUrl =
            window.location.href;


        if (
            currentUrl !==
            lastUrl
        ) {

            lastUrl =
                currentUrl;


            checkCurrentPage();

        }

    },
    1000
);


// ============================================================
// GLOBAL DRAG EVENTS
// ============================================================

document.addEventListener(
    "mousemove",
    handleDrag
);


document.addEventListener(
    "mouseup",
    stopDrag
);

// ============================================================
// EXPLAINABILITY VISIBILITY
// ============================================================

function updateExplainabilityVisibility(enabled) {

    const explainabilityToggle =
        document.getElementById(
            "explainabilitySectionToggle"
        );

    if (!explainabilityToggle) {
        return;
    }

    // Hide the entire Explainability Insights section,
    // including its heading and content.
    const explainabilitySection =
        explainabilityToggle.closest("section");

    if (explainabilitySection) {

        explainabilitySection.style.display =
            enabled ? "" : "none";

    }

}

// ============================================================
// MULTIMEDIA FEATURES VISIBILITY
// ============================================================

function updateMultimediaVisibility(enabled) {

    const multimediaToggle =
        document.getElementById(
            "multimediaSectionToggle"
        );

    if (!multimediaToggle) {
        return;
    }

    const multimediaSection =
        multimediaToggle.closest("section");

    if (multimediaSection) {

        multimediaSection.style.display =
            enabled ? "" : "none";

    }

}

// ============================================================
// MULTIMEDIA FEATURES VISIBILITY
// ============================================================

function updateMultimediaVisibility(enabled) {

    const multimediaToggle =
        document.getElementById(
            "multimediaSectionToggle"
        );

    if (!multimediaToggle) {
        return;
    }

    const multimediaContent =
        document.getElementById(
            "multimediaSectionContent"
        );

    // Find the parent section containing both
    // the multimedia heading and its content.
    const multimediaSection =
        multimediaContent?.parentElement;

    if (multimediaSection) {

        multimediaSection.style.display =
            enabled ? "" : "none";

    }

}

// ============================================================
// STORAGE CHANGES
// ============================================================

chrome.storage.onChanged.addListener(
    function (
        changes,
        areaName
    ) {

        if (
            areaName !==
            "local"
        ) {

            return;

        }


        // ====================================================
        // PROTECTION ENABLED / DISABLED
        // ====================================================

        if (
            changes.protectionEnabled
        ) {

            protectionEnabled =
                changes
                    .protectionEnabled
                    .newValue ===
                true;


            checkCurrentPage();

        }


        // ====================================================
        // NOTIFICATION SETTING
        // ====================================================

        if (
            changes
                .neuroshieldNotificationsEnabled
        ) {

            notificationsEnabled =
                changes
                    .neuroshieldNotificationsEnabled
                    .newValue !==
                false;


            const button =
                document.getElementById(
                    "neuroshield-notification"
                );


            if (button) {

                updateNotificationButton(
                    button
                );

            }

        }

        // ====================================================
        // EXPLAINABILITY SETTING
        // ====================================================

        if (changes.explainabilityEnabled) {

            updateExplainabilityVisibility(
                changes.explainabilityEnabled.newValue !== false
            );

        }

        // ====================================================
        // MULTIMEDIA FEATURES SETTING
        // ====================================================

        if (changes.neuroshieldMultimediaEnabled) {

            updateMultimediaVisibility(
                changes.neuroshieldMultimediaEnabled.newValue !== false
            );

        }

        // ====================================================
        // MULTIMEDIA FEATURES SETTING
        // ====================================================

        if (changes.neuroshieldMultimediaEnabled) {

            updateMultimediaVisibility(
                changes.neuroshieldMultimediaEnabled.newValue !== false
            );

        }

    }
);


// ============================================================
// START
// ============================================================

initialise();