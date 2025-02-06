class SceneData:
    def __init__(self, linked_list, container_widget, checked, point_winner, game, set, tiebreak):
        self.linked_list = linked_list
        self.container_widget = container_widget
        self.checked = checked
        self.point_winner = point_winner
        self.game = game
        self.set = set
        self.tiebreak = tiebreak

    def __repr__(self):
        return (f"SceneData(linked_list={self.linked_list}, container_widget={self.container_widget}, "
                f"checked={self.checked}, point_winner={self.point_winner}, game={self.game}, "
                f"set={self.set}, tiebreak={self.tiebreak})")