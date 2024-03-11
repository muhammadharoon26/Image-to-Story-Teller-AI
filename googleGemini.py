import google.generativeai as genai
# import google.ai.generativelanguage as glm
from gradio_client import Client
import moviepy.editor as moviepy
import moviepy.video.fx.all as vfx
import moviepy.audio.fx.all as afx
from faster_whisper import WhisperModel
import cv2
import numpy as np
import time
import json
import os
import requests
import io
import uuid
from PIL import Image
import shutil
from dotenv import load_dotenv, find_dotenv
import threading
import subprocess




# Setting up environment variables stored in .env file
load_dotenv(find_dotenv())
# genai.configure(api_key='AIzaSyCL_VqhF0rFuVDpfFWZtaSDH9-j8WmmV6w')
genai.configure()
HUGGINFACEHUB_API_TOKEN = os.getenv("HUGGINFACEHUB_API_TOKEN")
CLIENT_FOLDER = "client/"

class GeminiProductions:
    def __init__(self) -> None:
        # gemini configs
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
        self.story_prompt = "You are a Story Teller. You will be given a context and your job will be to generate a story that should be creative, humourous, engaging, interesting and it should have epic plot twists.\nCONTEXT:\n"
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
      "narrator_script": "A concise script that narrator will narrate to explain this scene. It should be detailed and should have the aspect of story telling. It should be coherent with the previous and next scene's narrations.",
      "scene_details": "Comma-separated tags that visualizes each and every detail of this scene. Also contains story context leading to this scene in detail.",
      "note": "Director's or writer's note about this scene."
    },
    {
      "scene_number": 2,
      "location": "EXT. PARK - DAY",
      "description": "Description of the setting and what happens in the scene.",
      "narrator_script": "A concise script that narrator will narrate to explain this scene. It should be detailed and should have the aspect of story telling. It should be coherent with the previous and next scene's narrations.",
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
        print("[Producer] Screenwriting Scenes Are Beautiful!\n")

        scene_artist_thread = threading.Thread(target=self.scene_artist)
        scene_narrator_thread = threading.Thread(target=self.scene_narrator)

        print("[Producer] Invoking Scene Artist To Create Scenes.....")
        scene_artist_thread.start()
        print("[Producer] Generated Scenes Are Beautiful!\n")

        print("[Producer] Invoking Scene Narrator To Narrate Scenes.....")
        scene_narrator_thread.start()
        print("[Producer] Narrator Narrated Scenes Beautifully!\n")

        scene_artist_thread.join()
        scene_narrator_thread.join()

        print("[Producer] Invoking Video Editor To Edit The Video..........")
        self.video_editor()
        print("[Producer] Wow! The Video Editor Is Very Efficient!\n")

        print("[Producer] Invoking Video Transcriber............")
        self.video_transcriber()
        print("[Producer] Wow! The Video Transcriber Is Very Efficient!\n")

        print("[Producer] Invoking Sound Engineer............")
        self.sound_engineer()
        print("[Producer] Wow! The Sound Engineer Is Very Efficient!\n")

    def sound_engineer(self):
        try:
            print("[Sound-Engineer] Engineering Sounds...")
            directory = self.dir_manager(CLIENT_FOLDER + self.production["id"] + "/")
            input_video_path = directory + "transcribed.mp4"
            output_video_path = directory + "spedup.mp4"
            final_output_video_path = directory + "final.mp4"
            background_audio_path = "bgm_library/dvrst_close_eyes.mp3"

            self.change_video_speed(input_video_path, output_video_path, 1.2)

            print("[Sound-Engineer] Adding Background Rythms!")
            my_clip = moviepy.VideoFileClip(output_video_path)
            audio_background = moviepy.AudioFileClip(background_audio_path)
            audio_background = audio_background.set_duration(my_clip.duration)
            audio_background = audio_background.fx(afx.volumex, 0.2)
            final_audio = moviepy.CompositeAudioClip([my_clip.audio, audio_background])
            final_clip = my_clip.set_audio(final_audio)
            final_clip.write_videofile(final_output_video_path, codec="libx264", audio_codec="aac")

            print("[Sound-Engineer] Sound Engineered Successfully!")
            print("[Sound-Engineer] Saved At:", output_video_path)
        except Exception as e:
            print("[Sound-Engineer][Error]:{}".format(str(e).split('\n')[0]))

    def video_transcriber(self):
        try:
            print("[Video-Transcriber] Compiling Source Files...")
            directory = self.dir_manager(CLIENT_FOLDER + self.production["id"] + "/")
            input_video_path = directory + "untranscribed.mp4"
            input_audio_path = directory + "untranscribed.mp3"
            output_video_path = directory + "transcribed.mp4"
            wordlevel_info = []

            model_size = "base"
            model = WhisperModel(model_size)

            segments, info = model.transcribe(input_audio_path, word_timestamps=True)
            segments = list(segments)  # The transcription will actually run here.

            for segment in segments:
                for word in segment.words:
                    wordlevel_info.append({'word':word.word,'start':word.start,'end':word.end})

            # Load the video file
            video = moviepy.VideoFileClip(input_video_path)

            # Generate a list of text clips based on timestamps
            clips = [self.generate_text_clip(item['word'], item['start'], item['end']) for item in wordlevel_info]

            # Overlay the text clips on the video
            final_video = moviepy.CompositeVideoClip([video] + clips)

            # Write the result to a file
            final_video.write_videofile(output_video_path, codec="libx264",audio_codec="aac")

            print("[Video-Transcriber] Video Transcribed Successfully!")
            print("[Video-Transcriber] Saved At:", output_video_path)
        except Exception as e:
            print("[Video-Transcriber][Error]:{}".format(str(e).split('\n')[0]))

    def video_editor(self):
        output_resolution = (1080, 1920)
        try:
            print("[Video-Editor] Compiling Source Files...")
            directory = self.dir_manager(CLIENT_FOLDER + self.production["id"] + "/")
            png_files = [file for file in os.listdir(directory) if file.endswith(".png")]
            final_clips = []

            for png_file in png_files:
                image_path = os.path.join(directory, png_file)
                audio_file = os.path.join(directory, os.path.splitext(png_file)[0] + ".wav")

                image = cv2.imread(image_path)
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB format

                # Resize the original image to 1080x1080
                image_resized = cv2.resize(image, (1080, 1080))

                # Blur the image
                blurred_img = cv2.GaussianBlur(image, (0, 0), 30)
                blurred_img = cv2.resize(blurred_img, output_resolution)

                # Overlay the original image on the blurred one
                y_offset = (output_resolution[1] - 1080) // 2
                blurred_img[y_offset:y_offset+1080, :] = image_resized

                # video_clip = moviepy.ImageClip(image)
                video_clip = moviepy.ImageClip(np.array(blurred_img))
                audio_clip = moviepy.AudioFileClip(audio_file)
                final_clip = video_clip.set_duration(audio_clip.duration).set_audio(audio_clip)
                final_clips.append(final_clip)

            print("[Video-Editor] Rendering Video...")
            combined_video_clip = moviepy.concatenate_videoclips(final_clips, method="compose")
            combined_video_clip.write_videofile((directory + "untranscribed.mp4"), codec="libx264", audio_codec="aac", fps=24)
            # Load the video clip
            video_clip = moviepy.VideoFileClip((directory + "untranscribed.mp4"))
            video_clip.audio.write_audiofile(directory + "untranscribed.mp3")
            video_clip.close()
            audio_clip.close()
            print("[Video-Editor] Video Rendered Successfully!")
            print("[Video-Editor] Saved At:", directory + "untranscribed.mp4")
        except Exception as e:
            print("[Video-Editor][Error]:{}".format(str(e).split('\n')[0]))

    def scene_narrator(self):
        while True:
            try:
                directory = self.dir_manager(CLIENT_FOLDER + self.production["id"] + "/")
                client = Client("https://collabora-whisperspeech.hf.space/",output_dir=directory)
                
                for i, scene in enumerate(self.production["screenwriting_json"]["screenplay"], 1):
                    narrator_script = scene["narrator_script"]
                    result = client.predict(
                        narrator_script,
                        None,
                        "https://english.voiceoversamples.com/ENG_UK_M_TonyH.mp3",
                        15,
                        api_name="/whisper_speech_demo"
                    )
                    audio_path = directory + f"{i}.wav"
                    self.save_audio_content(result, audio_path)
                    print("[Scene-Narrator][Scene {}/{}] Narration Generated Successfully".format(i,len(self.production["screenwriting_json"]["screenplay"])))

                # delete redundant folders and cleanup
                for item in os.listdir(directory):
                    item_path = os.path.join(directory, item)
                    # Check if the current item is a directory
                    if os.path.isdir(item_path):
                        # Remove the directory and its contents
                        shutil.rmtree(item_path)
                return
            except Exception as e:
                print("[Scene-Narrator][Retrying...][Error]:{}".format(str(e).split('\n')[0]))

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
                print("[Scene-Artist] All Scenes Generated Successfully!")
                return
            except Exception as e:
                print("[Scene-Artist][Retrying...][Error]:{}".format(str(e).split('\n')[0]))

    def screenwriter(self):
        while True:
            try:
                directory = self.dir_manager(CLIENT_FOLDER+self.production["id"]+"/")
                self.production["screenwriter_prompt"] = self.screenwriter_prompt + self.production["generated_story"]
                print("Screenwriter's Prompt:\n",self.production["screenwriter_prompt"])
                print()
                self.production["generated_screenwriting"] = self.model.generate_content(self.production["screenwriter_prompt"]).text
                self.production["screenwriting_json"] = json.loads(self.production["generated_screenwriting"])
                self.save_json(self.production["screenwriting_json"], directory+"screenwriting.json")
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

    def change_video_speed(self, input_file, output_file, speed_factor):
        try:
            # Prepare the command
            command = [
                'ffmpeg',
                '-i', input_file,
                '-filter_complex', f"[0:v]setpts={1/speed_factor}*PTS[v];[0:a]atempo={speed_factor}[a]",
                '-map', '[v]', '-map', '[a]',
                output_file
            ]
            
            # Execute the command
            subprocess.run(command, check=True)
            print(f"Successfully changed the speed of {input_file} by a factor of {speed_factor}.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to change the video speed due to an error: {e}")

    def generate_text_clip(self, word, start, end):
        '''Function to generate text clips'''
        txt_clip = (moviepy.TextClip(word,fontsize=150,color='white', font = "Arial-Rounded-MT-Bold",stroke_width=6, stroke_color='black').set_position(("center",0.65), relative=True)
               .set_duration(end - start))
        return txt_clip.set_start(start)

    def save_audio_content(self, result, audio_path):
        if os.path.isfile(result):
            # If result is a local file path, copy the file
            try:
                shutil.copy(result, audio_path)
                # print(f"Audio file copied to {audio_path}")
            except Exception as e:
                print(f"Failed to copy audio file: {e}")
        else:
            print(f"Unexpected audio content type or path: {result}")

    def dir_manager(self, dir):
        if not os.path.exists(dir):
            os.makedirs(dir)
        return dir
    
    def save_json(self, json_obj, path):
        with open(path, 'w') as outfile:
            json.dump(json_obj, outfile, indent=4)
        

if __name__ == '__main__':
    start_time = time.time()
    # -------------------------------------------------------
    gemini = GeminiProductions()
    gemini.producer("Elon Musk pitching his new company idea on shark tank show. Very hilarious comedy while elon throws some shade on other rival billioniare. Elon discusses why he didn't visited India to attend Ambani's son marraige.")
    # -------------------------------------------------------
    print("--- %s seconds ---" % (time.time() - start_time))