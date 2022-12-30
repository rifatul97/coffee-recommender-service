import re

from nltk import TweetTokenizer, SnowballStemmer

from file_reader import get_stop_words


def tokenizer(text):
    tweet_tokenizer = TweetTokenizer()
    tokens = tweet_tokenizer.tokenize(text)
    return tokens


def clean_blind_reviews(blind_reviews):
    # removes the punctuations and numeric values and lowercase for each reviews
    blind_reviews_cleaned = [re.sub("[^a-zA-Z]", " ", s.lower()) for s in blind_reviews]

    return blind_reviews_cleaned


def process_text(text):
    text = tokenizer(text)
    text = [t.lower() for t in text]
    text = [re.sub('[0-9]+', '', t) for t in text]
    text = [SnowballStemmer('english').stem(t) for t in text]
    text = [t for t in text if len(t) > 1]
    text = [t for t in text if ' ' not in t]
    text = [t for t in text if t not in get_stop_words()]
    return text
