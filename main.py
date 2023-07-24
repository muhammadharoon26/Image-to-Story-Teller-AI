from dotenv import find_dotenv, load_dotenv
from transformers import pipeline
from langchain import PromptTemplate, LLMChain, OpenAI
from langchain.chat_models import ChatOpenAI

load_dotenv(find_dotenv())

# img2text
def img2text(url):
    # Use a pipeline as a high-level helper
    image_to_text = pipeline("image-to-text", model="Salesforce/blip-image-captioning-base")
    
    text = image_to_text(url)[0]["generated_text"]

    print(text)
    return text

# LLM
def generate_story(scenario):
    template = """
    You are a story teller;
    Please generate a short story based on a simple narrative, the story should not be more than 200 words;

    CONTEXT: {scenario}
    STORY:
    """
    prompt = PromptTemplate(template=template, input_variables=["scenario"])

    story_llm = LLMChain(llm=OpenAI(model_name="gpt-3.5-turbo", temperature=1), prompt=prompt, verbose=True)

    story = story_llm.predict(scenario=scenario)

    print(story)

    return story

if __name__ == '__main__':
    # scenario = img2text("test_img3.png")
    scenario = "a gifet and a gifet"
    story = generate_story(scenario)