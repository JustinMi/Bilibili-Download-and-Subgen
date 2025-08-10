from videocr import save_subtitles_to_file

VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
CROP_X = 420
CROP_Y = 860
CROP_WIDTH = VIDEO_WIDTH
CROP_HEIGHT = VIDEO_HEIGHT - CROP_X

if __name__ == "__main__":
    save_subtitles_to_file(
        "shared_files/leg.mp4",
        "shared_files/leg2.srt",
        lang="ch",
        sim_threshold=80,
        use_gpu=True,
        use_fullframe=True,
        # Confidence threshold for word predictions. Words with lower confidence than this value
        # will be discarded. Bump it up there are too many excess words, lower it if there are too
        # many missing words. Default is 75.
        conf_threshold=90,
        # (0,0) is the top left corner of the video frame. (1920, 1080) is the bottom right corner.
        # crop_x, crop_y specify the top left corner of the crop rectangle, and crop_width,
        # crop_height specify the size of the crop rectangle.
        crop_x=CROP_X,
        crop_y=CROP_Y,
        crop_width=CROP_WIDTH,
        crop_height=CROP_HEIGHT,
        # If set, pixels whose brightness are less than the threshold will be blackened out. Valid
        # brightness values range from 0 (black) to 255 (white). This can help improve accuracy when
        # performing OCR on videos with white subtitles.
        brightness_threshold=210,
        similar_image_threshold=1000,
        frames_to_skip=1,
    )
