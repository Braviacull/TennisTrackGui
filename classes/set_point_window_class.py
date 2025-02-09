from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGroupBox, QInputDialog, QGridLayout
from PySide6.QtCore import Qt

class SetPointWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Set Point")
        self.setGeometry(100, 100, 400, 300)  # Set the size and position of the window
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint)  # Remove close button

        main_layout = QVBoxLayout()

        # Section 1: Final Result
        final_result_group = QGroupBox("Final Result")
        final_result_layout = QGridLayout()

        # Headers
        final_result_layout.addWidget(QLabel(""), 0, 0)
        final_result_layout.addWidget(QLabel("Sets"), 0, 1)

        # Player 1
        final_result_layout.addWidget(QLabel("Player 1"), 1, 0)
        self.player1_final_result = QLabel("0")
        final_result_layout.addWidget(self.player1_final_result, 1, 1)

        # Player 2
        final_result_layout.addWidget(QLabel("Player 2"), 2, 0)
        self.player2_final_result = QLabel("0")
        final_result_layout.addWidget(self.player2_final_result, 2, 1)

        self.set_final_result_button = QPushButton("Set Final Result")
        self.set_final_result_button.clicked.connect(self.on_set_final_result)
        final_result_layout.addWidget(self.set_final_result_button, 3, 0, 1, 2)

        final_result_group.setLayout(final_result_layout)
        main_layout.addWidget(final_result_group)

        # Section 2: Current Score
        current_score_group = QGroupBox("Current Score")
        current_score_layout = QGridLayout()

        # Headers
        current_score_layout.addWidget(QLabel(""), 0, 0)
        current_score_layout.addWidget(QLabel("Score"), 0, 1)
        current_score_layout.addWidget(QLabel("Games"), 0, 2)
        current_score_layout.addWidget(QLabel("Sets"), 0, 3)

        # Player 1
        current_score_layout.addWidget(QLabel("Player 1"), 1, 0)
        self.player1_score = QLabel("0")
        self.player1_games_won = QLabel("0")
        self.player1_sets_won = QLabel("0")
        current_score_layout.addWidget(self.player1_score, 1, 1)
        current_score_layout.addWidget(self.player1_games_won, 1, 2)
        current_score_layout.addWidget(self.player1_sets_won, 1, 3)

        # Player 2
        current_score_layout.addWidget(QLabel("Player 2"), 2, 0)
        self.player2_score = QLabel("0")
        self.player2_games_won = QLabel("0")
        self.player2_sets_won = QLabel("0")
        current_score_layout.addWidget(self.player2_score, 2, 1)
        current_score_layout.addWidget(self.player2_games_won, 2, 2)
        current_score_layout.addWidget(self.player2_sets_won, 2, 3)

        current_score_group.setLayout(current_score_layout)
        main_layout.addWidget(current_score_group)

        # Section 3: Buttons
        buttons_group = QGroupBox("Who won this point?")
        buttons_layout = QHBoxLayout()
        self.player1_button = QPushButton("Player 1")
        self.player2_button = QPushButton("Player 2")
        buttons_layout.addWidget(self.player1_button)
        buttons_layout.addWidget(self.player2_button)
        buttons_group.setLayout(buttons_layout)
        main_layout.addWidget(buttons_group)

        # Section 4: Other Actions
        other_actions_group = QGroupBox("Other Actions")
        other_actions_layout = QHBoxLayout()
        self.play_scene_button = QPushButton("Play Scene")
        self.filter_button = QPushButton("Filter")
        other_actions_layout.addWidget(self.play_scene_button)
        other_actions_layout.addWidget(self.filter_button)
        other_actions_group.setLayout(other_actions_layout)
        main_layout.addWidget(other_actions_group)

        self.setLayout(main_layout)

        self.player1_button.clicked.connect(self.on_player1)
        self.player2_button.clicked.connect(self.on_player2)
        self.play_scene_button.clicked.connect(self.on_play_scene)
        self.filter_button.clicked.connect(self.on_filter)

    def set_current_game_score(self):
        score1, score2 = self.parent().score
        self.player1_score.setText(str(score1)) 
        self.player2_score.setText(str(score2))
        if score1 == 0 and score2 == 0:
            self.set_current_games_won()

    def set_current_games_won(self):
        games_won1, games_won2 = self.parent().games
        self.player1_games_won.setText(str(games_won1))
        self.player2_games_won.setText(str(games_won2))
        if games_won1 == 0 and games_won2 == 0:
            self.set_current_sets_won()

    def set_current_sets_won(self):
        sets_won1, sets_won2 = self.parent().sets
        self.player1_sets_won.setText(str(sets_won1))
        self.player2_sets_won.setText(str(sets_won2))

    def on_set_final_result(self):
        player1_sets, ok1 = QInputDialog.getInt(self, "Set Final Result", "Enter Player 1 Sets Won:", 0, 0)
        if not ok1:
            return
        player2_sets, ok2 = QInputDialog.getInt(self, "Set Final Result", "Enter Player 2 Sets Won:", 0, 0)
        if not ok2:
            return
        self.player1_final_result.setText(str(player1_sets))
        self.player2_final_result.setText(str(player2_sets))

    def on_play_scene(self):
        self.parent().who_scored(0)

    def on_player1(self):
        self.parent().who_scored(1)
        self.set_current_game_score()

    def on_player2(self):
        self.parent().who_scored(2)
        self.set_current_game_score()

    def on_filter(self):
        self.parent().filter()