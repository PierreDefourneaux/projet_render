from flask import Flask
from flask import render_template, request, redirect, url_for, jsonify

from dotenv import load_dotenv
import os

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

load_dotenv() # je mise sur le fait que render recrée un fichier .env pour y lire ces variables
USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')
HOST = os.getenv('HOST')
CLUSTER = os.getenv('CLUSTER')

# uri = "mongodb+srv://pierredefourneaux:1LU4eHCPR5No2zC8@cluster0.we1k0.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
uri = f"mongodb+srv://{USER}:{PASSWORD}@{HOST}/?retryWrites=true&w=majority&appName={CLUSTER}"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)



#from joblib import dump, load

app = Flask(__name__)

# Page d'accueil
@app.route("/", methods=["GET"])
def index():
    print("Page d'accueil chargé")
    return render_template("index.html")

# Page de résultat
@app.route("/result", methods=["GET", "POST"])
def result():

    if request.method == "POST":
        phrase = request.form.get("label_phrase")

        prediction = "prédiction ..."

        return render_template("result.html", phrase_on_page=phrase, prediction_on_page=prediction)
        
    elif request.method == "GET":
        
        phrase = request.args.get("phrase")

        prediction = "prediction ..."
        return jsonify({"text": "Toutjours la même chose", "prediction":prediction})
    
    else:
        return redirect(url_for("index"))


if __name__ == '__main__':
    app.run(debug=True)