from flask import Flask, render_template, request
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import NMF

app = Flask(__name__)


@app.route('/')
def home():
    return "welcome to nmf service"


@app.route('/get_recommend_for')
def recommend():
    args = []
    for arg in request.args.to_dict().values():
        args.append(arg + " ")

    return ''.join(map(str, args));





if __name__ == '__main__':
    app.run()