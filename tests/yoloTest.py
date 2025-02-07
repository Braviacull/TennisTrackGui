from ultralytics import YOLO
import time

model = YOLO('yolov8x')

start = time.time()

result = model.predict("Inputs\sinner10sec.mp4", save = True)

print("Time taken: ", time.time() - start)