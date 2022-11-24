import os

from flask import Flask, render_template, request
import requests
import io
import json
from flask_caching import Cache
import redis
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import NMF
from pandas import pandas as pd

app = Flask(__name__)
r = redis.from_url(os.environ.get('coffee_redis_key'))
    # ("")
model = None
tfidfVect = None
file_url = "https://raw.githubusercontent.com/rifatul97/coffee-recommender-service/main/data/coffee_reviews_cleaned.txt"
# cache = Cache(config={"CACHE_TYPE":"RedisCache","CACHE_REDIS_HOST":"0.0.0.0", "CACHE_REDIS_PORT":6379})
# cache.init_app(app)
coffee_roasters = []
coffee_reviews = []


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
    # Read saved JSON str from Redis and unpack into python dict
    unpacked_json = json.loads(r.get('coffee_reviews_json'))

    number_of_coffee_review_text = "number of coffee reviews : " + str(len(unpacked_json))
    number_of_coffee_roaster_text = "number of coffee roasters : " + str(len(coffee_roasters))
    return number_of_coffee_roaster_text + "\n" + number_of_coffee_review_text


def readCoffeeReviewData():
    file_download = requests.get(file_url).content
    coffee_review_data = (io.StringIO(file_download.decode('utf-8')))
    index = 0
    for line in coffee_review_data.readlines():
        coffeeReview = line.rstrip().split(',')
        # coffee_roasters.append(coffeeReview[0])
        coffee_reviews.append(coffeeReview[1])

    coffee_reviews_json = json.dumps(coffee_reviews)
    r.append('coffee_reviews_json', coffee_reviews_json)
    # r.append('coffee-reviews-roasters', coffeeReview[1])


if __name__ == '__main__':
    r.delete('coffee_reviews_json')
    readCoffeeReviewData()
    app.run()
    # cache = Cache(config={"CACHE_TYPE": "RedisCache", "CACHE_REDIS_HOST": "0.0.0.0", "CACHE_REDIS_PORT": 6379})
    # cache.init_app(app)