def risk_level(value, low, high):
    if value < low:
        return "Low"
    elif value < high:
        return "Medium"
    else:
        return "High"


def compute_visual_score(saturation, motion):
    return {
        "saturation": risk_level(saturation, 0.4, 0.7),
        "motion": risk_level(motion, 2, 6)
    }


def compute_audio_score(loudness, density):
    return {
        "loudness": risk_level(loudness, 0.02, 0.05),
        "density": risk_level(density, 2, 5)
    }