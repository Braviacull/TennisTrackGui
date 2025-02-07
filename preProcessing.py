from court_detection_net import CourtDetectorNet
from utils.utils import scene_detect
from utils.obtain_directory import obtain_jsons_dir
import argparse
from utils.video_operations import get_frame_rate, get_total_frames, write_video_generator_intervals
import torch
import json
import numpy as np
import os
import time

# Funzione principale per elaborare i frame del video
def main(scenes, homography_matrices, kps_court):

    selected_indexes = []
    homography_matrices_res = []
    kps_court_res = []
    base = 0
    is_track = [x is not None for x in homography_matrices]
    for num_scene in range(len(scenes)):
        start = scenes[num_scene][0]
        end = scenes[num_scene][1]
        sum_track = sum(is_track[start:end])
        len_track = end - start

        eps = 1e-15
        scene_rate = sum_track / (len_track + eps)
        if (scene_rate > 0.5):
            selected_indexes.append(num_scene)
            homography_matrices_res.extend(homography_matrices[start:end])
            kps_court_res.extend(kps_court[start:end])

            # write without gaps
            if start == base:
                    pass # no gap
            elif start > base:
                gap = start - base
                start -= gap # == base
                end -= gap
            elif start < base:
                print("Invalid scene detected")
                return
            base = end

            with open(args.path_scene_file, 'a') as scene_file:
                scene_file.write(f"{start+1} {end}\n")

        else: print ("Scene rejected")

    return selected_indexes, homography_matrices_res, kps_court_res

# Funzione principale
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--path_court_model', type=str, help='path to pretrained model for court detection')
    parser.add_argument('--path_input_video', type=str, help='path to input video')
    parser.add_argument('--path_output_video', type=str, help='path to output video')
    parser.add_argument('--path_scene_file', type=str, help='path to scenes.txt file')
    args = parser.parse_args()

    start_time = time.time()

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print (device + "\n")

    print ("Detecting scenes\n")
    scenes = scene_detect(args.path_input_video)

    print('Court detection')
    court_detector = CourtDetectorNet(args.path_court_model, device)
    homography_matrices, kps_court = court_detector.infer_model(args.path_input_video)

    selected_indexes, homography_matrices, kps_court = main(scenes, homography_matrices, kps_court)

    selected_scenes = []
    for i in selected_indexes:
        selected_scenes.append(scenes[i])

    fps = get_frame_rate(args.path_input_video)
    for i in range(fps): # padding
        homography_matrices.append(homography_matrices[-1])
        kps_court.append(kps_court[-1])

    # Convert the numpy arrays to lists
    homography_matrices_list = [matrix.tolist() if isinstance(matrix, np.ndarray) else matrix for matrix in homography_matrices]
    kps_court_list = [kps.tolist() if isinstance(kps, np.ndarray) else kps for kps in kps_court]

    # Save the lists to json files
    jsons_dir = obtain_jsons_dir(args.path_output_video)
    os.makedirs(jsons_dir, exist_ok=True)

    with open(os.path.join(jsons_dir, "homography_matrices.json"), 'w') as json_file:
        json.dump(homography_matrices_list, json_file)

    with open(os.path.join(jsons_dir, "kps_court.json"), 'w') as json_file:
        json.dump(kps_court_list, json_file)

    write_video_generator_intervals(fps, selected_scenes, args.path_input_video, args.path_output_video)

    execution_time_in_seconds= time.time() - start_time
    execution_time_in_minutes = execution_time_in_seconds / 60
    print(f"Execution time: {execution_time_in_minutes} minutes")