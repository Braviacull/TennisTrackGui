import cv2
import numpy as np
import torch
from tracknet import BallTrackerNet
import torch.nn.functional as F
from tqdm import tqdm
from postprocess import refine_kps
from homography import get_trans_matrix, refer_kps
from utils.video_operations import read_video_generator, get_total_frames	


# Classe per il rilevamento del campo da tennis
class CourtDetectorNet():
    def __init__(self, path_model=None, device='cuda'):
        # Inizializza il modello di rilevamento della palla
        self.model = BallTrackerNet(out_channels=15)
        self.device = device
        if path_model:
            # Carica i pesi del modello pre-addestrato
            self.model.load_state_dict(torch.load(path_model, map_location=device, weights_only=False))
            self.model = self.model.to(device)
            self.model.eval()

    def infer_model(self, video_path):
        output_width = 640
        output_height = 360
        scale = 2

        kps_res = []  # Lista per memorizzare i punti chiave rilevati
        matrixes_res = []  # Lista per memorizzare le matrici di trasformazione

        total_frames = get_total_frames(video_path)
        
        for num_frame, image in enumerate(tqdm(read_video_generator(video_path), total = total_frames)):
            # Ridimensiona l'immagine
            img = cv2.resize(image, (output_width, output_height))
            inp = (img.astype(np.float32) / 255.)
            inp = torch.tensor(np.rollaxis(inp, 2, 0))
            inp = inp.unsqueeze(0)

            # Esegue il modello sul frame
            out = self.model(inp.float().to(self.device))[0]
            pred = F.sigmoid(out).detach().cpu().numpy()

            points = []  # Lista per memorizzare i punti chiave del frame corrente
            for kps_num in range(14):
                # Genera la mappa di calore per il punto chiave corrente
                heatmap = (pred[kps_num] * 255).astype(np.uint8)
                ret, heatmap = cv2.threshold(heatmap, 170, 255, cv2.THRESH_BINARY)
                circles = cv2.HoughCircles(heatmap, cv2.HOUGH_GRADIENT, dp=1, minDist=20, param1=50, param2=2,
                                           minRadius=10, maxRadius=25)
                if circles is not None:
                    x_pred = circles[0][0][0] * scale
                    y_pred = circles[0][0][1] * scale
                    if kps_num not in [8, 12, 9]:
                        x_pred, y_pred = refine_kps(image, int(y_pred), int(x_pred), crop_size=40)
                    points.append((x_pred, y_pred))
                else:
                    points.append(None)

            # Calcola la matrice di trasformazione
            matrix_trans = get_trans_matrix(points)
            points = None
            if matrix_trans is not None:
                points = cv2.perspectiveTransform(refer_kps, matrix_trans)
                matrix_trans = cv2.invert(matrix_trans)[1]
            kps_res.append(points)
            matrixes_res.append(matrix_trans)

        return matrixes_res, kps_res