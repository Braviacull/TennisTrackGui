import json
import os
import cv2
from tqdm import tqdm
from court_detection_net import CourtDetectorNet
import numpy as np
from court_reference import CourtReference
from bounce_detector import BounceDetector
from person_detector import PersonDetector
from ball_detector import BallDetector
import argparse
import torch
from utils.video_operations import get_frame_rate, get_height_width, read_video_generator, get_total_frames
from utils.obtain_directory import obtain_jsons_dir
import time
from utils.utils import print_execution_time

def get_court_img():
    court_reference = CourtReference()
    court = court_reference.build_court_reference()
    court = cv2.dilate(court, np.ones((10, 10), dtype=np.uint8))
    court_img = (np.stack((court, court, court), axis=2)*255).astype(np.uint8)
    return court_img

def drawing(input_video_path, output_video_path, bounces, ball_track, kps_court, persons_top, persons_bottom,
         draw_trace=False, trace=7):
    """
    :params
        input_video_path: path to input video
        output_video_path: path to output video
        bounces: list of image numbers where ball touches the ground
        ball_track: list of (x,y) ball coordinates
        kps_court: list of 14 key points of tennis court
        persons_top: list of person bboxes located in the top of tennis court
        persons_bottom: list of person bboxes located in the bottom of tennis court
        draw_trace: whether to draw ball trace
        trace: the length of ball trace
    """

    width_minimap = 166
    height_minimap = 350

    fps = get_frame_rate(input_video_path)
    height, width = get_height_width(input_video_path)
    out = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

    total_frames = get_total_frames(input_video_path)
    frame_iterator = iter(read_video_generator(input_video_path))

    print('drawing')
    for i in tqdm(range(total_frames)):
        court_img = get_court_img()

        frame = next(frame_iterator)
        inv_mat = homography_matrices[i]

        # draw ball trajectory
        if ball_track[i][0]:
            if draw_trace:
                for j in range(0, trace):
                    if i-j >= 0:
                        if ball_track[i-j][0]:
                            draw_x = int(ball_track[i-j][0])
                            draw_y = int(ball_track[i-j][1])
                            frame = cv2.circle(frame, (draw_x, draw_y),
                            radius=3, color=(0, 255, 0), thickness=2)
            else:    
                frame = cv2.circle(frame , (int(ball_track[i][0]), int(ball_track[i][1])), radius=5,
                                        color=(0, 255, 0), thickness=2)
                frame = cv2.putText(frame, 'ball', 
                        org=(int(ball_track[i][0]) + 8, int(ball_track[i][1]) + 8),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=0.8,
                        thickness=2,
                        color=(0, 255, 0))

        # draw court keypoints
        if kps_court[i] is not None:
            for j in range(len(kps_court[i])):
                frame = cv2.circle(frame, (int(kps_court[i][j][0, 0]), int(kps_court[i][j][0, 1])),
                                    radius=0, color=(0, 0, 255), thickness=10)

        height, width, _ = frame.shape

        # draw bounce in minimap
        if i in bounces and inv_mat is not None:
            ball_point = ball_track[i]
            ball_point = np.array(ball_point, dtype=np.float32).reshape(1, 1, 2)
            ball_point = cv2.perspectiveTransform(ball_point, inv_mat)
            court_img = cv2.circle(court_img, (int(ball_point[0, 0, 0]), int(ball_point[0, 0, 1])),
                                                radius=0, color=(0, 255, 255), thickness=50)

        minimap = court_img.copy()

        # draw persons
        persons = persons_top[i] + persons_bottom[i]                    
        for j, person in enumerate(persons):
            if len(person[0]) > 0:
                person_bbox = list(person[0])
                frame = cv2.rectangle(frame, (int(person_bbox[0]), int(person_bbox[1])),
                                        (int(person_bbox[2]), int(person_bbox[3])), [255, 0, 0], 2)

                # transmit person point to minimap
                person_point = list(person[1])
                person_point = np.array(person_point, dtype=np.float32).reshape(1, 1, 2)
                person_point = cv2.perspectiveTransform(person_point, inv_mat)
                minimap = cv2.circle(minimap, (int(person_point[0, 0, 0]), int(person_point[0, 0, 1])),
                                                    radius=0, color=(255, 0, 0), thickness=80)

        minimap = cv2.resize(minimap, (width_minimap, height_minimap))
        frame[30:(30 + height_minimap), (width - 30 - width_minimap):(width - 30), :] = minimap
        out.write(frame)

    out.release()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--path_ball_track_model', type=str, help='path to pretrained model for ball detection')
    parser.add_argument('--path_court_model', type=str, help='path to pretrained model for court detection')
    parser.add_argument('--path_bounce_model', type=str, help='path to pretrained model for bounce detection')
    parser.add_argument('--path_input_video', type=str, help='path to input video')
    parser.add_argument('--path_output_video', type=str, help='path to output video')
    args = parser.parse_args()
    
    jsons_dir = obtain_jsons_dir(args.path_output_video)
    homography_matrices_path = os.path.join(jsons_dir, 'homography_matrices.json')
    kps_court_path = os.path.join(jsons_dir, 'kps_court.json')

    if os.path.isfile(homography_matrices_path) and os.path.isfile(kps_court_path):
        start_time = time.time()
        device = 'cuda' if torch.cuda.is_available() else 'cpu'

        # Getting homography matrices and court keypoints
        homography_matrices = []
        kps_court = []

        with open(homography_matrices_path, 'r') as json_file:
            homography_matrices = json.load(json_file)
        with open(kps_court_path, 'r') as json_file:
            kps_court = json.load(json_file)

        # Converti le liste in array di NumPy
        homography_matrices = [np.array(matrix) for matrix in homography_matrices]
        kps_court = [np.array(kps) for kps in kps_court]

        print('person detection')
        person_detector = PersonDetector()
        persons_top, persons_bottom = person_detector.track_players(args.path_input_video, homography_matrices, filter_players=False)

        print('ball detection')
        ball_detector = BallDetector(args.path_ball_track_model, device)
        ball_track = ball_detector.infer_model(args.path_input_video)

        # bounce detection
        bounce_detector = BounceDetector(args.path_bounce_model)
        x_ball = [x[0] for x in ball_track]
        y_ball = [x[1] for x in ball_track]
        bounces = bounce_detector.predict(x_ball, y_ball)

        drawing(args.path_input_video, args.path_output_video, bounces, ball_track, kps_court, persons_top, persons_bottom, draw_trace=True)

        print_execution_time(start_time, time.time())
    else:
        print ("Error: homography_matrices.json or kps_court.json not found")