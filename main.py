import pymongo
import requests
import random
import json

from flask import Flask
from flask import request

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
    manga_collection.insert_one(manga)
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
categorie_collection.insert_many(categorieList)
"""

def check_args():
    """
    Check wich arguments are present in the URL
    :return:
        A dict of arguments with a key if they are present and a key with their values
    """
    args = {
        "sort": {
            "active": False,
            "value": None
        },
        "name": {
            "active": False,
            "value": None
        },
        "year": {
            "active": False,
            "value": None
        },
        "rating": {
            "active": False,
            "value": None
        },
        "pagging": {
            "active": False,
            "value": None
        },
    }
    for arg in args:
        if request.args.get(f"{arg}") != None:
            args[f"{arg}"]["active"] = True
            args[f"{arg}"]["value"] = request.args.get(f"{arg}")

    return args

def check_args_value(args):
    """
    Check if the values of arguments are rights
    :param args: dict of arguments with their values and if they are active
    :return:
        A dict with the arguments that are right
    """
    args_value = {
        "sort_right": {
            "value": None,
            "order": 0
        },
        "name_right": {
            "value": None,
            "order": 0
        },
        "year_right": {
            "value": None,
            "order": 0
        },
        "rating_right": {
            "value": None,
            "order": 0
        },
        "pagging_right": {
            "value": None,
            "order": 0
        }
    }
    if args["sort"]["active"]:
        sort_right = check_sort_arg(args["sort"]["value"])
        args_value["sort_right"] = sort_right
    return args_value

def check_sort_arg(sort_arg):
    """
    Fonction to check if the value of sort argument is right
    :param sort_arg: Value of of the sort argument
    :return:
        The value if right or False
    """
    if sort_arg == "name":
        return {
            "value": sort_arg,
            "order": 1
        }
    elif sort_arg == "date":
        return {
            "value": "creation_date",
            "order": 1
        }
    elif sort_arg == "rating":
        return {
            "value": "popular_rate",
            "order": 1
        }
    elif sort_arg == "-name":
        return {
            "value": sort_arg,
            "order": -1
        }
    elif sort_arg == "-date":
        return {
            "value": "creation_date",
            "order": -1
        }
    elif sort_arg == "-rating":
        return {
            "value": "popular_rate",
            "order": -1
        }
    else:
        return {
            "value": False,
            "order": -1
        }


app = Flask(__name__)


@app.route("/mangas", methods=["GET"])
def display_all_mangas():
    """
    Display all the mangas from the database
    Args:
        "?order=":
            alphabet(+/-),
            date(+/-),
            popularity(+/-)
        "?sort=":
            name,
            year,
            popularity,
        "?paging=":
            Number
    :return:
        Status 200,
        mangas: [
            {
                "id": Number,
                "name": String,
                "creation_date": String,
                "popular_rate": Float,
                "number_chapter": Number,
                "genres": String,
            } ...
        ]
    error gestion:
        Status 404:
            {
                error_code: 404,
                message: No mangas founded.
            }
        Status 405:
            {
                error_code: 405,,
                message: Not the right method maybe try another one.
            }
    """
    list_mangas = []
    args = check_args()
    args_values = check_args_value(args)
    print(args_values)
    if args_values["sort_right"]["value"] != None and args_values["sort_right"]["value"] != False:
        for manga in manga_collection.find().sort(args_values["sort_right"]["value"],
                                                  args_values["sort_right"]["order"]):
            list_mangas.append(manga)
    else:
        return "Erreur"

    return \
        {
            "mangas": list_mangas
        }

@app.route("/mangas", methods=["POST"])
def create_mangas():
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
                message : Manga has been successfully added
            }

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

    manga = json.loads(request.data.decode("utf-8"))
    existing_id = False
    for verify_id in db.mangas.find({}, {"_id": 1}):
        if verify_id["_id"] == manga["_id"]:
            existing_id = True

    if existing_id:
        return "A manga with this ID already exists"
    else:
        manga_collection.insert_one(manga)
        return "The manga has been successfully added"

@app.route(f"/mangas/<id>", methods=["DELETE"])
def delete_manga_list(id):
    """
    Delete manga in the data base manga

    Returns:
        status 200: "the manga is delete",
        manga[
            {
                "id": number
            }
        ]

    :Error gestion:
        Status 404:
            {
                error_code: 404,
                message: "id manga is not valid"
            }
        Status 400:
            {
                error_code: 400,
                message: "Not the right method maybe try another one"
            },
    """

    print("old list")
    for i in manga_collection.find()[:5]:
        print(i)

    id_select = int(id)

    if requests.method == "DELETE":
        if manga_collection.find({"id": f"{id_select}"}):

            manga_collection.delete_one({'_id': id_select})
            print("new list")

            for i in manga_collection.find()[:5]:
                print(i)

            return f"le manga avec l'id {id_select} a été supprimé"
        else:
            return f"le manga avec l'id {id_select} n'existe pas"
    else:
        return f"the method use is not good",

@app.route("/mangas/categorie/", methods=["GET"])
def display_all_category():
    """
    Display all categoie's mangas from the database

    :return:
        Status 200,
        categoies: [
            {
                "name": String,
            } ...
        ]
    error gestion:
        Status 404:
            {
                error_code: 404,
                message: No categories founded.
            }
        Status 405:
            {
                error_code: 405,,
                message: Not the right method maybe try another one.
            }
    """


    list_categories = []
    if categorie_collection.find():
        for categories in categorie_collection.find():
            list_categories.append(categories)
    else:
        return "error"
    return \
        {
            "categories": list_categories
        }

@app.route("/mangas/<id>", methods=["PATCH"])
def modify_manga(id):
    """ Modify the information of a manga
        args
            id: number,
            name: string,
            category: string,
            creation_date: string,
            popular_rate: number,
            number_chapter: number,
        :return:
                status 200:
        {
            message: "Le manga avec l'id {id} a bien été modifié"
        },
                mangas: [
            {
                "id": Number,
                "name": String,
                "creation_date": String,
                "popular_rate": Float,
                "number_chapter": Number,
                "genres": String,
            },
        error gestion:
                    {
                error_code: 404,
                message: "Le manga avec l'id {id} n'existe pas".
            }
        Status 400:
            {
                error_code: 400,
                message: "La méthode n'est pas bonne".
            }

    """

    id_select = int(id)

    if request.method == "PATCH":
        if manga_collection.find({"id": f"{id_select}"}):
            manga = json.loads(request.data.decode("utf-8"))
            if manga != manga_collection:
                manga_name = manga["name"]
                manga_create_date = manga["creation_date"]
                manga_popular_rate = manga["popular_rate"]
                manga_number_chapter = manga["number_chapter"]
                manga_genres = manga["genres"]
                manga_collection.update_one({"_id": id_select}, {"$set": {"name": manga_name, "creation_date": manga_create_date, "popular_rate": manga_popular_rate, "number_chapter": manga_number_chapter, "genres": manga_genres}})

                return f"Le manga avec l'id {id_select} a bien été modifié"
            else:
                return f"Le manga avec l'id {id_select} n'existe pas"
        else:
            return f"La méthode n'est pas bonne"