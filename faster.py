from faster_whisper import WhisperModel
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip


model_size = "base"
model = WhisperModel(model_size)

segments, info = model.transcribe("audio.mp3", word_timestamps=True)
segments = list(segments)  # The transcription will actually run here.
for segment in segments:
    for word in segment.words:
        print("[%.2fs -> %.2fs] %s" % (word.start, word.end, word.word))

wordlevel_info = []

for segment in segments:
    for word in segment.words:
      wordlevel_info.append({'word':word.word,'start':word.start,'end':word.end})

# Load the video file
video = VideoFileClip("test.mp4")

# Function to generate text clips
def generate_text_clip(word, start, end, video):
    txt_clip = (TextClip(word,fontsize=150,color='white', font = "Arial-Rounded-MT-Bold",stroke_width=6, stroke_color='black').set_position(("center",0.65), relative=True)
               .set_duration(end - start))

    return txt_clip.set_start(start)

# Generate a list of text clips based on timestamps
clips = [generate_text_clip(item['word'], item['start'], item['end'], video) for item in wordlevel_info]

# Overlay the text clips on the video
final_video = CompositeVideoClip([video] + clips)

finalvideoname = "final.mp4"
# Write the result to a file
final_video.write_videofile(finalvideoname, codec="libx264",audio_codec="aac")