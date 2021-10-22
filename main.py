import pymongo
import requests
import random
import json
import numpy as np
import math

from flask import Flask
from flask import request

user_name = "admin"
password = "admin1234"
client = pymongo.MongoClient(
    f"mongodb+srv://{user_name}:{password}@cluster0.rz1pu.mongodb.net/myFirstDatabase?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE")
db = client.mangaDB
manga_collection = db.mangas
category_collection = db.categories

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
categoryList =  [
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
category_collection.insert_many(categoryList)
"""


def check_args():
    """
    Check wich parameters are present in the URL
    :return:
        A dict of parameters with a key if they are present and a key with their values
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
        "page": {
            "active": False,
            "value": None
        },
    }
    # For all parameters, check wich are in the request
    for arg in args:
        if request.args.get(f"{arg}") != None:
            args[f"{arg}"]["active"] = True
            args[f"{arg}"]["value"] = request.args.get(f"{arg}")

    return args


def check_args_value(args):
    """
    Check if the values of parameters are rights
    :param args: dict of arguments with their values and if they are active
    :return:
        A dict with the parameter that are right
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
        "page_right": {
            "value": None,
            "order": 0
        }
    }
    # If sort is active, check if the value is right
    if args["sort"]["active"]:
        sort_right = check_sort_arg(args["sort"]["value"])
        args_value["sort_right"] = sort_right
    # If name is active, check if the value is right
    if args["name"]["active"]:
        name_right = check_name_arg(args["name"]["value"])
        args_value["name_right"] = name_right
    # If year is active, check if the value is right
    if args["year"]["active"]:
        year_right = check_year_arg(args["year"]["value"])
        args_value["year_right"] = year_right
    # If rating is active, check if the value is right
    if args["rating"]["active"]:
        rating_right = check_rating_arg(args["rating"]["value"])
        args_value["rating_right"] = rating_right
    # If pagging is active, check if the value is right
    if args["page"]["active"]:
        page_right = check_page_arg(args["page"]["value"])
        args_value["page_right"] = page_right
    return args_value


def check_sort_arg(sort_arg):
    """
    Fonction to check if the value of sort argument is right
    :param sort_arg: Value of of the sort argument
    :return:
        The value if right or False
    """
    # Check if the parameter value is existing and if he is ascending or descending
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
            "order": 0
        }


def check_name_arg(name_arg):
    """
    Fonction to check if the value of name argument is a string
    :param sort_arg: Value of of the sort argument
    :return:
        The value if right or False
    """
    # Check if the parameter is not a number
    digit = []
    digit.append(any(c.isdigit() for c in name_arg))
    if digit == [False]:
        return {
            "value": name_arg,
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
    # Check if the parameter is a number
    if year_arg.isnumeric():
        return {
            "value": year_arg,
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
    # Check if the parameter is a number an if it is between 0 and 5
    if rating_arg.isnumeric() and float(rating_arg) <= 5 and float(rating_arg) >= 0 and len(rating_arg) == 1:
        return {
            "value": rating_arg,
            "order": 1
        }
    else:
        return {
            "value": False,
            "order": 0
        }


def check_page_arg(page_arg):
    """
    Fonction to check if the value of pagging argument is a number
    :param sort_arg: Value of of the sort argument
    :return:
        The value if right or False
    """
    # Check if the parameter is a number > 0 and < to the length of the data collection
    if page_arg.isnumeric() and int(page_arg) > 0 and int(page_arg) <= int(math.ceil(manga_collection.count() / 10)):
        return {
            "value": page_arg,
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
    :error gestion:
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
    page = 1
    args = check_args()
    args_values = check_args_value(args)
    # Check if sort is write and then add with the sort parameter
    if args_values["sort_right"]["value"] != None and args_values["sort_right"]["value"] != False:
        for manga in manga_collection.find().sort(args_values["sort_right"]["value"],
                                                  args_values["sort_right"]["order"]):
            list_mangas.append(manga)
    # Check if the name is write and then add with the filter
    elif args_values["name_right"]["value"] != None and args_values["name_right"]["value"] != False:
        for manga in manga_collection.find({"name": {"$regex": f"{args_values['name_right']['value']}"}}):
            list_mangas.append(manga)
    # Check if the year is write and then add with the filter
    elif args_values["year_right"]["value"] != None and args_values["year_right"]["value"] != False:
        for manga in manga_collection.find({"creation_date": {"$regex": f"{args_values['year_right']['value']}"}}):
            list_mangas.append(manga)
    # Check if the rating is write and then add with the filter
    elif args_values["rating_right"]["value"] != None and args_values["rating_right"]["value"] != False:
        for manga in manga_collection.find():
            if args_values["rating_right"]["value"] in str(manga["popular_rate"])[0]:
                list_mangas.append(manga)
    else:
        for manga in manga_collection.find():
            list_mangas.append(manga)

    # Check if the pagging is write and then add with the things
    if args_values["page_right"]["value"] != None and args_values["page_right"]["value"] != False:
        page = int(args_values["page_right"]["value"])

    list_mangas_print = np.array(list_mangas)
    if list_mangas == []:
        return "There is no mangas in this collection"
    else:
        return \
            {
                "mangas": list_mangas_print[0 + ((page - 1) * 10):page * 10].tolist()
            }


@app.route("/mangas", methods=["POST"])
def create_mangas():
    """
    Add mangas in database
    :args:
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

    :error gestion:
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

    # Check if the Id we are trying to create does not already exist
    for verify_id in db.mangas.find({}, {"_id": 1}):

        # If the Id we are trying to create already exist, the variable changes to True
        if verify_id["_id"] == manga["_id"]:
            existing_id = True

    # If the variable is True then he return an error message else we had the new Id in our Collection with an succes message
    if existing_id:
        return "A manga with this ID already exists"
    else:
        manga_collection.insert_one(manga)
        return "The manga has been successfully added"


@app.route(f"/mangas/<id>", methods=["DELETE"])
def delete_manga(id):
    """
    Delete manga in the data base manga

    :returns:
        status 200: "the manga is delete",
        manga[
            {
                "id": number
            }
        ]

    :error gestion:
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
        return f"the method use is not good"


@app.route("/mangas/category/<genre>", methods=["GET"])
def display_mangas_by_category(genre):
    """
        Display all the mangas in one category from the database
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
    page = 1
    args = check_args()
    args_values = check_args_value(args)

    category_exist = False

    # Search in all the category that exist in our collection
    for category in category_collection.find({}, {"name": 1}):

        # Check if one of these category is equal to one asked and if yes, our variable changes to true
        if category["name"] == genre:
            category_exist = True

    # If the variable is true then we enter in other loop else we return an error message
    if category_exist == True:
        # Search the manga in our collections where genre is equal to the genre asked, we fill a list with these genre and we return the list to show them
        # Check if sort is write and then add with the sort parameter
        if args_values["sort_right"]["value"] != None and args_values["sort_right"]["value"] != False:
            for manga in manga_collection.find({"genres": {"$eq": genre}}).sort(args_values["sort_right"]["value"],
                                                      args_values["sort_right"]["order"]):
                list_mangas.append(manga)
        # Check if the name is write and then add with the filter
        elif args_values["name_right"]["value"] != None and args_values["name_right"]["value"] != False:
            for manga in manga_collection.find({"name": {"$regex": f"{args_values['name_right']['value']}"}, "genres": {"$eq": genre}}):
                list_mangas.append(manga)
        # Check if the year is write and then add with the filter
        elif args_values["year_right"]["value"] != None and args_values["year_right"]["value"] != False:
            for manga in manga_collection.find({"creation_date": {"$regex": f"{args_values['year_right']['value']}"}, "genres": {"$eq": genre}}):
                list_mangas.append(manga)
        # Check if the rating is write and then add with the filter
        elif args_values["rating_right"]["value"] != None and args_values["rating_right"]["value"] != False:
            for manga in manga_collection.find({"genres": {"$eq": genre}}):
                if args_values["rating_right"]["value"] in str(manga["popular_rate"])[0]:
                    list_mangas.append(manga)
        else:
            for manga in manga_collection.find({"genres": {"$eq": genre}}):
                list_mangas.append(manga)

        # Check if the pagging is write and then add with the things
        if args_values["page_right"]["value"] != None and args_values["page_right"]["value"] != False:
            page = int(args_values["page_right"]["value"])

        list_mangas_print = np.array(list_mangas)
        return \
            {
                "mangas": list_mangas_print[0 + ((page - 1) * 10):page * 10].tolist()
            }
    else:
        return "This category does not exist"

    return f"the method use is not good",


@app.route("/mangas/<id>", methods=["PATCH"])
def modify_manga(id):
    """ Modify the information of a manga
        :args:
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
        :error gestion:
            Status 404: {
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
    # if the request method is PATCH
    if request.method == "PATCH":
        # if the requested id is found
        if manga_collection.find({"id": f"{id_select}"}):
            # return a json with the new values of a manga
            manga = json.loads(request.data.decode("utf-8"))
            # compare the modifications with existing values
            if manga != manga_collection:
                manga_name = manga["name"]
                manga_create_date = manga["creation_date"]
                manga_popular_rate = manga["popular_rate"]
                manga_number_chapter = manga["number_chapter"]
                manga_genres = manga["genres"]
                # update the database with the new values using the update_one() method
                # The first parameter is a query object defining which document to update : id
                # The second parameter is an object defining the new values of the document : new values
                manga_collection.update_one({"_id": id_select}, {
                    "$set": {"name": manga_name, "creation_date": manga_create_date, "popular_rate": manga_popular_rate,
                             "number_chapter": manga_number_chapter, "genres": manga_genres}})

                # status 200  with message
                return f"Le manga avec l'id {id_select} a bien été modifié"
            else:
                # status 404 with message
                return f"Le manga avec l'id {id_select} n'existe pas"
        else:
            # status 400 with message
            return f"La méthode n'est pas bonne"


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
    :error gestion:
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
    if category_collection.find():
        for categories in category_collection.find():
            list_categories.append(categories)
    else:
        return "error"
    return \
        {
            "categories": list_categories
        }
