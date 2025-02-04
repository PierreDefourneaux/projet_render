from flask import Flask
from flask import render_template, request, redirect, url_for, jsonify

from dotenv import load_dotenv
import os

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from joblib import dump, load

from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer

import re

import nltk
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

##################################################################################################
# Connexion Mongo pour render

load_dotenv() #render recréera un fichier .env pour y lire ces variables
USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')
HOST = os.getenv('HOST')
CLUSTER = os.getenv('CLUSTER')
uri = f"mongodb+srv://{USER}:{PASSWORD}@{HOST}/?retryWrites=true&w=majority&appName={CLUSTER}"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("""Pinged your deployment to "admin". You successfully connected to MongoDB!""")
except Exception as e:
    print(e)

#####################################################################################################
# connection mongo pour les tests en local


# from dotenv import load_dotenv
# import os
# load_dotenv()
# uri = os.getenv('URI')
# # Create a new client and connect to the server
# client = MongoClient(uri, server_api=ServerApi('1'))

# # Send a ping to confirm a successful connection
# try:
#     client.admin.command('ping')
#     print("Pinged your deployment. You successfully connected to MongoDB!")
# except Exception as e:
#     print(e)
# a= client.list_database_names()
# print("client.list_database_names() =", a)
#####################################################################################################


app = Flask(__name__)

#charger le modèle
with open("classifier.pkl", "rb") as f:
    classifier_v2 = load(f)

#Prise en charge de l'input utilsateur
def filter_alpha(tweet):
    tweet = re.sub("[^A-Za-zâàéèêëïîôç']", " ", tweet)
    tweet = re.sub(r"\s+", " ", tweet)
    return tweet

nltk.download('wordnet')
nltk.download('punkt_tab')
lemmatizer = WordNetLemmatizer()

def tokenize_and_lemmatize(tweet):
    tokens = word_tokenize(tweet)
    tokens = ' '.join(tokens)
    tokens = tokens.lower()
    tokens = lemmatizer.lemmatize(tokens)
    return tokens

def get_sentiment(tweet):
    tweet = filter_alpha(tweet)
    tweet = tokenize_and_lemmatize(tweet)
    res = classifier_v2.predict([tweet])
    a = ""
    if res[0] == "1":
        a = "Ce tweet est positif"
    else :
        a = "Ce tweet est négatif"
    return a


# Page d'accueil
@app.route("/", methods=["GET"])
def index():
    print("Page d'accueil chargée")
    return render_template("index.html")

# Page de résultat
@app.route("/result", methods=["GET", "POST"])
def result():
    if request.method == "POST":
        print("Une méthode POST vient d'être faite dans le navigateur")
        phrase = request.form.get("label_phrase")
        prediction = get_sentiment(phrase)
        return render_template("result.html", phrase_on_page=phrase, prediction_on_page=prediction)
        
    elif request.method == "GET":
        print("Une méthode GET vient d'être faite dans le navigateur")
        phrase = request.args.get("phrase")
        prediction = "prediction ..."
        return jsonify({"text": phrase, "prediction":get_sentiment(phrase)})
    
    else:
        return redirect(url_for("index"))

@app.route("/feedback", methods=["POST"])
def feedback():
    evaluation = request.form.get("feedback_button")
    phrase = request.form.get("label_phrase")
    prediction = request.form.get("label_prediction")
    mydict = {"phrase": phrase, "prediction": prediction, "control": evaluation }
    db =client["tp_mlops"]
    feedbacks = db["feedbacks"]
    x = feedbacks.insert_one(mydict)
    print("Transaction mongoDB = ",x)
    return render_template("feedback.html", 
                           evaluation_on_page=evaluation,
                           transaction_mongo=x, 
                           phrase_on_page=phrase, 
                           prediction_on_page=prediction
                           )

if __name__ == '__main__':
    app.run(debug=True)