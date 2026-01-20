# BiliBili Download & Subtitle Generator

Download a BiliBili video with BBDown, generate subtitles via either videocr (OCR-based, default) or faster-whisper (ASR-based), convert Traditional ➜ Simplified Chinese with OpenCC, and align subtitles to the video with ffsubsync (`ffs` CLI).

## Features
- BBDown download wrapper that writes to `downloaded_videos/<name>.mp4`.
- Two subtitle engines: `videocr` (PaddleOCR GPU) or `whisper` (faster-whisper GPU).
- Automatic Traditional ➜ Simplified conversion and subtitle alignment with `ffs`.
- Docker image that bundles the Linux BBDown binary and Python deps.

## Requirements (bare metal)
- Python 3.11, `ffmpeg`, and an NVIDIA GPU/driver for videocr or faster-whisper.
- `BBDown` binary placed at the repo root as `./BBDown` (make it executable). Download the correct build for your OS from https://github.com/nilaoda/BBDown/releases.
- Install Python deps: `python -m pip install --upgrade pip` then `pip install -r requirements.txt`.

## Quick start (Docker, recommended)
1) Build: `docker build -t bilibili-subgen .`  
2) Run (downloads + subtitles):  
   `docker run --rm -it --gpus all -v "$PWD/downloaded_videos:/app/downloaded_videos" bilibili-subgen python download_and_subtitle.py <url> <video_name> [-e whisper] [--download-only]`  
   The Dockerfile already downloads and installs the Linux BBDown binary and symlinks it to `/app/BBDown`.

## Running with RunPod (Justin's specific workflow)
1) Push changes to Github; Github actions will build the image, run a smoketest, and store in GHCR under the `latest` tag.
2) Deploy a GPU pod in RunPod. Cheapest one you can get is fine.
  - Edit the pod template: the container image should be `ghcr.io/justinmi/bilibili-download-and-subgen:latest`.
3) Run `download_and_subtitle.py`.
4) Transfer files using `runpodctl send <files>`.

## Usage
- Download + videocr subtitles (default):  
  `python download_and_subtitle.py https://www.bilibili.com/video/<BVid> my_video`
- Download only (no subtitles):  
  `python download_and_subtitle.py <url> my_video --download-only`
- Use faster-whisper instead of videocr:  
  `python download_and_subtitle.py <url> my_video --engine whisper`

Outputs are written to `downloaded_videos/`:
- `<name>.mp4` (from BBDown)
- `<name>.srt` (generated)

## Notes & troubleshooting
- videocr uses GPU PaddleOCR; faster-whisper uses GPU with `WhisperModel("medium", device="cuda", compute_type="float16")`. Ensure the container/host sees the GPU (`--gpus all` for Docker, correct drivers locally).
- If BBDown is missing or not executable, downloads will fail; verify `./BBDown` exists and runs (`./BBDown --version`).
- `ffs` comes from `ffsubsync` (installed via requirements). If alignment fails, check stdout/stderr printed by the script in the container logs.
