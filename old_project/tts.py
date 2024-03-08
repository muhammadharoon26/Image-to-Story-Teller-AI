from gradio_client import Client

client = Client("https://collabora-whisperspeech.hf.space/--replicas/dx2sx/")
result = client.predict(
    "Amidst the vibrant city of Karachi, an extraordinary event was about to unfold. Joe Biden, the President of the United States, had arrived at a local comedy stage show, ready to unleash his unexpected comedic prowess. With the charisma of a seasoned comedian, Biden effortlessly commanded the stage.",	# str  in 'Enter multilingual text💬📝' Textbox component
    None,	# filepath  in 'Upload or Record Speaker Audio (optional)🌬💬' Audio component
    "https://english.voiceoversamples.com/ENG_UK_M_TonyH.mp3",	# str  in 'alternatively, you can paste in an audio file URL:' Textbox component
    15,	# float (numeric value between 10 and 15) in 'Tempo (in characters per second)' Slider component
    api_name="/whisper_speech_demo"
)
print(result)
from IPython.display import Audio
Audio(filename=result)
