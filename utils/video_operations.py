import cv2
from tqdm import tqdm

def open_video_with_check(video_path):
    cap = cv2.VideoCapture(video_path, apiPreference=cv2.CAP_FFMPEG)
    
    # Check if the video is opened
    if not cap.isOpened():
        print(f"ERRORE nell'apertura del video: {video_path}")
        return None
    
    return cap

def read_video_generator(video_path):
    cap = open_video_with_check(video_path)
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            yield frame #generate frame
        else:
            break
    cap.release()

def read_video_generator_interval(video_path, start_frame, end_frame):
    cap = open_video_with_check(video_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            if start_frame <= cap.get(cv2.CAP_PROP_POS_FRAMES) <= end_frame:
                yield frame #generate frame
            elif cap.get(cv2.CAP_PROP_POS_FRAMES) > end_frame:
                break
        else:
            break
        if cap.get(cv2.CAP_PROP_POS_FRAMES) == end_frame:
            break
    cap.release()

def write_video_generator_intervals_with_padding(fps, scenes, path_input_video, path_output_video):
    height, width = get_height_width(path_input_video)
    out = cv2.VideoWriter(path_output_video, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

    for num_scene, scene in enumerate(scenes):
        start_frame = scene[0]
        end_frame = scene[1]
        total_frames = end_frame - start_frame
        last_frame = None
        with tqdm(total=total_frames, desc=f"Writing scene {num_scene+1}", leave=True) as pbar:
            for frame in read_video_generator_interval(path_input_video, start_frame, end_frame):
                out.write(frame)
                last_frame = frame
                pbar.update(1)
    for i in range(fps): # padding
        out.write(last_frame)

    out.release()

def get_total_frames(video_path):
    cap = open_video_with_check(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    return total_frames

def get_height_width(video_path):
    cap = open_video_with_check(video_path)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    cap.release()
    return height, width

def get_frame_rate(video_path):
    cap = open_video_with_check(video_path)
    frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
    cap.release()
    return frame_rate

# Conversions
def frame_to_time(frame, frame_rate): # time in ms
    return int((frame / frame_rate) * 1000)

def time_to_frame(ms, frame_rate): # time in ms
    return int((ms / 1000) * frame_rate)

def frame_to_position(frame, tot_frame):
    return (frame / tot_frame)

def position_to_frame(position, tot_frame):
    return int(position * tot_frame)