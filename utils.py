from scenedetect.video_manager import VideoManager
from scenedetect.scene_manager import SceneManager
from scenedetect.stats_manager import StatsManager
from scenedetect.detectors import ContentDetector
from PySide6.QtWidgets import QPushButton

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

def get_selected_scenes_data(self):
    selected_scenes_data = []
    for data in self.scene_data:
        if data[2]:
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
        if data[1].findChild(QPushButton) == button:
            return data
        
def update_game (self, who_scored):
    if who_scored == 1:
        self.game[0] = update_score(self.game[0])
    elif who_scored == 2:
        self.game[1] = update_score(self.game[1])
    winner = check_game(self.game)

def update_score (score):
    if score < 30:
        score += 15
    elif score == 30:
        score += 10
    elif score == 40:
        score += 1
    return score

def check_game (game):
    winner = None
    if game[0] == 41 and game[1] < 40:
        winner = 1
    elif game[1] == 41 and game[0] < 40:
        winner = 2
    elif game[0] >= 40 and game[1] >= 40:
        if game[0] == game[1] + 2:
            winner = 1
        elif game[1] == game[0] + 2:
            winner = 2

    return winner