import cv2
from court_detection_net import CourtDetectorNet
from utils import scene_detect
import argparse
import torch

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

# def adjust_scenes(scenes, max_frames):
#     adjusted_scenes = []
#     for start, end in scenes:
#         if end - start > max_frames:
#             adjusted_scenes.append((start, start + max_frames))
#         else:
#             adjusted_scenes.append((start, end))
#     return adjusted_scenes
#
# def filter_frames(frames, scenes):
#     filtered_frames = []
#     for start, end in scenes:
#         filtered_frames.extend(frames[start:end])
#     return filtered_frames
pass

# Funzione principale per elaborare i frame del video
def main(frames, scenes, homography_matrices,
         draw_trace=False, trace=7):
    """
    :params
        frames: lista di immagini originali
        scenes: lista di inizio e fine dei frammenti video
        homography_matrices: lista di matrici omografiche
    :return
        imgs_res: lista di vettori (scene) di immagini risultanti
    """
    scene_scartate = 0
    imgs_res = []
    is_track = [x is not None for x in homography_matrices]
    for num_scene in range(len(scenes)):
        sum_track = sum(is_track[scenes[num_scene][0]:scenes[num_scene][1]])
        len_track = scenes[num_scene][1] - scenes[num_scene][0]

        eps = 1e-15
        scene_rate = sum_track / (len_track + eps)
        if (scene_rate > 0.5):
            imgs_res.append(frames[scenes[num_scene][0]:scenes[num_scene][1]])

        else:
            scene_scartate += 1
            print ("SCENA SCARTATA\n")

    print ("Scene scartate: ", scene_scartate)
    return imgs_res

# Funzione principale
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--path_court_model', type=str, help='path to pretrained model for court detection')
    parser.add_argument('--path_input_video', type=str, help='path to input video')
    parser.add_argument('--path_output_video', type=str, help='path to output video')
    args = parser.parse_args()

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print (device + "\n")
    print ("Reading video\n")
    frames, fps = read_video(args.path_input_video)
    print ("Detecting scenes\n")
    scenes = scene_detect(args.path_input_video)

    print('court detection')
    court_detector = CourtDetectorNet(args.path_court_model, device)
    homography_matrices, kps_court = court_detector.infer_model(frames)

    imgs_res = main(frames, scenes, homography_matrices,
                    draw_trace=True)

    for i in range(len(imgs_res)):
        output_path = f"{args.path_output_video.split('.')[0]}_{i + 1}.mp4"
        write(imgs_res[i], fps, output_path)