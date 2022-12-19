import pickle

from redis_util import get_coffee_roasters, get_coffee_reviews_from_cache, cache
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF
from sklearn.metrics import pairwise_distances
from nltk.corpus import stopwords


def computeFeatureModelling(redis):
    redis.delete('get_coffee_features')
    if redis.get('get_coffee_features') is None:
        coffee_reviews = get_coffee_reviews_from_cache(redis)
        stop_words = stopwords.words('english')

        # Instantiate the vectorizer class with setting
        vec = TfidfVectorizer(min_df=20,
                              max_df=0.85,
                              ngram_range=(1, 2),
                              stop_words=stop_words,
                              use_idf=True,
                              smooth_idf=True)

        # Train the model and transform the data
        tfIdf = vec.fit_transform(coffee_reviews[0:])

        # visualize_feature_words(vec, tfIdf)

        num_Of_feature_group = 9

        nmf = NMF(n_components=num_Of_feature_group)

        # fit the model to the tfIdf
        H = nmf.fit_transform(tfIdf)
        W = nmf.components_

        cache(redis, 'tfIdf_vec', pickle.dumps(vec))
        cache(redis, 'tfIdf', pickle.dumps(tfIdf))
        cache(redis, 'nmf_features', pickle.dumps(H))
        cache(redis, 'nmf_component', pickle.dumps(W))
        cache(redis, 'nmf_model', pickle.dumps(nmf))


def recommend_coffee_with_features(redis, list_of_features_requested):
    # load from the redis database
    coffee_roasters = get_coffee_roasters(redis)
    tfIdf_vec = pickle.loads(redis.get('tfIdf_vec'))
    nmf_model = pickle.loads(redis.get('nmf_model'))
    nmf_features = pickle.loads(redis.get('nmf_features'))

    # tfIdf vector transform using the feature words as the input
    tfIdf_using_feature_words = tfIdf_vec.transform(list_of_features_requested).todense()
    nmf_using_feature_words = nmf_model.transform(tfIdf_using_feature_words)

    similarities = pairwise_distances(nmf_using_feature_words.reshape
                                      (len(list_of_features_requested), -1),
                                      nmf_features, metric='cosine').argsort()

    top_ten_coffee_recommendations = list(similarities[0][0:10])
    recommended_coffees = ""
    for rec in top_ten_coffee_recommendations:
        recommended_coffees += str(coffee_roasters[rec])
        recommended_coffees += ", "

    return recommended_coffees


def get_feature_words(r):
    # get W, tfIdf vector from the redis database
    W = pickle.loads(r.get('nmf_W'))
    tfIdfVect = pickle.loads(r.get('tfIdfVect'))

    # get the feature names from the tfIdf vector
    feature_names = tfIdfVect.get_feature_names_out()

    # convert W to panda dataframe format for iteration
    nmf_tfIdfVect_df = pd.DataFrame(W, columns=feature_names)

    # get the top feature words from each group of the model
    top_feature_words_of_each_groups = []
    for group_num in range(nmf_tfIdfVect_df.shape[0]):
        feature_words_of_the_group = nmf_tfIdfVect_df.iloc[group_num]
        top_feature_word = feature_words_of_the_group.nlargest(1)
        for feature_word, tfIdf_value in top_feature_word.iteritems():
            top_feature_words_of_each_groups.append(feature_word)

    return str(top_feature_words_of_each_groups)
