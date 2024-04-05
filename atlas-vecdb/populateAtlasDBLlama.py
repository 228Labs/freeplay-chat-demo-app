from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bs4 import BeautifulSoup
from llama_index.readers.web import WholeSiteReader
from llama_index.core.node_parser import SentenceSplitter
from dotenv import load_dotenv
import os
import random
import json
from helperFuncs import embed_text, hash_text

load_dotenv("../.env")
# configure mongo credentials
mongo_user = os.getenv("MONGO_USER")
mongo_pass = os.getenv("MONGO_PASSWORD")
uri = f'mongodb+srv://{mongo_user}:{mongo_pass}@freeplay-content.izuvhvj.mongodb.net/?retryWrites=true&w=majority'
mongo_db_name = "freeplay-chat"
mongo_collection_name = "doc-chunks"

# create a new mongo clinet
mongoClient = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    mongoClient.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


### load url content and chunk it ###
urls = [
    "https://docs.freeplay.ai/docs", # all the docs content
    "https://freeplay.ai/blog" # all the blog content
]

all_docs = []

for url in urls:
    loader = WholeSiteReader(prefix=url, max_depth=10)
    docs = loader.load_data(url)
    # loop over each doc and add to docs dict with hash of key as doc id added to metadata
    for doc in docs:
        doc_id = hash_text(doc.text)
        doc.extra_info.update({"doc_id": doc_id})
        all_docs.append(doc)

# view 1 random doc
print(random.choice(docs))
print("\n\n")

# add each chunk to the db
for doc in docs:
    # add a tag for blogs or docs
    if "blog" in doc.extra_info['URL']:
        tag = "blog"
    else:
        tag = "docs"
    base_payload = {
        'doc_id': doc.extra_info['doc_id'],
        'link': doc.extra_info['URL'],
        'tag': tag,
        'number_times_relevant': 0
    }
    # split the text at paragraph level
    splitter = SentenceSplitter(chunk_size=1000)
    chunks = splitter.split_text(doc.text)
    for chunk in chunks:
        payload = base_payload.copy()
        payload['text'] = chunk
        payload['embedding'] = embed_text(chunk)
        print(json.dumps(payload, indent=2))
        collection = mongoClient[mongo_db_name][mongo_collection_name]
        collection.insert_one(payload)