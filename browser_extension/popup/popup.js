// ==========================================
// NeuroShield AI
// Popup Controller
// ==========================================


const protectionButton =
    document.getElementById(
        "protectionButton"
    );


const initialScreen =
    document.getElementById(
        "initialScreen"
    );


const analysingScreen =
    document.getElementById(
        "analysingScreen"
    );


const loadingBar =
    document.getElementById(
        "loadingBar"
    );


const steps = [

    document.getElementById("step1"),

    document.getElementById("step2"),

    document.getElementById("step3"),

    document.getElementById("step4")

];


/* =========================================
   PROTECTION BUTTON
========================================= */

if (protectionButton) {

    protectionButton.addEventListener(
        "click",
        toggleProtection
    );

}

// ==========================================
// PROTECTION TOGGLE
// ==========================================

async function toggleProtection() {

    try {

        const result =
            await chrome.storage.local.get(
                "protectionEnabled"
            );

        const currentlyEnabled =
            result.protectionEnabled === true;


        if (currentlyEnabled) {

            await stopProtection();

        } else {

            await startProtection();

        }

    } catch (error) {

        console.error(
            "NeuroShield AI: Could not toggle protection:",
            error
        );

    }

}

/* =========================================
   START PROTECTION
========================================= */

async function startProtection() {

    console.log(
        "NeuroShield AI: Turning protection on."
    );


    /* Show loading screen */

    if (initialScreen) {

        initialScreen.classList.remove(
            "active"
        );

    }


    if (analysingScreen) {

        analysingScreen.classList.add(
            "active"
        );

    }


    /* Save protection state */

    await chrome.storage.local.set({

        protectionEnabled: true

    });


    /* Animate popup */

    animateAnalysis();


    /* Find current tab */

    try {

        const tabs =
            await chrome.tabs.query({

                active: true,

                currentWindow: true

            });


        const activeTab =
            tabs[0];


        if (
            activeTab &&
            activeTab.id &&
            activeTab.url &&
            (
                activeTab.url.includes(
                    "youtube.com"
                )
            )
        ) {

            /*
                Tell the content script that
                protection has been enabled.

                We deliberately do NOT wait
                for a response.
            */

            try {

                await chrome.tabs.sendMessage(
                    activeTab.id,
                    {
                        action:
                            "START_ANALYSIS"
                    }
                );

            } catch (error) {

                /*
                    This can happen if the content
                    script has not loaded yet.

                    It is NOT a fatal error.
                */

                console.log(
                    "NeuroShield AI: YouTube page will detect protection automatically."
                );

            }

        }

    } catch (error) {

        console.error(
            "NeuroShield AI:",
            error
        );

    }


    /* Close popup after animation */

    setTimeout(
        () => {

            window.close();

        },
        3000
    );

}

// ==========================================
// STOP PROTECTION
// ==========================================

async function stopProtection() {

    console.log(
        "NeuroShield AI: Turning protection off."
    );


    await chrome.storage.local.set({

        protectionEnabled: false

    });


    try {

        const tabs =
            await chrome.tabs.query({

                active: true,

                currentWindow: true

            });


        const activeTab =
            tabs[0];


        if (
            activeTab &&
            activeTab.id &&
            activeTab.url &&
            activeTab.url.includes("youtube.com")
        ) {

            try {

                await chrome.tabs.sendMessage(
                    activeTab.id,
                    {
                        action: "STOP_ANALYSIS"
                    }
                );

            } catch (error) {

                console.log(
                    "NeuroShield AI: Content script not available. Protection state was still disabled."
                );

            }

        }

    } catch (error) {

        console.error(
            "NeuroShield AI:",
            error
        );

    }


    // Return to initial screen

    if (analysingScreen) {

        analysingScreen.classList.remove(
            "active"
        );

    }

    if (initialScreen) {

        initialScreen.classList.add(
            "active"
        );

    }


    updateProtectionButton();

}

// ==========================================
// UPDATE PROTECTION BUTTON
// ==========================================

async function updateProtectionButton() {

    if (!protectionButton) {

        return;

    }


    const result =
        await chrome.storage.local.get(
            "protectionEnabled"
        );


    const enabled =
        result.protectionEnabled === true;


    if (enabled) {
        const subtitle = document.querySelector(
            "#initialScreen h3"
        );

        if (subtitle) {
            subtitle.textContent = "Protection is currently active";
        }

        protectionButton.textContent =
            "Turn Off Protection";

        protectionButton.classList.add(
            "enabled"
        );

        protectionButton.setAttribute(
            "aria-pressed",
            "true"
        );

    } else {
        const subtitle = document.querySelector(
            "#initialScreen h3"
        );

        if (subtitle) {
            subtitle.textContent = "Protect Your Child's Viewing";
        }

        protectionButton.textContent =
            "Turn On Protection";

        protectionButton.classList.remove(
            "enabled"
        );

        protectionButton.setAttribute(
            "aria-pressed",
            "false"
        );

    }

}

/* =========================================
   ANIMATION
========================================= */

function animateAnalysis() {

    const percentages = [

        25,
        50,
        75,
        100

    ];


    percentages.forEach(
        (percentage, index) => {

            setTimeout(
                () => {

                    if (loadingBar) {

                        loadingBar.style.width =
                            percentage + "%";

                    }


                    if (steps[index]) {

                        steps[index]
                            .classList
                            .add(
                                "completed"
                            );

                    }

                },

                index * 700
            );

        }
    );

}

// ==========================================
// INITIALISE POPUP STATE
// ==========================================

updateProtectionButton();

// ============================================================
// LOAD SAVED APPEARANCE THEME
// ============================================================

async function loadPopupTheme() {

    try {

        const result = await chrome.storage.local.get(
            "neuroshieldTheme"
        );

        const theme =
            result.neuroshieldTheme === "dark"
                ? "dark"
                : "light";

        document.documentElement.setAttribute(
            "data-ns-theme",
            theme
        );

    } catch (error) {

        console.error(
            "NeuroShield AI: Failed to load popup theme:",
            error
        );

    }

}

loadPopupTheme();

// ============================================================
// OPEN ANALYSIS OVERLAY
// ============================================================

const openOverlayButton =
    document.getElementById("openOverlayButton");

const openOverlayMessage =
    document.getElementById("openOverlayMessage");

if (openOverlayButton) {

    openOverlayButton.addEventListener(
        "click",
        async function () {

            openOverlayButton.disabled = true;

            if (openOverlayMessage) {
                openOverlayMessage.textContent = "";
            }

            try {

                const tabs = await chrome.tabs.query({
                    active: true,
                    currentWindow: true
                });

                const activeTab = tabs[0];

                if (!activeTab || !activeTab.id) {
                    throw new Error("No active tab found.");
                }

                if (
                    !activeTab.url ||
                    !/^https:\/\/(www\.)?youtube\.com\/watch(?:\?|$)/.test(
                        activeTab.url
                    )
                ) {
                    throw new Error(
                        "Please open a YouTube video first."
                    );
                }

                const response =
                    await chrome.tabs.sendMessage(
                        activeTab.id,
                        {
                            action: "OPEN_NEUROSHIELD_OVERLAY"
                        }
                    );

                if (!response || !response.success) {

                    throw new Error(
                        response?.error ||
                        "Could not open the overlay."
                    );

                }

                window.close();

            } catch (error) {

                console.error(
                    "NeuroShield AI: Open overlay failed:",
                    error
                );

                if (openOverlayMessage) {

                    openOverlayMessage.textContent =
                        error.message;

                }

            } finally {

                openOverlayButton.disabled = false;

            }

        }
    );

}