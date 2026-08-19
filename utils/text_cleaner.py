"""
Text cleaning utilities for Whisper transcripts.

The cleaning process removes obvious Whisper noise and
hallucination artefacts while preserving meaningful
repetition for NLP analysis.
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


# =====================================================
# Whisper hallucination phrases
# =====================================================

HALLUCINATION_PHRASES = [

    "thank you for watching",

    "please subscribe",

    "don't forget to subscribe",

    "don't forget to click subscribe",

    "click subscribe",

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
# Remove nonsense tokens
# =====================================================

def remove_long_tokens(text):

    cleaned = []

    for word in text.split():

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
# Remove hallucination phrases
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

    # -------------------------------------------------
    # Lowercase
    # -------------------------------------------------

    text = text.lower()

    # -------------------------------------------------
    # Unicode
    # -------------------------------------------------

    text = remove_unicode(text)

    # -------------------------------------------------
    # IMPORTANT:
    # Remove hallucination phrases BEFORE
    # punctuation cleaning.
    #
    # This preserves phrases containing apostrophes.
    # -------------------------------------------------

    text = remove_hallucination_phrases(
        text
    )

    # -------------------------------------------------
    # Remove hallucination words
    # -------------------------------------------------

    text = remove_hallucinations(
        text
    )

    # -------------------------------------------------
    # Remove fillers
    # -------------------------------------------------

    text = remove_fillers(
        text
    )

    # -------------------------------------------------
    # Remove punctuation / symbols
    # -------------------------------------------------

    text = clean_punctuation(
        text
    )

    # -------------------------------------------------
    # Remove extremely long tokens
    # -------------------------------------------------

    text = remove_long_tokens(
        text
    )

    # -------------------------------------------------
    # Normalize spaces
    # -------------------------------------------------

    text = normalize_spaces(
        text
    )

    # -------------------------------------------------
    # IMPORTANT:
    # Do NOT remove repeated words or phrases here.
    #
    # Repetition is an important NLP feature in this FYP.
    # -------------------------------------------------

    return text