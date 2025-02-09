from scenedetect import open_video, SceneManager
from scenedetect.stats_manager import StatsManager
from scenedetect.detectors import ContentDetector
from tqdm import tqdm
from PySide6.QtWidgets import QPushButton
from typing import List
from classes.scene_data_class import SceneData

def scene_detect(path_video):
    """
    Split video to disjoint fragments based on color histograms
    """
    video = open_video(path_video)
    stats_manager = StatsManager()
    scene_manager = SceneManager(stats_manager)
    scene_manager.add_detector(ContentDetector())

    # Perform scene detection
    scene_manager.detect_scenes(video)

    # Get list of detected scenes
    scene_list = scene_manager.get_scene_list()

    if not scene_list:
        scene_list = [(video.base_timecode, video.duration)]
    scenes = [[scene[0].get_frames(), scene[1].get_frames()] for scene in scene_list]
    return scenes

def get_selected_scenes_data(self) -> List[SceneData]:
    selected_scenes_data: List[SceneData] = []
    for data in self.scene_data:
        if data.checked:
            selected_scenes_data.append(data)
    return selected_scenes_data

def remove_container_from_layout(container, layout):
    layout.removeWidget(container)
    container.deleteLater()

def activate_buttons(vec_of_buttons):
    for button in vec_of_buttons:
        button.setEnabled(True)

def deactivate_buttons(vec_of_buttons):
    for button in vec_of_buttons:
        button.setEnabled(False)

def clear_layout(layout):
    while layout.count():
        child = layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()

def get_macro_scene_correct_name (head):
    resulting_name = ""
    while (head is not None):
        resulting_name += " | "
        start = str(head.data[0])
        end = str(head.data[1])
        resulting_name += (start + "-" + end)
        head = head.next

    return resulting_name[3:]

def get_data_from_button(self, button):
    for data in self.scene_data:
        if data.container_widget.findChild(QPushButton) == button:
            return data

def get_current_game (self):
    return get_custom_score(self.games[0], self.games[1])

def get_current_set (self):
    return get_custom_score(self.sets[0], self.sets[1])

def get_custom_score (score1, score2):
    return score1 + score2 + 1

def print_execution_time(start_time, end_time):
    execution_time_in_seconds= end_time - start_time
    execution_time_in_minutes = execution_time_in_seconds / 60
    print(f"Execution time: {execution_time_in_seconds} seconds")
    print(f"Execution time: {execution_time_in_minutes} minutes")