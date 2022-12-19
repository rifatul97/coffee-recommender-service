import json
from pathlib import Path

import requests

import os
import io

file_url = "https://raw.githubusercontent.com/rifatul97/coffee-recommender-service/main/data/coffee_reviews_cleaned.txt"


def cache(r, key, value):
    r.set(key, value)
    # if r.get(key) is None:
    #     print("the key " + key + " is not stored!")
    #     r.set(key, value)
    # else:
    #     print("the key " + key + " is already stored :)")


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


def readCoffeeReviewData(r):
    # r.delete('coffee_reviews_json')
    # r.delete('coffee_roasters_json')
    #
    get_coffee_review_cache = r.get('coffee_reviews_json')  # .decode('utf-8');
    get_coffee_roaster_cache = r.get('coffee_roasters_json')  # .decode('utf-8');

    if get_coffee_review_cache is None or get_coffee_roaster_cache is None:
        coffee_reviews = []
        coffee_roasters = []
        file_download = requests.get(file_url).content
        coffee_review_data = (io.StringIO(file_download.decode('utf-8')))
        for line in coffee_review_data.readlines():
            coffeeReview = line.rstrip().split(',')
            coffee_roaster = coffeeReview[0].strip()
            coffee_review = coffeeReview[1].strip()
            coffee_reviews.append(coffee_review)
            coffee_roasters.append(coffee_roaster)

        r.append('coffee_reviews_json', json.dumps(coffee_reviews))
        r.append('coffee_roasters_json', json.dumps(coffee_roasters))
