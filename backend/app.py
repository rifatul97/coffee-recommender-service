import json

from flask import Flask, request, jsonify

from nmf import trainNMFModel, recommend_coffee_with_features
import redis
from redis_util import get_redis_url, readCoffeeReviewData
from visualizations import visualize_feature_words, visualize_number_of_feature
from nmf import get_feature_words

app = Flask(__name__)
r = redis.from_url(get_redis_url())


@app.route('/', methods=['GET'])
def home():
    routes = {}
    for r in app.url_map._rules:
        routes[r.rule] = {}
        routes[r.rule]["functionName"] = r.endpoint
        routes[r.rule]["methods"] = list(r.methods)

    routes.pop("/static/<path:filename>")

    return jsonify(routes)


@app.route('/get_features', methods=['GET'])
def get_features():
    return jsonify(get_feature_words(r))


@app.route('/get_recommendations', methods=['GET'])
def get_recommendation():
    features_requested = request.args.getlist("features")
    if len(features_requested) == 0:
        return ""
    return recommend_coffee_with_features(r, features_requested)


@app.route('/visualize_number_of_features', methods=['GET'])
def get_num_of_features_visualization():
    return visualize_number_of_feature(r)


@app.route('/get_features/visualize', methods=['GET'])
def display_feature_words_visualization():
    return visualize_feature_words(r)


if __name__ == '__main__':
    readCoffeeReviewData(r)
    trainNMFModel(r)
    app.run()
