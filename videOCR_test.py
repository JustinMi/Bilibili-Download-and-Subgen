from videocr import save_subtitles_to_file

if __name__ == "__main__":
    save_subtitles_to_file(
        "shared_files/leg.mp4",
        "shared_files/leg.srt",
        lang="ch",
        sim_threshold=80,
        use_gpu=True,
        use_fullframe=True,
        brightness_threshold=210,
        similar_image_threshold=1000,
        frames_to_skip=1,
    )
