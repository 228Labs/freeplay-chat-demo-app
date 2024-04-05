from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from langchain.document_loaders import RecursiveUrlLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import random
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
    loader = RecursiveUrlLoader(url=url, max_depth=10,
                                extractor=lambda x: BeautifulSoup(x, "html.parser").text)
    docs = loader.load()
    # loop over each doc and add to docs dict with hash of key as doc id added to metadata
    for doc in docs:
        doc_id = hash_text(doc.page_content)
        doc.metadata.update({"doc_id": doc_id})
        all_docs.append(doc)

# view 1 random doc
print(random.choice(docs))
print("\n\n")

# split all docs into chunks
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
chunks = splitter.split_documents(all_docs)
# view 1 random chunk
print(random.choice(chunks))
print("\n\n")
print("Number of chunks: ", len(chunks))

# add each chunk to the db
for chunk in chunks:
    # add a tag for blogs or docs
    if "blog" in chunk.metadata['source']:
        tag = "blog"
    else:
        tag = "docs"
    payload = {
        'doc_id': chunk.metadata['doc_id'],
        'title': chunk.metadata['title'],
        'link': chunk.metadata['source'],
        'description': chunk.metadata['description'],
        'text': chunk.page_content,
        'tag': tag,
        'embedding': embed_text(chunk.page_content),
        'number_times_relevant': 0
    }
    collection = mongoClient[mongo_db_name][mongo_collection_name]
    collection.insert_one(payload)

