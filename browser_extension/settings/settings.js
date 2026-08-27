const protectionToggle =
    document.getElementById(
        "protectionToggle"
    );

const liveToggle =
    document.getElementById(
        "liveToggle"
    );

const explainabilityToggle =
    document.getElementById(
        "explainabilityToggle"
    );


/* ==========================================
   LOAD SETTINGS
========================================== */

chrome.storage.local.get(
    [
        "protectionEnabled",
        "liveAnalysisEnabled",
        "explainabilityEnabled"
    ],
    (settings) => {

        protectionToggle.checked =
            settings.protectionEnabled !== false;

        liveToggle.checked =
            settings.liveAnalysisEnabled !== false;

        explainabilityToggle.checked =
            settings.explainabilityEnabled !== false;

    }
);


/* ==========================================
   PROTECTION
========================================== */

protectionToggle.addEventListener(
    "change",
    () => {

        chrome.storage.local.set({

            protectionEnabled:
                protectionToggle.checked

        });

    }
);


/* ==========================================
   LIVE ANALYSIS
========================================== */

liveToggle.addEventListener(
    "change",
    () => {

        chrome.storage.local.set({

            liveAnalysisEnabled:
                liveToggle.checked

        });

    }
);


/* ==========================================
   EXPLAINABILITY
========================================== */

explainabilityToggle.addEventListener(
    "change",
    () => {

        chrome.storage.local.set({

            explainabilityEnabled:
                explainabilityToggle.checked

        });

    }
);