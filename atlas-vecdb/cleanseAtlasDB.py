from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os

load_dotenv("../.env")
# configure mongo credentials
mongo_user = os.getenv("MONGO_USER")
mongo_pass = os.getenv("MONGO_PASSWORD")
uri = f'mongodb+srv://{mongo_user}:{mongo_pass}@freeplay-content.izuvhvj.mongodb.net/?retryWrites=true&w=majority'
mongo_db_name = "freeplay-chat"
mongo_collection_name = "doc-chunks"

# loop over docs in mongo collection and delete each one at a time
mongoClient = MongoClient(uri, server_api=ServerApi('1'))
collection = mongoClient[mongo_db_name][mongo_collection_name]
iter_ = 0
for doc in collection.find():
    # leave a couple docs behind to not break the index
    if iter_ > 330:
        break
    print(f"deleting doc {iter_}")
    collection.delete_one({"_id": doc["_id"]})
    iter_ += 1
