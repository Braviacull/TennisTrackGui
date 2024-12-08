from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QScrollArea, QHBoxLayout, QFileDialog, QLabel, QApplication, QSplitter, QInputDialog, QMenu, QCheckBox
from PySide6.QtGui import QPixmap
from PySide6.QtCore import QUrl, Qt
from video_operations import read_video, write
import os
import cv2
import sys
import subprocess
import shutil

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

        self.buttons_to_activate = []

        # New project button
        self.new_project_button = QPushButton("New Project")
        self.new_project_button.clicked.connect(self.create_new_project)
        self.layout.addWidget(self.new_project_button)

        # Load project button
        self.load_project_button = QPushButton("Load Project")
        self.load_project_button.clicked.connect(self.load_project)
        self.layout.addWidget(self.load_project_button)

        # Save project button
        self.save_project_button = QPushButton("Save Project")
        self.save_project_button.clicked.connect(self.save_project)
        self.layout.addWidget(self.save_project_button)

        # Select all button
        self.select_all_button = QPushButton("Select All")
        self.select_all_button.clicked.connect(self.select_all_checkboxes)
        self.layout.addWidget(self.select_all_button)
        self.select_all_button.setEnabled(False)
        self.buttons_to_activate.append(self.select_all_button)

        # Delete selected scenes button
        self.delete_selected_scenes_button = QPushButton("Delete Selected Scenes")
        self.delete_selected_scenes_button.clicked.connect(self.delete_selected_scenes)
        self.layout.addWidget(self.delete_selected_scenes_button)
        self.delete_selected_scenes_button.setEnabled(False)
        self.buttons_to_activate.append(self.delete_selected_scenes_button)

        # Merge scenes button
        self.merge_scenes_button = QPushButton("Merge Scenes")
        self.merge_scenes_button.clicked.connect(self.merge_scenes)
        self.layout.addWidget(self.merge_scenes_button)
        self.merge_scenes_button.setEnabled(False)
        self.buttons_to_activate.append(self.merge_scenes_button)

        # Directories and paths
        self.project_path = None
        self.video_path = None
        self.projects_directory = os.path.abspath("Projects")

        # Scene data
        self.scene_data = None # vettore che verrá popolato con tuple:(scene_path, thumbnail_path, container, selected)

        # Create a scroll area for thumbnails
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()  # container widget for the scroll area
        self.scroll_layout = QHBoxLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)
        self.splitter.addWidget(self.scroll_area)
        self.scroll_area.resize(150, 150)

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

    def obtain_tmp_dir(self):
        if not self.project_path:
            print("No project loaded")
            return
        return os.path.join(self.project_path, "tmp")
    
    def obtain_tmp_output_dir(self):
        if not self.project_path:
            print("No project loaded")
            return
        return os.path.join(self.obtain_tmp_dir(), "output")
    
    def obtain_tmp_thumbnails_dir(self):
        if not self.project_path:
            print("No project loaded")
            return
        return os.path.join(self.obtain_tmp_dir(), "thumbnails")

    def get_selected_scenes(self):
        selected_scenes = []
        for i, (_, _, _, selected) in enumerate(self.scene_data):
            if selected:
                selected_scenes.append(self.scene_data[i])
        return selected_scenes

    def get_data_from_scene_data(self, scene_path):
        for i, (path, thumbnail, label, selected) in enumerate(self.scene_data):
            if path == scene_path:
                return self.scene_data[i]
        print ("scene not found")

    def create_scenes(self):
        self.pre_processing()
        self.copy_folder_to_folder(self.obtain_output_dir(), self.obtain_tmp_output_dir())
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
        self.copy_folder_to_folder(self.obtain_tmp_thumbnails_dir(), self.obtain_thumbnails_dir())
        self.add_widgets_to_scroll_layout()

    def copy_folder_to_folder(self, source, destination):
        # empty the destination folder
        for file in os.listdir(destination):
            file_path = os.path.join(destination, file)
            os.remove(file_path)
        # copy the files from the source folder to the destination folder
        for file in os.listdir(source):
            file_path = os.path.join(source, file)
            shutil.copy(file_path, os.path.join(destination, file))

    def activate_buttons(self):
        for button in self.buttons_to_activate:
            button.setEnabled(True)

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
            # it is not necessary to create a temporary folder for the input (because it is never modified)
            os.makedirs(self.obtain_tmp_dir(), exist_ok=True)
            os.makedirs(self.obtain_tmp_output_dir(), exist_ok=True)
            os.makedirs(self.obtain_tmp_thumbnails_dir(), exist_ok=True)

            if video_path:
                shutil.copy(video_path, os.path.join(self.obtain_input_dir(), os.path.basename(video_path)))
                self.video_path = os.path.join(self.obtain_input_dir(), os.path.basename(video_path))
                self.create_scenes()
                self.activate_buttons()

    def load_project(self):
        project_path = QFileDialog.getExistingDirectory(self, "Select Project Directory", "projects")
        if project_path:
            self.project_path = project_path

            input_dir = self.obtain_input_dir()
            output_dir = self.obtain_output_dir()
            thumbnails_dir = self.obtain_thumbnails_dir()

            # Copy the project folders to the temporary folders so that if the modification were not saved the original project is not modified
            self.copy_folder_to_folder(output_dir, self.obtain_tmp_output_dir())
            self.copy_folder_to_folder(thumbnails_dir, self.obtain_tmp_thumbnails_dir())

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
            self.activate_buttons()
            self.select_all_button.setText("Select All") # Reset the text of the select all button

    def save_project(self):
        print("Saving project")
        self.copy_folder_to_folder(self.obtain_tmp_output_dir(), self.obtain_output_dir())
        self.copy_folder_to_folder(self.obtain_tmp_thumbnails_dir(), self.obtain_thumbnails_dir())
        print("Project saved")

    def create_thumbnails(self):
        print("Creating thumbnails")
        if not self.project_path:
            print("function create_thumbnails says there is no project loaded")
            return

        tmp_output_dir = self.obtain_tmp_output_dir()
        tmp_thumbnails_dir = self.obtain_tmp_thumbnails_dir()

        output_list = []
        thumbnails_list = []

        if not os.path.exists(tmp_thumbnails_dir):
            print("Thumbnails directory does not exists")
            return

        for scene in os.listdir(tmp_output_dir):
            if scene.endswith(".mp4"):
                scene_path = os.path.join(tmp_output_dir, scene)
                cap = cv2.VideoCapture(scene_path)
                ret, frame = cap.read()
                if ret:
                    print(f"Creating thumbnail for {scene}")
                    thumbnail_path = os.path.join(tmp_thumbnails_dir, os.path.splitext(scene)[0] + "_thumbnail.jpg")
                    cv2.imwrite(thumbnail_path, frame)
                    print(f"Thumbnail created at {thumbnail_path}")
                    # Add the path of the video to the list
                    output_list.append(scene_path)
                    # Add the path of the thumbnail to the list
                    thumbnails_list.append(thumbnail_path)
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
                lambda pos, s_path=scene_path: self.show_context_menu(pos, s_path)
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
            updated_scene_data.append((scene_path, thumbnail_path, container, False))

        self.scene_data = updated_scene_data

    def show_context_menu(self, pos, scene_path):
        menu = QMenu(self)
        play_action = menu.addAction("Play")
        delete_action = menu.addAction("Delete")

        data = self.get_data_from_scene_data(scene_path)
        thumbnail_path = data[1]
        container = data[2]
        label = container.findChild(QLabel)
        checkbox = container.findChild(QCheckBox)

        global_pos = label.mapToGlobal(pos) # Ottieni la posizione globale del click
        action = menu.exec(global_pos)
        if action == play_action:
            self.play_video(scene_path)
        elif action == delete_action:
            self.remove_scene(container, label, checkbox, scene_path, thumbnail_path)

    def on_checkbox_state_changed(self, state):
        # if state == 2 checked, 0 unchecked, 1 partial checked
        checkbox = self.sender()
        scene_path = checkbox.objectName()
        for i, (path, thumbnail, label, selected) in enumerate(self.scene_data):
            if path == scene_path:
                self.scene_data[i] = (path, thumbnail, label, state == 2)
                print (self.scene_data[i][3])
                break
        if state == 0:
            self.select_all_button.setText("Select All")

    def select_all_checkboxes(self):
        b = None
        if self.select_all_button.text() == "Select All":
            self.select_all_button.setText("Deselect All")
            b = True
        elif self.select_all_button.text() == "Deselect All":
            self.select_all_button.setText("Select All")
            b = False
        for (path, thumbnail, container, selected) in (self.scene_data):
            checkbox = container.findChild(QCheckBox)
            if checkbox:
                checkbox.setChecked(b)
            else: print ("errore in scene_data, dovrei avere trovato una checkbox ma non é successo")

    def delete_video (self, scene_path):
        if os.path.exists(scene_path):
            print("removing video")
            os.remove(scene_path)
        else :
            print("video not found")

    def delete_thumbnail (self, thumbnail_path):
        if os.path.exists(thumbnail_path):
            print("removing thumbnail")
            os.remove(thumbnail_path)
        else :
            print("thumbnail not found")

    def remove_widget_from_container(self, container, widget):
        layout = container.layout()
        if layout:
            layout.removeWidget(widget)
            widget.deleteLater()
        else:
            print("layout not found, make sure you are passing the right container")

    def remove_container_from_layout(self, container):
        layout = container.parentWidget().layout()
        if layout:
            layout.removeWidget(container)
            container.deleteLater()
        else:
            print("Layout not found, make sure the container has a parent widget with a layout")

    def remove_data_from_scene_data(self, scene_path):
        data = self.get_data_from_scene_data(scene_path)
        self.scene_data.remove(data)

    def remove_scene (self, container, label, checkbox, scene_path, thumbnail_path):
        self.delete_video(scene_path)
        self.delete_thumbnail(thumbnail_path)
        self.remove_widget_from_container(container, label)
        self.remove_widget_from_container(container, checkbox)
        self.remove_container_from_layout(container)
        self.remove_data_from_scene_data(scene_path)
        print("scene deleted")

    def delete_selected_scenes(self):
        # [:] itera su una copia della lista originale per evitare problemi di modifica durante l'iterazione
        # alla fine della funzione la lista originale viene sovrascritta con la copia modificata
        for scene_path, thumbnail_path, container, selected in self.scene_data[:]:
            if selected:
                label = container.findChild(QLabel)
                checkbox = container.findChild(QCheckBox)
                self.remove_scene(container, label, checkbox, scene_path, thumbnail_path)

    def play_video(self, video_path):
        self.media_player.setSource(QUrl.fromLocalFile(video_path))
        self.media_player.play()


    def merge_scenes (self):
        scenes_to_merge = self.get_selected_scenes()
        if scenes_to_merge is None:
            print("No scenes selected")
            return
        
        final_frames = []
        final_fps = None
        for (scene_path, thumbnail_path, container, selected) in scenes_to_merge: 
            frames, fps= read_video(scene_path)
            final_frames.extend(frames)
            if final_fps is None: # first iteration
                final_fps = fps
            elif final_fps != fps:
                print("Error: different frame rates")
                return
            
        if final_frames == [] or final_fps is None:
            print("Error: no frames to merge")
            return
        
        os.remove(scenes_to_merge[0][0]) # remove the first scene
        write(final_frames, final_fps, scenes_to_merge[0][0])

        res_scene = scenes_to_merge[0]

        # deselect the resulting scene
        container = res_scene[2]
        checkbox = container.findChild(QCheckBox)
        checkbox.setChecked(False)

        self.delete_selected_scenes()
        print (self.scene_data)


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