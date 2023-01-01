from flask import Flask, request, jsonify, Response
import base64
from file_reader import get_feature_words
from nmf import trainNMFModel, recommend_coffee_with_features, create_coffee_feature_distribution_chart
from redis_util import readDatasetsAndCache, trackFeaturesUserSelected, checkIfValueCached, load_json_value_from_cache, cache, get_value_from_key
from visualizations import visualize_feature_words, visualize_number_of_feature, visualize_feature_groups, \
    visualize_user_feature_requested_count

app = Flask(__name__)


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


@app.route('/get_coffee_roasters', methods=['GET'])
def get_coffee_roasters():
    return jsonify(load_json_value_from_cache('coffee_roasters'))


@app.route('/get_features', methods=['GET'])
def get_features():
    feature_words = get_feature_words()
    return jsonify(feature_words)


@app.route('/get_recommendations', methods=['GET'])
def get_recommendation():
    features_requested = [''.join([(feature + ' ') for feature in request.args.getlist("features")])]
    trackFeaturesUserSelected(request.args.getlist("features"))
    return jsonify(recommend_coffee_with_features(features_requested))


@app.route('/get_features/users/count', methods=['GET'])
def get_user_feature_requested_counts_visual():
    return jsonify(visualize_user_feature_requested_count(get_feature_words()))


@app.route('/get_coffee_roaster_feature_distribution', methods=['GET'])
def get_coffee_roaster_data_by_id():
    coffee_id_selected = request.args.get("coffee_id")
    return jsonify(create_coffee_feature_distribution_chart(coffee_id_selected))


if __name__ == '__main__':
    readDatasetsAndCache()
    trainNMFModel()
    app.run()
