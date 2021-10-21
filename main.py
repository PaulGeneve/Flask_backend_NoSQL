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
    if args["name"]["active"]:
        name_right = check_name_arg(args["name"]["value"])
        args_value["name_right"] = name_right
    if args["year"]["active"]:
        year_right = check_year_arg(args["year"]["value"])
        args_value["year_right"] = year_right
    if args["rating"]["active"]:
        rating_right = check_rating_arg(args["rating"]["value"])
        args_value["rating_right"] = rating_right
    if args["pagging"]["active"]:
        pagging_right = check_pagging_arg(args["pagging"]["value"])
        args_value["pagging_right"] = pagging_right
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
            "order": 0
        }

def check_name_arg(name_arg):
    """
    Fonction to check if the value of name argument is a string
    :param sort_arg: Value of of the sort argument
    :return:
        The value if right or False
    """
    digit = []
    digit.append(any(c.isdigit() for c in name_arg))
    if digit == [False]:
        return {
            "value":name_arg,
            "order": 1
        }
    else:
        return {
            "value": False,
            "order": 0
        }

def check_year_arg(year_arg):
    """
    Fonction to check if the value of year argument is a number
    :param sort_arg: Value of of the sort argument
    :return:
        The value if right or False
    """
    if year_arg.isnumeric():
        return {
            "value":year_arg,
            "order": 1
        }
    else:
        return {
            "value": False,
            "order": 0
        }

def check_rating_arg(rating_arg):
    """
    Fonction to check if the value of rating argument is a number
    :param sort_arg: Value of of the sort argument
    :return:
        The value if right or False
    """
    if rating_arg.isnumeric() and float(rating_arg) <= 5 and float(rating_arg) >= 0 and len(rating_arg) == 1:
        return {
            "value":rating_arg,
            "order": 1
        }
    else:
        return {
            "value": False,
            "order": 0
        }

def check_pagging_arg(pagging_arg):
    """
    Fonction to check if the value of pagging argument is a number
    :param sort_arg: Value of of the sort argument
    :return:
        The value if right or False
    """
    if pagging_arg.isnumeric() and int(pagging_arg) > 0 and int(pagging_arg) <= manga_collection.count() :
        return {
            "value":pagging_arg,
            "order": 1
        }
    else:
        return {
            "value": False,
            "order": 0
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
    elif args_values["name_right"]["value"] != None and args_values["name_right"]["value"] != False:
        for manga in manga_collection.find({ "name": { "$regex": f"{args_values['name_right']['value']}"} }):
            list_mangas.append(manga)
    elif args_values["year_right"]["value"] != None and args_values["year_right"]["value"] != False:
        for manga in manga_collection.find({"creation_date": {"$regex": f"{args_values['year_right']['value']}"}}):
            list_mangas.append(manga)
    elif args_values["rating_right"]["value"] != None and args_values["rating_right"]["value"] != False:
        for manga in manga_collection.find():
            if args_values["rating_right"]["value"] in str(manga["popular_rate"])[0]:
                list_mangas.append(manga)
    elif args_values["pagging_right"]["value"] != None and args_values["pagging_right"]["value"] != False:
        for i in range(0 , int(args_values["pagging_right"]["value"])):
            list_mangas.append(manga_collection.find()[i])

    return \
        {
            "mangas": list_mangas
        }
