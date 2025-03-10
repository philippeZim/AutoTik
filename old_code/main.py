from kokoro import KPipeline
from IPython.display import display, Audio
import soundfile as sf
import numpy as np

# Set up the pipeline
pipeline = KPipeline(lang_code='a')  # American English

# Your text
with open("../input.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Split text into lines (assuming each \n+ is a segment)
text_segments = [line.strip() for line in text.split('\n') if line.strip()]

# Generate audio segments and collect them
generator = pipeline(
    text, voice='af_heart',
    speed=1, split_pattern=r'\n+'
)

audio_segments = []  # List to store all audio data
audio_durations = []  # List to store duration of each segment
for i, (gs, ps, audio) in enumerate(generator):
    audio_segments.append(audio)
    # Calculate duration in seconds (audio length / sample rate)
    duration = len(audio) / 24000  # 24000 is the sample rate
    audio_durations.append(duration)
    display(Audio(data=audio, rate=24000, autoplay=(i == 0)))  # Optional: play each segment

# Concatenate all audio segments into one
full_audio = np.concatenate(audio_segments)

# Save the single audio file
sf.write('output.wav', full_audio, 24000)
print("Saved as 'output.wav'")

# Function to split text into 1-3 word chunks
def split_into_chunks(text, max_words=3):
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_words):
        chunk = ' '.join(words[i:i + max_words])
        chunks.append(chunk)
    return chunks


# Generate SRT file
def generate_srt(text_segments, audio_durations, filename="output.srt"):
    with open(filename, "w", encoding="utf-8") as srt_file:
        subtitle_index = 1
        current_time = 0  # Start time in seconds

        for text, duration in zip(text_segments, audio_durations):
            # Split each text segment into 1-3 word chunks
            chunks = split_into_chunks(text)
            chunk_duration = duration / len(chunks) if chunks else duration  # Divide duration evenly

            for chunk in chunks:
                # Format start and end times
                start_time = format_time(current_time)
                end_time = format_time(current_time + chunk_duration)

                # Write SRT entry
                srt_file.write(f"{subtitle_index}\n")
                srt_file.write(f"{start_time} --> {end_time}\n")
                srt_file.write(f"{chunk}\n\n")

                subtitle_index += 1
                current_time += chunk_duration

# Format time for SRT (HH:MM:SS,MMM)
def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

# Generate the SRT file
generate_srt(text_segments, audio_durations)
print("Generated 'output.srt' for TikTok format")