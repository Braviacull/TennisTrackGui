from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QScrollArea, QHBoxLayout, QFileDialog, QLabel, QApplication, QSplitter, QInputDialog, QMenu, QCheckBox
from PySide6.QtGui import QPixmap
from PySide6.QtCore import QUrl, Qt
import os
import cv2
import sys
import subprocess
import shutil

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set the window title
        self.setWindowTitle("Prototipo")

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

        # Create buttons for project management
        self.new_project_button = QPushButton("New Project")
        self.new_project_button.clicked.connect(self.create_new_project)
        self.layout.addWidget(self.new_project_button)

        self.load_project_button = QPushButton("Load Project")
        self.load_project_button.clicked.connect(self.load_project)
        self.layout.addWidget(self.load_project_button)

        # JOLLY BUTTON
        self.load_project_button = QPushButton("Jolly Button")
        self.load_project_button.clicked.connect(self.delete_selected_scenes)
        self.layout.addWidget(self.load_project_button)

        # Directories and paths
        self.project_path = None
        self.video_path = None
        self.projects_directory = os.path.abspath("Projects")

        # Scene data
        self.scene_data = None # vettore che verrá popolato con tuple:(path_scene, path_thumbnail, label, selected)

        # Create a scroll area for thumbnails
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()  # container widget for the scroll area
        self.scroll_layout = QHBoxLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)
        self.splitter.addWidget(self.scroll_area)

    def obtain_input_dir(self):
        if not self.project_path:
            print("No project loaded")
            return
        return os.path.join(self.project_path, "input")

    def obtain_output_dir(self):
        if not self.project_path:
            print("No project loaded")
            return
        return os.path.join(self.project_path, "output")

    def obtain_thumbnails_dir(self):
        if not self.project_path:
            print("No project loaded")
            return
        return os.path.join(self.project_path, "thumbnails")

    def create_scenes(self):
        self.pre_processing()
        self.populate_scroll_area()

    def pre_processing(self):
        if not self.video_path:
            print("No video file in input directory")
            return
        output_path = os.path.join(self.obtain_output_dir(), "output_video.mp4")
        model_path = "model_tennis_court_det.pt"
        command = [
            "python", "main.py",
            "--path_court_model", model_path,
            "--path_input_video", self.video_path,
            "--path_output_video", output_path
        ]
        subprocess.run(command)

    def populate_scroll_area(self):
        self.create_thumbnails()
        self.add_widgets_to_scroll_layout()

    def create_new_project(self):
        project_name, ok = QInputDialog.getText(self, "New Project", "Enter project name:")
        project_path = os.path.join(self.projects_directory, project_name)
        if os.path.isdir(project_path) and ok:
            print("Project already exists, CHOOSE ANOTHER NAME FOR YOUR PROJECT")
            return
        elif ok and project_name:
            self.project_path = project_path
            video_path = QFileDialog.getOpenFileName(self, "Open Video File", "", "Video Files (*.mp4 *.avi *.mov)")[0]
            os.makedirs(self.obtain_input_dir(), exist_ok=True)
            os.makedirs(self.obtain_output_dir(), exist_ok=True)
            os.makedirs(self.obtain_thumbnails_dir(), exist_ok=True)
            if video_path:
                shutil.copy(video_path, os.path.join(self.obtain_input_dir(), os.path.basename(video_path)))
                self.video_path = os.path.join(self.obtain_input_dir(), os.path.basename(video_path))
                self.create_scenes()

    def load_project(self):
        project_path = QFileDialog.getExistingDirectory(self, "Select Project Directory", "projects")
        if project_path:
            self.project_path = project_path

            input_dir = self.obtain_input_dir()
            output_dir = self.obtain_output_dir()
            thumbnails_dir = self.obtain_thumbnails_dir()

            # Check if the input, output, and thumbnail directories exist
            if not os.path.exists(input_dir):
                print(f"Input directory does not exist: {input_dir}")
                return

            if not os.path.exists(output_dir):
                print(f"Output directory does not exist: {output_dir}")
                return

            if not os.path.exists(thumbnails_dir):
                print(f"Thumbnail directory does not exist: {thumbnails_dir}")
                return

            video_files = os.listdir(input_dir)
            if not video_files:
                print("No video files found in the input directory")
                self.video_path = None
                return

            self.video_path = os.path.join(input_dir, video_files[0])
            if not os.path.exists(self.video_path):
                print("No video file found in the input directory")
                self.video_path = None
                return

            self.populate_scroll_area()

    def create_thumbnails(self):
        print("Creating thumbnails")
        if not self.project_path:
            print("function create_thumbnails says there is no project loaded")
            return

        output_dir = self.obtain_output_dir()
        thumbnails_dir = self.obtain_thumbnails_dir()

        output_list = []
        thumbnails_list = []

        if not os.path.exists(thumbnails_dir):
            print("Thumbnails directory does not exists")
            return

        for scene in os.listdir(output_dir):
            if scene.endswith(".mp4"):
                scene_path = os.path.join(output_dir, scene)
                cap = cv2.VideoCapture(scene_path)
                ret, frame = cap.read()
                if ret:
                    print(f"Creating thumbnail for {scene}")
                    thumbnail_path = os.path.join(thumbnails_dir, os.path.splitext(scene)[0] + "_thumbnail.jpg")
                    cv2.imwrite(thumbnail_path, frame)
                    print(f"Thumbnail created at {thumbnail_path}")
                    # Add the path of the thumbnail to the list
                    thumbnails_list.append(thumbnail_path)
                    # Add the path of the video to the list
                    output_list.append(scene_path)
                else:
                    print(f"Failed to read frame from {scene_path}")
                cap.release()

        self.scene_data = list(zip(output_list, thumbnails_list))

    def add_widgets_to_scroll_layout(self):
        print("Adding scene thumbnails to scroll layout")
        self.clear_layout(self.scroll_layout)

        if self.scene_data is None:
            print("scene_data is None, devi chiamare self.populate_scroll_area() prima")
            return

        updated_scene_data = []
        for scene_path, thumbnail_path in self.scene_data:
            thumbnail_label = QLabel()
            thumbnail_label.setPixmap(QPixmap(thumbnail_path).scaled(100, 100, Qt.KeepAspectRatio))
            thumbnail_label.setContextMenuPolicy(Qt.CustomContextMenu)
            thumbnail_label.customContextMenuRequested.connect(
                lambda pos, s_path=scene_path, t_path=thumbnail_path, label=thumbnail_label: self.show_context_menu(pos, s_path, t_path, label)
            )

            # Aggiungi una QCheckBox per la selezione
            checkbox = QCheckBox()
            checkbox.setObjectName(scene_path)  # Usa il percorso della scena come nome dell'oggetto per l'identificazione
            checkbox.stateChanged.connect(self.on_checkbox_state_changed)

            # Crea un widget contenitore per la miniatura e la checkbox
            container = QWidget()
            container_layout = QHBoxLayout(container)
            container_layout.addWidget(checkbox)
            container_layout.addWidget(thumbnail_label)

            self.scroll_layout.addWidget(container)  # Aggiungi il contenitore al layout di scorrimento

            # Aggiorna la tupla aggiungendo il container dei widget e un attributo booleano per la selezione (checkbox)
            updated_scene_data.append((scene_path, thumbnail_path, thumbnail_label, False))

        self.scene_data = updated_scene_data

    def show_context_menu(self, pos, scene_path, thumbnail_path, label):
        menu = QMenu(self)
        play_action = menu.addAction("Play")
        delete_action = menu.addAction("Delete")

        global_pos = label.mapToGlobal(pos)
        action = menu.exec(global_pos)
        if action == play_action:
            self.play_video(scene_path)
        elif action == delete_action:
            self.delete_video(scene_path, thumbnail_path, label)

    def get_selected_scenes(self):
        selected_scenes = []
        for i, (path, thumbnail, label, selected) in enumerate(self.scene_data):
            if selected:
                selected_scenes.append(self.scene_data[i])
        return selected_scenes

    def on_checkbox_state_changed(self, state):
        # if state == 2 checked, 0 unchecked, 1 partial checked
        checkbox = self.sender()
        scene_path = checkbox.objectName()
        for i, (path, thumbnail, label, selected) in enumerate(self.scene_data):
            if path == scene_path:
                self.scene_data[i] = (path, thumbnail, label, state == 2)
                print (self.scene_data[i][3])
                break
        # if state == 2:
        #     print("Checkbox is checked")
        # elif state == 0:
        #     print("Checkbox is unchecked")

    def delete_video(self, scene_path, thumbnail_path, label):
        if os.path.exists(scene_path):
            print("removing video")
            os.remove(scene_path)

        if os.path.exists(thumbnail_path):
            print("removing thumbnail")
            os.remove(thumbnail_path)

        self.remove_thumbnail(label)

    def delete_selected_scenes(self):
        selected_scenes = self.get_selected_scenes()
        for scene_path, thumbnail_path, label, selected in selected_scenes:
            self.remove_thumbnail(label)
            self.delete_video(scene_path, thumbnail_path, label)

    def remove_thumbnail(self, label):
        self.scroll_layout.removeWidget(label)
        label.deleteLater()

    def play_video(self, video_path):
        self.media_player.setSource(QUrl.fromLocalFile(video_path))
        self.media_player.play()

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

# Create the application and main window, then run the application
app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()