import base64
import io
import re

import dill as pickle
from matplotlib import pyplot as plt

from redis_util import get_coffee_roasters, get_coffee_reviews_from_cache, cache, \
    get_unmodified_coffee_reviews_from_file
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF
from sklearn.metrics import pairwise_distances


def trainNMFModel(redis):
    redis.delete('nmf_model')
    redis.delete('nmf_features')
    redis.delete('nmf_components')

    tfIdf_trained = tfIdf_for_blind_reviews(redis)['trained']

    num_Of_feature_group = 11

    nmf = NMF(n_components=num_Of_feature_group)

    # fit the model to the tfIdf
    H = nmf.fit_transform(tfIdf_trained)
    W = nmf.components_

    cache(redis, 'nmf_features', pickle.dumps(H))
    cache(redis, 'nmf_model', pickle.dumps(nmf))
    cache(redis, 'nmf_components', pickle.dumps(W))

def tfIdf_for_blind_reviews(redis):
    # load blind assessment part of the coffee reviews
    blind_reviews = get_coffee_reviews_from_cache(redis)

    from nltk.corpus import stopwords
    sw = stopwords.words("english")
    sw = sw + ['coffee', 'coffees', 'cup', 'john', 'diruocco', 'jen', 'apodaca', 'ken', 'kevin', 'keurig', 'espresso',
               'serve', 'capsule', 'device', 'serving', 'flavor', 'notes', 'mouthfeel', 'aroma', 'finish', 'brewed',
               'brewing', 'parts', 'one', 'two', 'three', 'evaluate', 'evaluated', 'hint']
    blind_reviews = [re.sub("[^a-zA-Z]", " ", s.lower()) for s in blind_reviews]

    # Instantiate the vectorizer class with setting
    tfIdf_vector = TfidfVectorizer(min_df=10,
                                   max_df=0.85,
                                   ngram_range=(1, 1),
                                   stop_words='english')
                                   # use_idf=True,
                                   # smooth_idf=True)

    # Train the model and transform the data
    tfIdf_trained = tfIdf_vector.fit_transform(blind_reviews)

    return {'vec': tfIdf_vector, 'trained': tfIdf_trained}


def get_feature_words():
    coffee_feature_list = ['dark', 'cocoa', 'baking',
                           'savory', 'cocoa', 'orange',
                           'grapefruit', 'fresh', 'cherry']
    return coffee_feature_list


def recommend_coffee_with_features(redis, list_of_features_requested):
    # load various data from the redis database
    coffee_roasters = get_coffee_roasters(redis)
    coffee_blind_reviews = get_coffee_reviews_from_cache(redis)
    coffee_descriptions = get_unmodified_coffee_reviews_from_file(redis)
    nmf_model = pickle.loads(redis.get('nmf_model'))
    nmf_features = pickle.loads(redis.get('nmf_features'))

    # get tfIdf vector
    tfIdf_vec = tfIdf_for_blind_reviews(redis)['vec']

    # store the notes of the coffee reviews
    coffee_descriptions = [review for review in coffee_descriptions]

    # tfIdf vector transform using the feature words as the input
    tfIdf_using_feature_words = tfIdf_vec.transform(list_of_features_requested).todense()
    nmf_using_feature_words = nmf_model.transform(tfIdf_using_feature_words)

    # compute cosine similarities between the nmf using feature words selected
    # and the original nmf feature
    similarities = pairwise_distances(nmf_using_feature_words.reshape
                                      (1, -1),
                                      nmf_features, metric='cosine')

    # sort the similarities calculated by order
    similarities = similarities.argsort()

    # get the highest 10 cosine similarities values
    top_ten_recommendations = list(similarities[0][0:5])

    recommended_coffees = []
    for rec in top_ten_recommendations:
        coffee_blind_review = ["" + coffee_blind_reviews[rec]]
        tfIdf_blind = tfIdf_vec.transform(coffee_blind_review).todense()
        nmf_tfIdf_blind = nmf_model.transform(tfIdf_blind)
        genre_dist_chart_image_bytes = create_pie_chart(nmf_tfIdf_blind.tolist()[0])
        recommended_coffees.append({"coffeeRoasterName": str(coffee_roasters[rec]),
                                    "description": coffee_descriptions[rec],
                                    "imagebytes": genre_dist_chart_image_bytes})

    return recommended_coffees


def create_image(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return data
    # return f"<img src='data:image/png;base64,{}'/>"


def create_pie_chart(stats):
    feature_words = ['dark', 'cocoa', 'baking',
                     'espresso', 'sweet', 'grapefruit',
                     'almond', 'lemon', 'cherry',
                     'juicy', 'apricot']
    show_label = []
    sizes = []
    for feature_num in range(len(feature_words)):
        if stats[feature_num] > 0:
            show_label.append(feature_words[feature_num])
            sizes.append(stats[feature_num])

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=show_label, autopct='%1.1f%%',
            shadow=True, startangle=90) #, textprops={'fontsize': 14})
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.tight_layout()
    # plt.show()
    return create_image(fig1)

