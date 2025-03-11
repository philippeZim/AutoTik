from kokoro import KPipeline
from IPython.display import display, Audio
import soundfile as sf
import numpy as np


def setup_pipeline(lang_code='a'):
    """Initialize the KPipeline with the specified language code."""
    return KPipeline(lang_code=lang_code)


def read_input_file(file_path="../input.txt"):
    """Read text from the input file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def split_text_into_segments(text):
    """Split text into segments based on newlines."""
    return [line.strip() for line in text.split('\n') if line.strip()]


def generate_audio_segments(pipeline, text_segments, voice='af_heart', speed=1.25):
    """Generate audio segments from text segments using the pipeline."""
    generator = pipeline(
        '\n'.join(text_segments),
        voice=voice,
        speed=speed,
        split_pattern=r'\n+'
    )
    audio_segments = []
    audio_durations = []

    for i, (gs, ps, audio) in enumerate(generator):
        audio_segments.append(audio)
        duration = len(audio) / 24000  # 24000 is the sample rate
        audio_durations.append(duration)
        display(Audio(data=audio, rate=24000, autoplay=(i == 0)))  # Optional: play first segment

    return audio_segments, audio_durations


def save_audio_file(audio_segments, output_file='output.wav', sample_rate=24000):
    """Concatenate audio segments and save to a single file."""
    full_audio = np.concatenate(audio_segments)
    sf.write(output_file, full_audio, sample_rate)
    print(f"Saved as '{output_file}'")

def split_into_chunks(text, min_chars=10, max_words=3):
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        word_length = len(word)
        if word_length >= min_chars and current_chunk:
            if current_chunk:
                chunks.append(' '.join(current_chunk))
            chunks.append(word)
            current_chunk = []
            current_length = 0
        else:
            if len(current_chunk) < max_words and (current_length + word_length + len(current_chunk)) < min_chars:
                current_chunk.append(word)
                current_length += word_length
            else:
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_length = word_length

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    # Merge last chunk if too short, preserving order
    if chunks and len(chunks[-1]) < min_chars and len(chunks) > 1:
        second_last = chunks[-2]
        last = chunks[-1]
        chunks[-2:] = [second_last + ' ' + last]

    return chunks


# Generate SRT file
def generate_srt(text_segments, audio_durations, filename="output.srt"):
    with open(filename, "w", encoding="utf-8") as srt_file:
        subtitle_index = 1
        current_time = 0  # Start time in seconds

        for text, duration in zip(text_segments, audio_durations):
            # Split each text segment into chunks of at least 10 characters
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


def main():
    """Main function to orchestrate the audio generation process."""
    # Setup
    pipeline = setup_pipeline(lang_code='a')
    text = read_input_file("../Stories/5.txt")
    text_segments = split_text_into_segments(text)

    # Generate audio
    audio_segments, audio_durations = generate_audio_segments(pipeline, text_segments, speed=1.25)

    # Save output
    save_audio_file(audio_segments)

    return text_segments, audio_durations  # Return for potential SRT generation


if __name__ == "__main__":
    text_segments, audio_durations = main()
    # The rest of your code (split_into_chunks, generate_srt, format_time) can follow here
    generate_srt(text_segments, audio_durations)