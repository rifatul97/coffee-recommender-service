import re

from nltk import TweetTokenizer, SnowballStemmer


def tokenizer(text):
    tweet_tokenizer = TweetTokenizer()
    tokens = tweet_tokenizer.tokenize(text)
    return tokens


def process_text(text):
    text = tokenizer(text)
    text = [t.lower() for t in text]
    text = [re.sub('[0-9]+', '', t) for t in text]
    text = [SnowballStemmer('english').stem(t) for t in text]
    text = [t for t in text if len(t) > 1]
    text = [t for t in text if ' ' not in t]
    return text
