import supervision as sv
import cv2


# ===============================
# Get total frames + FPS
# ===============================
def get_number_of_frames(video_path):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"❌ Error: Cannot open video -> {video_path}")
        return 0, 0  # return safe values instead of -1

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    cap.release()

    # Safety fallback
    if fps == 0 or fps is None:
        fps = 25  # default fallback FPS

    return total_frames, int(fps)


# ===============================
# Frame generator
# ===============================
def get_frames(video_path, stride=1, start=0, end=None):
    try:
        frame_generator = sv.get_video_frames_generator(
            source_path=video_path,
            stride=stride,
            start=start,
            end=end
        )
        return frame_generator

    except Exception as e:
        print(f"❌ Error generating frames: {e}")
        return None