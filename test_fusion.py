from modules.feature_fusion import fuse_features


visual = {
    "brightness":0.5
}

audio = {
    "tempo":100
}

text = {
    "sentence_complexity":70
}

behaviour = {
    "loop_detection_score":0.4
}



result = fuse_features(
    visual,
    audio,
    text,
    behaviour
)


print(result)