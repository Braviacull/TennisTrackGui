from court_detection_net import CourtDetectorNet
from utils.utils import scene_detect
import argparse
from utils.video_operations import read_video, write
import torch

# Funzione principale per elaborare i frame del video
def main(frames, scenes, homography_matrices):
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
    base = 0
    is_track = [x is not None for x in homography_matrices]
    for num_scene in range(len(scenes)):
        sum_track = sum(is_track[scenes[num_scene][0]:scenes[num_scene][1]])
        len_track = scenes[num_scene][1] - scenes[num_scene][0]

        eps = 1e-15
        scene_rate = sum_track / (len_track + eps)
        if (scene_rate > 0.5):
            start = scenes[num_scene][0]
            end = scenes[num_scene][1]
            imgs_res.extend(frames[start:end])

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
            base = end + 1

            with open(args.path_scene_file, 'a') as scene_file:
                scene_file.write(f"{start} {end}\n")

        else:
            scene_scartate += 1

    print ("Scene scartate: ", scene_scartate)
    return imgs_res

# Funzione principale
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--path_court_model', type=str, help='path to pretrained model for court detection')
    parser.add_argument('--path_input_video', type=str, help='path to input video')
    parser.add_argument('--path_output_video', type=str, help='path to output video')
    parser.add_argument('--path_scene_file', type=str, help='path to scenes.txt file')
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

    imgs_res = main(frames, scenes, homography_matrices)
    num_imgs_res = len(imgs_res) # numero di scene risultanti
    num_digits = len(str(num_imgs_res)) # numero di cifre del numero di scene risultanti

    for i in range(fps):
        imgs_res.append(imgs_res[-1])

    write(imgs_res, fps, args.path_output_video)



    