from modules.behavioural_features import extract_behavioural_features



visual = {

    "scene_rate": 0.8,
    "motion_std": 0.3,
    "motion_spike_rate": 0.6,
    "flicker_rate": 0.1

}


audio = {

    "audio_repetition": 0.7,
    "audio_variation": 0.5

}


text = {

    "reward_keyword_frequency": 0.2

}



result = extract_behavioural_features(
    visual,
    audio,
    text
)



for key,value in result.items():

    print(
        key,
        ":",
        value
    )