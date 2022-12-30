import base64
import io
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np
from gensim.corpora import Dictionary
from gensim.models import CoherenceModel, Nmf
from matplotlib.figure import Figure
from pandas import pandas as pd
from wordcloud import WordCloud

from file_reader import get_feature_words
from nmf import tfIdf_for_blind_reviews
from text_utils import process_text
from redis_util import load_json_value_from_cache, load_pickle_value_from_cache


def create_image(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return data


def render_plot(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return f"<img src='data:image/png;base64,{data}'/>"


def display_frequency_chart(word_freq):
    # Generate the figure **without using pyplot**.
    fig = Figure()
    fig.set_size_inches(20, 20)
    ax = fig.subplots()

    # Plot horizontal bar graph
    word_freq.sort_values(by='count').plot.barh(x='words',
                                                y='count',
                                                ax=ax)
    # ,color="brown")
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


def visualize_feature_words():
    tfidf = tfIdf_for_blind_reviews()
    word_list = tfidf['vec'].get_feature_names_out()
    count_list = tfidf['trained'].toarray().sum(axis=0)

    cnt = Counter()
    i = 0
    for word in word_list:
        cnt[word] = count_list[i]
        i += 1

    word_freq = pd.DataFrame(cnt.most_common(100),
                             columns=['words', 'count'])
    word_freq.head()

    return create_image(display_frequency_chart(word_freq))


def visualize_feature_groups():
    tfIdf_vec = tfIdf_for_blind_reviews()['vec']
    W = load_pickle_value_from_cache('nmf_components')

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

    return create_image(fig)


def visualize_number_of_feature(start, end):
    scores = measureCoherenceScores()

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

    return create_image(fig)


def measureCoherenceScores(r):
    coffee_reviews_words = []
    for review in load_json_value_from_cache('coffee_blind_reviews'):
        coffee_reviews_words.append(process_text(review))

    dictionary = Dictionary(coffee_reviews_words)
    dictionary.filter_extremes(
        no_below=20,
        no_above=0.85,
    )

    corpus = [dictionary.doc2bow(text) for text in coffee_reviews_words]
    min_num_of_feature_group = 6
    max_num_of_feature_group = 16
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

    return {'k_values': k_values, 'coherence_scores': coherence_scores}


def visualize_user_feature_requested_count(redis, feature_words):
    counts = []
    for feature_word in feature_words:
        count = redis.get(feature_word + '_count')
        if count is None:
            count = 0
        else:
            count = int(count.decode())
        counts.append(count)

    fig, ax = plt.subplots()
    bars = ax.barh(feature_words, counts)

    ax.bar_label(bars)

    for bars in ax.containers:
        ax.bar_label(bars)

    return create_image(fig)


def create_pie_chart(stats):
    print(stats)
    feature_words = get_feature_words()
    show_label = []
    sizes = []
    for feature_num in range(len(feature_words)):
        if stats[feature_num] > 0.001:
            show_label.append(feature_words[feature_num])
            sizes.append(stats[feature_num])
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, autopct='%1.1f%%', labels=show_label,
            shadow=True, startangle=90)
    total_sizes = 0
    for size in sizes:
        total_sizes += size
    distributions = []
    for size in sizes:
        distributions.append((size * 100) / total_sizes)
    labels = [f'{l}, {s:0.1f}%' for l, s in zip(show_label, distributions)]
    plt.legend(bbox_to_anchor=(0.85, 1), loc='upper left', labels=labels)
    plt.tight_layout()
    return create_image(fig1)
