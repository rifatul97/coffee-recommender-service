from flask import Flask, request, jsonify, Response

from file_reader import get_feature_words
from nmf import trainNMFModel, recommend_coffee_with_features, create_coffee_feature_distribution_chart
from redis_util import readDatasetsAndCache, trackFeaturesUserSelected, load_json_value_from_cache
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
    return jsonify(visualize_user_feature_requested_count(get_feature_words))


@app.route('/visualize_number_of_features', methods=['GET'])
def get_num_of_features_visualization():
    start = request.args.get("from")
    end = request.args.get("to")
    if start is None or end is None:
        return jsonify("must have start and end")
    elif int(start) < 0 or int(start) > int(end):
        return jsonify("enter valid start end")

    return jsonify(visualize_number_of_feature(start, end))


@app.route('/visualize_top_feature_words_from_blind_review', methods=['GET'])
def display_feature_words_visualization():
    return jsonify(visualize_feature_words())


@app.route('/visualize_feature_groups', methods=['GET'])
def display_feature_group():
    return jsonify(visualize_feature_groups())


@app.route('/get_coffee_roaster_feature_distribution', methods=['GET'])
def get_coffee_roaster_feature_distribution_chart():
    coffee_id_selected = request.args.get("coffee_id")
    return jsonify(create_coffee_feature_distribution_chart(coffee_id_selected))


if __name__ == '__main__':
    readDatasetsAndCache()
    trainNMFModel()
    app.run()
