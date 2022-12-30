import dill as pickle
from sklearn.feature_extraction import text

from visualizations import create_pie_chart
from file_reader import get_unmodified_coffee_reviews_summary, get_stop_words
from text_utils import clean_blind_reviews
from redis_util import cache, load_json_value_from_cache, load_pickle_value_from_cache

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF
from sklearn.metrics import pairwise_distances


def trainNMFModel():
    # obtained the trained tfIdf value
    tfIdf_trained = tfIdf_for_blind_reviews()['trained']

    num_Of_feature_group = 9

    nmf = NMF(n_components=num_Of_feature_group)

    # fit the model to the tfIdf
    H = nmf.fit_transform(tfIdf_trained)
    W = nmf.components_

    cache('nmf_features', pickle.dumps(H))
    cache('nmf_model', pickle.dumps(nmf))
    cache('nmf_components', pickle.dumps(W))


def tfIdf_for_blind_reviews():
    # load blind assessment part of the coffee reviews from cache
    blind_reviews = load_json_value_from_cache('coffee_blind_reviews')

    # call function to remove the punctuations and numeric values
    # and lowercase for each reviews
    blind_reviews_cleaned = clean_blind_reviews(blind_reviews)

    # default stop words list from the sklearn library
    stop_words = text.ENGLISH_STOP_WORDS;

    # some stop words findings added to the default stop words list
    my_stop_words = stop_words.union(get_stop_words())

    # Instantiate the vectorizer class with setting
    tfIdf_vector = TfidfVectorizer(min_df=20,
                                   max_df=0.25,
                                   ngram_range=(1, 1),
                                   stop_words=my_stop_words,
                                   use_idf=True,
                                   smooth_idf=True)

    # Train the model and transform the data
    tfIdf_trained = tfIdf_vector.fit_transform(blind_reviews_cleaned)

    return {'vec': tfIdf_vector, 'trained': tfIdf_trained}


def recommend_coffee_with_features(list_of_features_requested):
    # load various data from the redis database
    coffee_roasters = load_json_value_from_cache('coffee_roasters')
    coffee_blind_reviews = load_json_value_from_cache('coffee_blind_reviews')
    nmf_model = load_pickle_value_from_cache('nmf_model')
    nmf_features = load_pickle_value_from_cache('nmf_features')

    # get tfIdf vector
    tfIdf_vec = tfIdf_for_blind_reviews()['vec']

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

    # get the highest 5 cosine similarities values
    top_five_recommendations = list(similarities[0][0:5])

    # store the notes section of the unmodified coffee reviews
    coffee_summaries = get_unmodified_coffee_reviews_summary()

    # stores additional information for each recommended items
    recommended_coffees = []
    for rec in top_five_recommendations:
        coffee_blind_review = ["" + coffee_blind_reviews[rec]]
        tfIdf_blind = tfIdf_vec.transform(coffee_blind_review).todense()
        nmf_tfIdf_blind = nmf_model.transform(tfIdf_blind)
        genre_dist_chart_image_bytes = create_pie_chart(nmf_tfIdf_blind.tolist()[0])
        recommended_coffees.append({"coffeeRoasterName": str(coffee_roasters[rec]),
                                    "description": coffee_summaries[rec],
                                    "imagebytes": genre_dist_chart_image_bytes})

    return recommended_coffees


def create_coffee_feature_distribution_chart(coffee_id):
    tfIdf_vec = tfIdf_for_blind_reviews()['vec']
    coffee_roaster = load_json_value_from_cache('coffee_roasters')[int(coffee_id) - 1]
    unmodified_coffee_review = load_json_value_from_cache('coffee_blind_reviews')[int(coffee_id) - 1]
    nmf_model = load_pickle_value_from_cache('nmf_model')

    print("coffee roaster selected = " + coffee_roaster)

    tfIdf_blind = tfIdf_vec.transform(clean_blind_reviews(["" + unmodified_coffee_review])).todense()
    nmf_tfIdf_blind = nmf_model.transform(tfIdf_blind)
    genre_dist_chart_image_bytes = create_pie_chart(nmf_tfIdf_blind.tolist()[0])

    return {"coffeeRoasterName": str(coffee_roaster),
            "description": unmodified_coffee_review,
            "imagebytes": genre_dist_chart_image_bytes}

