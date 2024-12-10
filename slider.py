import cv2

def get_frame_count(video_path):
    # Apri il video
    cap = cv2.VideoCapture(video_path)
    
    # Controlla se il video è stato aperto correttamente
    if not cap.isOpened():
        print(f"Errore nell'apertura del video: {video_path}")
        return None
    
    # Ottieni il numero di frame
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Rilascia il video
    cap.release()
    
    return frame_count

def update_frame_label(self, value):
        self.frame_label.setText(f"Frame: {value}")