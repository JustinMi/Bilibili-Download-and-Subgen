"""
Combined downloader and subtitle generator for BiliBili videos.

Features:
- Downloads video via BBDown.
- Generates SRT using either videocr (default) or faster-whisper.
- Converts SRT to Simplified Chinese with OpenCC.
- Aligns subtitles to the video using ffs, keeping the original SRT filename.

Usage:
    python download_and_subtitle.py <BiliBili video URL> <video name> [--engine videocr|whisper]
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import urlparse, urlunparse

from opencc import OpenCC

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


def generate_srt_videocr(video_name: str) -> None:
    print("📝 Generating SRT file with videocr...")
    # Lazy import to avoid requiring videocr unless selected
    from videocr import save_subtitles_to_file

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
    print("✅ SRT file generated successfully (videocr).")


def format_time_srt(t: float) -> str:
    """
    Given input time t, returns in srt format.

    Args:
        t (float): Time in seconds.
    Returns:
        str: Time formatted as HH:MM:SS,mmm
    """
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = int(t % 60)
    ms = int((t % 1) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def generate_srt_whisper(video_name: str) -> None:
    print("📝 Generating SRT file with faster-whisper...")
    # Lazy import to avoid requiring faster-whisper unless selected
    from faster_whisper import WhisperModel

    # Transcribe with word timestamps
    model = WhisperModel("medium", device="cuda", compute_type="float16")
    segments, _info = model.transcribe(
        audio=f"{DOWNLOAD_FOLDER}/{video_name}.mp4",
        language="en",
        beam_size=5,
        log_progress=True,
        condition_on_previous_text=True,
        # log_prob_threshold can help filter nonsense transcriptions from real but low-confidence
        # speech. Default is -1, closer to 0 is stricter.
        log_prob_threshold=0.8,
        # If the probability of the <|nospeech|> token is higher than this value AND the decoding
        # has failed due to `logprob_threshold`, consider the segment as silence (default: 0.6)
        no_speech_threshold=0.8,
    )

    # Write raw transcript to SRT; conversion to Simplified is a separate step
    with open(f"{DOWNLOAD_FOLDER}/{video_name}.srt", "w", encoding="utf-8") as f:
        for i, segment in enumerate(segments, start=1):
            start = segment.start
            end = segment.end
            text = segment.text.strip()
            f.write(f"{i}\n")
            f.write(f"{format_time_srt(start)} --> {format_time_srt(end)}\n")
            f.write(f"{text}\n\n")
    print("✅ SRT file generated successfully (whisper).")


def convert_srt_to_simplified(video_name: str) -> None:
    print("🔄 Converting SRT to Simplified Chinese...")
    srt_path = f"{DOWNLOAD_FOLDER}/{video_name}.srt"
    dir_name = os.path.dirname(srt_path)
    fd, temp_path = tempfile.mkstemp(dir=dir_name, suffix=".srt")
    os.close(fd)

    try:
        with (
            open(srt_path, "r", encoding="utf-8") as src,
            open(temp_path, "w", encoding="utf-8") as dst,
        ):
            for line in src:
                dst.write(cc.convert(line))

        shutil.move(temp_path, srt_path)
        print("✅ SRT file converted to Simplified Chinese successfully.")
    except Exception as e:
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except Exception:
            pass
        raise RuntimeError(f"Error converting SRT to simplified: {e}")


def align_subtitles_with_ffs(video_name: str) -> None:
    print("🔄 Aligning subtitles with ffs...")
    video_path = f"{DOWNLOAD_FOLDER}/{video_name}.mp4"
    srt_path = f"{DOWNLOAD_FOLDER}/{video_name}.srt"
    synced_path = srt_path + ".synced"

    result = subprocess.run(
        ["ffs", video_path, "-i", srt_path, "-o", synced_path],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        # Clean up temp file if created
        try:
            if os.path.exists(synced_path):
                os.remove(synced_path)
        except Exception:
            pass
        raise RuntimeError(
            f"ffs failed with exit code {result.returncode}: {result.stderr}"
        )

    shutil.move(synced_path, srt_path)
    print("✅ Subtitles aligned successfully with ffs.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Download a BiliBili video, generate subtitles (videocr|whisper), "
            "convert to Simplified Chinese, and align with ffs."
        )
    )
    parser.add_argument("url", help="BiliBili video URL")
    parser.add_argument("video_name", help="Output video name (without extension)")
    parser.add_argument(
        "--engine",
        "-e",
        choices=["videocr", "whisper"],
        default="videocr",
        help="Subtitle engine to use (default: videocr)",
    )
    return parser


def main() -> None:
    # Parse arguments
    parser = build_parser()
    args = parser.parse_args()

    # Clean the URL of trackers
    parsed = urlparse(args.url)
    clean_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, "", "", ""))

    # Download the video
    try:
        download_video(clean_url, args.video_name)
    except Exception as e:
        print(f"Error downloading video: {e}")
        sys.exit(1)

    # Generate SRT
    try:
        if args.engine == "videocr":
            generate_srt_videocr(args.video_name)
        else:
            generate_srt_whisper(args.video_name)
    except Exception as e:
        print(f"Error generating SRT file: {e}")
        sys.exit(1)

    # Convert to Simplified Chinese
    try:
        convert_srt_to_simplified(args.video_name)
    except Exception as e:
        print(e)
        sys.exit(1)

    # Align with ffs and keep original filename
    try:
        align_subtitles_with_ffs(args.video_name)
    except Exception as e:
        print(f"Error aligning subtitles with ffs: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
