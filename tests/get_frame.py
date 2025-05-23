import cv2

# Percorso del video e numero del frame da salvare e visualizzare
video_path = r"C:\Users\aless\Desktop\yolo.mp4"
frame_number = 1
 # Cambialo col frame che ti serve
output_image = f'frame_{frame_number}.jpg'

# Apri il video
cap = cv2.VideoCapture(video_path)

# Vai al frame desiderato
cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

# Leggi il frame
ret, frame = cap.read()

if ret:
    # Salva il frame come immagine
    cv2.imwrite(output_image, frame)
    print(f"Frame salvato come {output_image}")

    # Mostra il frame salvato
    img = cv2.imread(output_image)
    cv2.imshow(f'Frame {frame_number}', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    print("Errore: impossibile leggere il frame.")

cap.release()