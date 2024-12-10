from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QScrollArea, QHBoxLayout, QSlider, QFileDialog, QLabel, QApplication, QSplitter, QInputDialog, QMenu, QCheckBox
from PySide6.QtGui import QPixmap
from PySide6.QtCore import QUrl, Qt, QThread
from video_operations import *
from obtain_directory import *
import os
import cv2
import sys
import subprocess
import shutil

class ProcessingThread(QThread):
    def __init__(self, scene_path, output_path):
        super().__init__()
        self.scene_path = scene_path
        self.output_path = output_path

    def run(self):
        ball_model_path = "model_best.pt"
        court_model_path = "model_tennis_court_det.pt"
        bounce_model_path = "ctb_regr_bounce.cbm"

        command = [
            "python", "main.py",
            "--path_ball_track_model", ball_model_path,
            "--path_court_model", court_model_path,
            "--path_bounce_model", bounce_model_path,
            "--path_input_video", self.scene_path,
            "--path_output_video", self.output_path
        ]
        subprocess.run(command)

        os.remove(self.scene_path)
        os.rename(self.output_path, self.scene_path)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set the window title
        self.setWindowTitle("TennisTrack")

        # Set the initial size of the main window
        self.resize(800, 600)

        # Create the central widget and set it as the central widget of the main window
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Create a vertical layout for the central widget
        self.layout = QVBoxLayout(self.central_widget)

        # Create a splitter to hold the video player and thumbnails
        self.splitter = QSplitter(Qt.Vertical)
        self.layout.addWidget(self.splitter)

        # Create a video player
        self.video_widget = QVideoWidget()
        self.splitter.addWidget(self.video_widget)

        # Create a media player
        self.media_player = QMediaPlayer()
        self.media_player.setVideoOutput(self.video_widget)

        # Create a widget to hold the frame label and slider
        self.frames_and_slider = QWidget()
        self.frames_and_slider_layout = QHBoxLayout(self.frames_and_slider)

        # Create a label to display the current frame
        self.frame_label = QLabel("Frame: 0")
        self.frames_and_slider_layout.addWidget(self.frame_label)

        # Create a slider for video position
        self.video_slider = QSlider(Qt.Horizontal)
        self.video_slider.setRange(0, 0)
        self.frames_and_slider_layout.addWidget(self.video_slider)
        self.video_slider.valueChanged.connect(self.update_frame_label)

        # Add the frame label and slider widget to the splitter
        self.splitter.addWidget(self.frames_and_slider)

        # Create a list of buttons to activate
        self.buttons_to_activate = []

        # BUTTONS

        # New project button
        self.new_project_button = QPushButton("New Project")
        self.new_project_button.clicked.connect(self.create_new_project)
        self.layout.addWidget(self.new_project_button)

        # Load project button
        self.load_project_button = QPushButton("Load Project")
        self.load_project_button.clicked.connect(self.load_project)
        self.layout.addWidget(self.load_project_button)

        # Jolly button
        self.jolly_button = QPushButton("Jolly")
        # self.jolly_button.clicked.connect(self.jolly)
        self.layout.addWidget(self.jolly_button)
        self.jolly_button.setEnabled(False)
        self.buttons_to_activate.append(self.jolly_button)

        # Directories and paths
        self.project_path = None

        # ANDRÁ SOSTITUITO CON UNA LISTA DI SCENE (first frame, last frame, path, thumbnail, container, selected)
        # Scene data
        self.scene_data = None # vettore che verrá popolato con tuple:(scene_path, thumbnail_path, container, selected)

        # Gestione Threads
        self.processing_threads = []

        # Create a scroll area for thumbnails
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()  # container widget for the scroll area
        self.scroll_layout = QHBoxLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)
        self.splitter.addWidget(self.scroll_area)
        self.scroll_area.resize(150, 150)

    def update_frame_label(self, value):
        self.frame_label.setText(f"Frame: {value}")

    def pre_processing(self, base_name):
        input_path = os.path.join(obtain_input_dir(self), base_name)
        output_path = os.path.join(obtain_output_dir(self), base_name)
        if not os.path.isfile(input_path):
            print("Input file not found")
            return
        model_path = "model_tennis_court_det.pt"
        if not os.path.isfile(model_path):
            print("Model file not found")
        command = [
            "python", "preProcessing.py",
            "--path_court_model", model_path,
            "--path_input_video", input_path,
            "--path_output_video", output_path
        ]
        subprocess.run(command)

    def create_new_project(self):
        project_name, ok = QInputDialog.getText(self, "New Project", "Enter project name:")
        project_path = os.path.join("Projects", project_name)
        if os.path.isdir(project_path) and ok:
            print("Project already exists, CHOOSE ANOTHER NAME FOR YOUR PROJECT")
            return
        if ok and project_name:
            inputs_dir = os.path.join(os.path.dirname("Projects"), "Inputs")
            input_video_path = QFileDialog.getOpenFileName(self, "Open Video File", inputs_dir, "Video Files (*.mp4 *.avi *.mov)")[0]

            # Create project directories
            os.makedirs(obtain_input_dir(self), exist_ok=True)
            os.makedirs(obtain_output_dir(self), exist_ok=True)

            if input_video_path:
                shutil.copy(input_video_path, obtain_input_dir(self))
                base_name = os.path.basename(input_video_path)
                self.pre_processing(base_name)
                self.load_project(project_path)

    def load_project(self, project_path=None):
        if not project_path:
            project_path = QFileDialog.getExistingDirectory(self, "Select Project Directory", "projects")
        if project_path:
            if not os.path.abspath(os.path.dirname(project_path)) == os.path.abspath("Projects"):
                print("Invalid project directory")
                return

            self.project_path = project_path

            # Check if the input and output directories exist
            if not os.path.exists(obtain_input_dir(self)):
                print(f"Input directory does not exists")
                return

            if not os.path.exists(obtain_output_dir(self)):
                print(f"Output directory does not exists")
                return

            base_name = os.listdir(obtain_output_dir(self))[0]
            if not base_name:
                print("No video files found in the output directory")
                return
            video_path = os.path.join(obtain_output_dir(self), base_name)

            num_frames = get_frame_count(video_path)
            self.video_slider.setRange(0, num_frames)

# Create the application and main window, then run the application
app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()