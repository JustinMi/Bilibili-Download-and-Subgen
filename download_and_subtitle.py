from faster_whisper import WhisperModel
import subprocess

URL = "https://www.bilibili.com/video/BV1g4421S71g/?vd_source=92aedfd5d64af18306567e5db62cf592"
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
    # Run BBDown executable with the provided URL and output name
    cmd = ["./BBDown", url, "-F", output_name]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print("Download completed successfully.")
        print(result.stdout)
    else:
        raise RuntimeError(
            f"BBDown failed with exit code {result.returncode}: {result.stderr}"
        )


def format_time_srt(t: float) -> str:
    """Given input time t, returns in srt format."""
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = int(t % 60)
    ms = int((t % 1) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def generate_srt_file(output_srt_file: str) -> None:
    # Transcribe with word timestamps (optional)
    segments, _info = MODEL.transcribe(
        audio=DOWNLOADED_VIDEO_FILENAME,
        language="zh",
        beam_size=5,
        log_progress=True,
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


if __name__ == "__main__":
    try:
        download_video(URL, DOWNLOADED_VIDEO_FILENAME)
        print(f"Video downloaded as {DOWNLOADED_VIDEO_FILENAME}")
    except Exception as e:
        print(f"Error downloading video: {e}")

    try:
        generate_srt_file(OUTPUT_SRT_FILENAME)
        print("SRT file generated successfully.")
    except Exception as e:
        print(f"Error generating SRT file: {e}")
