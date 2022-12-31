import json


def get_stop_words():
    file = open("stop_words", 'r')
    stop_words = []
    for line in file.readlines():
        fname = line.rstrip().split(',')
        for name in fname:
            if name != '':
                stop_words.append(name)
    return stop_words


def get_feature_words():
    file = open("feature_words_selected", 'r')
    feature_words = []
    for line in file.readlines():
        fname = line.rstrip().split(',')
        for name in fname:
            if name != '':
                feature_words.append(name)
    return feature_words


def get_unmodified_coffee_reviews_summary():
    coffee_description_list = []
    with open("coffee_reviews_details.json", 'r', encoding="cp866") as json_file:
        json_data = json.load(json_file)
        for data in json_data:
            coffee_description_list.append(data["Summary"])

    return [summary for summary in coffee_description_list]
