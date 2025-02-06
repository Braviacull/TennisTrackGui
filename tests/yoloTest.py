from ultralytics import YOLO
import time

model = YOLO('yolov8x')

start = time.time()

result = model.predict("5 seconds more persons.mp4", save = True)

print("Time taken: ", time.time() - start)