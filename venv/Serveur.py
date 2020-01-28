from flask import Flask, escape, request
from aws import S3

# Importer le package.

from mon_super_analyseur import Analyze

app = Flask(_name_)

@app.route('/')
def hello():
    name = request.args.get("name", "World")
    return f'Hello, {escape(name)}!'

@app.route('/upload')
def upload():
    photo = request.args.get("photo.jpg") #photo.jpg par exemple
    user_id = request.args.get("user_id")
    # Upload la photo sur S3.
    photo_url = S3.upload_photo(photo)
    # Écrire l'URL en base de données.
    database.query("INSERT INTO photos (user_id, url) VALUES {user_id}, {photo_url}") # SQL
    database.write({ "photo_url": photo_url, "user_id": user_id }) # NoSQL
    # Récupérer les metadonnées.
    metadata = Analyze.analyze_photo(photo)
    # Écrire les métadonnées en base de données.
    database.query("UPDATE photos SET metadata = {metadata} WHERE photo_url = {photo_url}") # SQL
    database.update({ "photo_url": photo_url, "user_id": user_id, "metadata": metadata }) # NoSQL
    return 'OK'