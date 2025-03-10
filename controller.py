from model import generate_audio_and_titles, generate_video

story_path = "Stories/1.txt"

with open(story_path, "r", encoding="utf-8") as f:
    story_text = f.read()

generate_audio_and_titles(story_text)

generate_video()