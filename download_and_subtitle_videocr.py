"""
This script downloads a video from BiliBili using BBDown and generates subtitles in SRT format using
videOCR.
"""

import subprocess
import sys

from videocr import save_subtitles_to_file

SHARED_FOLDER = "shared_files"


def download_video(url: str, video_name: str) -> None:
    """
    Download a video from BiliBili using BBDown.

    Args:
        url (str): The BiliBili video URL.
        video_name (str): The name to give the downloaded video.
    """
    print(f"📥 Downloading video from {url}...")

    # Run BBDown executable with the provided URL and video name
    output_path = f"{SHARED_FOLDER}/{video_name}.mp4"
    cmd = ["./BBDown", url, "-F", output_path]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print("✅ Download completed successfully.")
    else:
        raise RuntimeError(
            f"BBDown failed with exit code {result.returncode}: {result.stderr}"
        )


if __name__ == "__main__":
    # Take in video url and name as arguments
    if len(sys.argv) < 3:
        print(
            "Usage: python download_and_subtitle_videocr.py <BiliBili video URL> <video name>"
        )
        sys.exit(1)
    video_url = sys.argv[1]
    video_name = sys.argv[2]

    # Download the video
    try:
        download_video(video_url, video_name)
    except Exception as e:
        print(f"Error downloading video: {e}")
        sys.exit(1)

    # Extract subtitles and generate SRT file
    try:
        print("📝 Generating SRT file...")
        save_subtitles_to_file(
            f"{SHARED_FOLDER}/{video_name}.mp4",
            f"{SHARED_FOLDER}/{video_name}.srt",
            lang="ch",
            use_gpu=True,
            # Confidence threshold for word predictions. Words with lower confidence than this value
            # will be discarded. Bump it up there are too many excess words, lower it if there are
            # too many missing words. Default is 75.
            conf_threshold=90,
            # If set, pixels whose brightness are less than the threshold will be blackened out.
            # Valid brightness values range from 0 (black) to 255 (white). This can help improve
            # accuracy when performing OCR on videos with white subtitles.
            brightness_threshold=210,
            # The number of frames to skip before sampling a frame for OCR. 1 means every frame will
            # be sampled, 2 means every other frame will be sampled, and so on. This can help reduce
            # the number of frames processed, which can speed up the OCR process.
            frames_to_skip=1,
        )
        print("✅ SRT file generated successfully.")
    except Exception as e:
        print(f"Error generating SRT file: {e}")
        sys.exit(1)
