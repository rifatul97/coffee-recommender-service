import json
from pathlib import Path

import requests

import os
import io

file_url = "https://raw.githubusercontent.com/rifatul97/coffee-recommender-service/main/data/coffee_reviews_cleaned.txt"


def checkIfValuesCached(redis, keys):
    for key in keys:
        if redis.get(key) is None:
            return False
    return True


def cache(r, key, value):
    r.set(key, value)


def get_redis_url():
    if Path('properties').exists():
        with open("properties") as f:
            read_line = [line.split("=") for line in f.readlines()]
            key_value_pair = {key.strip(): value.strip() for key, value in read_line}
            return key_value_pair['coffee_redis_key']
    else:
        url = os.environ.get('coffee_redis_key')
        return url


def get_coffee_roasters(r):
    unpacked_coffee_roasters_json = r.get('coffee_roasters_json').decode('utf-8')
    coffee_roasters = json.loads(unpacked_coffee_roasters_json)
    return coffee_roasters


def get_coffee_reviews_from_cache(r):
    unpacked_coffee_reviews_json = r.get('coffee_reviews_json').decode('utf-8')
    coffee_reviews = json.loads(unpacked_coffee_reviews_json)
    return coffee_reviews


def get_unmodified_coffee_reviews_from_file(r):
    coffee_description_list = []
    # coffee_link = []
    with open("coffee_reviews_details.json", 'r', encoding="cp866") as json_file:
        json_data = json.load(json_file)
        for data in json_data:
            coffee_description_list.append(data["Summary"])

    # base_url = "https://www.coffeereview.com/review/"
    # with open("coffee_reviews_titles.json", 'r', encoding="cp866") as json_file:
    #     json_data = json.load(json_file)
    #     for data in json_data:
    #         coffee_description_list.append(base_url + data["slug"])

    return coffee_description_list


def readDatasetsAndCache(redis):
    redis.delete('coffee_reviews_json')
    redis.delete('coffee_roasters_json')
    cleaned_coffee_reviews = []
    coffee_roasters = []

    with open("coffee_reviews_details.json", 'r', encoding="cp866") as json_file:
        json_data = json.load(json_file)
        print(len(json_data))
        for data in json_data:
            coffee_roasters.append(data["Name"])
            cleaned_coffee_reviews.append(data["BlindReview"])

        cache(redis, 'coffee_reviews_json', json.dumps(cleaned_coffee_reviews))
        cache(redis, 'coffee_roasters_json', json.dumps(coffee_roasters))