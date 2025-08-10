from videocr import save_subtitles_to_file

VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
CROP_X = 420
CROP_Y = 860
CROP_WIDTH = VIDEO_WIDTH
CROP_HEIGHT = VIDEO_HEIGHT - CROP_X

if __name__ == "__main__":
    save_subtitles_to_file(
        "shared_files/mihoyo_workplace.mp4",
        "shared_files/mihoyo_workplace.srt",
        lang="ch",
        use_gpu=True,
        # Confidence threshold for word predictions. Words with lower confidence than this value
        # will be discarded. Bump it up there are too many excess words, lower it if there are too
        # many missing words. Default is 75.
        conf_threshold=90,
        # If set, pixels whose brightness are less than the threshold will be blackened out. Valid
        # brightness values range from 0 (black) to 255 (white). This can help improve accuracy when
        # performing OCR on videos with white subtitles.
        brightness_threshold=210,
        # The number of frames to skip before sampling a frame for OCR. 1 means every frame will be
        # sampled, 2 means every other frame will be sampled, and so on. This can help reduce the
        # number of frames processed, which can speed up the OCR process.
        frames_to_skip=1,
    )
