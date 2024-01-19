import google.generativeai as genai
import google.ai.generativelanguage as glm
from chromadb import Documents, EmbeddingFunction, Embeddings
import chromadb
import numpy as np
import pandas as pd
import pathlib
import textwrap
from dotenv import load_dotenv, find_dotenv

# Setting up environment variables stored in .env file
load_dotenv(find_dotenv())
genai.configure()

class GeminiEmbeddingFunction(EmbeddingFunction):
    def __call__(self, input: Documents) -> Embeddings:
        model = 'models/embedding-001'
        title = "Custom query"
        return genai.embed_content(model=model,
                                    content=input,
                                    task_type="retrieval_document",
                                    title=title)["embedding"]

class GeminiChatbot:
    def __init__(self) -> None:
        self.model = genai.GenerativeModel('gemini-pro')
        self.chat = self.model.start_chat(history=[])
        self.ch_client = chromadb.PersistentClient(path="Vectordb/")
        self.db = self.ch_client.get_collection(name="lululemon_products_database", embedding_function=GeminiEmbeddingFunction())

    def get_relevant_document(self, query):
        # passage = db.query(query_texts=[query], n_results=3)['documents'][0][0]
        passage = self.db.query(query_texts=[query], n_results=3)['documents'][0]
        return passage
    
    def make_prompt(self, query, relevant_passage):
        # escaped = relevant_passage.replace("'", "").replace('"', "").replace("\n", " ")
        prompt = ("""
        You are a Lululemon Product Recomendation Chatbot on Lululemon's Website and you will recommend products using text from the reference passage included below. \
        Your job is to help customers make purchase decisions for products at Lululemon's website. \
        PASSAGE will constantly give product recomendations but it's your duty to only recommend the product when needed. \
        You must first ask the customer their gender and then recommend the product depending on their interests and tastes. \
        Product recommendations must include the details like product's title, colors available, price, and a URL link to the product page. \
        Make the responses concise, engaging, and interesting. \
        Only fetch the product information from reference passage, if no relative information is found then simply say "Currently Lululemon does not have such products in the inventory".
        Donot overwhelm the customer with alot of recommendations. \
        QUESTION: '{query}'
        PASSAGE: '{relevant_passage}'

            ANSWER:
        """).format(query=query, relevant_passage=relevant_passage)


        return prompt

    def send_message(self, querry, verbose=False):
        ref_doc = self.get_relevant_document(querry)
        ref_doc_prompt = ""
        for i in ref_doc:
            ref_doc_prompt += str(i).replace("\\n","")
            print(ref_doc_prompt)
        prompt = self.make_prompt(querry, ref_doc_prompt)
        if verbose == True:
            print(prompt)
        return self.chat.send_message(prompt)
    
    def chatbot(self):
        response = self.send_message("Who are you?", verbose=True)
        print("Gemini: ", response.text)
        while True:
            user_q = input("You: ")
            if user_q == "quit":
                break
            response = self.send_message(user_q, verbose=True)
            print("Gemini: ", response.text)

        print("-------------------------------------------")
        print(self.chat.history)
    



if __name__ == '__main__':
    chatbot = GeminiChatbot()
    chatbot.chatbot()