/* ============================================================
   NeuroShield AI
   Embedded Settings Functionality
============================================================ */

const NeuroShieldSettings = (() => {

    let settingsRoot = null;
    let onBackToAnalysis = null;


    // ========================================================
    // INITIALISE SETTINGS
    // ========================================================

    async function initialise(root, backCallback) {

        settingsRoot = root;
        onBackToAnalysis = backCallback;

        if (!settingsRoot) {
            console.error(
                "NeuroShield AI: Settings container not found."
            );
            return;
        }

        setupBackButton();
        setupPreferenceToggles();
        setupBackendCheck();
        setupResetPreferences();

        await loadPreferences();

        // ============================================================
        // MULTIMEDIA FEATURES PREFERENCE
        // ============================================================

        const multimediaToggle =
            getElement(
                "ns-multimedia-toggle"
            );

        if (multimediaToggle) {

            const savedSettings =
                await chrome.storage.local.get(
                    "neuroshieldMultimediaEnabled"
                );

            multimediaToggle.checked =
                savedSettings.neuroshieldMultimediaEnabled !== false;

            multimediaToggle.addEventListener(
                "change",
                async function () {

                    await chrome.storage.local.set({

                        neuroshieldMultimediaEnabled:
                        multimediaToggle.checked

                    });

                }
            );

        }
    }


    // ========================================================
    // GET ELEMENT
    // ========================================================

    function getElement(id) {

        return settingsRoot
            ? settingsRoot.querySelector(`#${id}`)
            : null;
    }


    // ========================================================
    // BACK TO ANALYSIS
    // ========================================================

    function setupBackButton() {

        const backButton =
            getElement("ns-settings-back");

        if (!backButton) return;

        backButton.addEventListener("click", () => {

            if (typeof onBackToAnalysis === "function") {
                onBackToAnalysis();
            }

        });
    }


    // ========================================================
    // LOAD SAVED PREFERENCES
    // ========================================================

    async function loadPreferences() {

        try {

            const preferences =
                await chrome.storage.local.get([
                    "protectionEnabled",
                    "neuroshieldNotificationsEnabled",
                    "explainabilityEnabled",
                    "neuroshieldMultimediaEnabled"
                ]);

            const protectionToggle =
                getElement("ns-protection-toggle");

            const notificationsToggle =
                getElement("ns-notifications-toggle");

            const explainabilityToggle =
                getElement("ns-explainability-toggle");

            const multimediaToggle =
                getElement("ns-multimedia-toggle");


            // Protection defaults OFF.
            if (protectionToggle) {

                protectionToggle.checked =
                    preferences.protectionEnabled === true;
            }


            // Notifications default ON.
            if (notificationsToggle) {

                notificationsToggle.checked =
                    preferences.neuroshieldNotificationsEnabled
                    !== false;
            }


            // Explainability defaults ON.
            if (explainabilityToggle) {

                explainabilityToggle.checked =
                    preferences.explainabilityEnabled !== false;
            }


            // Multimedia Features default ON.
            if (multimediaToggle) {

                multimediaToggle.checked =
                    preferences.neuroshieldMultimediaEnabled !== false;

            }

        } catch (error) {

            console.error(
                "NeuroShield AI: Failed to load settings:",
                error
            );

        }
    }


    // ========================================================
    // PREFERENCE TOGGLES
    // ========================================================

    function setupPreferenceToggles() {

        const protectionToggle =
            getElement("ns-protection-toggle");

        const notificationsToggle =
            getElement("ns-notifications-toggle");

        const explainabilityToggle =
            getElement("ns-explainability-toggle");


        if (protectionToggle) {

            protectionToggle.addEventListener(
                "change",
                async () => {

                    try {

                        await chrome.storage.local.set({
                            protectionEnabled:
                            protectionToggle.checked
                        });

                    } catch (error) {

                        console.error(
                            "Failed to save protection setting:",
                            error
                        );

                    }

                }
            );
        }


        if (notificationsToggle) {

            notificationsToggle.addEventListener(
                "change",
                async () => {

                    try {

                        await chrome.storage.local.set({
                            neuroshieldNotificationsEnabled:
                            notificationsToggle.checked
                        });

                    } catch (error) {

                        console.error(
                            "Failed to save notification setting:",
                            error
                        );

                    }

                }
            );
        }


        if (explainabilityToggle) {

            explainabilityToggle.addEventListener(
                "change",
                async () => {

                    try {

                        await chrome.storage.local.set({
                            explainabilityEnabled:
                            explainabilityToggle.checked
                        });

                    } catch (error) {

                        console.error(
                            "Failed to save explainability setting:",
                            error
                        );

                    }

                }
            );
        }

    }

    // ========================================================
    // RESET PREFERENCES - LIVE UPDATE
    // ========================================================

    function setupResetPreferences() {

        const resetButton =
            getElement("ns-reset-preferences");

        const resetMessage =
            getElement("ns-reset-message");

        if (!resetButton) return;

        resetButton.addEventListener("click", async () => {

            try {

                resetButton.disabled = true;

                // Keep the current protection state so
                // the overlay remains open.
                const currentSettings =
                    await chrome.storage.local.get(
                        "protectionEnabled"
                    );

                await chrome.storage.local.set({

                    protectionEnabled:
                        currentSettings.protectionEnabled === true,

                    neuroshieldNotificationsEnabled: true,

                    explainabilityEnabled: true,

                    neuroshieldMultimediaEnabled: true

                });

                // Update Settings switches immediately.
                await loadPreferences();

                // Show success feedback.
                if (resetMessage) {

                    resetMessage.textContent =
                        "Preferences restored successfully.";

                }

            } catch (error) {

                console.error(
                    "NeuroShield AI: Reset failed:",
                    error
                );

                if (resetMessage) {

                    resetMessage.textContent =
                        "Unable to reset preferences.";

                }

            } finally {

                resetButton.disabled = false;

            }

        });

    }


    // ========================================================
    // SYSTEM STATUS
    // ========================================================

    function setupBackendCheck() {

        const checkButton =
            getElement("ns-check-backend");

        if (!checkButton) return;

        checkButton.addEventListener(
            "click",
            checkBackendConnection
        );
    }


    // ========================================================
    // UPDATE STATUS LABEL
    // ========================================================

    function updateStatus(element, text, statusClass) {

        if (!element) return;

        element.textContent = text;

        element.classList.remove(
            "ns-status-connected",
            "ns-status-disconnected",
            "ns-status-warning"
        );

        if (statusClass) {
            element.classList.add(statusClass);
        }
    }


    // ========================================================
    // CHECK BACKEND CONNECTION
    // ========================================================

    async function checkBackendConnection() {

        const checkButton =
            getElement("ns-check-backend");

        const backendStatus =
            getElement("ns-backend-status");

        const modelStatus =
            getElement("ns-model-status");

        if (!checkButton) return;

        checkButton.disabled = true;
        checkButton.textContent = "Checking...";

        updateStatus(
            backendStatus,
            "Checking...",
            null
        );

        updateStatus(
            modelStatus,
            "Checking...",
            null
        );

        try {

            const response = await chrome.runtime.sendMessage({
                action: "CHECK_BACKEND"
            });

            if (!response || response.connected !== true) {

                updateStatus(
                    backendStatus,
                    "Disconnected",
                    "ns-status-disconnected"
                );

                updateStatus(
                    modelStatus,
                    "Unavailable",
                    "ns-status-warning"
                );

                return;
            }

            updateStatus(
                backendStatus,
                "Connected",
                "ns-status-connected"
            );

            if (response.modelLoaded === true) {

                updateStatus(
                    modelStatus,
                    "Loaded",
                    "ns-status-connected"
                );

            } else {

                updateStatus(
                    modelStatus,
                    "Not loaded",
                    "ns-status-warning"
                );

            }

        } catch (error) {

            console.error(
                "NeuroShield AI: Backend check failed:",
                error
            );

            updateStatus(
                backendStatus,
                "Disconnected",
                "ns-status-disconnected"
            );

            updateStatus(
                modelStatus,
                "Unavailable",
                "ns-status-warning"
            );

        } finally {

            checkButton.disabled = false;
            checkButton.textContent = "Check Connection";

        }
    }


    // ========================================================
    // PUBLIC FUNCTIONS
    // ========================================================

    return {
        initialise,
        loadPreferences,
        checkBackendConnection
    };

})();
