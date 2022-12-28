import json

from flask import Flask, request, jsonify, Response
from nmf import trainNMFModel, recommend_coffee_with_features
import redis
from redis_util import get_redis_url, readDatasetsAndCache
from visualizations import visualize_feature_words, visualize_number_of_feature, visualize_feature_groups

app = Flask(__name__)
redis = redis.from_url(get_redis_url())


@app.after_request
def after_request(response: Response) -> Response:
    response.access_control_allow_origin = "*"
    return response


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
    feature_words = ['dark', 'cocoa', 'baking',
                     'espresso', 'sweet', 'grapefruit',
                     'almond', 'lemon', 'cherry',
                     'juicy', 'apricot']

    return jsonify(feature_words)


@app.route('/get_recommendations', methods=['GET'])
def get_recommendation():
    features_requested = [''.join([(feature + ' ') for feature in request.args.getlist("features")])]
    return jsonify(recommend_coffee_with_features(redis, features_requested))


@app.route('/visualize_number_of_features', methods=['GET'])
def get_num_of_features_visualization():
    start = request.args.get("from")
    end = request.args.get("to")
    if start is None or end is None:
        return jsonify("must have start and end")
    elif int(start) < 0 or int(start) > int(end):
        return jsonify("enter valid start end")

    return visualize_number_of_feature(redis, start, end)


@app.route('/visualize_feature_words_from_blind_assessment', methods=['GET'])
def display_feature_words_visualization():
    return visualize_feature_words(redis)


@app.route('/visualize_feature_groups', methods=['GET'])
def display_feature_group():
    return visualize_feature_groups(redis)


if __name__ == '__main__':
    readDatasetsAndCache(redis)
    trainNMFModel(redis)
    app.run()


