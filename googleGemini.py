import google.generativeai as genai
# import google.ai.generativelanguage as glm
import time
import json
from dotenv import load_dotenv, find_dotenv

# Setting up environment variables stored in .env file
load_dotenv(find_dotenv())
genai.configure()

class GeminiProductions:
    def __init__(self) -> None:
        self.generation_config = genai.types.GenerationConfig(
            # Only one candidate for now.
            candidate_count=1,
            # stop_sequences=['x'],
            max_output_tokens=2000,
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
      "narrator_script": "A script that narrator will narrate during the scene.",
      "scene_details": "Comma-separated tags that visualizes each and every detail of this scene. Also contains story context leading to this scene in detail.",
      "note": "Director's or writer's note about this scene."
    },
    {
      "scene_number": 2,
      "location": "EXT. PARK - DAY",
      "description": "Description of the setting and what happens in the scene.",
      "narrator_script": "A script that narrator will narrate during the scene.",
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
            "story_prompt": None,
            "generated_story": None,
            "screenwriter_prompt": None,
            "generated_screenwriting": None,
            "screenwriting_json": None,
        }
        self.model = genai.GenerativeModel('gemini-pro', safety_settings=self.safety_settings, generation_config=self.generation_config)

    def producer(self, context):
        print("[Producer] Invoking Story Writer.....")
        self.generate_story(context)
        print("[Producer] Writer Wrote The Story Incredibley!")

        print("[Prodcer] Invoking Screenwriter To Create Screenwriting.....")
        self.screenwriter()
        print("\n\nScreenwriting:\n{}".format(self.production["generated_screenwriting"]))
        print("\n\nScreenwriting_JSON:\n{}".format(json.dumps(self.production["screenwriting_json"], indent=4)))
        print("[Producer] Screenwriting Scenes Are Beautiful!")

        print("[Prodcer] Invoking Scene Artist To Create Scenes.....")
        self.scene_artist()
        print("\n\nScenes:\n{}".format(self.production["generated_scenes"]))
        print("\n\nScenes_JSON:\n{}".format(json.dumps(self.production["scenes_json"], indent=4)))
        print("[Producer] Screenwriting Scenes Are Beautiful!")

    def scene_artist(self):
        self.production["scene_artist_prompt"] = self.scene_artist_prompt + self.production["generated_screenwriting"]
        print("Scene Artist's Prompt:\n",self.production["scene_artist_prompt"])
        print()
        self.production["generated_scenes"] = self.model.generate_content(self.production["scene_artist_prompt"]).text
        self.production["scenes_json"] = json.loads(self.production["generated_scenes"])
        return self.production["generated_scenes"]

    def screenwriter(self):
        self.production["screenwriter_prompt"] = self.screenwriter_prompt + self.production["generated_story"]
        print("Screenwriter's Prompt:\n",self.production["screenwriter_prompt"])
        print()
        self.production["generated_screenwriting"] = self.model.generate_content(self.production["screenwriter_prompt"]).text
        self.production["screenwriting_json"] = json.loads(self.production["generated_screenwriting"])
        return self.production["generated_screenwriting"]

    def generate_story(self, context):
        # Generates Story Based on Given Context
        self.production["story_prompt"] = self.story_prompt + context
        self.production["generated_story"] = self.model.generate_content(self.production["story_prompt"]).text
        return self.production["generated_story"]

if __name__ == '__main__':
    start_time = time.time()
    # -------------------------------------------------------
    gemini = GeminiProductions()
    gemini.producer("Two Chickens Playing Football")
    # -------------------------------------------------------
    print("--- %s seconds ---" % (time.time() - start_time))