"""
===========================================================
FEATURE FUSION MODULE

Combines:
Visual + Audio + Text + Behavioural Features

Output:
Single multimodal feature vector

===========================================================
"""


def fuse_features(
        visual_features,
        audio_features,
        text_features,
        behavioural_features
):

    """
    Combines all modalities into
    one dictionary for ML training.
    """


    fused_features = {}


    # Visual features

    for key,value in visual_features.items():

        fused_features[
            key
        ] = value



    # Audio features

    for key,value in audio_features.items():

        fused_features[
            key
        ] = value



    # Text features

    for key,value in text_features.items():

        fused_features[
            key
        ] = value



    # Behavioural features

    for key,value in behavioural_features.items():

        fused_features[
            key
        ] = value



    return fused_features