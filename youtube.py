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
        output_path,
        "-y"  # Overwrite output file if it exists
    ]
    subprocess.run(cmd, check=True)

def download_video(url, output_dir="."):
    """Download a YouTube video at the highest resolution available."""
    try:
        yt = YouTube(url)

        # Get the highest resolution progressive stream
        stream = yt.streams.filter(progressive=True).order_by('resolution').desc().first()
        if stream:
            print(f"Downloading progressive stream: {yt.title} at {stream.resolution}")
            stream.download(output_path=output_dir)
            print("Download completed!")
        else:
            # No progressive stream found, use adaptive streams
            print("No progressive stream found. Switching to adaptive streams...")
            video_stream = yt.streams.filter(adaptive=True, only_video=True).order_by('resolution').desc().first()
            audio_stream = yt.streams.filter(adaptive=True, only_audio=True).order_by('abr').desc().first()

            if not video_stream:
                print("No video streams available.")
                return


            if not check_ffmpeg():
                print("Error: FFmpeg is required to merge video and audio streams.")
                print("Please install FFmpeg: https://ffmpeg.org/download.html")
                print("On Linux: 'sudo apt install ffmpeg'")
                print("On macOS: 'brew install ffmpeg'")
                return

            # Download video and audio separately
            print(f"Downloading video stream: {yt.title} at {video_stream.resolution}")
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

def main():
    # Specify your YouTube URL here
    url = "https://www.youtube.com/watch?v=your_video_id"  # Replace with your desired URL
    output_dir = "."  # Current directory, you can change this to a specific path if needed
    download_video(url, output_dir)

if __name__ == "__main__":
    main()