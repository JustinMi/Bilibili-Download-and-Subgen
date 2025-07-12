import whisperx
from opencc import OpenCC

# Create a converter to Simplified
cc = OpenCC("t2s")  # 't2s' = Traditional to Simplified

video_name = "云南德宏阿昌族美食"  # Name of the video file without extension
device = "cpu"  # Use CPU for processing; change to "cuda" for GPU if available
audio_file = "云南德宏阿昌族美食.mp4"
compute_type = "int8"  # Balanced precision and speed

# Load WhisperX model with aligned options
model = whisperx.load_model(
    whisper_arch="small",  # Balanced between speed and accuracy for MacOS
    language="zh",  # Specify the language for better accuracy
    device=device,
    compute_type=compute_type,
    asr_options={
        "segment_resolution": "sentence",  # Segment resolution for better alignment
        "chunk_size": 15,  # Process in chunks of 15 seconds. Smaller chunks → finer-grained, shorter audio batches; larger chunks → faster processing but more chance of drifts/skipped speech.)
        "log_prob_threshold": 0.8,  # log_prob_threshold can help filter nonsense transcriptions from real but low-confidence speech. Default is -1, closer to 0 is stricter.
        "no_speech_threshold": 0.8,  # If the probability of the <|nospeech|> token is higher than this value AND the decoding has failed due to `logprob_threshold`, consider the segment as silence (default: 0.6)
    },
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


# 1. Transcribe with original whisper (batched)
audio = whisperx.load_audio(audio_file)
result = model.transcribe(
    audio,
    batch_size=2,  # Keep low to fit within 8GB RAM
)

# 2. Align whisper output
model_a, metadata = whisperx.load_align_model(
    language_code=result["language"], device=device
)
result = whisperx.align(
    result["segments"], model_a, metadata, audio, device, return_char_alignments=False
)

# Write the transcription to a file
with open(f"{video_name}.srt", "w", encoding="utf-8") as f:
    for i, segment in enumerate(result["segments"], start=1):
        start = segment["start"]
        end = segment["end"]
        text = segment["text"].strip()
        simplified_text = cc.convert(
            text
        )  # Ensure the text is converted to simplified Chinese

        f.write(f"{i}\n")
        f.write(f"{format_time_srt(start)} --> {format_time_srt(end)}\n")
        f.write(f"{simplified_text}\n\n")
