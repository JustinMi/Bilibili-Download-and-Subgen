"""
This script downloads a video from BiliBili using BBDown and generates subtitles in SRT format using
videOCR.
"""

import os
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import urlparse, urlunparse

from opencc import OpenCC
from videocr import save_subtitles_to_file

DOWNLOAD_FOLDER = "downloaded_videos"

# Create a converter to Simplified
cc = OpenCC("t2s")  # 't2s' = Traditional to Simplified


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
            "Usage: python download_and_subtitle_videocr.py <BiliBili video URL> <video name>"
        )
        sys.exit(1)
    video_url = sys.argv[1]
    video_name = sys.argv[2]

    # Clean the URL of trackers
    parsed = urlparse(video_url)
    clean_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, "", "", ""))

    # Download the video
    try:
        download_video(clean_url, video_name)
    except Exception as e:
        print(f"Error downloading video: {e}")
        sys.exit(1)

    # Extract subtitles and generate SRT file
    try:
        print("📝 Generating SRT file...")
        save_subtitles_to_file(
            f"{DOWNLOAD_FOLDER}/{video_name}.mp4",
            f"{DOWNLOAD_FOLDER}/{video_name}.srt",
            lang="ch",
            use_gpu=True,
            # Confidence threshold for word predictions. Words with lower confidence than this value
            # will be discarded. Bump it up there are too many excess words, lower it if there are
            # too many missing words. Default is 75.
            conf_threshold=95,
            # If set, pixels whose brightness are less than the threshold will be blackened out.
            # Valid brightness values range from 0 (black) to 255 (white). This can help improve
            # accuracy when performing OCR on videos with white subtitles.
            brightness_threshold=235,
            # The number of frames to skip before sampling a frame for OCR. 1 means every frame will
            # be sampled, 2 means every other frame will be sampled, and so on. This can help reduce
            # the number of frames processed, which can speed up the OCR process.
            frames_to_skip=1,
            # Similarity threshold for subtitle lines. Subtitle lines with larger Levenshtein ratios
            # than this threshold will be merged together. Make it closer to 0 if you get too many
            # duplicated subtitle lines, or make it closer to 100 if you get too few subtitle lines.
            # Default is 80.
            sim_threshold=85,
            # Specifies the bounding area in pixels for the portion of the frame that will be used
            # for OCR. See image in the repo for reference.
            # The crop tries to exclude any logos or watermarks in the bottom left and right hand
            # corners of the video.
            crop_x=290,
            crop_y=865,
            crop_width=1430,
            crop_height=215,
        )
        print("✅ SRT file generated successfully.")
    except Exception as e:
        print(f"Error generating SRT file: {e}")
        sys.exit(1)

    # Convert SRT to Simplified Chinese
    try:
        print("🔄 Converting SRT to Simplified Chinese...")

        srt_path = f"{DOWNLOAD_FOLDER}/{video_name}.srt"
        lines = []

        # Create a temp file in the same directory
        dir_name = os.path.dirname(srt_path)
        fd, temp_path = tempfile.mkstemp(dir=dir_name, suffix=".srt")
        os.close(fd)

        # Read the original SRT file and convert each line
        # to Simplified Chinese, writing to the temp file
        with (
            open(srt_path, "r", encoding="utf-8") as src,
            open(temp_path, "w", encoding="utf-8") as dst,
        ):
            for line in src:
                dst.write(cc.convert(line))

        # Atomically replace the original SRT file with the temp file
        shutil.move(temp_path, srt_path)

        print("✅ SRT file converted to Simplified Chinese successfully.")
    except Exception as e:
        print(f"Error converting SRT to simplified: {e}")
        os.remove(temp_path)  # Clean up temp file if something goes wrong
        sys.exit(1)
