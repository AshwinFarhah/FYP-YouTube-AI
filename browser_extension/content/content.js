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


// ============================================================
// INITIALISE
// ============================================================

async function initialise() {

    try {

        const result = await chrome.storage.local.get(
            ["protectionEnabled"]
        );

        protectionEnabled =
            result.protectionEnabled === true;

        checkCurrentPage();

    } catch (error) {

        console.error(
            "NeuroShield AI: Could not initialise:",
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


    // No video selected
    if (!videoId) {

        currentVideoId = null;

        removeOverlay();

        return;

    }


    // New video
    if (videoId !== currentVideoId) {

        currentVideoId = videoId;

        showAnalysisTemplate();

        return;

    }


    // Same video but overlay somehow disappeared
    if (!document.getElementById("neuroshield-overlay")) {

        showAnalysisTemplate();

    }

}


// ============================================================
// GET CURRENT VIDEO ID
// ============================================================

function getCurrentVideoId() {

    const url = new URL(window.location.href);


    // Standard YouTube video page
    if (
        url.hostname.includes("youtube.com") &&
        url.pathname === "/watch"
    ) {

        return url.searchParams.get("v");

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


    overlay.innerHTML = `

        <div class="neuroshield-window">

            <!-- HEADER -->

            <div
                class="neuroshield-header"
                id="neuroshield-drag-handle"
            >

                <div class="neuroshield-brand">

                    <img
                        src="${chrome.runtime.getURL("icons/logo.png")}"
                        class="neuroshield-logo"
                        alt="NeuroShield AI"
                    >

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

                    <button
                        id="neuroshield-minimize"
                        class="neuroshield-action"
                        title="Minimize"
                    >
                        −
                    </button>

                    <button
                        id="neuroshield-close"
                        class="neuroshield-action"
                        title="Close"
                    >
                        ×
                    </button>

                </div>

            </div>


            <!-- CONTENT -->

            <div
                class="neuroshield-content"
                id="neuroshield-content"
            >

                <!-- ANALYSIS STATUS -->

                <div class="neuroshield-status-card">

                    <div class="status-left">

                        <span class="status-dot"></span>

                        <div>

                            <div class="status-title">
                                AI Monitoring
                            </div>

                            <div class="status-text">
                                Waiting for analysis
                            </div>

                        </div>

                    </div>

                    <div class="status-badge">
                        ACTIVE
                    </div>

                </div>


                <!-- MAIN SCORE -->

                <section class="neuroshield-main-card">

                    <div class="live-badge">
                        ANALYSIS
                    </div>

                    <div class="main-score-title">
                        Overall Developmental Score
                    </div>

                    <div class="main-score-empty">
                        —
                    </div>

                    <div class="main-score-label">
                        Awaiting analysis
                    </div>

                    <div class="main-score-description">

                        Analysis results will appear here once
                        the NeuroShield AI backend processes
                        the selected video.

                    </div>

                </section>


                <!-- DEVELOPMENTAL IMPACT -->

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

                                <strong>
                                    —
                                </strong>

                            </div>

                            <div class="progress-track">

                                <div class="progress-fill"></div>

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

                                <strong>
                                    —
                                </strong>

                            </div>

                            <div class="progress-track">

                                <div class="progress-fill"></div>

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

                                <strong>
                                    —
                                </strong>

                            </div>

                            <div class="progress-track">

                                <div class="progress-fill"></div>

                            </div>

                            <div class="score-description">
                                Emotional intensity and tone
                            </div>

                        </div>

                    </div>

                </section>


                <!-- EXPLAINABILITY -->

                <section class="neuroshield-card">

                    <div class="card-title">
                        Explainability Insights
                    </div>


                    <div class="empty-insight">

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


                <!-- MULTIMEDIA FEATURES -->

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

                                <span class="feature-level">
                                    —
                                </span>

                            </div>


                            <div class="mini-progress">

                                <div class="mini-fill"></div>

                            </div>


                            <div class="feature-bubbles">

                                <span>
                                    Motion Intensity
                                </span>

                                <span>
                                    Scene Changes
                                </span>

                                <span>
                                    Brightness
                                </span>

                                <span>
                                    Saturation
                                </span>

                                <span>
                                    Flicker Rate
                                </span>

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

                                <span class="feature-level">
                                    —
                                </span>

                            </div>


                            <div class="mini-progress">

                                <div class="mini-fill"></div>

                            </div>


                            <div class="feature-bubbles">

                                <span>
                                    Loudness
                                </span>

                                <span>
                                    Pitch Variation
                                </span>

                                <span>
                                    Tempo
                                </span>

                                <span>
                                    Spectral Density
                                </span>

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

                                <span class="feature-level">
                                    —
                                </span>

                            </div>


                            <div class="mini-progress">

                                <div class="mini-fill"></div>

                            </div>


                            <div class="feature-bubbles">

                                <span>
                                    Phrase Repetition
                                </span>

                                <span>
                                    Sentence Complexity
                                </span>

                                <span>
                                    Vocabulary Diversity
                                </span>

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

                                <span class="feature-level">
                                    —
                                </span>

                            </div>


                            <div class="mini-progress">

                                <div class="mini-fill"></div>

                            </div>


                            <div class="feature-bubbles">

                                <span>
                                    Reward Cues
                                </span>

                                <span>
                                    Attention Resets
                                </span>

                                <span>
                                    Loop Detection
                                </span>

                                <span>
                                    Motion Spikes
                                </span>

                            </div>

                        </div>

                    </div>

                </section>


                <!-- RECOMMENDATION -->

                <section class="neuroshield-card">

                    <div class="card-title">
                        Recommendation
                    </div>

                    <div class="empty-recommendation">

                        <span>
                            💡
                        </span>

                        <p>
                            Recommendation will be generated
                            after the developmental analysis
                            is completed.
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


    if (!windowElement || !dragHandle) {

        return;

    }


    // --------------------------------------------------------
    // CLOSE
    // --------------------------------------------------------

    if (closeButton) {

        closeButton.addEventListener(
            "click",
            function(event) {

                event.stopPropagation();

                removeOverlay();

            }
        );

    }


    // --------------------------------------------------------
    // MINIMIZE
    // --------------------------------------------------------

    if (minimizeButton) {

        minimizeButton.addEventListener(
            "click",
            function(event) {

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


    // --------------------------------------------------------
    // DRAGGING
    // --------------------------------------------------------

    dragHandle.addEventListener(
        "mousedown",
        function(event) {

            // Don't drag when clicking buttons
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


    document.addEventListener(
        "mousemove",
        handleDrag
    );


    document.addEventListener(
        "mouseup",
        stopDrag
    );

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


    // Keep window inside browser
    const maxX =
        window.innerWidth - width;

    const maxY =
        window.innerHeight - 60;


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


    saveOverlayPosition();

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
// SAVE SIZE / POSITION
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
// LOAD SIZE / POSITION
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


        if (position.width) {

            windowElement.style.width =
                `${position.width}px`;

        }


        if (position.height) {

            windowElement.style.height =
                `${position.height}px`;

        }


        if (
            typeof position.left === "number"
        ) {

            windowElement.style.left =
                `${position.left}px`;

            windowElement.style.right =
                "auto";

        }


        if (
            typeof position.top === "number"
        ) {

            windowElement.style.top =
                `${position.top}px`;

        }

    } catch (error) {

        console.log(
            "NeuroShield AI: Could not restore window position."
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
// POPUP MESSAGES
// ============================================================

chrome.runtime.onMessage.addListener(
    function(message, sender, sendResponse) {

        if (!message) {

            return;

        }


        // ----------------------------------------------------
        // TURN PROTECTION ON
        // ----------------------------------------------------

        if (
            message.action ===
            "START_ANALYSIS"
        ) {

            protectionEnabled = true;

            checkCurrentPage();


            sendResponse({
                success: true
            });

            return;

        }


        // ----------------------------------------------------
        // TURN PROTECTION OFF
        // ----------------------------------------------------

        if (
            message.action ===
            "STOP_ANALYSIS"
        ) {

            protectionEnabled = false;

            removeOverlay();


            sendResponse({
                success: true
            });

            return;

        }


        // ----------------------------------------------------
        // BACKEND ANALYSIS RESULT
        // ----------------------------------------------------

        if (
            message.type ===
            "NEUROSHIELD_ANALYSIS_UPDATE"
        ) {

            applyBackendResults(
                message.data
            );


            sendResponse({
                success: true
            });

        }

    }
);


// ============================================================
// BACKEND RESULTS
// ============================================================

function applyBackendResults(data) {

    if (!data) {

        return;

    }


    /*
        IMPORTANT:

        This function is intentionally empty-ish for now.

        Your Python backend will eventually send something
        like:

        {
            overall: 72,
            cognitive: 78,
            behavioural: 65,
            emotional: 72,

            visual: 88,
            audio: 82,
            text: 58,
            engagement: 90
        }

        We will connect these values to the UI once your
        backend communication is ready.
    */


    console.log(
        "NeuroShield AI: Backend result received:",
        data
    );

}


// ============================================================
// YOUTUBE SPA NAVIGATION DETECTION
// ============================================================

let lastUrl =
    window.location.href;


setInterval(
    function() {

        const currentUrl =
            window.location.href;


        if (currentUrl !== lastUrl) {

            lastUrl =
                currentUrl;


            checkCurrentPage();

        }

    },
    1000
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

    }
);


// ============================================================
// START
// ============================================================

initialise();