from chat import newConvo, getCompletion
from helperFuncs import generate_random_string
import random
from dotenv import load_dotenv
import os

load_dotenv("./.env")

convoId = generate_random_string()
customer_id = "test@freeplay.ai"
session, history = newConvo(convoId=convoId, customer_id=customer_id)

questions = [
    "What is freeplay?", "How does prompt bundling work?", "What is the status of the freeplay thin sdk?",
     "Does freeplay have a public api?", "Does Freeplay support MultiModal foundation models?",
     "Give me an example of how to record a new LLM completion using Kotlin", "How do I record customer feedback?",
     "What's Freeplay good for?", "Describe Freeplay's SDK Desgin approach", "What languages does the Freeplay sdk offer?",
     "How do evaluations work in freeplay?", "How can freeplay help me optimize my LLM features?", "Do I have to fetch my prompts from the freeplay server every time?",
     "How do I get started with Freeplay?", "What are the core nouns in freeplay sdk?", "WHo is freeplay build for?",
     "Does freeplay support batch testing?", "How do I run test runs with the python sdk?", "How do I run test runs with the node sdk?",
     "How do I run test runs with the java sdk?", "How do I run test runs with the kotlin sdk?", "What is a Test Case?",
     "How do I record custom metadata?", "What is a completion?", "What is a session?", "What is a prompt template?"
]

question = random.choice(questions)

response, completion_id = getCompletion(message=question, history=history, session=session)