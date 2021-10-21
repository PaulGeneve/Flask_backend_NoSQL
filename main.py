import pymongo
import requests
import random
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
    if sort_arg == "name" :
        return {
            "value":sort_arg,
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
        for manga in manga_collection.find().sort(args_values["sort_right"]["value"], args_values["sort_right"]["order"]):
            list_mangas.append(manga)
    else:
        return "Erreur"

    return \
        {
            "mangas": list_mangas
        }
