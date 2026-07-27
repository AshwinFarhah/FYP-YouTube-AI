from modules.text_features import extract_text_features
from modules.behavioural_features import extract_behavioural_features


print("\nTEXT TEST")
print("================")


text = extract_text_features(
    "The baby learns colours and numbers. "
    "The child wins a reward and plays again."
)

for k,v in text.items():
    print(k, ":", v)



print("\nBEHAVIOURAL TEST")
print("================")


visual = {

    "scene_rate":0.5,
    "motion_std":0.3,
    "motion_spike_rate":0.4,
    "flicker_rate":0.2

}


audio = {

    "audio_variation":0.2,
    "audio_repetition":0.5

}


behaviour = extract_behavioural_features(
    visual,
    audio,
    text
)


for k,v in behaviour.items():
    print(k,":",v)