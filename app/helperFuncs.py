from dotenv import load_dotenv
import os
from openai import OpenAI
import hashlib
import random
import string

load_dotenv("./.env")

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


def generate_random_string(length=10):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))
