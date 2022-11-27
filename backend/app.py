import os

from flask import Flask, render_template, request, jsonify
from pathlib import Path
import requests
import io
import json
import redis
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import NMF
from pandas import pandas as pd


def get_redis_url():
    if Path('properties').exists():
        with open("properties") as f:
            read_line = [line.split("=") for line in f.readlines()]
            key_value_pair = {key.strip(): value.strip() for key, value in read_line}
            return key_value_pair['coffee_redis_key']
    else:
        url = os.environ.get('coffee_redis_key')
        return url


app = Flask(__name__)
r = redis.from_url(get_redis_url())
model = None
tfidfVect = None
file_url = "https://raw.githubusercontent.com/rifatul97/coffee-recommender-service/main/data/coffee_reviews_cleaned.txt"


@app.route('/')
def home():
    return "welcome to coffee recommender service"


@app.route('/get_recommend_for', methods=['GET'])
def recommend():
    bar = request.args.to_dict()
    args = []
    for arg in bar.values():
        print(arg)
        args.append(arg + " ")

    return ''.join(map(str, args))


@app.route('/get_number_of_coffee_reviews', methods=['GET'])
def get_number_of_coffee_reviews():
    unpacked_json = r.get('coffee_reviews_json').decode('utf-8')
    unpacked_json_len = len(unpacked_json)
    print(unpacked_json[unpacked_json_len-1])
    load_unpacked_json = json.loads(unpacked_json)

    number_of_coffee_review_text = {"number_of_coffee_reviews" : str(len(load_unpacked_json))}

    return number_of_coffee_review_text


def readCoffeeReviewData():
    get_coffee_review_cache = r.get('coffee_reviews_json').decode('utf-8');
    if len(get_coffee_review_cache) == 0:
        coffee_reviews = []
        coffee_roaster = []
        file_download = requests.get(file_url).content
        coffee_review_data = (io.StringIO(file_download.decode('utf-8')))
        for line in coffee_review_data.readlines():
            coffeeReview = line.rstrip().split(',')
            coffee_review = coffeeReview[1].strip()
            coffee_reviews.append(coffee_review)

        r.append('coffee_reviews_json', json.dumps(coffee_reviews))


if __name__ == '__main__':
    readCoffeeReviewData()
    app.run()
