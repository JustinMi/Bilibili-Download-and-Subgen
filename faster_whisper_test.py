from faster_whisper import WhisperModel

# Load the model (choose "base", "small", "medium", or "large")
model = WhisperModel("medium", device="cuda", compute_type="float16")

# Set your input file path
input_audio = "island.mp4"
final_path = f"shared_files/{input_audio}"

# Transcribe with word timestamps (optional)
segments, info = model.transcribe(
    final_path, 
    language="zh",
    beam_size=5,
    condition_on_previous_text=True,
    log_prob_threshold=0.8,  # log_prob_threshold can help filter nonsense transcriptions from real but low-confidence speech. Default is -1, closer to 0 is stricter.
    no_speech_threshold=0.8,  # If the probability of the <|nospeech|> token is higher than this value AND the decoding has failed due to `logprob_threshold`, consider the segment as silence (default: 0.6)
)

# Write to SRT
with open("shared_files/output.srt", "w", encoding="utf-8") as f:
    for i, segment in enumerate(segments, start=1):
        start = segment.start
        end = segment.end
        text = segment.text.strip()

        # Format time
        def format_time(t: float) -> str:
            h = int(t // 3600)
            m = int((t % 3600) // 60)
            s = int(t % 60)
            ms = int((t % 1) * 1000)
            return f"{h:02}:{m:02}:{s:02},{ms:03}"

        f.write(f"{i}\n")
        f.write(f"{format_time(start)} --> {format_time(end)}\n")
        f.write(f"{text}\n\n")
