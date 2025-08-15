"""
download_video.py
This script downloads a video from BiliBili using BBDown and saves it to a specified folder.
"""

import subprocess
import sys
from urllib.parse import urlparse, urlunparse

DOWNLOAD_FOLDER = "downloaded_videos"


def download_video(url: str, video_name: str) -> None:
    """
    Download a video from BiliBili using BBDown.

    Args:
        url (str): The BiliBili video URL.
        video_name (str): The name to give the downloaded video.
    """
    print(f"📥 Downloading video from {url}...")

    # Run BBDown executable with the provided URL and video name
    output_path = f"{DOWNLOAD_FOLDER}/{video_name}.mp4"
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
            "Usage: python download_video.py <BiliBili video URL> <video name>"
        )
        sys.exit(1)
    video_url = sys.argv[1]
    video_name = sys.argv[2]

    # Clean the URL of trackers
    parsed = urlparse(video_url)
    clean_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))

    # Download the video
    try:
        download_video(clean_url, video_name)
    except Exception as e:
        print(f"Error downloading video: {e}")
        sys.exit(1)
