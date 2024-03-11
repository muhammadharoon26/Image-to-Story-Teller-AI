def save_audio_content(self, result, audio_path):
        if isinstance(result, str) and result.startswith(("http://", "https://")):
            response = requests.get(result)
            if response.status_code == 200:
                with open(audio_path, "wb") as audio_file:
                    audio_file.write(response.content)
                print(f"Audio downloaded and saved to {audio_path}")
            else:
                print(f"Failed to download audio: {response.status_code}")
        else:
            print(f"Unexpected audio content type or path: {result}")