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

                <!-- STATUS -->

                <div class="neuroshield-status-card">

                    <div class="status-left">

                        <span class="status-dot"></span>

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

                    <div class="status-badge">
                        ACTIVE
                    </div>

                </div>


                <!-- ================================================= -->
                <!-- MAIN SCORE -->
                <!-- ================================================= -->

                <section
                    class="neuroshield-main-card"
                    id="mainScoreCard"
                >

                    <div class="live-badge">
                        READY
                    </div>

                    <div class="main-score-title">
                        Overall Developmental Score
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

                    <div class="main-score-description">

                        This video has not been analysed yet.
                        Results will appear here only after
                        the NeuroShield AI backend provides
                        verified analysis data.

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
                            🧠
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
                            ⚠
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
                            ♥
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
                            ✦
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


                        <!-- VISUAL -->

                        <div class="feature-card">

                            <div class="feature-top">

                                <div class="feature-heading">

                                    <div class="feature-icon visual">
                                        👁
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


                        <!-- AUDIO -->

                        <div class="feature-card">

                            <div class="feature-top">

                                <div class="feature-heading">

                                    <div class="feature-icon audio">
                                        🔊
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


                        <!-- TEXT -->

                        <div class="feature-card">

                            <div class="feature-top">

                                <div class="feature-heading">

                                    <div class="feature-icon text">
                                        💬
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


                        <!-- ENGAGEMENT -->

                        <div class="feature-card">

                            <div class="feature-top">

                                <div class="feature-heading">

                                    <div class="feature-icon engagement">
                                        🎯
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


                <!-- FOOTER -->

                <div class="neuroshield-footer">

                    Explainable Multimodal AI
                    <span>•</span>
                    NeuroShield AI

                </div>

            </div>

        </div>

    `;

    document.body.appendChild(overlay);

    initialiseOverlayControls();

    loadOverlayPosition();

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


    if (!windowElement || !dragHandle) {

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
            async function(event) {

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
            function(event) {

                event.preventDefault();
                event.stopPropagation();

                chrome.runtime.sendMessage(
                    {
                        action: "OPEN_SETTINGS"
                    },
                    function() {

                        if (chrome.runtime.lastError) {

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
            function(event) {

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
            function(event) {

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

                    minimizeButton.textContent = "+";

                } else {

                    minimizeButton.textContent = "−";

                }

            }
        );

    }


    // ========================================================
    // DRAG
    // ========================================================

    dragHandle.addEventListener(
        "mousedown",
        function(event) {

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
                event.clientX - rect.left;

            dragOffsetY =
                event.clientY - rect.top;

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
                function() {

                    if (!windowElement.classList.contains("minimized")) {

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

function updateNotificationButton(button) {

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

function handleDrag(event) {

    if (!isDragging || !overlay) {

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
        event.clientX - dragOffsetX;

    let y =
        event.clientY - dragOffsetY;

    const width =
        windowElement.offsetWidth;

    const height =
        windowElement.offsetHeight;

    const maxX =
        Math.max(
            0,
            window.innerWidth - width
        );

    const maxY =
        Math.max(
            0,
            window.innerHeight - height
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

    isDragging = false;

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

            left: rect.left,
            top: rect.top,
            width: rect.width,
            height: rect.height

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
            typeof position.width === "number"
        ) {

            windowElement.style.width =
                `${position.width}px`;

        }

        if (
            typeof position.height === "number"
        ) {

            windowElement.style.height =
                `${position.height}px`;

        }

        if (
            typeof position.left === "number"
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
            typeof position.top === "number"
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

    overlay = null;

}


// ============================================================
// MESSAGE HANDLING
// ============================================================

chrome.runtime.onMessage.addListener(
    function(message, sender, sendResponse) {

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
                protectionEnabled: true
            });

            checkCurrentPage();

            sendResponse({
                success: true
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
                protectionEnabled: false
            });

            removeOverlay();

            sendResponse({
                success: true
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

            applyBackendResults(
                message.data
            );

            sendResponse({
                success: true
            });

            return true;

        }

    }
);


// ============================================================
// APPLY REAL BACKEND RESULTS
// ============================================================

function applyBackendResults(data) {

    if (!data) {

        return;

    }

    console.log(
        "NeuroShield AI: Applying verified backend data:",
        data
    );


    // ========================================================
    // OVERALL
    // ========================================================

    if (
        typeof data.overall === "number"
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
        typeof data.recommendation === "string" &&
        data.recommendation.trim() !== ""
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
        Array.isArray(data.insights) &&
        data.insights.length > 0
    ) {

        renderInsights(
            data.insights
        );

    }


    // ========================================================
    // HIGH ALERT
    // ========================================================

    if (
        typeof data.overall === "number" &&
        data.overall > 75
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
        typeof value !== "number"
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
            `${Math.round(safeValue)}%`;

    }

    if (labelElement) {

        if (safeValue > 75) {

            labelElement.textContent =
                "High Stimulation";

        } else if (safeValue < 40) {

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

function updateMainCardLevel(score) {

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

    if (score > 75) {

        card.classList.add(
            "high"
        );

    } else if (score < 40) {

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
        typeof value !== "number"
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
            `${Math.round(safeValue)}%`;

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
        typeof value !== "number"
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

        if (safeValue > 75) {

            level.textContent =
                "High";

        } else if (safeValue < 40) {

            level.textContent =
                "Low";

        } else {

            level.textContent =
                "Moderate";

        }

    }

}


// ============================================================
// INSIGHTS
// ============================================================

function renderInsights(insights) {

    const container =
        document.getElementById(
            "insightContainer"
        );

    if (!container) {

        return;

    }

    container.innerHTML = "";

    insights.forEach(
        function(insight) {

            const box =
                document.createElement("div");

            box.className =
                "empty-insight";

            box.innerHTML = `

                <div class="empty-insight-icon">
                    ✦
                </div>

                <div>

                    <strong>
                        Explainability Insight
                    </strong>

                    <p>
                        ${escapeHTML(insight)}
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

function triggerHighRiskAlert() {

    if (!notificationsEnabled) {

        return;

    }

    if (
        !currentVideoId ||
        lastAlertedVideoId === currentVideoId
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

    if (mainCard) {

        mainCard.classList.add(
            "alert-pulse"
        );

        setTimeout(
            function() {

                mainCard.classList.remove(
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
            audioContext.currentTime + 0.15
        );

        gain.gain.setValueAtTime(
            0.0001,
            audioContext.currentTime
        );

        gain.gain.exponentialRampToValueAtTime(
            0.18,
            audioContext.currentTime + 0.03
        );

        gain.gain.exponentialRampToValueAtTime(
            0.0001,
            audioContext.currentTime + 0.35
        );

        oscillator.connect(gain);

        gain.connect(
            audioContext.destination
        );

        oscillator.start();

        oscillator.stop(
            audioContext.currentTime + 0.4
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

function escapeHTML(value) {

    const div =
        document.createElement("div");

    div.textContent =
        String(value);

    return div.innerHTML;

}


// ============================================================
// YOUTUBE SPA NAVIGATION
// ============================================================

let lastUrl =
    window.location.href;

setInterval(
    function() {

        const currentUrl =
            window.location.href;

        if (
            currentUrl !== lastUrl
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
    function(changes, areaName) {

        if (
            areaName !== "local"
        ) {

            return;

        }


        if (
            changes.protectionEnabled
        ) {

            protectionEnabled =
                changes.protectionEnabled.newValue === true;

            checkCurrentPage();

        }


        if (
            changes.neuroshieldNotificationsEnabled
        ) {

            notificationsEnabled =
                changes
                    .neuroshieldNotificationsEnabled
                    .newValue !== false;

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