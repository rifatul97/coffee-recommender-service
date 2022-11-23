from flask import Flask, render_template, request

app = Flask(__name__)
model = None
tfidfVect = None
file_name = 'coffee_reviews_cleaned.txt'
coffee_roasters = []
coffee_reviews = []


@app.route('/')
def home():
    return "welcome to nmf service"


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
    return str(len(coffee_reviews))


def readCoffeeReviewData():
    file = open(file_name, 'r')
    for line in file.readlines():
        coffeeReview = line.rstrip().split(',')
        coffee_roasters.append(coffeeReview[0])
        coffee_reviews.append(coffeeReview[1])


if __name__ == '__main__':
    readCoffeeReviewData()
    app.run()
