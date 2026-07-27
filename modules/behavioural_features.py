"""
===========================================================
BEHAVIOURAL FEATURE EXTRACTION MODULE

Multimodal Explainable AI Framework
YouTube Child Content Analysis

Features:
- Loop Detection
- Reward Cue Frequency
- Attention Reset Rate

===========================================================
"""


import numpy as np



# =====================================================
# LOOP DETECTION
# =====================================================

def calculate_loop_detection(
        scene_rate,
        motion_variation,
        audio_repetition
):
    """
    Estimates repeated content patterns.

    Higher value means:
    - more repeated scenes
    - less variation
    - repeated audio patterns

    Range:
    0 = low repetition
    1 = high repetition
    """


    # Scene repetition component
    visual_repeat = min(
        scene_rate / 10,
        1
    )


    # Low motion variation indicates repetitive content
    motion_repeat = 1 - min(
        motion_variation,
        1
    )


    score = (

        visual_repeat * 0.4

        +

        motion_repeat * 0.3

        +

        audio_repetition * 0.3

    )


    return float(
        np.clip(
            score,
            0,
            1
        )
    )



# =====================================================
# REWARD CUE FREQUENCY
# =====================================================

def calculate_reward_frequency(
        reward_keyword_frequency,
        motion_spike_rate,
        flicker_rate
):
    """
    Estimates attention-grabbing reward patterns.

    Combines:
    - engagement words
    - rapid movement
    - visual stimulation
    """


    score = (

        reward_keyword_frequency * 0.4

        +

        min(
            motion_spike_rate,
            1
        ) * 0.4

        +

        min(
            flicker_rate,
            1
        ) * 0.2

    )


    return float(
        np.clip(
            score,
            0,
            1
        )
    )



# =====================================================
# ATTENTION RESET RATE
# =====================================================

def calculate_attention_reset(
        scene_rate,
        motion_spike_rate,
        audio_variation
):
    """
    Measures how frequently new stimuli are introduced.

    High value:
    - frequent scene changes
    - fast movement
    - changing audio

    Low value:
    - stable educational content
    """


    score = (

        min(
            scene_rate,
            1
        ) * 0.4

        +

        min(
            motion_spike_rate,
            1
        ) * 0.3

        +

        min(
            audio_variation,
            1
        ) * 0.3

    )


    return float(
        np.clip(
            score,
            0,
            1
        )
    )



# =====================================================
# MAIN BEHAVIOURAL EXTRACTION
# =====================================================

def extract_behavioural_features(
        visual_features,
        audio_features,
        text_features
):
    """
    Combines multimodal information
    to produce behavioural indicators.
    """


    return {


        "loop_detection_score":

            calculate_loop_detection(

                visual_features.get(
                    "scene_rate",
                    0
                ),

                visual_features.get(
                    "motion_std",
                    0
                ),

                audio_features.get(
                    "audio_repetition",
                    0
                )

            ),



        "reward_cue_frequency":

            calculate_reward_frequency(

                text_features.get(
                    "reward_keyword_frequency",
                    0
                ),

                visual_features.get(
                    "motion_spike_rate",
                    0
                ),

                visual_features.get(
                    "flicker_rate",
                    0
                )

            ),



        "attention_reset_rate":

            calculate_attention_reset(

                visual_features.get(
                    "scene_rate",
                    0
                ),

                visual_features.get(
                    "motion_spike_rate",
                    0
                ),

                audio_features.get(
                    "audio_variation",
                    0
                )

            )

    }