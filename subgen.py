from faster_whisper import WhisperModel

# Load the model (choose "base", "small", "medium", or "large")
model = WhisperModel("medium", device="cpu", compute_type="int8")

# Set your input file path
input_audio = "云南瑞丽香辣螃蟹，缅甸甩粑粑，傣寨香茅草排骨，阿星逛翡翠鬼市.mp4"

# Transcribe with word timestamps (optional)
segments, info = model.transcribe(input_audio, language="zh", beam_size=5)

# Write to SRT
with open("output.srt", "w", encoding="utf-8") as f:
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
