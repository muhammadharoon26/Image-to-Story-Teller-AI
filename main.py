from dotenv import find_dotenv, load_dotenv
from transformers import pipeline

load_dotenv(find_dotenv())

# img2text
def img2text(url):
    # Use a pipeline as a high-level helper
    image_to_text = pipeline("image-to-text", model="Salesforce/blip-image-captioning-base")\
    
    text = image_to_text(url)[0]["generated_text"]

    print(text)
    return text

# LLM

# Text to Speech