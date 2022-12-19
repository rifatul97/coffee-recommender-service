import base64
import io
import pickle
import re
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np
from gensim.corpora import Dictionary
from gensim.models import CoherenceModel, Nmf
from matplotlib.figure import Figure
from nltk import TweetTokenizer, SnowballStemmer
from pandas import pandas as pd

from redis_util import get_coffee_reviews_from_cache


def render_plot(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return f"<img src='data:image/png;base64,{data}'/>"


def visualize_feature_words(r):
    word_list = pickle.loads(r.get('tfIdf_vec')).get_feature_names_out()
    count_list = pickle.loads(r.get('tfIdf')).toarray().sum(axis=0)

    cnt = Counter()
    i = 0
    for word in word_list:
        cnt[word] = count_list[i]
        i += 1

    word_freq = pd.DataFrame(cnt.most_common(50),
                             columns=['words', 'count'])
    word_freq.head()

    # Generate the figure **without using pyplot**.
    fig = Figure()
    fig.set_size_inches(12, 12)
    ax = fig.subplots()

    # Plot horizontal bar graph
    word_freq.sort_values(by='count').plot.barh(x='words',
                                                y='count',
                                                ax=ax,
                                                color="brown")
    ax.set_title("Common Feature Words Appeared Throughout the Coffee Reviews")

    return render_plot(fig);


def casual_tokenizer(text):
    return TweetTokenizer.tokenize(text=text)


def process_text(text):
    text = casual_tokenizer(text)
    text = [t.lower() for t in text]
    text = [re.sub('[0-9]+', '', t) for t in text]
    text = [SnowballStemmer('english').stem(t) for t in text]
    text = [t for t in text if len(t) > 1]
    text = [t for t in text if ' ' not in t]
    return text


def visualize_number_of_feature(r):
    coffee_reviews_words = []
    for review in get_coffee_reviews_from_cache(r):
        coffee_reviews_words.append(process_text(review))

    dictionary = Dictionary(coffee_reviews_words)
    dictionary.filter_extremes(
        no_below=3,
        no_above=0.85,
        keep_n=5000
    )

    corpus = [dictionary.doc2bow(text) for text in coffee_reviews_words]
    min_num_of_feature_group = 6
    max_num_of_feature_group = 20
    step = 3

    # Create a list of the feature numbers I want to try
    feature_nums = list(np.arange(min_num_of_feature_group, max_num_of_feature_group, step))

    # Run the nmf model and calculate the coherence score for each number of topics
    k_values = []
    coherence_scores = []
    i = min_num_of_feature_group

    for num in feature_nums:
        nmf = Nmf(
            corpus=corpus,
            num_topics=num,
            id2word=dictionary,
            chunksize=2000,
            passes=5,
            kappa=.1,
            minimum_probability=0.01,
            w_max_iter=300,
            w_stop_condition=0.0001,
            h_max_iter=100,
            h_stop_condition=0.001,
            eval_every=10,
            normalize=True,
            random_state=42
        )

        # Run the coherence model to get the score
        cm = CoherenceModel(
            model=nmf,
            texts=coffee_reviews_words,
            dictionary=dictionary,
            coherence='c_v'
        )

        coherence_scores.append(round(cm.get_coherence(), 5))
        k_values.append(i)
        i += 1

    fig = plt.figure(figsize=(15, 10))
    ax = plt.plot(k_values, coherence_scores)
    plt.xticks(k_values)
    plt.xlabel("Number of Topics")
    plt.ylabel("Mean Coherence")
    # add the points
    plt.scatter(k_values, coherence_scores, s=120)
    # find and annotate the maximum point on the plot
    ymax = max(coherence_scores)

    xpos = coherence_scores.index(ymax)
    best_k = k_values[xpos]
    plt.annotate("k=%d" % best_k, xy=(best_k, ymax), xytext=(best_k, ymax),
                 textcoords="offset points", fontsize=18)

    return render_plot(fig)
