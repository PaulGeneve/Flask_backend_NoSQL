import pymongo
import requests
import random

from flask import Flask



def main():
    user_name = "admin"
    password = "admin1234"
    client = pymongo.MongoClient(
        f"mongodb+srv://{user_name}:{password}@cluster0.rz1pu.mongodb.net/myFirstDatabase?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE")
    db = client.mangaDB
    manga_collection = db.mangas
    categorie_collection = db.categories

    # Getting elements from an API
    response = requests.get("https://kitsu.io/api/edge/manga?page[limit]=13&page[offset]=1200").json()["data"]

    # Doing a loop to push them in our database
    """
        for i in range(0,13):
        chapter_count = int
        rating = float
        if response[i]["attributes"]["averageRating"] != None:
            rating = round(float(response[i]["attributes"]["averageRating"]) / 20, 2)
        else:
            rating = round(random.uniform(0.0, 5.0), 2)
        if response[i]["attributes"]["chapterCount"] != None:
            chapter_count = int(response[i]["attributes"]["chapterCount"])
        else:
            chapter_count = random.randrange(50, 200)
        manga = {
            "_id": int(response[i]["id"]),
            "name": response[i]["attributes"]["titles"]["en_jp"],
            "creation_date": response[i]["attributes"]["startDate"],
            "popular_rate": rating,
            "number_chapter": chapter_count,
            "genres": "Furyo"
        }
        mangaCollection.insert_one(manga)
    """

    # Adding documents to the differents categories
    """
    categorieList =  [
        {
            "_id": 1,
            "name": "Shonen"
        },
        {
            "_id": 2,
            "name": "Seinen"
        },
        {
            "_id": 3,
            "name": "Josei"
        },
        {
            "_id": 4,
            "name": "Furyo"
        },
    ]
    categorieCollection.insert_many(categorieList)
    """


app = Flask(__name__)


@app.route("/mangas", methods=["POST"])
def created_mangas():
    """
    Add mangas in database
    Args :
        "id" : Number,
        "name" : String,
        "creation_date" : String,
        "popular_rate" : Float,
        "number_chapter" : String,
    :return:
        Status 200:
            {
                message : Manga has been succesfully added
            }
        mangas: [
            {
                "id": Number,
                "name": String,
                "creation_date": String,
                "popular_rate": Float,
                "number_chapter": String,
            }
        ]
    error gestion:
        Status 400:
            {
                error_code: 400,
                message: Not the right method
            }
        Status 404:
            {
                error_code: 409,
                message : A file with the same "id" already exist
    """



if __name__ == "__main__":
    main()
