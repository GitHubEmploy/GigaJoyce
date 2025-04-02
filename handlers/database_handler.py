from pymongo import MongoClient

def setup_database(uri):
    client = MongoClient(uri)
    db = client["bot_database"]
    return db
