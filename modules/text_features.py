import nltk
from nltk.tokenize import sent_tokenize, word_tokenize

nltk.download('punkt')

def compute_sentence_complexity(text):
    sentences = sent_tokenize(text)

    if len(sentences) == 0:
        return 0

    avg_length = sum(len(word_tokenize(s)) for s in sentences) / len(sentences)
    return avg_length