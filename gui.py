import os
import sys
import subprocess
import shutil
import threading
import vlc

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton, QScrollArea, QHBoxLayout, 
    QSlider, QFileDialog, QLabel, QApplication, QSplitter, QInputDialog, QCheckBox, QMessageBox, 
    QMenu, QMenuBar
)
from PySide6.QtGui import QAction, QIcon
from PySide6.QtCore import Qt, QThread, QTimer
from functools import partial

from costants import *
from utils.video_operations import *
from utils.obtain_directory import *
from utils.play import *
from utils.linked_list import LinkedList
from utils.utils import *
from utils.tennis_point_system import *
from classes.scene_data_class import SceneData
from typing import List
from classes.filter_dialog_class import *
from classes.set_point_window_class import *

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

        # BUTTONS
        # Create a list of buttons to activate
        self.buttons_to_activate = []
        self.buttons_to_deactivate_when_points = [] # disactivate when scenes are points
        self.buttons_to_activate_when_points = [] # activate when scenes are points
        # Create a menu bar
        self.menu_bar = QMenuBar()
        self.setMenuBar(self.menu_bar)

        # Create menus
        self.project_menu = self.menu_bar.addMenu("Project")
        self.select_menu = self.menu_bar.addMenu("Select")
        self.edit_menu = self.menu_bar.addMenu("Edit")
        self.video_menu = self.menu_bar.addMenu("Video")
        self.match_menu = self.menu_bar.addMenu("Match")
        self.others_menu = self.menu_bar.addMenu("Others")

        # Project menu actions
        self.new_project_action = QAction("New Project", self)
        self.new_project_action.triggered.connect(self.create_new_project)
        self.project_menu.addAction(self.new_project_action)

        self.load_project_action = QAction("Load Project", self)
        self.load_project_action.triggered.connect(self.load_project)
        self.project_menu.addAction(self.load_project_action)

        self.save_project_action = QAction("Save Project", self)
        self.save_project_action.triggered.connect(self.save_project)
        self.project_menu.addAction(self.save_project_action)
        self.buttons_to_activate.append(self.save_project_action)
        self.save_project_action.setEnabled(False)

        # Select menu actions
        self.select_all_action = QAction("Select All", self)
        self.select_all_action.triggered.connect(self.select_all)
        self.select_menu.addAction(self.select_all_action)
        self.buttons_to_activate.append(self.select_all_action)
        self.select_all_action.setEnabled(False)

        self.deselect_all_action = QAction("Deselect All", self)
        self.deselect_all_action.triggered.connect(self.deselect_all)
        self.select_menu.addAction(self.deselect_all_action)
        self.buttons_to_activate.append(self.deselect_all_action)
        self.deselect_all_action.setEnabled(False)

        # Edit menu actions
        self.delete_selected_action = QAction("Delete Selected", self)
        self.delete_selected_action.triggered.connect(self.delete_selected)
        self.edit_menu.addAction(self.delete_selected_action)
        self.buttons_to_activate.append(self.delete_selected_action)
        self.delete_selected_action.setEnabled(False)
        self.buttons_to_deactivate_when_points.append(self.delete_selected_action)

        self.create_macroscene_action = QAction("Create Macroscene", self)
        self.create_macroscene_action.triggered.connect(self.obtain_scene_list_and_create_macroscene)
        self.edit_menu.addAction(self.create_macroscene_action)
        self.buttons_to_activate.append(self.create_macroscene_action)
        self.create_macroscene_action.setEnabled(False)
        self.buttons_to_deactivate_when_points.append(self.create_macroscene_action)

        self.merge_action = QAction("Merge", self)
        self.merge_action.triggered.connect(self.merge)
        self.edit_menu.addAction(self.merge_action)
        self.buttons_to_activate.append(self.merge_action)
        self.merge_action.setEnabled(False)
        self.buttons_to_deactivate_when_points.append(self.merge_action)

        self.group_action = QAction("Group", self)
        self.group_action.triggered.connect(self.group)
        self.edit_menu.addAction(self.group_action)
        self.buttons_to_activate.append(self.group_action)
        self.group_action.setEnabled(False)
        self.buttons_to_deactivate_when_points.append(self.group_action)

        self.split_action = QAction("Split", self)
        self.split_action.triggered.connect(self.split)
        self.edit_menu.addAction(self.split_action)
        self.buttons_to_activate.append(self.split_action)
        self.split_action.setEnabled(False)
        self.buttons_to_deactivate_when_points.append(self.split_action)

        # Video menu actions
        self.play_selected_action = QAction("Play Selected", self)
        self.play_selected_action.triggered.connect(self.select_and_play)
        self.video_menu.addAction(self.play_selected_action)
        self.buttons_to_activate.append(self.play_selected_action)
        self.play_selected_action.setEnabled(False)

        self.process_action = QAction("Process", self)
        self.process_action.triggered.connect(self.start_processing_thread)
        self.video_menu.addAction(self.process_action)
        self.buttons_to_activate.append(self.process_action)
        self.process_action.setEnabled(False)

        self.generate_video_action = QAction("Generate Video", self)
        self.generate_video_action.triggered.connect(self.generate_video)
        self.video_menu.addAction(self.generate_video_action)
        self.buttons_to_activate.append(self.generate_video_action)
        self.generate_video_action.setEnabled(False)

        # Match menu actions
        self.set_points_action = QAction("Set Points", self)
        self.set_points_action.triggered.connect(self.initiate_set_points)
        self.match_menu.addAction(self.set_points_action)
        self.buttons_to_activate.append(self.set_points_action)
        self.buttons_to_deactivate_when_points.append(self.set_points_action)
        self.set_points_action.setEnabled(False)

        # Others menu actions
        self.jolly_action = QAction("Jolly", self)
        self.jolly_action.triggered.connect(self.jolly)
        self.others_menu.addAction(self.jolly_action)
        self.buttons_to_activate.append(self.jolly_action)
        self.jolly_action.setEnabled(False)

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
        self.scroll_layout = QGridLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)
        self.splitter.addWidget(self.scroll_area)
        self.scroll_area_widgets = []
        self.scroll_area.resizeEvent = self.on_resize # Connect the resize event

        # Directories, paths and base names
        self.project_path = None
        self.scene_file_path = None  # path del file scenes.txt
        self.points_file_path = None  # path del file points.txt
        self.base_name = None  # path del video pre-processato

        # Scene data MAIN DATA STRUCTURE
        self.scene_data: List[SceneData] = []
        self.modified = False

        # Gestione Threads e wait
        self.processing_threads = []
        self.condition = threading.Condition()

        # video data
        self.frame_rate = None
        self.num_frames = None
        self.current_data = None # [LinkedList, container_widget, checked, winner]
        self.current_node = None
        self.end_time = None

        # Set a timer to check the video time
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_time)

        # Indicates if every scene is a point or if the scenes needs to be modified by the user
        self.set_point_window = SetPointWindow(self)
        self.scene_is_point = False # If True, the scenes cannot be modified anymore (no merge, split, etc.)
        self.player1 = "Player 1"
        self.player2 = "Player 2"
        self.score = [0,0] # the game score
        self.games = [0,0] # the games score
        self.sets = [0,0] # the sets score
        self.max_sets = 2 # the maximum number of sets
        self.tiebreak = False # if True, the current set is a tiebreak
        self.winner = None # the winner of the match

        # Gestione Threads
        self.processing_threads = []

    def ask_for_save(self):
        if not self.modified:
            return True
        reply = QMessageBox.question(self, 'Save Project',
                                     "Do you want to save the project before closing?",
                                     QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                                     QMessageBox.Cancel)

        if reply == QMessageBox.Yes:
            self.save_project()
            return True
        elif reply == QMessageBox.No:
            return True
        else:
            return False
        
    def ask_for_processing(self):
        reply = QMessageBox.question(self, 'Process Video',
                                     "Do you want to process the video after its creation?",
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)

        if reply == QMessageBox.Yes:
            return True
        else:
            return False
        
    def ask_for_player(self):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Player Selection")
        msg_box.setText("Who won the point?")
        
        player1_button = msg_box.addButton(self.player1, QMessageBox.ActionRole)
        player2_button = msg_box.addButton(self.player2, QMessageBox.ActionRole)
        play_point_button = msg_box.addButton("Play point", QMessageBox.ActionRole)
        msg_box.addButton(QMessageBox.Cancel)
        
        msg_box.exec()
        
        if msg_box.clickedButton() == player1_button:
            return 1
        elif msg_box.clickedButton() == player2_button:
            return 2
        elif msg_box.clickedButton() == play_point_button:
            self.select_and_play()
            return None
        else:
            return None

    def closeEvent(self, event):
        if self.ask_for_save():
            event.accept()
        else:
            event.ignore()

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
            if data.container_widget == container:
                data.checked = not data.checked
                break

    def play_macro_scene(self):
        container = self.sender().parentWidget()
        for data in self.scene_data:
            if data.container_widget == container: # uses container to recognize the scene
                self.current_data = data
                self.current_node = data.linked_list.head

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

    def obtain_scene_list_and_create_macroscene(self):
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
        # [LinkedList, container_widget, checked, winner]
        data = SceneData(scene_list, None, False, None, None, None, False)
        
        # Create a container widget for the button and checkbox
        container = QWidget()
        container_layout = QHBoxLayout(container)
        
        # Create a button with the name of the macroscene and connect its clicked signal
        button = QPushButton(name)
        button.clicked.connect(self.play_macro_scene)
        button.setContextMenuPolicy(Qt.CustomContextMenu)
        button.customContextMenuRequested.connect(self.show_context_menu)
        container_layout.addWidget(button)
        
        # Create a checkbox and connect its stateChanged signal
        checkbox = QCheckBox()
        checkbox.stateChanged.connect(self.check_scene)
        container_layout.addWidget(checkbox)
        
        # Add the container to the data list
        data.container_widget = container
        
        # Insert the container into the scroll_layout at the specified position
        if (position is None):
            self.scroll_area_widgets.append(container)
        else:
            self.scroll_area_widgets.insert(position, container)
        self.update_layout()
        
        # Insert the macroscene data into the scene_data list at the specified position
        if (position is None):
            self.scene_data.append(data)
        else:
            self.scene_data.insert(position, data)

        self.modified = True

    def on_resize(self, event):
        self.update_layout()
        event.accept()

    def update_layout(self):
        # Clear the layout
        for i in reversed(range(self.scroll_layout.count())):
            self.scroll_layout.itemAt(i).widget().setParent(None)

        # Calculate the number of columns based on the available width
        available_width = self.scroll_area.viewport().width()
        if self.scroll_area_widgets :
            widget_width = self.scroll_area_widgets[0].sizeHint().width()
            num_columns = max(1, available_width // widget_width)

            # Add widgets to the layout
            row, col = 0, 0
            for widget in self.scroll_area_widgets :
                self.scroll_layout.addWidget(widget, row, col)
                col += 1
                if col >= num_columns:
                    col = 0
                    row += 1

    def show_context_menu(self, position):
        menu = QMenu()
        button = self.sender()
        
        if self.scene_is_point == False:
            ungroup = QAction("ungroup", self)
            ungroup.triggered.connect(partial(self.ungroup_menu_action, button))
            menu.addAction(ungroup)

        elif self.scene_is_point == True:
            data = get_data_from_button(self, button)
            if data.point_winner is not None:
                set_point = QAction("set point", self)
                set_point.triggered.connect(partial(self.set_point_menu_action, data))
                menu.addAction(set_point)
            else:
                set_point = QAction("too far", self)
                menu.addAction(set_point)
        
        # Show the context menu at the position of the button
        menu.exec(button.mapToGlobal(position))

    def set_point_menu_action(self, data):
        winner = self.ask_for_player()
        if winner is None:
            return
        data.point_winner = winner
        recalculate_match_state(self)
        self.set_point_window.set_current_game_score()
        self.set_point_window.set_current_games_won()
        self.set_point_window.set_current_sets_won()
        self.modified = True

    def ungroup_menu_action(self, button):
        self.deselect_all()
        data = get_data_from_button(self, button)
        check_box = data.container_widget.findChild(QCheckBox)
        check_box.setChecked(True)
        self.ungroup()

    def group (self):
        selected_scenes_data = get_selected_scenes_data(self)
        if len(selected_scenes_data) < 2:
            print ("Select at least two scenes")
            return
        
        resulting_name = ""
        position = self.scene_data.index(selected_scenes_data[0])
        
        new_macroscene = LinkedList()
        for data in selected_scenes_data:
            current_node = data.linked_list.head
            button = data.container_widget.findChild(QPushButton)
            resulting_name += (" | " + button.text())
            while current_node:
                new_macroscene.append_to_list(current_node.data)
                current_node = current_node.next

        # remove the initial two spaces
        resulting_name = resulting_name[3:]

        self.create_macroscene(new_macroscene, resulting_name, position)

    def ungroup (self):
        selected_scenes_data = get_selected_scenes_data(self)
        if len(selected_scenes_data) < 1:
            print ("Select at least one scene")
            return
        for data in selected_scenes_data:
            position = self.scene_data.index(data)
            head = data.linked_list.head
            while head:
                scene_list = LinkedList()
                scene_list.append_to_list(head.data)

                name = f"{head.data[0]}-{head.data[1]}"
                
                position += 1

                self.create_macroscene(scene_list, name, position)
                head = head.next

    def merge (self):
        selected_scenes_data = get_selected_scenes_data(self)
        if len(selected_scenes_data) < 2:
            print ("Select at least two scenes")
            return
        
        resulting_name = ""
        
        new_macroscene = LinkedList()
        for data in selected_scenes_data:
            current_node = data.linked_list.head
            button = data.container_widget.findChild(QPushButton)
            resulting_name += (" | " + button.text())
            while current_node:
                new_macroscene.append_to_list(current_node.data)
                current_node = current_node.next

        # remove the initial two spaces
        resulting_name = resulting_name[3:]

        resulting_scene_data = selected_scenes_data[0]
        container = resulting_scene_data.container_widget
        button = container.findChild(QPushButton)
        button.setText(resulting_name)

        checkbox = container.findChild(QCheckBox)
        checkbox.setChecked(False)
        resulting_scene_data.linked_list = new_macroscene

        self.delete_selected()

    def split(self):
        if self.mediaplayer.is_playing(): # pause the video if necessary
            self.play_and_pause()

        start_frame = self.current_node.data[0]
        current_frame = time_to_frame(self.mediaplayer.get_time(), self.frame_rate)
        end_frame = self.current_node.data[1]

        self.current_node.set_data([start_frame, current_frame])
        second_scene = [current_frame + 1, end_frame]
        self.current_data.linked_list.insert_after_node(self.current_node, second_scene)

        button_text = get_macro_scene_correct_name(self.current_data.linked_list.head)

        button = self.current_data.container_widget.findChild(QPushButton)
        button.setText(button_text)

        self.deselect_all()
        self.current_data.checked = True
        self.ungroup()
        self.delete_selected()

        self.play_and_pause_button.setEnabled(False)
        self.play_and_pause_button.setText("Play/Pause")        

    def generate_video(self):
        if (self.frame_rate is None):
            print ("Error: frame rate is None")
            return
        
        project_dir = obtain_project_dir(self) # here we will save the video
        
        while(True):
            output_name, ok = QInputDialog.getText(self, "Generate Video", "Enter video name:")
            if not ok:
                return
            output_name = output_name + ".mp4"
            if (os.path.isfile(os.path.join(project_dir, output_name))):
                print ("File already exists, choose another name")
            else:
                break

        base_name = obtain_base_name(self)
        input_video_path = os.path.join(obtain_output_dir(self), base_name)
        output_video_path = os.path.join(project_dir, output_name)

        selected_scenes_data = get_selected_scenes_data(self)
        frames = []
        for data in selected_scenes_data:
            current_node = data.linked_list.head
            while current_node:
                frames.extend(range(current_node.data[0], current_node.data[1] + 1))
                current_node = current_node.next

        # Open the original video
        cap = cv2.VideoCapture(input_video_path)
        if not cap.isOpened():
            print("Error: Could not open video.")
            return
        
        # Read the selected frames
        imgs_res = []
        for frame_number in frames:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = cap.read()
            if ret:
                imgs_res.append(frame)
            else:
                print(f"Error: Could not read frame {frame_number}.")

        # Release the video capture object
        cap.release()

        # Write the frames to the new video using the write function
        write(imgs_res, self.frame_rate, output_video_path)
        print(f"Video saved to {output_video_path}")

    def initiate_set_points(self):
        self.scene_is_point = True
        deactivate_buttons(self.buttons_to_deactivate_when_points)
        activate_buttons(self.buttons_to_activate_when_points)

        # create a new file points.txt
        if not os.path.isfile(self.points_file_path):
            with open(self.points_file_path, "w") as _:
                pass
        if not os.path.isfile(self.scores_file_path):
            with open(self.scores_file_path, "w") as scores_file:
                scores_file.write("0 0\n0 0\n0 0 "+str(self.max_sets)+"\n")

        if not os.path.isfile(self.scores_file_path) or not os.path.isfile(self.points_file_path):
            print ("Error: scores file not found")
            return

        with open(self.points_file_path, "r") as points_file:
            for line in points_file:
                player, game, set, tiebreak, index = line.split()
                self.scene_data[int(index)].point_winner = int(player)
                self.scene_data[int(index)].game = int(game)
                self.scene_data[int(index)].set = int(set)
                self.scene_data[int(index)].tiebreak = tiebreak.lower() == "True"

        with open(self.scores_file_path, "r") as scores_file:
            score = scores_file.readline().split()
            self.score = [int(score[0]), int(score[1])]
            games = scores_file.readline().split()
            self.games = [int(games[0]), int(games[1])]
            sets = scores_file.readline().split()
            self.sets = [int(sets[0]), int(sets[1])]
            self.max_sets = int(sets[2])

        self.set_point_window.set_current_game_score()
        self.set_point_window.set_current_games_won()
        self.set_point_window.set_current_sets_won()
        self.set_point_window.show()

    def who_scored(self, who_scored=None):
        current_point = None
        for point in self.scene_data:
            if point.point_winner is None:
                current_point = point
                break

        if current_point is None:
            print ("All points have been played \n")
            return
        
        # select only the current point
        self.deselect_all()
        check_box = current_point.container_widget.findChild(QCheckBox)
        check_box.setChecked(True)

        # point play
        if who_scored == 0:
            self.select_and_play()
        elif who_scored is None:
            who_scored = self.ask_for_player()
        elif who_scored is not None:
            current_point.point_winner = who_scored
            current_point.game = get_current_game(self)
            current_point.set = get_current_set(self)

            if self.tiebreak == False:
                assign_point(self, who_scored)
            elif self.tiebreak == True:
                current_point.tiebreak = True
                assign_point_tiebreak(self, who_scored)
            self.modified = True

        print (f"Score: {self.score}")
        print (f"Games: {self.games}")
        print (f"Sets: {self.sets}")

    def filter(self):
        dialog = FilterDialog(self)
        if dialog.exec():
            filters = dialog.get_filters()
            print(filters)
            self.deselect_all()
            if filters.player == 0:
                for data in self.scene_data:
                    if data.point_winner is not None:
                        check_box = data.container_widget.findChild(QCheckBox)
                        check_box.setChecked(True)
            else:
                for data in self.scene_data:
                    if data.point_winner == filters.player:
                        check_box = data.container_widget.findChild(QCheckBox)
                        check_box.setChecked(True)

            for data in self.scene_data:
                if filters.game != 0:
                    if data.game != filters.game:
                        check_box = data.container_widget.findChild(QCheckBox)
                        check_box.setChecked(False)
                if filters.set != 0:
                    if data.set != filters.set:
                        check_box = data.container_widget.findChild(QCheckBox)
                        check_box.setChecked(False)
                if filters.tiebreak is not None:
                    if data.tiebreak != filters.tiebreak:
                        print (data.tiebreak)
                        print (filters.tiebreak)
                        check_box = data.container_widget.findChild(QCheckBox)
                        check_box.setChecked(False)

    def jolly(self):
        # for data in self.scene_data:
        #     list = data.linked_list
        #     container = data.container_widget
        #     button = container.findChild(QPushButton)
        #     print (button.text())
        #     list.print_list()
        #     print (data.checked)
        #     if (data.point_winner is not None):
        #         print ("point wininer is " + str(data.point_winner))
        #     if (data.game is not None):
        #         print ("Game: " + str(data.game))
        #     if (data.set is not None):
        #         print ("Set: " + str(data.set))
        #     if (data.tiebreak == True):
        #         print ("Tiebreak")
        #     print ("---")
        # print ("\n")
        print (self.score)
        print (self.games)
        print (self.sets)
        print ("\n")

    def select_and_play(self):
        merged_scenes_macroscenes = LinkedList()
        for data in self.scene_data:
            if data.checked:
                current_node = data.linked_list.head
                while current_node:
                    merged_scenes_macroscenes.append_to_list(current_node.data)
                    current_node = current_node.next

        self.current_node = merged_scenes_macroscenes.head

        if self.current_node is None:
            print ("Select some checkboxes")
            return
        
        play_scene(self)

    def delete_selected(self):
        selected_scenes_data = get_selected_scenes_data(self)
        for data in selected_scenes_data:
            remove_container_from_layout(data.container_widget, self.scroll_layout)
            self.scene_data.remove(data)
            self.scroll_area_widgets.remove(data.container_widget)
        self.update_layout()
        self.modified = True

    def select_all(self):
        for data in self.scene_data:
            checkbox = data.container_widget.findChild(QCheckBox)
            checkbox.setChecked(True)

    def deselect_all(self):
        for data in self.scene_data:
            checkbox = data.container_widget.findChild(QCheckBox)
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
        ok = self.ask_for_save()
        if not ok:
            return
        project_name, ok = QInputDialog.getText(self, "New Project", "Enter project name:")
        project_path = os.path.join("Projects", project_name)
        if ok: processing = self.ask_for_processing()
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
                if processing:
                    self.start_processing_thread()

    def load_project(self, project_path=None):
        if not project_path: # if the load project button is clicked
            ok = self.ask_for_save()
            if not ok:
                return
            project_path = QFileDialog.getExistingDirectory(self, "Select Project Directory", "projects")
        if project_path:
            self.setWindowTitle("TennisTrack" + " - " + os.path.basename(project_path))
            self.project_path = project_path
            self.scene_file_path = os.path.join(self.project_path, "scenes.txt")
            self.points_file_path = os.path.join(self.project_path, "points.txt")
            self.scores_file_path = os.path.join(self.project_path, "scores.txt")
            self.base_name = obtain_base_name(self)

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
            self.scroll_area_widgets = [] # in this way, if you load more than once, the widgets are not appended

            activate_buttons(self.buttons_to_activate)

            if self.base_name == PROCESSED:
                self.process_action.setEnabled(False)

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

                    # Crea il testo del pulsante con i trattini tra le coppie di numeri
                    button_text = ' | '.join(f"{scenes[j]}-{scenes[j+1]}" for j in range(0, len(scenes), 2))

                    self.create_macroscene(macro_scene, button_text, None)

            self.set_point_window.hide()
            if os.path.isfile(self.points_file_path):
                self.initiate_set_points()

            if not os.path.isfile(self.points_file_path) and not os.path.isfile(self.scores_file_path):
                self.scene_is_point = False

            if self.games[0] == 6 and self.games[1] == 6:
                self.tiebreak = True

            self.save_project()

            self.play_and_pause_button.setEnabled(False)
            self.play_and_pause_button.setText("Play/Pause")

    def save_project(self):
        if self.project_path:
            with open(self.scene_file_path, "w") as scene_file:
                for data in self.scene_data:
                    current_node = data.linked_list.head
                    while current_node:
                        start, end = current_node.data
                        scene_file.write(f"{start} {end} ")
                        current_node = current_node.next
                    scene_file.write("\n")
            if os.path.isfile(self.points_file_path):
                with open (self.points_file_path, "w") as points_file:
                    for data in self.scene_data:
                        if data.point_winner is not None:
                            index = self.scene_data.index(data)
                            points_file.write(f"{data.point_winner} {data.game} {data.set} {data.tiebreak} {index}\n")
            if os.path.isfile(self.scores_file_path):
                with open (self.scores_file_path, "w") as scores_file:
                    scores_file.write(f"{self.score[0]} {self.score[1]}\n{self.games[0]} {self.games[1]}\n{self.sets[0]} {self.sets[1]} {self.max_sets}\n")
            self.modified = False

if __name__ == "__main__":
    # Create the application and main window, then run the application
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icons/icon.png"))
    window = MainWindow()
    window.show()
    window.raise_()  # Porta la finestra in primo piano
    window.activateWindow()  # Attiva la finestra
    app.exec()