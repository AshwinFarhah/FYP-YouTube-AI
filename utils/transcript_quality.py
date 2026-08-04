"""
Transcript Quality Assessment Module

Evaluates Whisper transcript reliability before
NLP feature extraction and dataset generation.

Used for:
- Dataset validation
- Transcript filtering
- Chapter 4 analysis

Features:
- Word count
- Vocabulary diversity
- Repetition detection
- Hallucination detection
- English confidence
- Noise detection
- Quality scoring
- Quality label
"""


import re
from collections import Counter



# =====================================================
# Whisper hallucination patterns
# =====================================================

HALLUCINATION_PATTERNS = [

    "thank you for watching",

    "please subscribe",

    "thanks for watching",

    "see you next time",

    "subscribe",

    "music",

    "applause",

    "laughing",

    "laughter",

    "subtitle",

    "caption",

    "inaudible",

    "foreign"

]



# =====================================================
# Count words
# =====================================================

def count_words(text):

    if not text:
        return 0

    return len(
        text.split()
    )



# =====================================================
# Vocabulary diversity
#
# Unique words / total words
# =====================================================

def unique_word_ratio(text):

    words = text.split()


    if len(words) == 0:

        return 0


    return (

        len(set(words))
        /
        len(words)

    )



# =====================================================
# Repetition detection
#
# Detects:
#
# baby shark baby shark baby shark
#
# =====================================================

def repeated_word_ratio(text):

    words = text.split()


    if len(words)==0:

        return 0


    counter = Counter(words)


    repeated = sum(

        count - 1

        for count in counter.values()

        if count > 1

    )


    return (

        repeated
        /
        len(words)

    )



# =====================================================
# Hallucination score
#
# 0 = clean
# 1 = high hallucination
# =====================================================

def hallucination_score(text):

    if not text:

        return 1


    text = text.lower()


    detected = 0


    for pattern in HALLUCINATION_PATTERNS:

        if pattern in text:

            detected += 1



    return min(

        detected /
        len(HALLUCINATION_PATTERNS),

        1

    )



# =====================================================
# English confidence
#
# Simple language estimation
# =====================================================

def english_ratio(text):

    if not text:

        return 0


    characters = len(text)

    english_characters = len(

        re.findall(
            r"[a-zA-Z]",
            text
        )

    )


    return (

        english_characters
        /
        characters

    )



# =====================================================
# Short transcript detection
#
# Whisper sometimes produces:
#
# "music"
# "hello"
# ""
#
# =====================================================

def length_score(text):

    words = count_words(text)


    if words == 0:

        return 0


    elif words < 5:

        return 0.2


    elif words < 20:

        return 0.5


    elif words < 50:

        return 0.7


    else:

        return 1



# =====================================================
# Nonsense token detection
#
# Example:
#
# asdfghjklqwerty
#
# =====================================================

def nonsense_ratio(text):

    words = text.split()


    if len(words)==0:

        return 1



    nonsense = 0


    for word in words:


        if len(word) > 15:

            nonsense += 1


        elif not re.search(
            "[aeiou]",
            word
        ):

            nonsense += 1



    return (

        nonsense /
        len(words)

    )



# =====================================================
# Transcript quality score
#
# Range:
#
# 0 = unusable
# 1 = reliable
#
# =====================================================

def transcript_quality_score(text):


    word_count = count_words(text)

    length = length_score(text)

    diversity = unique_word_ratio(text)

    repetition = repeated_word_ratio(text)

    hallucination = hallucination_score(text)

    english = english_ratio(text)

    nonsense = nonsense_ratio(text)



    score = (

        0.25 * length

        +

        0.20 * diversity

        +

        0.20 * english

        +

        0.15 * (1-repetition)

        +

        0.10 * (1-hallucination)

        +

        0.10 * (1-nonsense)

    )


    # =====================================
    # Additional transcript reliability rules
    # =====================================

    # Very short Whisper outputs are unreliable
    if word_count < 20:
        score *= 0.2


    # Non-English or corrupted transcripts
    if english < 0.75:
        score *= 0.5



    return max(

        0,

        min(score,1)

    )



# =====================================================
# Quality label
# =====================================================

def quality_label(score):

    if score >= 0.85:
        return "good"

    elif score >= 0.70:
        return "acceptable"

    elif score >= 0.50:
        return "poor"

    else:
        return "rejected"


# =====================================================
# MAIN FUNCTION
# =====================================================

def evaluate_transcript_quality(text):


    score = transcript_quality_score(
        text
    )


    return {


        "transcript_word_count":

            count_words(text),



        "unique_word_ratio":

            unique_word_ratio(text),



        "repeated_word_ratio":

            repeated_word_ratio(text),



        "hallucination_score":

            hallucination_score(text),



        "english_ratio":

            english_ratio(text),



        "nonsense_ratio":

            nonsense_ratio(text),



        "transcript_quality_score":

            score,



        "transcript_quality_label":

            quality_label(score)

    }