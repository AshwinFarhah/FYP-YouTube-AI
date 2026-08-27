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
        startProtection
    );

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
                            "PROTECTION_ENABLED"
                    }
                );

            }

            catch (error) {

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

    }

    catch (error) {

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