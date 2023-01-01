import json
import pickle
from pathlib import Path
import os
import redis


def get_redis_url():
    if Path('properties').exists():
        with open("properties") as f:
            read_line = [line.split("=") for line in f.readlines()]
            key_value_pair = {key.strip(): value.strip() for key, value in read_line}
            return key_value_pair['coffee_redis_key']
    else:
        url = os.environ.get('coffee_redis_key')
        return url


def get_redis():
    return redis.from_url(get_redis_url())

def get_value_from_key(key):
    return get_redis().get(key)


def checkIfValueCached(key):
    if get_redis().get(key) is None:
        return False
    return True

def checkIfValuesCached(keys):
    for key in keys:
        if get_redis().get(key) is None:
            return False
    return True


def cache(key, value):
    if checkIfValuesCached([key]) is False:
        get_redis().set(key, value)


def get_coffee_roasters_from_cache(r):
    unpacked_coffee_roasters_json = r.get('coffee_roasters_json').decode('utf-8')
    coffee_roasters = json.loads(unpacked_coffee_roasters_json)
    return coffee_roasters


def get_coffee_reviews_from_cache(r):
    unpacked_coffee_reviews_json = r.get('coffee_reviews_json').decode('utf-8')
    coffee_reviews = json.loads(unpacked_coffee_reviews_json)
    return coffee_reviews


def trackFeaturesUserSelected(feature_requested):
    r = get_redis()
    for feature in feature_requested:
        count = r.get(feature + '_count');
        if count is None:
            r.set(feature + '_count', 1)
        else:
            count = int(count.decode())
            count += 1
            r.set(feature + '_count', count)


def load_json_value_from_cache(key):
    unpacked_coffee_roasters_json = get_redis().get(key).decode('utf-8')
    loaded_json_value = json.loads(unpacked_coffee_roasters_json)
    return loaded_json_value


def load_pickle_value_from_cache(key):
    unpacked_value = get_redis().get(key)
    return pickle.loads(unpacked_value)


def readDatasetsAndCache():
    with open("coffee_reviews_details.json", 'r', encoding="cp866") as json_file:
        uncleaned_coffee_reviews = []
        coffee_roasters = []

        for data in json.load(json_file):
            coffee_roasters.append(data["Name"])
            uncleaned_coffee_reviews.append(data["BlindReview"])

        cache('coffee_blind_reviews', json.dumps(uncleaned_coffee_reviews))
        cache('coffee_roasters', json.dumps(coffee_roasters))

