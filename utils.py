from scenedetect.video_manager import VideoManager
from scenedetect.scene_manager import SceneManager
from scenedetect.stats_manager import StatsManager
from scenedetect.detectors import ContentDetector
from PySide6.QtWidgets import QPushButton
from typing import List
from scene_data_class import SceneData

def scene_detect(path_video):
    """
    Split video to disjoint fragments based on color histograms
    """
    video_manager = VideoManager([path_video])
    stats_manager = StatsManager()
    scene_manager = SceneManager(stats_manager)
    scene_manager.add_detector(ContentDetector())
    base_timecode = video_manager.get_base_timecode()

    video_manager.set_downscale_factor()
    video_manager.start()
    scene_manager.detect_scenes(frame_source=video_manager)
    scene_list = scene_manager.get_scene_list(base_timecode)

    if scene_list == []:
        scene_list = [(video_manager.get_base_timecode(), video_manager.get_current_timecode())]
    scenes = [[x[0].frame_num, x[1].frame_num]for x in scene_list]    
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
    return self.games[0] + self.games[1]

def get_current_set (self):
    return self.sets[0] + self.sets[1]