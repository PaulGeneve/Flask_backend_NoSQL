import pymongo
import requests

def main():
    user_name = "admin"
    password = "admin1234"
    client = pymongo.MongoClient(
        f"mongodb+srv://{user_name}:{password}@cluster0.rz1pu.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
    db = client.mangaDB
    mangaCollection = db.mangas
    categorieCollection = db.categories

    reponse = requests.get("https://kitsu.io/api/edge/manga").json()["data"]

    print(reponse[0]["relationships"]["genres"])



if __name__ == "__main__":
    main()
