from dotenv import find_dotenv, load_dotenv
from transformers import pipeline
from langchain import PromptTemplate, LLMChain, OpenAI
from langchain.chat_models import ChatOpenAI
from huggingchat import HuggingChatScraperBot
from moviepy.editor import *
from pydub import AudioSegment
from PIL import Image
import numpy as np
import requests
import tempfile
import os
import io


load_dotenv(find_dotenv())
HUGGINFACEHUB_API_TOKEN = os.getenv("HUGGINFACEHUB_API_TOKEN")

class ImageToStory:
    def __init__(self):
        self.scenario = []
        self.story = ""
        self.prompt = ""

    def driver(self, img_url, export_url="export", export_name="video"):
        # Calll a Directory Handler
        # self.directory_handler(export_url)

        # Image Scenario Captioning
        self.scenario = [self.img2text_blip(img_url), self.img2text_coco(img_url)]
        print(self.scenario)

        # Building the prompt
        self.prompt = """
        You are a story teller.
        Please generate a short story based on a simple narrative, the story should not be more than 140 words.

        Following are given two separate contexts, choose either one or maybe both to construct a perfect story.

        CONTEXT 1: {}
        CONTEXT 2: {}
        STORY:
        """.format(self.scenario[0],self.scenario[1])

        # Passing to LLM for Story Generation from given Scenario
        self.story = self.generate_story(self.prompt)

        # Story to Speech Synthesis
        audio_mp3_bytes = self.text2speech(self.story)        

        # Compile all of it into a movie clip
        return self.convert2movie(img_url, audio_mp3_bytes, export_url, export_name)

    def directory_handler(self, folder_path):
        # Check if the folder exists
        if os.path.exists(folder_path):
            # If it exists, delete it
            try:
                os.rmdir(folder_path)  # Remove the folder (only works if it's empty)
            except OSError:
                # If the folder is not empty, remove it with all its contents
                import shutil
                shutil.rmtree(folder_path)
            print(f"Deleted existing folder: {folder_path}")

        # Create a new folder
        try:
            os.makedirs(folder_path)
            print(f"Created new folder: {folder_path}")
        except OSError:
            print(f"Failed to create the folder: {folder_path}")
    
    def img2text_blip(self, img_url):
        print("Converting Image to Text [BLIP]")
        API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-base"
        headers = {"Authorization": "Bearer {}".format(HUGGINFACEHUB_API_TOKEN)}
        with open(img_url, "rb") as f:
            data = f.read()
        response = requests.post(API_URL, headers=headers, data=data)
        return response.json()[0]["generated_text"]
    
    def img2text_coco(self, img_url):
        print("Converting Image to Text [COCO]")
        API_URL = "https://api-inference.huggingface.co/models/microsoft/git-large-coco"
        headers = {"Authorization": "Bearer {}".format(HUGGINFACEHUB_API_TOKEN)}
        with open(img_url, "rb") as f:
            data = f.read()
        response = requests.post(API_URL, headers=headers, data=data)
        return response.json()[0]["generated_text"]

    # LLM
    def generate_story(self, prompt):
        i=1
        while True:
            try:
                print("Hugging Bot is Waking Up.........................")
                agent = HuggingChatScraperBot(True)
                response = agent.prosecutor(prompt=prompt)
                break
            except Exception as e:
                print("[{}]Hugging Bot [Error]:{}\n[{}]Hugging Bot [Active]: Activating Hugging Bot".format(i,str(e).split('\n')[0],i))
            i+=1

        print(response[2])
        return response[1]
    
    # Text to speech
    def text2speech(self, story):
        API_URL = "https://api-inference.huggingface.co/models/espnet/kan-bayashi_ljspeech_vits"
        headers = {"Authorization": "Bearer {}".format(HUGGINFACEHUB_API_TOKEN)}
        payloads = {
            "inputs": story
        }
        print("Converting Story to Speech..............")
        response = requests.post(API_URL, headers=headers, json=payloads)

        audio_mp3_bytes = self.convert_flac_to_mp3(response.content)

        return audio_mp3_bytes
    
    def convert_flac_to_mp3(self, audio_bytes, bitrate='128k'):
        """
        Converts audio from FLAC format to MP3 bytes format.

        Parameters:
            input_path (str): Path to the input FLAC audio file.
            output_path (str): Path to save the output MP3 audio file.
            bitrate (str): Bitrate of the output MP3 file (default: '128k').
                        You can choose from different bitrates like '64k', '128k', '192k', etc.

        Returns:
            audio_mp3.getvalue(): mp3 audio in bytes
        """
        print("Converting flac to mp3............")
        audio_flac = io.BytesIO(audio_bytes)
        audio_segment = AudioSegment.from_file(audio_flac, format="flac")

        audio_mp3 = io.BytesIO()
        audio_segment.export(audio_mp3, format="mp3", bitrate=bitrate)
        return audio_mp3.getvalue()

    def resize_image(self, image_path, target_width, target_height):
        print("Resizing the Image.............")
        with Image.open(image_path) as img:
            # Get the original dimensions
            original_width, original_height = img.size

            # Calculate the aspect ratios
            original_aspect_ratio = original_width / original_height
            target_aspect_ratio = target_width / target_height

            # Determine how to resize the image
            if original_aspect_ratio > target_aspect_ratio:
                # Fit by width
                new_width = target_width
                new_height = int(new_width / original_aspect_ratio)
            else:
                # Fit by height
                new_height = target_height
                new_width = int(new_height * original_aspect_ratio)

            # Resize the image
            resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Create a new blank image with the target dimensions
            background = Image.new('RGB', (target_width, target_height), (0, 0, 0))

            # Calculate the position to paste the resized image
            paste_x = (target_width - new_width) // 2
            paste_y = (target_height - new_height) // 2

            # Paste the resized image onto the blank image
            background.paste(resized_img, (paste_x, paste_y))

            # Convert the PIL Image to a NumPy array
            image_array = np.array(background)

            return image_array

    def convert2movie(self, image_path, audio_mp3_bytes, output_path, export_name="video"):
        print("Compiling into Movie.............")

        # Resize the image to 1080x1920
        target_width, target_height = 1080, 1920
        resized_image = self.resize_image(image_path, target_width, target_height)

        # Load the image
        image_clip = ImageClip(resized_image)

        # Load the audio
        # if (nilter := audio_path.split("."))[-1] == "flac":
        #     self.convert_flac_to_mp3(audio_path, nilter[0] + ".mp3", "320k")
        #     audio_path = nilter[0] + ".mp3"
        # Create a temporary MP3 file
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False, dir=output_path) as temp_file:
            temp_file.write(audio_mp3_bytes)
            temp_file_path = temp_file.name
        audio_clip = AudioFileClip(temp_file_path)

        # Set the duration of the video to match the audio duration
        image_clip = image_clip.set_duration(audio_clip.duration)

        # Combine the image and audio
        video_clip = image_clip.set_audio(audio_clip)

        # Write the final video to the output path
        export_video_path = output_path+"/{}.mp4".format(export_name)
        video_clip.write_videofile(export_video_path, codec='libx264', audio_codec='aac', fps=24)

        # Delete the temporary file after use
        temp_file.close()
        os.remove(temp_file_path)

        return export_video_path

    def generate_story_with_ChatGPT(self, scenario):
        template = """
        You are a story teller;
        Please generate a short story based on a simple narrative, the story should not be more than 100 words;

        CONTEXT: {scenario}
        STORY:
        """
        prompt = PromptTemplate(template=template, input_variables=["scenario"])

        story_llm = LLMChain(llm=OpenAI(model_name="gpt-3.5-turbo", temperature=1), prompt=prompt, verbose=True)

        story = story_llm.predict(scenario=scenario)

        print(story)

        return story

if __name__ == '__main__':
    agent = ImageToStory()
    agent.driver("images/test_img5.jpg")
    print("Done!")