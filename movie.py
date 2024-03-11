import moviepy.editor as moviepy
import os

def video_editor():
    png_files = [file for file in os.listdir('client') if file.endswith(".png")]
    final_clips = []

    for png_file in png_files:
        image_path = os.path.join('client', png_file)
        audio_file = os.path.join('client', os.path.splitext(png_file)[0] + ".mp3")
        images = [image_path]

        for image in images:
            video_clip = moviepy.ImageClip(image)
            audio_clip = moviepy.AudioFileClip(audio_file)
            final_clip = video_clip.set_duration(audio_clip.duration).set_audio(audio_clip)
            final_clips.append(final_clip)

    combined_clips = moviepy.concatenate_videoclips(final_clips, method="compose")
    combined_clips.write_videofile("Videos/final.mp4", codec="libx264", audio_codec="aac", fps=24)

video_editor()






#    def file_manager():
#        tcount = os.listdir("./Images")
#        return tcount




#def file_manager():
#        tcount = os.listdir("./Images")
#        for count in tcount:
#            return count   


#    def audio_guy(self):
#        aud = moviepy.AudioFileClip()

# def compiler():
#         tcount = os.listdir("Videos")
#         video_clips = [moviepy.VideoFileClip("Videos/" + file) for file in tcount]
#         final_clip = moviepy.concatenate_videoclips(video_clips, method="compose")
#         final_clip.write_videofile("Videos/final.mp4", codec="libx264", audio_codec="aac")


#         for clip in video_clips:
#             clip.close()

#Editor.compiler()

# def imager():

#         png_file = [file for file in os.listdir('client') if file.endswith(".png")]
#         final = []
#         for png_file in png_file:
#             images = [png_file]
#             print(images)
#             for count in images:
#                 filenames_without_extension = [os.path.splitext(filename)[0] for filename in count]
#                 vid = moviepy.ImageClip("client/" + count)
#                 aud = moviepy.AudioFileClip("client/" + filenames_without_extension[0] + ".mp3")
#                 fnnl = vid.set_duration(aud.duration).set_audio(aud)
#                 final.append(fnnl)
#         final_clips = moviepy.concatenate_videoclips(final, method="compose")
#         final_clips.write_videofile("Videos/final.mp4", codec="libx264", audio_codec="aac", fps = 24)