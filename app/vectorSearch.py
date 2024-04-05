from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os
import random
import json
from helperFuncs import embed_text
from pydantic import BaseModel

load_dotenv("../.env")
# configure mongo credentials
mongo_user = os.getenv("MONGO_USER")
mongo_pass = os.getenv("MONGO_PASSWORD")
uri = f'mongodb+srv://{mongo_user}:{mongo_pass}@freeplay-content.izuvhvj.mongodb.net/?retryWrites=true&w=majority'
mongo_db_name = "freeplay-chat"
mongo_collection_name = "doc-chunks"

# create a new mongo clinet
mongoClient = MongoClient(uri, server_api=ServerApi('1'))
collection = mongoClient[mongo_db_name][mongo_collection_name]

class SearchChunk(BaseModel):
    title: str
    link: str
    content: str


def vector_search(text, top_k=5, cosine_threshold=0.75, tag=["docs", "blogs"], title=None):
    # vectorsearch config
    vector_search_config = {
                'index': 'vector_index',
                'path': 'embedding',
                'queryVector': embed_text(text),
                'numCandidates': top_k * 10, # use 10 nearest neighbors for each return result, suggested in mongo docs
                'limit': top_k
    }
    if tag:
        pre_filter = {'tag': {'$in': tag}}
        vector_search_config['filter'] = pre_filter
    elif title:
        pre_filter = {'title': {'$in': [title]}}
        vector_search_config['filter'] = pre_filter
    else:
        pre_filter = None

    print("Running semantic search with the following config: ")
    print("numCandidates: ", vector_search_config['numCandidates'])
    print("limit: ", vector_search_config['limit'])
    print("filter: ", json.dumps(pre_filter, indent=2))
    print("\n\n")
    # create the search query
    pipeline = [
        {
            '$vectorSearch': vector_search_config
        },
        {
            '$project': {
                '_id': 1,
                'doc_id': 1,
                'title': 1,
                'link': 1,
                'description': 1,
                'text': 1,
                'tag': 1,
                'embedding': 1,
                'number_time_relevant': 1,
                'sim_score': {
                    '$meta': 'vectorSearchScore'
                }
            }
        }
    ]
    # run the query
    result = collection.aggregate(pipeline)
    # build the return set
    return_set = []
    for record in result:
        if record['sim_score'] < cosine_threshold:
            continue
        else:
            return_set.append(SearchChunk(title=record['title'],
                                          link=record['link'], 
                                          content=record['text']))
            # increment the releavance counter
            collection.update_one({'_id': record['_id']}, {'$inc': {'number_time_relevant': 1}})
    return return_set, pre_filter


'''
resSet, pre_filter = vector_search("How do I log customer feedback?", tag="docs")
print(resSet)
print(pre_filter)
'''
