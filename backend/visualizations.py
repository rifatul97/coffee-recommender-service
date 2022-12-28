import base64
import io
import pickle
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np
from gensim.corpora import Dictionary
from gensim.models import CoherenceModel, Nmf
from matplotlib.figure import Figure
from pandas import pandas as pd
from wordcloud import WordCloud

from backend.nmf import tfIdf_for_blind_reviews
from backend.text_utils import process_text
from redis_util import get_coffee_reviews_from_cache, checkIfValuesCached, cache


def render_plot(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return f"<img src='data:image/png;base64,{data}'/>"


def display_frequency_chart(word_freq):
    # Generate the figure **without using pyplot**.
    fig = Figure()
    fig.set_size_inches(30, 30)
    ax = fig.subplots()

    # Plot horizontal bar graph
    word_freq.sort_values(by='count').plot.barh(x='words',
                                                y='count',
                                                ax=ax,
                                                color="brown")
    ax.set_title("Common Feature Words Appeared Throughout the Coffee Reviews")

    return fig


def create_word_freq_df(words, counts):
    cnt = Counter()
    i = 0
    for word in words:
        cnt[word] = counts[i]
        i += 1

    return pd.DataFrame(cnt.most_common(10),
                        columns=['words', 'count'])


def visualize_feature_words(r):
    tfidf = tfIdf_for_blind_reviews(r)
    word_list = tfidf['vec'].get_feature_names_out()
    count_list = tfidf['trained'].toarray().sum(axis=0)

    cnt = Counter()
    i = 0
    for word in word_list:
        cnt[word] = count_list[i]
        i += 1

    word_freq = pd.DataFrame(cnt.most_common(200),
                             columns=['words', 'count'])
    word_freq.head()

    return render_plot(display_frequency_chart(word_freq))


def visualize_feature_groups(r):
    tfIdf = tfIdf_for_blind_reviews(r)
    W = pickle.loads(r.get('nmf_components'))

    tfIdf_vec = tfIdf['vec']
    feature_names = tfIdf_vec.get_feature_names_out()

    nmf_features_df = pd.DataFrame(W, columns=feature_names)

    top_feature_words_of_each_groups = []
    fig = plt.figure(figsize=(15, 12))
    plt.subplots_adjust(hspace=0.5)
    plt.suptitle("Feature Word Groups", fontsize=18, y=0.95)

    for group_num in range(nmf_features_df.shape[0]):
        feature_words_of_the_group = nmf_features_df.iloc[group_num]
        top_feature_word = feature_words_of_the_group.nlargest(10)
        tops = []
        counts = []
        for feature_word, tfIdf_value in top_feature_word.iteritems():
            top_feature_words_of_each_groups.append(feature_word)
            tops.append(feature_word)
            counts.append(tfIdf_value)
        df = pd.DataFrame({'word': tops,
                           'count': counts})
        data = df.set_index('word').to_dict()['count']
        plt.subplot(4, 3, group_num + 1).set_title("Group #" + str(group_num + 1))
        plt.imshow(WordCloud(margin=3, prefer_horizontal=0.7, scale=1, background_color='white',
                             relative_scaling=0).generate_from_frequencies(data))
        plt.axis("off")

    return render_plot(fig)


def visualize_number_of_feature(r, start, end):
    # if checkIfValuesCached(['k_values', 'coherence_scores']) is False:
    scores = measureCoherenceScores(r)

    k_values = scores['k_values']
    coherence_scores = scores['coherence_scores']

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


def measureCoherenceScores(r):
    coffee_reviews_words = []
    for review in get_coffee_reviews_from_cache(r):
        coffee_reviews_words.append(process_text(review))

    dictionary = Dictionary(coffee_reviews_words)
    dictionary.filter_extremes(
        no_below=20,
        no_above=0.85,
    )

    corpus = [dictionary.doc2bow(text) for text in coffee_reviews_words]
    min_num_of_feature_group = 6
    max_num_of_feature_group = 15
    step = 1

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

    return {'k_values': k_values, 'coherence_scores' : coherence_scores}
    # cache(r, 'k_values', k_values)
    # cache(r, 'coherence_scores', coherence_scores)
