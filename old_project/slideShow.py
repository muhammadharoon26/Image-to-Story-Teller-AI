import os
from moviepy.editor import ImageSequenceClip
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip

#Image to Video
def create_slideshow_video(images_folder, output_path, fps=24):
    image_files = [f for f in os.listdir(images_folder) if f.endswith(('.jpg', '.png', '.jpeg'))]
    image_files.sort()  # Sorting to maintain order

    if not image_files:
        print("No image files found in the folder.")
        return

    image_paths = [os.path.join(images_folder, img) for img in image_files]

    # Duration of each image in seconds
    duration_per_image = 5

    clip = ImageSequenceClip(image_paths, durations=[duration_per_image] * len(image_paths))
    clip.set_duration(len(image_paths) * duration_per_image)
    clip = clip.set_fps(fps)

    # Saving the video with libx264 codec
    final_output_path = os.path.join(output_path, 'slideshow_video.mp4')
    clip.write_videofile(final_output_path, codec='libx264')

if __name__ == "__main__":
    # Replace 'input_folder_path' with the path to the folder containing images
    input_folder_path = 'C:\\Users\\Khalil Ur Rehman\\Desktop\\Image to Text\\ART'

    # Replace 'output_folder_path' with the path where you want to save the output video
    output_folder_path = 'C:\\Users\\Khalil Ur Rehman\\Desktop\\Image to Text\\ART'

    create_slideshow_video(input_folder_path, output_folder_path) 



#Adding Voice to
def add_voice_to_video(video_path, audio_path, output_path):
    # Load video and audio clips
    video_clip = VideoFileClip(video_path)
    audio_clip = AudioFileClip(audio_path)

    # Make sure the audio duration matches the video duration
    audio_clip = audio_clip.set_duration(video_clip.duration)

    # Combine video and audio
    video_with_audio = video_clip.set_audio(audio_clip)

    # Save the final video with audio
    video_with_audio.write_videofile(output_path, codec="libx264", audio_codec='aac', fps=video_clip.fps)

    # Close the video and audio clips
    video_clip.close()
    audio_clip.close()

if __name__ == "__main__":
    # Replace these file paths with your actual video and audio file paths
    video_file_path = "C:\\Users\\Khalil Ur Rehman\\Desktop\\Image to Text\\ART\\slideshow_video.mp4"
    audio_file_path = "C:\\Users\\Khalil Ur Rehman\\Desktop\\Image to Text\\Voice.mp3"
    output_video_path = "C:\\Users\\Khalil Ur Rehman\\Desktop\\Image to Text\\video.mp4"

    add_voice_to_video(video_file_path, audio_file_path, output_video_path)

