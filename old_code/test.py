import subprocess
import sys


def get_audio_duration(audio_path):
    """Get the duration of the audio file using ffprobe."""
    try:
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            audio_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        duration = float(result.stdout.strip())
        return duration
    except subprocess.CalledProcessError as e:
        print(f"Error getting audio duration: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error converting duration to float: {e}")
        sys.exit(1)


def combine_video_audio_subtitles(video_path, audio_path, srt_path, output_path):
    """Combine video and audio, cut video to audio length, and add subtitles using ffmpeg."""
    # Get audio duration
    audio_duration = get_audio_duration(audio_path)

    # Build ffmpeg command
    cmd = [
        'ffmpeg',
        '-i', video_path,  # Input video
        '-i', audio_path,  # Input audio
        '-vf', f"subtitles={srt_path}",  # Add subtitles from SRT file
        '-map', '0:v',  # Map video from first input
        '-map', '1:a',  # Map audio from second input
        '-c:v', 'libx264',  # Re-encode video with H.264 (required for subtitles)
        '-c:a', 'aac',  # Encode audio to AAC
        '-t', str(audio_duration),  # Set duration to audio length
        '-y',  # Overwrite output file if it exists
        output_path  # Output file
    ]

    try:
        # Execute ffmpeg command
        result = subprocess.run(cmd, check=True, stderr=subprocess.PIPE)
        print(f"Successfully created {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error processing video, audio, and subtitles: {e.stderr.decode()}")
        sys.exit(1)



# Get file paths from command line arguments
video_path = "vid1.mp4"
audio_path = "../../Downloads/output.wav"
output_path = "main.mp4"
srt_path = "output.srt"

# Combine video, audio, and subtitles
combine_video_audio_subtitles(video_path, audio_path, srt_path, output_path)

