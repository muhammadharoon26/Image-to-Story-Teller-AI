import google.generativeai as genai
# import google.ai.generativelanguage as glm
import time
import json
import os
import requests
import io
import uuid
from PIL import Image
import shutil
from dotenv import load_dotenv, find_dotenv

# Setting up environment variables stored in .env file
load_dotenv(find_dotenv())
genai.configure()
HUGGINFACEHUB_API_TOKEN = os.getenv("HUGGINFACEHUB_API_TOKEN")
CLIENT_FOLDER = "client/"

class GeminiProductions:
    def __init__(self) -> None:
        self.generation_config = genai.types.GenerationConfig(
            # Only one candidate for now.
            candidate_count=1,
            # stop_sequences=['x'],
            max_output_tokens=20000,
            temperature=1.0
        )
        self.safety_settings = {
            'HARASSMENT':'block_none',
            'HATE_SPEECH':'block_none',
            'SEXUAL':'block_none',
            'DANGEROUS':'block_none',
        }
        self.story_prompt = "You are a Story Teller. You will be given a context and your job will be to generate a 200 word story. Story should be creative, humourous, engaging, interesting and it should have epic plot twists.\nCONTEXT:\n"
        self.screenwriter_prompt = """You are a movie producer. You will be given a story and your job is to convert that story into screenwriting. The screenwriting should be in JSON format and should follow the exact format as specified.
SCREENWRITING JSON FORMAT:
{
  "title": "Movie Title",
  "logline": "A brief summary of the movie's plot.",
  "screenplay": [
    {
      "scene_number": 1,
      "location": "INT. HOUSE - DAY",
      "description": "A brief description of the scene's setting and action.",
      "narrator_script": "A lenghty script that narrator will narrate during the scene. I should be detailed and should have the aspect of story-telling.",
      "scene_details": "Comma-separated tags that visualizes each and every detail of this scene. Also contains story context leading to this scene in detail.",
      "note": "Director's or writer's note about this scene."
    },
    {
      "scene_number": 2,
      "location": "EXT. PARK - DAY",
      "description": "Description of the setting and what happens in the scene.",
      "narrator_script": "A lenghty script that narrator will narrate during the scene. I should be detailed and should have the aspect of story-telling.",
      "scene_details": "Comma-separated tags that visualizes each and every detail of this scene. Also contains story context leading to this scene in detail.",
      "note": "Director's or writer's note about this scene."
    }
  ]
}

STORY:

"""
        self.scene_artist_prompt = """You are a scene artist for a movie. You will be given a screenwriting in JSON format, your job is to understand the details of each scene and describe the visuals in scenes. Your response should be in JSON format as specified.
SCENE DETAILS JSON FORMAT:
{
    1: "Comma separated tags representing scene 1",
    2: "Comma separated tags representing scene 2",
    3: "Comma separated tags representing scene 3",
}

SCREENWRITING JSON:

"""
        self.production = {
            "id": None,
            "story_prompt": None,
            "generated_story": None,
            "screenwriter_prompt": None,
            "generated_screenwriting": None,
            "screenwriting_json": None,
        }
        self.model = genai.GenerativeModel('gemini-1.0-pro-latest', safety_settings=self.safety_settings, generation_config=self.generation_config)

    def producer(self, context):
        self.production["id"] = uuid.uuid4().hex
        print("[Producer] Initiating Production:",self.production["id"])

        print("[Producer] Invoking Story Writer.....")
        self.generate_story(context)
        print("[Producer] Writer Wrote The Story Incredibley!")

        print("[Producer] Invoking Screenwriter To Create Screenwriting.....")
        self.screenwriter()
        print("\n\nScreenwriting:\n{}".format(self.production["generated_screenwriting"]))
        print("\n\nScreenwriting_JSON:\n{}".format(json.dumps(self.production["screenwriting_json"], indent=4)))
        print("[Producer] Screenwriting Scenes Are Beautiful!")

        print("[Prodcer] Invoking Scene Artist To Create Scenes.....")
        self.scene_artist()
        print("[Producer] Generated Scenes Are Beautiful!")

    def scene_artist(self):
        while True:
            try:
                API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
                headers = {"Authorization": "Bearer "+HUGGINFACEHUB_API_TOKEN}
                directory = self.dir_manager(CLIENT_FOLDER+self.production["id"]+"/")
                for i,scene in enumerate(self.production["screenwriting_json"]["screenplay"],1):
                    prompt = self.production["screenwriting_json"]["logline"] + " " + scene["description"] + " " + scene["scene_details"]
                    response = requests.post(API_URL, headers=headers, json={"inputs":prompt})
                    # You can access the image with PIL.Image for example
                    image = Image.open(io.BytesIO(response.content))
                    image.save(directory+str(i)+".png")
                    print("[Scene-Artist][Scene {}/{}] Image Generated Successfully".format(i,len(self.production["screenwriting_json"]["screenplay"])))
                self.save_json(self.production["screenwriting_json"], directory+"screenwriting.json")
                print("[Scene-Artist] All Scenes Generated Successfully!")
                return
            except Exception as e:
                print("[Scene-Artist][Retrying...][Error]:{}".format(str(e).split('\n')[0]))

    def screenwriter(self):
        while True:
            try:
                self.production["screenwriter_prompt"] = self.screenwriter_prompt + self.production["generated_story"]
                print("Screenwriter's Prompt:\n",self.production["screenwriter_prompt"])
                print()
                self.production["generated_screenwriting"] = self.model.generate_content(self.production["screenwriter_prompt"]).text
                self.production["screenwriting_json"] = json.loads(self.production["generated_screenwriting"])
                return self.production["generated_screenwriting"]
            except Exception as e:
                print("[Screenwriter][Retrying...][Error]:{}".format(str(e).split('\n')[0]))

    def generate_story(self, context):
        while True:
            try:
                # Generates Story Based on Given Context
                self.production["story_prompt"] = self.story_prompt + context
                self.production["generated_story"] = self.model.generate_content(self.production["story_prompt"]).text
                return self.production["generated_story"]
            except Exception as e:
                print("[Story-Writer][Retrying...][Error]:{}".format(str(e).split('\n')[0]))

    def dir_manager(self, dir):
        if os.path.exists(dir):
            shutil.rmtree(dir)
        os.makedirs(dir)
        return dir
    
    def save_json(self, json_obj, path):
        with open(path, 'w') as outfile:
            json.dump(json_obj, outfile, indent=4)
        

if __name__ == '__main__':
    start_time = time.time()
    # -------------------------------------------------------
    gemini = GeminiProductions()
    gemini.producer("A computer science student working on an innovaive idea hoping it to be a potential startup.")
    # -------------------------------------------------------
    print("--- %s seconds ---" % (time.time() - start_time))