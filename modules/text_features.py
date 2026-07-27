import re
import numpy as np

import nltk
import textstat

from collections import Counter

from modules.config import COMMON_EDUCATIONAL_WORDS

# =====================================================
# Text Feature Extraction (NLP)
# =====================================================
# =====================================================
# CLEAN TRANSCRIPT
# =====================================================

def clean_transcript(text):

    if not text:
        return ""

    text = text.lower()

    text = re.sub(
        r"[^a-zA-Z\s]",
        "",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()



# =====================================================
# SENTENCE COMPLEXITY
# =====================================================

def calculate_sentence_complexity(text):

    if len(text) == 0:
        return 0


    try:

        score = textstat.flesch_reading_ease(text)

    except:

        score = 0


    return float(score)



# =====================================================
# AVERAGE SENTENCE LENGTH
# =====================================================

def average_sentence_length(text):

    if len(text) == 0:
        return 0


    sentences = re.split(
        r'[.!?]+',
        text
    )


    sentences = [

        s.strip()

        for s in sentences

        if s.strip()

    ]


    words = text.split()


    if len(sentences) == 0:

        return 0


    return float(

        len(words)
        /
        len(sentences)

    )



# =====================================================
# VOCABULARY DIVERSITY
# =====================================================

def vocabulary_diversity(text):

    words = text.split()


    if len(words)==0:

        return 0


    unique_words = set(words)


    return float(

        len(unique_words)
        /
        len(words)

    )



# =====================================================
# PHRASE REPETITION
# =====================================================

def phrase_repetition(text):

    words = text.split()


    if len(words)<3:

        return 0


    phrases=[]


    for i in range(len(words)-2):

        phrase = (

            words[i]
            +" "
            +words[i+1]
            +" "
            +words[i+2]

        )

        phrases.append(phrase)



    frequency = Counter(
        phrases
    )


    repeated = sum(

        1

        for value in frequency.values()

        if value > 1

    )


    return float(

        repeated /
        len(frequency)

    )



# =====================================================
# EDUCATIONAL WORD RATIO
# =====================================================

def educational_word_ratio(text):

    words=text.split()


    if len(words)==0:

        return 0



    count=0


    for word in words:

        if word in COMMON_EDUCATIONAL_WORDS:

            count +=1



    return float(

        count /
        len(words)

    )



# =====================================================
# REWARD / ENGAGEMENT KEYWORDS
# =====================================================

def reward_keyword_frequency(text):


    keywords=[

        "again",
        "subscribe",
        "like",
        "watch",
        "fun",
        "play",
        "game",
        "wow"

    ]


    words=text.split()


    if len(words)==0:

        return 0


    count=sum(

        1

        for word in words

        if word in keywords

    )


    return float(

        count /
        len(words)

    )



# =====================================================
# MAIN FUNCTION
# =====================================================

def extract_text_features(transcript):


    transcript = clean_transcript(
        transcript
    )


    return {


        "transcript_length":

            len(transcript),


        "sentence_complexity":

            calculate_sentence_complexity(
                transcript
            ),


        "average_sentence_length":

            average_sentence_length(
                transcript
            ),


        "vocabulary_diversity":

            vocabulary_diversity(
                transcript
            ),


        "phrase_repetition":

            phrase_repetition(
                transcript
            ),


        "educational_word_ratio":

            educational_word_ratio(
                transcript
            ),


        "reward_keyword_frequency":

            reward_keyword_frequency(
                transcript
            )

    }