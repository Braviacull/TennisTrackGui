# GET SCENES FROM SCENE FILE
def get_scenes(self):
    with open(self.scene_file_path, "r") as scene_file:
        for line in scene_file:
            start, end = map(int, line.split())
            self.num_frames = end

            # scene_data[i] = [LinkedList, container, bool]
            scene = [start, end]
            macro_scene = LinkedList()
            macro_scene.append_to_list(scene)

            # create a checkbox for each scene
            container = QWidget()
            container_layout = QHBoxLayout(container)

            # create a button for each scene
            button = QPushButton(f"{start}-{end}")
            button.clicked.connect(self.play_macro_scene)
            container_layout.addWidget(button)

            checkbox = QCheckBox()
            container_layout.addWidget(checkbox)
            checkbox.stateChanged.connect(self.check_scene)

            self.scroll_layout.addWidget(container)

            data = [macro_scene, container, False]

            self.scene_data.append(data)
    self.save_project()