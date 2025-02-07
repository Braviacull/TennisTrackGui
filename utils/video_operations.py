import cv2

def read_video(path_video):
    cap = cv2.VideoCapture(path_video, apiPreference=cv2.CAP_FFMPEG)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frames = []
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            frames.append(frame)
        else:
            break
    cap.release()
    return frames, fps

def read_video_generator(path_video):
    cap = cv2.VideoCapture(path_video, apiPreference=cv2.CAP_FFMPEG)
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            yield frame #generate frame
        else:
            break
    cap.release()

def read_video_generator_interval(path_video, start_frame, end_frame):
    cap = cv2.VideoCapture(path_video, apiPreference=cv2.CAP_FFMPEG)
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

def get_total_frames(path_video):
    cap = cv2.VideoCapture(path_video)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    return total_frames

# Funzione per scrivere i frame risultanti in un video
def write(imgs_res, fps, path_output_video):
    height, width = imgs_res[0].shape[:2]
    out = cv2.VideoWriter(path_output_video, cv2.VideoWriter_fourcc(*'DIVX'), fps, (width, height))
    for num in range(len(imgs_res)):
        frame = imgs_res[num]
        out.write(frame)
    out.release()

def get_frame_rate(video_path):
    # Apri il video
    cap = cv2.VideoCapture(video_path)
    
    # Controlla se il video è stato aperto correttamente
    if not cap.isOpened():
        print(f"Errore nell'apertura del video: {video_path}")
        return None
    
    # Ottieni il frame rate
    frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
    
    # Rilascia il video
    cap.release()
    
    return frame_rate

def frame_to_time(frame, frame_rate): # time in ms
    return int((frame / frame_rate) * 1000)

def time_to_frame(ms, frame_rate): # time in ms
    return int((ms / 1000) * frame_rate)


def frame_to_position(frame, tot_frame):
    return (frame / tot_frame)

def position_to_frame(position, tot_frame):
    return int(position * tot_frame)