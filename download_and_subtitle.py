from faster_whisper import WhisperModel
import subprocess
import sys

DOWNLOADED_VIDEO_FILENAME = "downloaded_vid.mp4"
OUTPUT_SRT_FILENAME = "output.srt"

# Load the model (choose "base", "small", "medium", or "large")
MODEL = WhisperModel("medium", device="cpu", compute_type="int8")


def download_video(url: str, output_name: str) -> None:
    """
    Download a video from BiliBili using BBDown.

    Args:
        url (str): The BiliBili video URL.
        output_name (str): The desired output file name.
    """
    print(f"📥 Downloading video from {video_url}...")

    # Run BBDown executable with the provided URL and output name
    cmd = ["./BBDown", url, "-F", output_name]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print("✅ Download completed successfully.")
    else:
        raise RuntimeError(
            f"BBDown failed with exit code {result.returncode}: {result.stderr}"
        )


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


def generate_srt_file(output_srt_file: str) -> None:
    """
    Generate an SRT file from the downloaded video.

    Args:
        output_srt_file (str): The name of the output SRT file.
    """
    print("🏗️ Generating SRT file...")

    # Transcribe with word timestamps
    segments, _info = MODEL.transcribe(
        audio=DOWNLOADED_VIDEO_FILENAME,
        language="zh",
        beam_size=5,
        log_progress=True,
        no_speech_threshold=0.7,  # If the probability of the <|nospeech|> token is higher than this value AND the decoding has failed due to `logprob_threshold`, consider the segment as silence (default: 0.6)
    )

    # Write to SRT
    with open(output_srt_file, "w", encoding="utf-8") as f:
        for i, segment in enumerate(segments, start=1):
            start = segment.start
            end = segment.end
            text = segment.text.strip()

            f.write(f"{i}\n")
            f.write(f"{format_time_srt(start)} --> {format_time_srt(end)}\n")
            f.write(f"{text}\n\n")

    print("✅ SRT file generated successfully.")


if __name__ == "__main__":
    # Take in URL as an argument
    if len(sys.argv) < 2:
        print("Usage: python download_and_subtitle.py <BiliBili video URL>")
        sys.exit(1)
    video_url = sys.argv[1]

    try:
        download_video(video_url, DOWNLOADED_VIDEO_FILENAME)
    except Exception as e:
        print(f"Error downloading video: {e}")

    try:
        generate_srt_file(OUTPUT_SRT_FILENAME)
    except Exception as e:
        print(f"Error generating SRT file: {e}")
