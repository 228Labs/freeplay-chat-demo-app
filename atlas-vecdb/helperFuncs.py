from dotenv import load_dotenv
import os
from openai import OpenAI
import hashlib

load_dotenv("../.env")

openai_key = os.getenv("OPENAI_API_KEY")


def embed_text(text: str) -> list:
    openaiClient = OpenAI(api_key=openai_key)
    res = openaiClient.embeddings.create(
        input=text,
        model='text-embedding-ada-002'
    )
    return res.data[0].embedding


def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()