from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QScrollArea, QHBoxLayout, QSlider, QFileDialog, QLabel, QApplication, QSplitter, QInputDialog, QMenu, QCheckBox
from PySide6.QtGui import QPixmap
from PySide6.QtCore import QUrl, Qt, QThread
from video_operations import write, read_video
from obtain_directory import *
import os
import cv2
import sys
import subprocess
import shutil
from linked_list import Node, LinkedList

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

        # Directories and paths
        self.project_path = None
        self.base_name = None  # path del video pre-processato
        self.scene_file_path = None  # path del file scenes.txt
        self.scene_data = [] # vettore di vettori [[start_frame, end_frame] [button]]

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

    def pre_processing(self):
        input_path = os.path.join(obtain_input_dir(self), self.base_name)
        output_path = os.path.join(obtain_output_dir(self), self.base_name)
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
            "--path_output_video", output_path,
            "--path_scene_file", self.scene_file_path
        ]
        subprocess.run(command)

    def create_new_project(self):
        project_name, ok = QInputDialog.getText(self, "New Project", "Enter project name:")
        project_path = os.path.join("Projects", project_name)
        if os.path.isdir(project_path) and ok:
            print("Project already exists, CHOOSE ANOTHER NAME FOR YOUR PROJECT")
            return
        if ok and project_name:
            self.project_path = project_path
            self.scene_file_path = os.path.join(self.project_path, "scenes.txt")

            inputs_dir = os.path.join(os.path.dirname("Projects"), "Inputs")
            input_video_path = QFileDialog.getOpenFileName(self, "Open Video File", inputs_dir, "Video Files (*.mp4 *.avi *.mov)")[0]

            # Create project directories
            os.makedirs(obtain_input_dir(self), exist_ok=True)
            os.makedirs(obtain_output_dir(self), exist_ok=True)

            # crea il file scenes.txt
            with open(self.scene_file_path, "w") as scene_file:
                pass

            if input_video_path:
                self.base_name = os.path.basename(input_video_path)
                shutil.copy(input_video_path, obtain_input_dir(self))
                self.pre_processing()

                self.load_project(project_path)

    def load_project(self, project_path=None):
        if not project_path:
            project_path = QFileDialog.getExistingDirectory(self, "Select Project Directory", "projects")
        if project_path:
            self.project_path = project_path
            self.scene_file_path = os.path.join(self.project_path, "scenes.txt")
            self.base_name = os.listdir(obtain_output_dir(self))[0]

            # Check if the project directory choosen is in the Projects directory
            if not os.path.abspath(os.path.dirname(project_path)) == os.path.abspath("Projects"):
                print("Invalid project directory")
                return
            
            # Check if the output directory contains video files
            if not self.base_name:
                print("No video files found in the output directory")
                return
            
            # Check if the input and output directories exist
            if not os.path.exists(obtain_input_dir(self)):
                print (obtain_input_dir(self))
                print(f"Input directory does not exists")
                return

            if not os.path.exists(obtain_output_dir(self)):
                print(f"Output directory does not exists")
                return

            self.clear_layout(self.scroll_layout) # clear the layout before loading new project

            last_frame = 0 # used to set the range of the video slider
            # GET SCENES FROM SCENE FILE
            self.scene_data = [] # in this way, if you load more than once, the scene_data are not appended
            with open(self.scene_file_path, "r") as scene_file:
                base = 0	
                for i, line in enumerate(scene_file):
                    start, end = map(int, line.split())
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
                    last_frame = end

                    # scene_data[i] = [LinkedList, QPushButton, bool]
                    scene = [start, end]
                    macro_scene = LinkedList()
                    macro_scene.append_to_list(scene)

                    button = QPushButton(f"{start}-{end}")
                    button.clicked.connect(self.play_macro_scene)
                    self.scroll_layout.addWidget(button)

                    data = [macro_scene, button, False]

                    self.scene_data.append(data)
                    
            self.video_slider.setRange(0, last_frame)

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def play_macro_scene(self):
        for data in self.scene_data:
            list = data[0]
            list.show()
            
# Create the application and main window, then run the application
app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()