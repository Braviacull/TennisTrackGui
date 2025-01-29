import os
import sys
import subprocess
import shutil
import threading
import vlc

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton, QScrollArea, QHBoxLayout, 
    QSlider, QFileDialog, QLabel, QApplication, QSplitter, QInputDialog, QCheckBox, QMessageBox
)
from PySide6.QtCore import Qt, QThread, QTimer

from costants import *
from video_operations import *
from obtain_directory import *
from play import *
from linked_list import LinkedList
from utils import (
    get_selected_scenes_data, remove_container_from_layout, activate_buttons, deactivate_buttons,
    clear_layout, get_macro_scene_correct_name
)

class ProcessingThread(QThread):
    def __init__(self, input_path, output_path, application):
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.application = application

    def run(self):
        self.application.setWindowTitle("PROCESSING. THIS MAY TAKE A WHILE, YOU CAN CONTINUE USING THE APPLICATION...")

        ball_model_path = "model_best.pt"
        court_model_path = "model_tennis_court_det.pt"
        bounce_model_path = "ctb_regr_bounce.cbm"

        command = [
            "python", "main.py",
            "--path_ball_track_model", ball_model_path,
            "--path_court_model", court_model_path,
            "--path_bounce_model", bounce_model_path,
            "--path_input_video", self.input_path,
            "--path_output_video", self.output_path
        ]
        subprocess.run(command)

        self.application.setWindowTitle("PROCESSED, PLEASE RELOAD THE PROJECT TO SEE THE CHANGES, BUT REMEMBER TO SAVE IT FIRST")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("TennisTrack")

        # Create the main window
        # Set the initial size of the main window
        self.resize(800, 600)
        # Create the central widget and set it as the central widget of the main window
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        # Create a vertical layout for the central widget
        self.layout = QVBoxLayout(self.central_widget)
        # Create a splitter to hold the video frame the slider and the scroll area
        self.splitter = QSplitter(Qt.Vertical)
        self.layout.addWidget(self.splitter)

        # Video player
        # Create a basic vlc instance
        self.istance = vlc.Instance()
        self.media = None
        # Create a media player
        self.mediaplayer = self.istance.media_player_new()
        # Create a videoframe
        self.videoframe = QWidget(self)
        self.videoframe.setAttribute(Qt.WA_OpaquePaintEvent)
        # Add the videoframe to the splitter
        self.splitter.addWidget(self.videoframe)
        self.splitter.setStretchFactor(0, 1)  # Il video player occupa tutto lo spazio

        # frame label, slider and play/pause button
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
        self.video_slider.sliderPressed.connect(self.video_slider_touched)
        # self.video_slider.sliderReleased.connect(self.play)
        self.video_slider.sliderMoved.connect(self.slider_moved)
        # Create a button to play and pause the video
        self.play_and_pause_button = QPushButton("Play/Pause")
        self.play_and_pause_button.clicked.connect(self.play_and_pause)
        self.frames_and_slider_layout.addWidget(self.play_and_pause_button)
        self.play_and_pause_button.setEnabled(False)
        # Add the frame label and slider widget to the layout
        self.splitter.addWidget(self.frames_and_slider)

        # Create a scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_content = QWidget()  # container widget for the scroll area
        self.scroll_layout = QHBoxLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)
        self.splitter.addWidget(self.scroll_area)

        # BUTTONS
        # Create a list of buttons to activate
        self.buttons_to_activate = []
        self.buttons = []
        # Create a horizontal layout for the buttons
        self.buttons_layout = QHBoxLayout()
        # New project button
        self.new_project_button = QPushButton("New Project")
        self.new_project_button.clicked.connect(self.create_new_project)
        self.buttons_layout.addWidget(self.new_project_button)
        # Load project button
        self.load_project_button = QPushButton("Load Project")
        self.load_project_button.clicked.connect(self.load_project)
        self.buttons_layout.addWidget(self.load_project_button)
        # Save project button
        self.save_project_button = QPushButton("Save Project")
        self.save_project_button.clicked.connect(self.save_project)
        self.buttons_layout.addWidget(self.save_project_button)
        self.buttons_to_activate.append(self.save_project_button)
        self.save_project_button.setEnabled(False)
        # Process button
        self.process_button = QPushButton("Process")
        self.process_button.clicked.connect(self.start_processing_thread)
        self.buttons_layout.addWidget(self.process_button)
        self.buttons_to_activate.append(self.process_button)
        self.process_button.setEnabled(False)
        # Select all button
        self.select_all_button = QPushButton("Select All")
        self.select_all_button.clicked.connect(self.select_all)
        self.buttons_layout.addWidget(self.select_all_button)
        self.buttons_to_activate.append(self.select_all_button)
        self.select_all_button.setEnabled(False)
        # Deselect all button
        self.deselect_all_button = QPushButton("Deselect All")
        self.deselect_all_button.clicked.connect(self.deselect_all)
        self.buttons_layout.addWidget(self.deselect_all_button)
        self.buttons_to_activate.append(self.deselect_all_button)
        self.deselect_all_button.setEnabled(False)
        # Play selected scenes button
        self.play_selected_button = QPushButton("Play Selected")
        self.play_selected_button.clicked.connect(self.select_and_play)
        self.buttons_layout.addWidget(self.play_selected_button)
        self.buttons_to_activate.append(self.play_selected_button)
        self.play_selected_button.setEnabled(False)
        # Create macroscene button
        self.create_macroscene_button = QPushButton("Create Macroscene")
        self.create_macroscene_button.clicked.connect(self.obtain_scene_list)
        self.buttons_layout.addWidget(self.create_macroscene_button)
        self.buttons_to_activate.append(self.create_macroscene_button)
        self.create_macroscene_button.setEnabled(False)
        # Merge button
        self.merge_button = QPushButton("Merge")
        self.merge_button.clicked.connect(self.merge)
        self.buttons_layout.addWidget(self.merge_button)
        self.buttons_to_activate.append(self.merge_button)
        self.merge_button.setEnabled(False)
        # Group button
        self.group_button = QPushButton("Group")
        self.group_button.clicked.connect(self.group)
        self.buttons_layout.addWidget(self.group_button)
        self.buttons_to_activate.append(self.group_button)
        self.group_button.setEnabled(False)
        # Split button
        self.split_button = QPushButton("Split")
        self.split_button.clicked.connect(self.split) # TODO
        self.buttons_layout.addWidget(self.split_button)
        self.buttons_to_activate.append(self.split_button)
        self.split_button.setEnabled(False)
        # Jolly button
        self.jolly_button = QPushButton("Jolly")
        self.jolly_button.clicked.connect(self.jolly)
        self.buttons_layout.addWidget(self.jolly_button)
        self.buttons_to_activate.append(self.jolly_button)
        self.jolly_button.setEnabled(False)

        # Add the buttons layout to the main layout
        self.layout.addLayout(self.buttons_layout)

        # Directories, paths and base names
        self.project_path = None
        self.scene_file_path = None  # path del file scenes.txt
        self.base_name = None  # path del video pre-processato

        # Scene data MAIN DATA STRUCTURE
        self.scene_data = [] # [[LinkedList, container_widget, checked]]

        # Gestione Threads e wait
        self.processing_threads = []
        self.condition = threading.Condition()

        # video data
        self.frame_rate = None
        self.num_frames = None
        self.current_data = None # [LinkedList, container_widget, checked]
        self.current_node = None
        self.end_time = None
        # Set a timer to check the video time
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_time)

        # Gestione Threads
        self.processing_threads = []

    def video_slider_touched(self):
        time = frame_to_time(self.video_slider.value(), self.frame_rate)
        self.mediaplayer.set_time(time)
        if self.mediaplayer.is_playing():
            self.mediaplayer.pause()
            self.timer.stop()
            self.play_and_pause_button.setText("▶️")
    
    def slider_moved(self):
        frame = self.video_slider.value()
        time = frame_to_time(frame, self.frame_rate)
        self.mediaplayer.set_time(time)

    def play_and_pause(self):
        if self.mediaplayer.is_playing():
            self.mediaplayer.pause()
            self.timer.stop()
            self.play_and_pause_button.setText("▶️")
        elif not self.mediaplayer.is_playing():
            self.mediaplayer.play()
            self.timer.start(100)
            self.play_and_pause_button.setText("⏸")

    def update_frame_label(self, value):
        self.frame_label.setText(f"Frame: {value}")

    def check_scene(self, state):
        container = self.sender().parentWidget()
        for data in self.scene_data:
            if data[1] == container:
                data[2] = not data[2]
                break

    def play_macro_scene(self):
        container = self.sender().parentWidget()
        for data in self.scene_data:
            if data[1] == container: # uses container to recognize the scene
                self.current_data = data
                self.current_node = data[0].head

        if self.current_node is None:
            print ("Error: macroscene is None")
            return
        
        play_scene(self)

    def check_time(self):
        epsilon = 0.01 # 10 ms for calculation errors
        current_time = self.mediaplayer.get_time()
        # print (f"Current time: {current_time} [ms]")
        self.video_slider.setValue(time_to_frame(current_time, self.frame_rate))
        if current_time >= (self.end_time - epsilon):
            self.mediaplayer.pause()
            self.timer.stop()
            print ("Scene ended")
            end = self.current_node.data[1]
            self.video_slider.setValue(end)
            play_next_scene(self)

    def obtain_scene_list(self):  # self.scene_data = [[LinkedList, container, bool]]
        data = []
        scene_list = LinkedList()
        # asks the user to enter the name of the macroscene
        macroscene_name, ok = QInputDialog.getText(self, "Macroscene Name", "Enter the name of the macroscene:")
        if not ok:
            return
        while True:
            # asks the user to enter the start and end frame of the scene
            start, ok = QInputDialog.getInt(self, "Start Frame", "Enter the start frame:", 0, 0, self.num_frames)
            if not ok:
                return
            end, ok = QInputDialog.getInt(self, "End Frame", "Enter the end frame:", 0, 0, self.num_frames)
            if not ok:
                return
            if start >= end:
                print("Invalid scene: end frame must be greater than start frame")
                return
            scene = [start, end]
            scene_list.append_to_list(scene)
            # asks the user if he wants to add another scene to the macroscene
            reply = QMessageBox.question(self, "Add another scene", "Do you want to add another scene to the macroscene?",
                                        QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.No:
                break
        print("Macroscene created")
        data.append(scene_list)

        self.create_macroscene(scene_list, macroscene_name, 0)

    def create_macroscene(self, scene_list, name, position):
        # Create a list to hold the macroscene data
        data = []
        
        # Add the scene list to the data list
        data.append(scene_list)
        
        # Create a container widget for the button and checkbox
        container = QWidget()
        container_layout = QHBoxLayout(container)
        
        # Create a button with the name of the macroscene and connect its clicked signal
        button = QPushButton(name)
        button.clicked.connect(self.play_macro_scene)
        container_layout.addWidget(button)
        
        # Create a checkbox and connect its stateChanged signal
        checkbox = QCheckBox()
        checkbox.stateChanged.connect(self.check_scene)
        container_layout.addWidget(checkbox)
        
        # Add the container to the data list
        data.append(container)
        
        # Insert the container into the scroll_layout at the specified position
        self.scroll_layout.insertWidget(position, container)
        
        # Add a boolean value to indicate whether the scene is selected
        data.append(False)
        
        # Insert the macroscene data into the scene_data list at the specified position
        self.scene_data.insert(position, data)

    def group (self):
        selected_scenes_data = get_selected_scenes_data(self)
        if len(selected_scenes_data) < 2:
            print ("Select at least two scenes")
            return
        
        resulting_name = ""
        
        new_macroscene = LinkedList()
        for data in selected_scenes_data:
            current_node = data[0].head
            button = data[1].findChild(QPushButton)
            resulting_name += (" | " + button.text())
            while current_node:
                new_macroscene.append_to_list(current_node.data)
                current_node = current_node.next

        # remove the initial two spaces
        resulting_name = resulting_name[3:]

        self.create_macroscene(new_macroscene, resulting_name, 0)

    def merge (self):
        selected_scenes_data = get_selected_scenes_data(self)
        if len(selected_scenes_data) < 2:
            print ("Select at least two scenes")
            return
        
        resulting_name = ""
        
        new_macroscene = LinkedList()
        for data in selected_scenes_data:
            current_node = data[0].head
            button = data[1].findChild(QPushButton)
            resulting_name += (" | " + button.text())
            while current_node:
                new_macroscene.append_to_list(current_node.data)
                current_node = current_node.next

        # remove the initial two spaces
        resulting_name = resulting_name[3:]

        resulting_scene_data = selected_scenes_data[0]
        container = resulting_scene_data[1]
        button = container.findChild(QPushButton)
        button.setText(resulting_name)

        checkbox = container.findChild(QCheckBox)
        checkbox.setChecked(False)
        resulting_scene_data[0] = new_macroscene

        for data in selected_scenes_data[1:]: # work with a copy of the list for deleting elements
            remove_container_from_layout(data[1], self.scroll_layout)
            self.scene_data.remove(data)

    def split(self):
        if self.mediaplayer.is_playing(): # pause the video if necessary
            self.play_and_pause()

        start_frame = self.current_node.data[0]
        current_frame = time_to_frame(self.mediaplayer.get_time(), self.frame_rate)
        end_frame = self.current_node.data[1]

        self.current_node.set_data([start_frame, current_frame])
        second_scene = [current_frame + 1, end_frame]
        self.current_data[0].insert_after_node(self.current_node, second_scene)

        button_text = get_macro_scene_correct_name(self.current_data[0].head)

        button = self.current_data[1].findChild(QPushButton)
        button.setText(button_text)

        self.play_and_pause_button.setEnabled(False)
        self.play_and_pause_button.setText("Play/Pause")
        
    def jolly(self): # self.scene_data = [[LinkedList, container, bool]]
        for data in self.scene_data:
            list = data[0]
            container = data[1]
            button = container.findChild(QPushButton)
            print (button.text())
            list.print_list()
            print (data[2])
            print ("---")
        print ("\n")

    def select_and_play(self):
        merged_scenes_macroscenes = LinkedList()
        for data in self.scene_data:
            if data[2]:
                current_node = data[0].head
                while current_node:
                    merged_scenes_macroscenes.append_to_list(current_node.data)
                    current_node = current_node.next

        self.current_node = merged_scenes_macroscenes.head

        if self.current_node is None:
            print ("Select some checkboxes")
            return
        
        # disattiva il bottone split
        play_scene(self)
        # riattiva il bottone split

    def select_all(self):
        for data in self.scene_data:
            checkbox = data[1].findChild(QCheckBox)
            checkbox.setChecked(True)

    def deselect_all(self):
        for data in self.scene_data:
            checkbox = data[1].findChild(QCheckBox)
            checkbox.setChecked(False)
        
    def pre_processing(self):
        input_path = os.path.join(obtain_input_dir(self), self.base_name)
        output_path = os.path.join(obtain_output_dir(self), PRE_PROCESSED)
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

        self.setWindowTitle("PREPROCESSING. THIS MAY TAKE A WHILE, PLEASE WAIT...")

        subprocess.run(command)

        self.setWindowTitle("TennisTrack")

    def start_processing_thread(self):
        input_path = os.path.join(obtain_output_dir(self), PRE_PROCESSED)
        output_path = os.path.join(obtain_output_dir(self), PROCESSED)
        processing_thread = ProcessingThread(input_path, output_path, self)
        self.processing_threads.append(processing_thread)  # need to keep a reference to the thread
        processing_thread.start()

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
                self.load_project(self.project_path)

    def load_project(self, project_path=None):
        if not project_path:
            project_path = QFileDialog.getExistingDirectory(self, "Select Project Directory", "projects")
        if project_path:
            self.project_path = project_path
            self.scene_file_path = os.path.join(self.project_path, "scenes.txt")
            self.base_name = PRE_PROCESSED
            
            # If the processed video exists, set it as the base name
            processed_path = os.path.join(obtain_output_dir(self), PROCESSED)
            if os.path.isfile(processed_path):
                self.base_name = PROCESSED

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

            clear_layout(self.scroll_layout) # clear the layout before loading new project
            self.scene_data = [] # in this way, if you load more than once, the scene_data are not appended

            activate_buttons(self.buttons_to_activate)

            self.num_frames = 0
            with open(self.scene_file_path, "r") as scene_file:
                for line in scene_file:
                    scenes = line.split()
                    macro_scene = LinkedList()

                    # Popola la linked list con le scene
                    for i in range(0, len(scenes), 2):
                        start = int(scenes[i])
                        end = int(scenes[i + 1])

                        # serve per la create macroscene
                        self.num_frames = end

                        scene = [start, end]
                        macro_scene.append_to_list(scene)

                    container = QWidget()
                    container_layout = QHBoxLayout(container)

                    # Crea il testo del pulsante con i trattini tra le coppie di numeri
                    button_text = ' | '.join(f"{scenes[j]}-{scenes[j+1]}" for j in range(0, len(scenes), 2))
                    button = QPushButton(button_text.strip())
                    button.clicked.connect(self.play_macro_scene)
                    container_layout.addWidget(button)

                    checkbox = QCheckBox()
                    container_layout.addWidget(checkbox)
                    checkbox.stateChanged.connect(self.check_scene)

                    self.scroll_layout.addWidget(container)

                    data = [macro_scene, container, False] # [LinkedList, container, checked]
                    self.scene_data.append(data)

            self.save_project()

            self.play_and_pause_button.setEnabled(False)
            self.play_and_pause_button.setText("Play/Pause")

    def save_project(self):
        with open(self.scene_file_path, "w") as scene_file:
            for data in self.scene_data:
                current_node = data[0].head
                while current_node:
                    start, end = current_node.data
                    scene_file.write(f"{start} {end} ")
                    current_node = current_node.next
                scene_file.write("\n")

if __name__ == "__main__":
    # Create the application and main window, then run the application
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()