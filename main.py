from dotenv import find_dotenv, load_dotenv
from transformers import pipeline
from langchain import PromptTemplate, LLMChain, OpenAI
from langchain.chat_models import ChatOpenAI
from huggingchat import HuggingChatScraperBot
from moviepy.editor import *
from pydub import AudioSegment
from PIL import Image
import requests
import os

load_dotenv(find_dotenv())
HUGGINFACEHUB_API_TOKEN = os.getenv("HUGGINFACEHUB_API_TOKEN")

class ImageToStory:
    def __init__(self):
        self.scenerio = []
        self.story = ""

    def driver(self, img_url, export_url="export"):
        # Calll a Directory Handler
        self.directory_handler(export_url)

        # Image Scenario Captioning
        self.scenerio = [self.img2text_blip(img_url), self.img2text_coco(img_url)]
        print(self.scenerio)

        # Passing to LLM for Story Generation from given Scenario
        self.story = self.generate_story(self.scenerio)

        # Story to Speech Synthesis
        audio_url = self.text2speech(self.story, export_url)

        # Compile all of it into a movie clip
        self.convert2movie(img_url, audio_url, export_url)

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
    def generate_story(self, scenario):
        agent = HuggingChatScraperBot(True)
        response = agent.prosecutor(scenario=scenario)
        print(response[2])
        return response[1]
    
    # Text to speech
    def text2speech(self, story, export_url):
        API_URL = "https://api-inference.huggingface.co/models/espnet/kan-bayashi_ljspeech_vits"
        headers = {"Authorization": "Bearer {}".format(HUGGINFACEHUB_API_TOKEN)}
        payloads = {
            "inputs": story
        }
        print("Converting Story to Speech..............")
        response = requests.post(API_URL, headers=headers, json=payloads)
        audio_path = export_url+'/audio.flac'
        with open(audio_path, 'wb') as file:
            file.write(response.content)
        return audio_path

    def convert2movie(self, image_path, audio_path, output_path):
        print("Compiling into Movie.............")
        # Load the image
        image_clip = ImageClip(image_path)

        # Load the audio
        if (nilter := audio_path.split("."))[-1] == "flac":
            self.convert_flac_to_mp3(audio_path, nilter[0] + ".mp3", "320k")
            audio_path = nilter[0] + ".mp3"
        audio_clip = AudioFileClip(audio_path)

        # Set the duration of the video to match the audio duration
        image_clip = image_clip.set_duration(audio_clip.duration)

        # Resize the image to 1080x1920
        target_width, target_height = 1080, 1920
        image_clip = image_clip.resize((target_width, target_height)).set_position(('center', 'center'))

        # Combine the image and audio
        video_clip = image_clip.set_audio(audio_clip)

        # Write the final video to the output path
        video_clip.write_videofile(output_path+"/video.mp4", codec='libx264', audio_codec='aac', fps=30)




    def convert_flac_to_mp3(self, input_path, output_path, bitrate='128k'):
        """
        Converts audio from FLAC format to MP3 format.

        Parameters:
            input_path (str): Path to the input FLAC audio file.
            output_path (str): Path to save the output MP3 audio file.
            bitrate (str): Bitrate of the output MP3 file (default: '128k').
                        You can choose from different bitrates like '64k', '128k', '192k', etc.

        Returns:
            None
        """
        print("Converting flac to mp3............")
        audio = AudioSegment.from_file(input_path, format="flac")
        audio.export(output_path, format="mp3", bitrate=bitrate) 

    def resize_image(image_path, output_path, target_width, target_height):
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
            resized_img = img.resize((new_width, new_height), Image.ANTIALIAS)

            # Create a new blank image with the target dimensions
            background = Image.new('RGBA', (target_width, target_height), (255, 255, 255, 0))

            # Calculate the position to paste the resized image
            paste_x = (target_width - new_width) // 2
            paste_y = (target_height - new_height) // 2

            # Paste the resized image onto the blank image
            background.paste(resized_img, (paste_x, paste_y))

            # Save the final image
            background.save(output_path)

    def generate_story_with_ChatGPT(self, scenario):
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
    agent = ImageToStory()
    agent.driver("images/test_img6.jpg")
    print("Done!")