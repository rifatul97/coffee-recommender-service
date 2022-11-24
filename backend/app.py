from flask import Flask, render_template, request
import requests
import io
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import NMF
from pandas import pandas as pd

app = Flask(__name__)
model = None
tfidfVect = None
file_url = "https://raw.githubusercontent.com/rifatul97/coffee-recommender-service/main/data/coffee_reviews_cleaned.txt"
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
    number_of_coffee_review_text = "number of coffee reviews : " + str(len(coffee_reviews))
    number_of_coffee_roaster_text = "number of coffee roasters : " + str(len(coffee_roasters))
    return number_of_coffee_roaster_text + "\n" + number_of_coffee_review_text


def readCoffeeReviewData():
    file_download = requests.get(file_url).content
    coffee_review_data = (io.StringIO(file_download.decode('utf-8')))

    for line in coffee_review_data.readlines():
        coffeeReview = line.rstrip().split(',')
        coffee_roasters.append(coffeeReview[0])
        coffee_reviews.append(coffeeReview[1])


if __name__ == '__main__':
    readCoffeeReviewData()
    app.run()
