import os
import shutil
import subprocess
from pytubefix import YouTube

def check_ffmpeg():
    """Check if FFmpeg is installed on the system."""
    return shutil.which("ffmpeg") is not None

def merge_video_audio(video_path, audio_path, output_path):
    """Merge video and audio streams using FFmpeg."""
    cmd = [
        "ffmpeg",
        "-i", video_path,
        "-i", audio_path,
        "-c", "copy",
        "-map", "0:v:0",  # Map video from first input
        "-map", "1:a:0",  # Map audio from second input
        output_path,
        "-y"  # Overwrite output file if it exists
    ]
    subprocess.run(cmd, check=True)

def download_video(url, output_dir="."):
    """Download a YouTube video at the highest resolution available."""
    try:
        yt = YouTube(url)
        print(f"Fetching streams for: {yt.title}")

        # Prioritize adaptive streams for highest resolution
        video_stream = yt.streams.filter(adaptive=True, only_video=True).order_by('resolution').desc().first()
        audio_stream = yt.streams.filter(adaptive=True, only_audio=True).order_by('abr').desc().first()

        if not video_stream:
            print("No video streams available.")
            return

        if not audio_stream:
            print("No audio streams available, downloading video only.")
            video_path = video_stream.download(output_path=output_dir)
            print(f"Download completed! File saved as: {video_path}")
            return

        if not check_ffmpeg():
            print("Error: FFmpeg is required to merge video and audio streams.")
            print("Please install FFmpeg: https://ffmpeg.org/download.html")
            print("On Linux: 'sudo apt install ffmpeg'")
            print("On macOS: 'brew install ffmpeg'")
            return

        # Download video and audio separately
        print(f"Downloading video stream at {video_stream.resolution}")
        video_path = video_stream.download(output_path=output_dir, filename="video_temp.mp4")
        print("Downloading audio stream...")
        audio_path = audio_stream.download(output_path=output_dir, filename="audio_temp.mp3")

        # Merge the streams
        output_file = os.path.join(output_dir, f"{yt.title} - {video_stream.resolution}.mp4")
        print("Merging video and audio...")
        merge_video_audio(video_path, audio_path, output_file)

        # Clean up temporary files
        os.remove(video_path)
        os.remove(audio_path)
        print(f"Download and merge completed! File saved as: {output_file}")

    except Exception as e:
        print(f"An error occurred: {e}")




def crop_video_to_9_16(input_path: str, output_path: str = None):
    """
    Crops a 16:9 video to a 9:16 aspect ratio using FFmpeg, keeping the center.

    :param input_path: Path to the input video file.
    :param output_path: Path to save the cropped output video. If None, saves as 'cropped_<input_filename>'.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file '{input_path}' not found.")

    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_cropped{ext}"

    command = [
        "ffmpeg", "-i", input_path,
        "-vf", "crop=ih*9/16:ih:(iw-ih*9/16)/2:0",
        "-c:a", "copy",
        output_path
    ]

    try:
        subprocess.run(command, check=True)
        print(f"Cropped video saved to {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error cropping video: {e}")

    return output_path


def is_vertical(video_path: str) -> bool:
    """
    Returns True if the video is in a vertical format (height > width).

    :param video_path: Path to the video file.
    :return: Boolean indicating if the video is vertical.
    """
    command = [
        "ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
        "-of", "csv=p=0", video_path
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        width, height = map(int, result.stdout.strip().split(","))
        return width < height
    except subprocess.CalledProcessError as e:
        print(f"Error checking video dimensions: {e}")
        return False


# Example usage:
# cropped_video = crop_video_to_9_16("input.mp4")


def main():
    # Specify your YouTube URL here
    with open("../URLs/OrbitalNCG.txt", "r", encoding="utf-8") as f:
        urls = [l.rstrip() for l in f]
    for url in urls:
        output_dir = "../Videos/Minecraft"  # Current directory, you can change this to a specific path if needed
        download_video(url, output_dir)

if __name__ == "__main__":
    main()