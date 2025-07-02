from faster_whisper import WhisperModel
import subprocess
import sys


def download_video(url: str, video_name: str) -> None:
    """
    Download a video from BiliBili using BBDown.

    Args:
        url (str): The BiliBili video URL.
        video_name (str): The name to give the downloaded video.
    """
    print(f"📥 Downloading video from {video_url}...")

    # Run BBDown executable with the provided URL and video name
    cmd = ["./BBDown", url, "-F", f"{video_name}.mp4"]
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


def generate_srt_file(model: WhisperModel, video_name: str) -> None:
    """
    Generate an SRT file from the downloaded video using FasterWhisper.

    Args:
        video_name (str): The name of the downloaded video.

    Generates:
        {video_name}.srt: SRT file with subtitles extracted from the video.
    """
    print("🏗️ Generating SRT file...")

    # Transcribe with word timestamps
    segments, _info = model.transcribe(
        audio=f"{video_name}.mp4",
        language="zh",
        beam_size=5,
        log_progress=True,
        no_speech_threshold=0.7,  # If the probability of the <|nospeech|> token is higher than this value AND the decoding has failed due to `logprob_threshold`, consider the segment as silence (default: 0.6)
    )

    # Write to SRT
    with open(f"{video_name}.srt", "w", encoding="utf-8") as f:
        for i, segment in enumerate(segments, start=1):
            start = segment.start
            end = segment.end
            text = segment.text.strip()

            f.write(f"{i}\n")
            f.write(f"{format_time_srt(start)} --> {format_time_srt(end)}\n")
            f.write(f"{text}\n\n")

    print("✅ SRT file generated successfully.")


if __name__ == "__main__":
    # Take in video url and name as arguments
    if len(sys.argv) < 3:
        print(
            "Usage: python download_and_subtitle.py <BiliBili video URL> <video name>"
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
        # Load the model (choose "base", "small", "medium", or "large")
        model = WhisperModel("medium", device="cpu", compute_type="int8")
        generate_srt_file(model, video_name)
    except Exception as e:
        print(f"Error generating SRT file: {e}")
        sys.exit(1)
