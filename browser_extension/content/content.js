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

function showAnalysisTemplate() {

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

    overlay.innerHTML = `

        <div class="neuroshield-window">

            <!-- ================================================= -->
            <!-- HEADER -->
            <!-- ================================================= -->

            <div
                class="neuroshield-header"
                id="neuroshield-drag-handle"
            >

                <div class="neuroshield-brand">

                    <div class="neuroshield-logo-container">

                        <img
                            src="${logoURL}"
                            class="neuroshield-logo"
                            alt="NeuroShield AI Logo"
                            onerror="this.style.display='none'; console.error('NeuroShield AI: Logo failed to load:', this.src);"
                        >

                    </div>

                    <div class="neuroshield-brand-text">

                        <div class="neuroshield-title">
                            NeuroShield AI
                        </div>

                        <div class="neuroshield-subtitle">
                            Explainable Developmental Analysis
                        </div>

                    </div>

                </div>


                <div class="neuroshield-actions">

                    <!-- NOTIFICATION -->

                    <button
                        id="neuroshield-notification"
                        class="neuroshield-action"
                        title="Mute high-risk alerts"
                        aria-label="Mute high-risk alerts"
                        type="button"
                    >
                        🔔
                    </button>


                    <!-- SETTINGS -->

                    <button
                        id="neuroshield-settings"
                        class="neuroshield-action"
                        title="Open settings"
                        aria-label="Open settings"
                        type="button"
                    >
                        ⚙
                    </button>


                    <!-- MINIMIZE -->

                    <button
                        id="neuroshield-minimize"
                        class="neuroshield-action"
                        title="Minimize"
                        aria-label="Minimize"
                        type="button"
                    >
                        −
                    </button>


                    <!-- CLOSE -->

                    <button
                        id="neuroshield-close"
                        class="neuroshield-action close"
                        title="Close"
                        aria-label="Close"
                        type="button"
                    >
                        ×
                    </button>

                </div>

            </div>


            <!-- ================================================= -->
            <!-- CONTENT -->
            <!-- ================================================= -->

            <div
                class="neuroshield-content"
                id="neuroshield-content"
            >


                <!-- ================================================= -->
                <!-- MONITORING STATUS -->
                <!-- ================================================= -->

                <div
                    class="neuroshield-status-card waiting"
                    id="monitoringStatusCard"
                >

                    <div class="status-left">

                        <span
                            class="status-dot waiting"
                            id="monitoringStatusDot"
                        ></span>

                        <div>

                            <div class="status-title">
                                AI Monitoring
                            </div>

                            <div
                                class="status-text"
                                id="analysisStatusText"
                            >
                                Waiting for backend analysis
                            </div>

                        </div>

                    </div>

                    <div
                        class="status-badge waiting"
                        id="monitoringStatusBadge"
                    >
                        Waiting
                    </div>

                </div>


                <!-- ================================================= -->
                <!-- HYBRID DEVELOPMENTAL ASSESSMENT -->
                <!-- ================================================= -->

                <section
                    class="neuroshield-main-card hybrid-assessment-card"
                    id="hybridAssessmentCard"
                >

                    <div
                        class="live-badge"
                        id="hybridAssessmentBadge"
                    >
                        WAITING
                    </div>

                    <div class="main-score-title">
                        Hybrid Developmental Assessment
                    </div>

                    <div
                        class="main-score-empty"
                        id="hybridAssessmentScore"
                    >
                        —
                    </div>

                    <div
                        class="main-score-label"
                        id="hybridAssessmentCategory"
                    >
                        Awaiting analysis
                    </div>

                    <div
                        class="main-score-description"
                        id="hybridAssessmentDescription"
                    >
                        Combines AI risk evidence with the
                        developmental impact assessment.
                    </div>

                </section>


                <!-- ================================================= -->
                <!-- AI RISK ASSESSMENT -->
                <!-- ================================================= -->

                <section
                    class="neuroshield-main-card ai-risk-card"
                    id="mainScoreCard"
                >

                    <div
                        class="live-badge"
                        id="analysisLiveBadge"
                    >
                        WAITING
                    </div>

                    <div class="main-score-title">
                        AI Risk Assessment
                    </div>

                    <div
                        class="main-score-empty"
                        id="overallScore"
                    >
                        —
                    </div>

                    <div
                        class="main-score-label"
                        id="overallScoreLabel"
                    >
                        Awaiting analysis
                    </div>

                    <div
                        class="main-score-description"
                        id="mainScoreDescription"
                    >
                        The AI risk classification and model
                        confidence will appear after analysis.
                    </div>

                </section>


                <!-- ================================================= -->
                <!-- DEVELOPMENTAL IMPACT -->
                <!-- ================================================= -->

                <section class="neuroshield-card">

                    <div class="card-title">
                        Developmental Impact Scores
                    </div>


                    <!-- COGNITIVE -->

                    <div class="score-row">

                        <div class="score-icon cognitive-icon">
                            <img
                                src="${chrome.runtime.getURL('icons/cognitive.png')}"
                                alt=""
                            >
                        </div>

                        <div class="score-content">

                            <div class="score-header">

                                <span>
                                    Cognitive Impact
                                </span>

                                <strong id="cognitiveScore">
                                    —
                                </strong>

                            </div>

                            <div class="progress-track">

                                <div
                                    class="progress-fill cognitive-fill"
                                    id="cognitiveBar"
                                ></div>

                            </div>

                            <div class="score-description">
                                Learning and language-related stimulation
                            </div>

                        </div>

                    </div>


                    <!-- BEHAVIOURAL -->

                    <div class="score-row">

                        <div class="score-icon behavioural-icon">
                            <img
                                src="${chrome.runtime.getURL('icons/behavioural.png')}"
                                alt=""
                            >
                        </div>

                        <div class="score-content">

                            <div class="score-header">

                                <span>
                                    Behavioural Risk
                                </span>

                                <strong id="behaviouralScore">
                                    —
                                </strong>

                            </div>

                            <div class="progress-track">

                                <div
                                    class="progress-fill behavioural-fill"
                                    id="behaviouralBar"
                                ></div>

                            </div>

                            <div class="score-description">
                                Attention and repetitive stimulation risk
                            </div>

                        </div>

                    </div>


                    <!-- EMOTIONAL -->

                    <div class="score-row">

                    <div class="score-icon emotional-icon">
                        <img
                            src="${chrome.runtime.getURL('icons/emotional.png')}"
                            alt=""
                        >
                    </div>

                        <div class="score-content">

                            <div class="score-header">

                                <span>
                                    Emotional Stimulation
                                </span>

                                <strong id="emotionalScore">
                                    —
                                </strong>

                            </div>

                            <div class="progress-track">

                                <div
                                    class="progress-fill emotional-fill"
                                    id="emotionalBar"
                                ></div>

                            </div>

                            <div class="score-description">
                                Emotional intensity and tone
                            </div>

                        </div>

                    </div>
                    <!-- OVERALL DEVELOPMENTAL IMPACT -->

                    <div class="score-row overall-developmental-row">
                    
                    <div class="score-icon overall-icon">
                        <img
                            src="${chrome.runtime.getURL('icons/overall.png')}"
                            alt=""
                        >
                    </div>
                    
                        <div class="score-content">
                    
                            <div class="score-header">
                    
                                <span>
                                    Overall Developmental Impact
                                </span>
                    
                                <strong id="overallDevelopmentalScore">
                                    —
                                </strong>
                    
                            </div>
                    
                            <div class="progress-track">
                    
                                <div
                                    class="progress-fill overall-developmental-fill"
                                    id="overallDevelopmentalBar"
                                ></div>
                    
                            </div>
                    
                            <div class="score-description">
                                Combined cognitive, behavioural and emotional impact
                            </div>
                    
                        </div>
                    
                    </div>

                </section>


                <!-- ================================================= -->
                <!-- EXPLAINABILITY -->
                <!-- ================================================= -->

                <section class="neuroshield-card">

                    <div class="card-title">
                        Explainability Insights
                    </div>

                    <div
                        class="empty-insight"
                        id="insightContainer"
                    >

                        <div class="empty-insight-icon">
                            <img
                                src="${chrome.runtime.getURL('icons/explainability.png')}"
                                alt=""
                            >
                        </div>

                        <div>

                            <strong>
                                No analysis available yet
                            </strong>

                            <p>
                                Explainable AI insights will appear
                                here after the backend completes
                                analysis of this video.
                            </p>

                        </div>

                    </div>

                </section>


                <!-- ================================================= -->
                <!-- MULTIMEDIA FEATURES -->
                <!-- ================================================= -->

                <section class="neuroshield-card">

                    <div class="card-title">
                        Detected Multimedia Features
                    </div>

                    <div class="feature-stack">


                        <!-- ================================================= -->
                        <!-- VISUAL -->
                        <!-- ================================================= -->

                        <div class="feature-card">

                            <div class="feature-top">

                                <div class="feature-heading">

                                    <div class="feature-icon visual">
                                        <img
                                            src="${chrome.runtime.getURL('icons/visual.png')}"
                                            alt=""
                                        >
                                    </div>

                                    <div>

                                        <div class="feature-name">
                                            Visual Features
                                        </div>

                                        <div class="feature-subtitle">
                                            Motion and scene-based stimulation
                                        </div>

                                    </div>

                                </div>

                                <span
                                    class="feature-level"
                                    id="visualLevel"
                                >
                                    —
                                </span>

                            </div>

                            <div class="mini-progress">

                                <div
                                    class="mini-fill"
                                    id="visualBar"
                                ></div>

                            </div>

                            <div
                                class="feature-bubbles"
                                id="visualFeatures"
                            >

                                <span>Motion Intensity</span>
                                <span>Scene Changes</span>
                                <span>Brightness</span>
                                <span>Saturation</span>
                                <span>Flicker Rate</span>

                            </div>

                        </div>


                        <!-- ================================================= -->
                        <!-- AUDIO -->
                        <!-- ================================================= -->

                        <div class="feature-card">

                            <div class="feature-top">

                                <div class="feature-heading">

                                    <div class="feature-icon audio">
                                        <img
                                            src="${chrome.runtime.getURL('icons/audio.png')}"
                                            alt=""
                                        >
                                    </div>

                                    <div>

                                        <div class="feature-name">
                                            Audio Features
                                        </div>

                                        <div class="feature-subtitle">
                                            Sound and auditory stimulation
                                        </div>

                                    </div>

                                </div>

                                <span
                                    class="feature-level"
                                    id="audioLevel"
                                >
                                    —
                                </span>

                            </div>

                            <div class="mini-progress">

                                <div
                                    class="mini-fill"
                                    id="audioBar"
                                ></div>

                            </div>

                            <div
                                class="feature-bubbles"
                                id="audioFeatures"
                            >

                                <span>Loudness</span>
                                <span>Pitch Variation</span>
                                <span>Tempo</span>
                                <span>Spectral Density</span>

                            </div>

                        </div>


                        <!-- ================================================= -->
                        <!-- TEXT -->
                        <!-- ================================================= -->

                        <div class="feature-card">

                            <div class="feature-top">

                                <div class="feature-heading">

                                    <div class="feature-icon text">
                                        <img
                                            src="${chrome.runtime.getURL('icons/textual.png')}"
                                            alt=""
                                        >
                                    </div>

                                    <div>

                                        <div class="feature-name">
                                            Textual Features
                                        </div>

                                        <div class="feature-subtitle">
                                            Language and textual characteristics
                                        </div>

                                    </div>

                                </div>

                                <span
                                    class="feature-level"
                                    id="textLevel"
                                >
                                    —
                                </span>

                            </div>

                            <div class="mini-progress">

                                <div
                                    class="mini-fill"
                                    id="textBar"
                                ></div>

                            </div>

                            <div
                                class="feature-bubbles"
                                id="textFeatures"
                            >

                                <span>Phrase Repetition</span>
                                <span>Sentence Complexity</span>
                                <span>Vocabulary Diversity</span>

                            </div>

                        </div>


                        <!-- ================================================= -->
                        <!-- ENGAGEMENT -->
                        <!-- ================================================= -->

                        <div class="feature-card">

                            <div class="feature-top">

                                <div class="feature-heading">

                                    <div class="feature-icon engagement">
                                        <img
                                            src="${chrome.runtime.getURL('icons/engagement.png')}"
                                            alt=""
                                        >
                                    </div>

                                    <div>

                                        <div class="feature-name">
                                            Engagement Patterns
                                        </div>

                                        <div class="feature-subtitle">
                                            Attention and reward mechanisms
                                        </div>

                                    </div>

                                </div>

                                <span
                                    class="feature-level"
                                    id="engagementLevel"
                                >
                                    —
                                </span>

                            </div>

                            <div class="mini-progress">

                                <div
                                    class="mini-fill"
                                    id="engagementBar"
                                ></div>

                            </div>

                            <div
                                class="feature-bubbles"
                                id="engagementFeatures"
                            >

                                <span>Reward Cues</span>
                                <span>Attention Resets</span>
                                <span>Loop Detection</span>
                                <span>Motion Spikes</span>

                            </div>

                        </div>


                        <!-- ================================================= -->
                        <!-- EMOTIONAL FEATURES -->
                        <!-- NEW -->
                        <!-- ================================================= -->

                        <div class="feature-card">

                            <div class="feature-top">

                                <div class="feature-heading">

                                    <div class="feature-icon emotional-feature">
                                        <img
                                            src="${chrome.runtime.getURL('icons/emotion-feature.png')}"
                                            alt=""
                                        >
                                    </div>

                                    <div>

                                        <div class="feature-name">
                                            Emotional Features
                                        </div>

                                        <div class="feature-subtitle">
                                            Emotional tone, arousal and stability
                                        </div>

                                    </div>

                                </div>

                                <span
                                    class="feature-level"
                                    id="emotionalFeatureLevel"
                                >
                                    —
                                </span>

                            </div>

                            <div class="mini-progress">

                                <div
                                    class="mini-fill emotional-feature-fill"
                                    id="emotionalFeatureBar"
                                ></div>

                            </div>

                            <div
                                class="feature-bubbles"
                                id="emotionalFeatures"
                            >

                                <span>Emotional Arousal</span>
                                <span>Emotional Tone</span>
                                <span>Emotional Stability</span>

                            </div>

                        </div>


                        <!-- ================================================= -->
                        <!-- VIDEO CONTEXT -->
                        <!-- NEW -->
                        <!-- ================================================= -->

                        <div class="feature-card">

                            <div class="feature-top">

                                <div class="feature-heading">

                                    <div class="feature-icon metadata">
                                        <img
                                            src="${chrome.runtime.getURL('icons/metadata.png')}"
                                            alt=""
                                        >
                                    </div>

                                    <div>

                                        <div class="feature-name">
                                            Video Context
                                        </div>

                                        <div class="feature-subtitle">
                                            Video and analysis context features
                                        </div>

                                    </div>

                                </div>

                                <span
                                    class="feature-level"
                                    id="metadataLevel"
                                >
                                    —
                                </span>

                            </div>

                            <div class="mini-progress">

                                <div
                                    class="mini-fill metadata-fill"
                                    id="metadataBar"
                                ></div>

                            </div>

                            <div
                                class="feature-bubbles"
                                id="metadataFeatures"
                            >

                                <span>Video Duration</span>

                            </div>

                        </div>


                    </div>

                </section>


                <!-- ================================================= -->
                <!-- RECOMMENDATION -->
                <!-- ================================================= -->

                <section class="neuroshield-card">

                    <div class="card-title">
                        Recommendation
                    </div>

                    <div
                        class="empty-recommendation"
                        id="recommendation"
                    >

                        <span>
                            💡
                        </span>

                        <p>
                            No recommendation is available.
                            A recommendation will appear only
                            after verified backend analysis.
                        </p>

                    </div>

                </section>


                <!-- ================================================= -->
                <!-- FOOTER -->
                <!-- ================================================= -->

                <div class="neuroshield-footer">

                    Explainable Multimodal AI
                    <span>•</span>
                    NeuroShield AI

                </div>

            </div>

        </div>

    `;


    document.body.appendChild(
        overlay
    );


    initialiseOverlayControls();


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
    // SETTINGS
    // ========================================================

    if (settingsButton) {

        settingsButton.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                event.stopPropagation();


                chrome.runtime.sendMessage(
                    {
                        action: "OPEN_SETTINGS"
                    },
                    function () {

                        if (
                            chrome.runtime.lastError
                        ) {

                            console.log(
                                "NeuroShield AI: Settings request sent."
                            );

                        }

                    }
                );

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
// REQUEST VIDEO ANALYSIS
// ============================================================

async function requestVideoAnalysis() {

    if (!currentVideoId) {

        console.warn(
            "NeuroShield AI: No YouTube video ID available."
        );

        return;
    }


    const requestedVideoId =
        currentVideoId;


    const youtubeUrl =
        `https://www.youtube.com/watch?v=${requestedVideoId}`;


    console.log(
        "NeuroShield AI: Requesting analysis:",
        youtubeUrl
    );


    try {

        const response =
            await chrome.runtime.sendMessage({

                action:
                    "ANALYZE_VIDEO",

                youtubeUrl:
                    youtubeUrl

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

            return;
        }


        activeAnalysisJobId =
            response.job_id;


        console.log(
            "NeuroShield AI: Analysis started successfully."
        );


        console.log(
            "NeuroShield AI: Job ID:",
            activeAnalysisJobId
        );


        pollAnalysisFromContentScript(
            activeAnalysisJobId,
            requestedVideoId
        );

    } catch (error) {

        console.error(
            "NeuroShield AI: Could not request video analysis:",
            error
        );

    }

}
// ============================================================
// POLL ANALYSIS FROM CONTENT SCRIPT
// ============================================================

async function pollAnalysisFromContentScript(
    jobId,
    requestedVideoId
) {

    if (!jobId) {

        console.error(
            "NeuroShield AI: Cannot poll without a job ID."
        );

        return;
    }


    analysisPolling =
        true;


    for (
        let attempt = 1;
        attempt <= MAX_ANALYSIS_POLL_ATTEMPTS;
        attempt++
    ) {

        // --------------------------------------------------------
        // STOP IF USER NAVIGATED TO ANOTHER VIDEO
        // --------------------------------------------------------

        if (
            currentVideoId !==
            requestedVideoId
        ) {

            console.log(
                "NeuroShield AI: Video changed. Stopping old analysis polling."
            );

            analysisPolling =
                false;

            return;
        }


        // --------------------------------------------------------
        // WAIT 5 SECONDS
        // --------------------------------------------------------

        await sleepInContentScript(
            ANALYSIS_POLL_INTERVAL_MS
        );


        try {

            console.log(
                `NeuroShield AI: Checking analysis status (${attempt}/${MAX_ANALYSIS_POLL_ATTEMPTS})...`
            );


            const response =
                await chrome.runtime.sendMessage({

                    action:
                        "CHECK_ANALYSIS_STATUS",

                    jobId:
                        jobId

                });


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


            const data =
                response.data;


            console.log(
                "NeuroShield AI: Analysis status:",
                data.status
            );


            // ----------------------------------------------------
            // ANALYSIS COMPLETE
            // ----------------------------------------------------

            if (
                data.status ===
                "complete"
            ) {

                if (!data.result) {

                    console.error(
                        "NeuroShield AI: Analysis completed but no result was returned."
                    );

                    analysisPolling =
                        false;

                    return;
                }


                // Make absolutely sure the user is still
                // viewing the video that requested this job.

                if (
                    currentVideoId !==
                    requestedVideoId
                ) {

                    console.log(
                        "NeuroShield AI: Ignoring result because the video changed."
                    );

                    analysisPolling =
                        false;

                    return;
                }


                console.log(
                    "NeuroShield AI: Backend analysis received."
                );


                console.log(
                    "NeuroShield AI: REAL ANALYSIS RESULT:",
                    data.result
                );


                updateRealRiskResult(
                    data.result
                );


                activeAnalysisJobId =
                    null;


                analysisPolling =
                    false;


                console.log(
                    "NeuroShield AI: UI updated successfully."
                );


                return;
            }


            // ----------------------------------------------------
            // ANALYSIS FAILED
            // ----------------------------------------------------

            if (
                data.status ===
                "failed"
            ) {

                console.error(
                    "NeuroShield AI: Analysis failed:",
                    data.error ||
                    "Unknown backend error."
                );


                activeAnalysisJobId =
                    null;


                analysisPolling =
                    false;


                return;
            }


            // queued / processing
            console.log(
                "NeuroShield AI: Analysis still processing..."
            );


        } catch (error) {

            console.warn(
                "NeuroShield AI: Analysis status request failed:",
                error
            );

            // Do NOT stop immediately.
            // A temporary service-worker restart or request
            // failure should not destroy the analysis session.

        }

    }


    activeAnalysisJobId =
        null;


    analysisPolling =
        false;


    console.error(
        "NeuroShield AI: Analysis polling timed out."
    );

}
// ============================================================
// CONTENT SCRIPT SLEEP
// ============================================================

function sleepInContentScript(
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

    updateHybridAssessment(
        data.hybrid_assessment
    );

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

        updateScoreBar(
            developmentalScores.overall,
            "overallDevelopmentalScore",
            "overallDevelopmentalBar"
        );

        console.log(
            "NeuroShield AI: Developmental scores updated:",
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
            explainability.feature_contributions
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
// ============================================================
// HYBRID DEVELOPMENTAL ASSESSMENT
// ============================================================

function updateHybridAssessment(
    hybridAssessment
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

            scoreElement.textContent =
                "—";

        }


        if (categoryElement) {

            categoryElement.textContent =
                "Assessment unavailable";

        }


        if (badge) {

            badge.textContent =
                "UNAVAILABLE";

        }


        return;

    }


    // ========================================================
    // READ LIVE BACKEND RESULT
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


    // ========================================================
    // DISPLAY SCORE
    // ========================================================

    if (scoreElement) {

        scoreElement.textContent =
            `${safeScore.toFixed(2)} / 100`;

    }


    // ========================================================
    // DISPLAY CATEGORY
    // ========================================================

    if (categoryElement) {

    if (category === "High") {

        categoryElement.textContent =
            "High Developmental Impact";

    } else if (category === "Medium") {

        categoryElement.textContent =
            "Moderate Developmental Impact";

    } else if (category === "Low") {

        categoryElement.textContent =
            "Low Developmental Impact";

    } else {

        categoryElement.textContent =
            "Developmental Impact Unavailable";

    }

}


    // ========================================================
    // RESULT BADGE
    // ========================================================

    if (badge) {

        badge.textContent =
            "HYBRID RESULT";

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

            card.classList.add(
                "high"
            );

        } else if (category === "Medium") {

            card.classList.add(
                "moderate"
            );

        } else if (category === "Low") {

            card.classList.add(
                "low"
            );

        }

    }


    // ========================================================
    // DESCRIPTION
    // ========================================================

    if (description) {

        description.textContent =
            "Combined assessment using Random Forest " +
            "risk evidence and developmental impact scoring.";

    }


    console.log(
        "NeuroShield AI: Hybrid assessment updated:",
        `${safeScore.toFixed(2)} / 100`,
        category
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

function renderExplainability(
    explainability
) {

    const container =
        document.getElementById(
            "insightContainer"
        );


    if (
        !container ||
        !explainability
    ) {

        return;

    }


    const predictedLabel =
        explainability.predicted_label ||
        "the predicted class";


    const parentExplanation =
        explainability.parent_explanation ||
        "No explanation is available.";


    const supportingFactors =
        Array.isArray(
            explainability.supporting_factors
        )
            ? explainability.supporting_factors
            : [];


    const opposingFactors =
        Array.isArray(
            explainability.opposing_factors
        )
            ? explainability.opposing_factors
            : [];


    // ========================================================
    // BUILD SUPPORTING FACTORS
    // ========================================================

    const supportingHTML =
        supportingFactors
            .map(
                function (factor) {

                    return `
                        <li>
                            ${escapeHTML(
                                factor.friendly_name ||
                                factor.feature
                            )}
                        </li>
                    `;

                }
            )
            .join("");


    // ========================================================
    // BUILD OPPOSING FACTORS
    // ========================================================

    const opposingHTML =
        opposingFactors
            .map(
                function (factor) {

                    return `
                        <li>
                            ${escapeHTML(
                                factor.friendly_name ||
                                factor.feature
                            )}
                        </li>
                    `;

                }
            )
            .join("");


    // ========================================================
    // DISPLAY EXPLANATION
    // ========================================================

    container.innerHTML = `

       <div class="empty-insight-icon">
            <img
                src="${chrome.runtime.getURL('icons/explainability.png')}"
                alt=""
            >
        </div>

        <div>

            <strong>
                Why ${escapeHTML(
                    predictedLabel
                )}?
            </strong>

            <p>
                ${escapeHTML(
                    parentExplanation
                )}
            </p>

            ${
                supportingHTML
                    ? `
                        <div class="shap-factor-group supporting">

                            <strong>
                                Supporting the prediction
                            </strong>

                            <ul>
                                ${supportingHTML}
                            </ul>

                        </div>
                    `
                    : ""
            }

            ${
                opposingHTML
                    ? `
                        <div class="shap-factor-group opposing">

                            <strong>
                                Opposing the prediction
                            </strong>

                            <ul>
                                ${opposingHTML}
                            </ul>

                        </div>
                    `
                    : ""
            }

        </div>

    `;

}
// ============================================================
// SHAP-BASED DETECTED MULTIMEDIA FEATURES
// ============================================================

function renderContributingFeatures(
    featureContributions
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
        selectedGroups.visual,
        allGroups.visual,
        totalAbsoluteShap
    );


    // ========================================================
    // AUDIO
    // ========================================================

    renderLiveContributionGroup(
        "audioFeatures",
        "audioBar",
        "audioLevel",
        selectedGroups.audio,
        allGroups.audio,
        totalAbsoluteShap
    );


    // ========================================================
    // TEXT
    // ========================================================

    renderLiveContributionGroup(
        "textFeatures",
        "textBar",
        "textLevel",
        selectedGroups.text,
        allGroups.text,
        totalAbsoluteShap
    );


    // ========================================================
    // ENGAGEMENT
    // ========================================================

    renderLiveContributionGroup(
        "engagementFeatures",
        "engagementBar",
        "engagementLevel",
        selectedGroups.engagement,
        allGroups.engagement,
        totalAbsoluteShap
    );


    // ========================================================
    // EMOTIONAL
    // ========================================================

    renderLiveContributionGroup(
        "emotionalFeatures",
        "emotionalFeatureBar",
        "emotionalFeatureLevel",
        selectedGroups.emotional,
        allGroups.emotional,
        totalAbsoluteShap
    );


    // ========================================================
    // VIDEO CONTEXT / METADATA
    // ========================================================

    renderLiveContributionGroup(
        "metadataFeatures",
        "metadataBar",
        "metadataLevel",
        selectedGroups.metadata,
        allGroups.metadata,
        totalAbsoluteShap
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
    totalAbsoluteShap
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

    container.innerHTML =
        selectedFeatures
            .map(
                function (feature) {


                    const featureName =
                        feature.friendly_name ||
                        feature.feature;


                    const value =
                        formatFeatureValue(
                            feature.feature_value
                        );


                    const shapValue =
                        typeof feature.shap_value ===
                            "number"
                            ? feature.shap_value
                            : 0;


                    const absoluteShap =
                        typeof feature.absolute_shap ===
                            "number"
                            ? feature.absolute_shap
                            : Math.abs(
                                shapValue
                            );


                    const direction =
                        feature.direction ||
                        (
                            shapValue >= 0
                                ? "supports"
                                : "opposes"
                        );


                    return `

                        <span
                            class="detected-feature"
                            title="${escapeHTML(
                                direction
                            )} prediction | Absolute SHAP: ${escapeHTML(
                                absoluteShap.toFixed(
                                    4
                                )
                            )}"
                        >

                            ${escapeHTML(
                                featureName
                            )}

                            <strong>
                                ${escapeHTML(
                                    value
                                )}
                            </strong>

                        </span>

                    `;

                }
            )
            .join("");

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

    }
);


// ============================================================
// START
// ============================================================

initialise();