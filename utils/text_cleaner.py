"""
Text cleaning utilities for Whisper transcripts.

This module cleans noisy transcripts before NLP feature extraction.
"""

import re
import unicodedata


# =====================================================
# Whisper hallucination words
# =====================================================

REMOVE_WORDS = {

    "music",
    "applause",
    "laughing",
    "laughter",
    "subtitle",
    "subtitles",
    "caption",
    "captions",
    "foreign",
    "inaudible"

}
HALLUCINATION_PHRASES = [
    "thank you for watching",
    "please subscribe",
    "thanks for watching",
    "see you next time"
]


# =====================================================
# Filler words
# =====================================================

FILLER_WORDS = {

    "uh",
    "um",
    "erm",
    "hmm",
    "mmm",
    "ah"

}


# =====================================================
# Unicode cleaning
# =====================================================

def remove_unicode(text):

    text = unicodedata.normalize(
        "NFKD",
        text
    )

    cleaned = ""

    for char in text:

        if char.isascii():

            cleaned += char

    return cleaned



# =====================================================
# Remove emojis
# Keep sentence punctuation
# =====================================================

def clean_punctuation(text):

    text = re.sub(

        r"[^a-zA-Z.!?\s]",

        "",

        text

    )

    return text



# =====================================================
# Normalize spaces
# =====================================================

def normalize_spaces(text):

    return re.sub(

        r"\s+",

        " ",

        text

    ).strip()



# =====================================================
# Remove repeated consecutive words
#
# baby baby baby shark
#
# ->
#
# baby shark
# =====================================================

def remove_repeated_words(text):

    words = text.split()

    cleaned = []

    previous = None


    for word in words:

        if word != previous:

            cleaned.append(word)

        previous = word


    return " ".join(cleaned)



# =====================================================
# Remove repeated phrases
#
# do do do do do do
#
# ->
#
# do do do
# =====================================================

def remove_repeated_phrases(text):

    words = text.split()

    if len(words) < 6:

        return text


    cleaned = []

    i = 0


    while i < len(words):

        if i + 5 < len(words):

            first = words[i:i+3]

            second = words[i+3:i+6]


            if first == second:

                cleaned.extend(first)

                i += 6

                continue


        cleaned.append(words[i])

        i += 1


    return " ".join(cleaned)



# =====================================================
# Remove nonsense tokens
# =====================================================

def remove_long_tokens(text):

    cleaned = []


    for word in text.split():

        # remove extremely long Whisper errors

        if len(word) <= 20:

            cleaned.append(word)


    return " ".join(cleaned)



# =====================================================
# Remove hallucination words
# =====================================================

def remove_hallucinations(text):

    words = []

    for word in text.split():

        if word not in REMOVE_WORDS:

            words.append(word)


    return " ".join(words)

# =====================================================
# Remove hallucination phrase
# =====================================================
def remove_hallucination_phrases(text):

    for phrase in HALLUCINATION_PHRASES:

        text = text.replace(
            phrase,
            ""
        )

    return text

# =====================================================
# Remove filler sounds
# =====================================================

def remove_fillers(text):

    words = []


    for word in text.split():

        if word not in FILLER_WORDS:

            words.append(word)


    return " ".join(words)



# =====================================================
# MAIN CLEAN FUNCTION
# =====================================================

def clean_transcript(text):

    if not isinstance(text, str):

        return ""


    text = text.lower()


    text = remove_unicode(text)


    text = clean_punctuation(text)


    text = normalize_spaces(text)


    text = remove_hallucination_phrases(text)


    text = remove_hallucinations(text)


    text = remove_fillers(text)


    text = remove_long_tokens(text)


    text = remove_repeated_words(text)


    text = remove_repeated_phrases(text)


    text = normalize_spaces(text)


    return text