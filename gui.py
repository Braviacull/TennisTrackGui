from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QScrollArea, QHBoxLayout, QSlider, QFileDialog, QLabel, QApplication, QSplitter, QInputDialog, QMenu, QCheckBox
from PySide6.QtGui import QPixmap, QPalette, QColor
from PySide6.QtCore import QUrl, Qt, QThread, QTimer
from video_operations import *
from obtain_directory import *
import os
import cv2
import sys
import subprocess
import shutil
from linked_list import Node, LinkedList
import vlc
import threading

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

        # VIDEO
        # Create a basic vlc instance
        self.istance = vlc.Instance()
        self.media = None

        # Create a media player
        self.mediaplayer = self.istance.media_player_new()

        # Create a videoframe
        self.videoframe = QWidget(self)
        self.videoframe.setAttribute(Qt.WA_OpaquePaintEvent)
        self.splitter.addWidget(self.videoframe)

        # Set a timer to check the video time
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_time)

        # video data
        self.frame_rate = None
        self.num_frame = None
        self.current_node = None
        self.end_time = None

        # Create a widget to hold the frame label and slider
        self.frames_and_slider = QWidget()
        self.frames_and_slider_layout = QHBoxLayout(self.frames_and_slider)

        # Create a label to display the current frame
        self.frame_label = QLabel("Frame: 0")
        self.frames_and_slider_layout.addWidget(self.frame_label)

        # Create a slider for video time
        self.video_slider = QSlider(Qt.Horizontal)
        self.video_slider.setRange(0, 0)
        self.frames_and_slider_layout.addWidget(self.video_slider)
        self.video_slider.valueChanged.connect(self.update_frame_label)

        # Add the frame label and slider widget to the layout
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

        # Gestione Threads e wait
        self.processing_threads = []
        self.condition = threading.Condition()

        # Create a scroll area for thumbnails
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()  # container widget for the scroll area
        self.scroll_layout = QHBoxLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)
        self.splitter.addWidget(self.scroll_area)

    def update_frame_label(self, value):
        self.frame_label.setText(f"Frame: {value}")

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

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

            video_path = os.path.join(obtain_output_dir(self), self.base_name)
            self.media = self.istance.media_new(video_path)
            self.mediaplayer.set_media(self.media)

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

            self.frame_rate = get_frame_rate(video_path)

            self.clear_layout(self.scroll_layout) # clear the layout before loading new project
            self.scene_data = [] # in this way, if you load more than once, the scene_data are not appended

            # GET SCENES FROM SCENE FILE
            with open(self.scene_file_path, "r") as scene_file:
                base = 0	
                for line in scene_file:
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
                    self.num_frame = end

                    # scene_data[i] = [LinkedList, QPushButton, bool]
                    scene = [start, end]
                    macro_scene = LinkedList()
                    macro_scene.append_to_list(scene)

                    dummy = [0,100] # for testing
                    macro_scene.append_to_list(dummy)

                    button = QPushButton(f"{start}-{end}")
                    button.clicked.connect(self.play_macro_scene)
                    self.scroll_layout.addWidget(button)

                    data = [macro_scene, button, False]

                    self.scene_data.append(data)
                    
            self.video_slider.setRange(0, self.num_frame)

    def play_macro_scene(self):
        button = self.sender()
        start = None
        for data in self.scene_data:
            if data[1] == button:
                self.current_node = data[0].head

        if self.current_node is None:
            print ("Error: macroscene is None")
            return
        
        self.play_scene()

    def play_scene(self):
        start, end = self.current_node.data
        print (f"Playing segment {start}-{end}")
        if start is None or end is None:
            print ("Error: start is None or end is None")
            return

        # bind the vlc media player to the videoframe
        if sys.platform.startswith('linux'):  # for Linux using the X Server
            self.mediaplayer.set_xwindow(self.videoframe.winId())
        elif sys.platform == "win32":  # for Windows
            self.mediaplayer.set_hwnd(self.videoframe.winId()) # handle to the window
        elif sys.platform == "darwin":  # for MacOS
            self.mediaplayer.set_nsobject(int(self.videoframe.winId()))

        start_time = frame_to_time(start, self.frame_rate)
        self.end_time = frame_to_time(end, self.frame_rate)

        if not self.mediaplayer.is_playing():
            self.mediaplayer.play()
        self.mediaplayer.set_time(start_time) # it only works if the video is playing and takes a float value (time) between 0 and 1

        self.timer.start(100) # check the video time every 100 ms

    def play_next_scene(self):
        self.current_node = self.current_node.next # update the current node
        if self.current_node is None:
            print ("There are no more scenes")
            return
        self.play_scene()

    def check_time(self):
        epsilon = 0.01 # 10 ms for calculation errors
        current_time = self.mediaplayer.get_time()
        print (f"Current time: {current_time} [ms]")
        self.video_slider.setValue(time_to_frame(current_time, self.frame_rate))
        if current_time >= (self.end_time - epsilon):
            self.mediaplayer.pause()
            self.timer.stop()
            print ("Scene ended")
            self.video_slider.setValue(time_to_frame(self.end_time, self.frame_rate))
            self.play_next_scene()

            
# Create the application and main window, then run the application
app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()