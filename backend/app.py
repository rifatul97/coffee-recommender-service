from flask import Flask, request

from nmf import computeFeatureModelling, recommend_coffee_with_features
import redis
from redis_util import get_redis_url, readCoffeeReviewData
from visualizations import visualize_feature_words, visualize_number_of_feature
from nmf import get_feature_words

app = Flask(__name__)
r = redis.from_url(get_redis_url())


@app.route('/', methods=['GET'])
def home():
    return ""


@app.route('/get_features', methods=['GET'])
def get_features():
    return get_feature_words(r)


@app.route('/get_recommendations', methods=['GET'])
def get_recommendation():
    features_requested = request.args.to_dict()
    features = []
    for arg in features_requested.values():
        features.append(arg + " ")

    return recommend_coffee_with_features(r, features)


@app.route('/visualize_number_of_features', methods=['GET'])
def get_num_of_features_visualization():
    return visualize_number_of_feature(r)


@app.route('/get_features/visualize', methods=['GET'])
def display_feature_words_visualization():
    return visualize_feature_words(r)


if __name__ == '__main__':
    readCoffeeReviewData(r)
    computeFeatureModelling(r)
    app.run()
