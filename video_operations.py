import cv2
import numpy as np


# Funzione per leggere un video e restituire i frame e il frame rate
def read_video(path_video):
    cap = cv2.VideoCapture(path_video)
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