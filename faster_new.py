import subprocess

def change_video_speed(input_file, output_file, speed_factor):
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

# Example usage
change_video_speed('test.mp4', 'speed.mp4', 1.5)  # Adjust 1.5 to your desired speed factor
