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
    
# NON USATA
# def get_frame_count(video_path):
#     # Apri il video
#     cap = cv2.VideoCapture(video_path)
    
#     # Controlla se il video è stato aperto correttamente
#     if not cap.isOpened():
#         print(f"Errore nell'apertura del video: {video_path}")
#         return None
    
#     # Ottieni il numero di frame
#     frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
#     # Rilascia il video
#     cap.release()
    
#     return frame_count