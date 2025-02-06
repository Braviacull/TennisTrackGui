from ultralytics import YOLO

model = YOLO('yolov8x')

result = model.predict("5 seconds more persons.mp4", save = True)