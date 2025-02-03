from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QMessageBox
from PySide6.QtGui import QIntValidator

class Filters:
    def __init__(self, player: str, game: int, set: int, tiebreak: str):
        self.player = player
        self.game = game
        self.set = set
        self.tiebreak = tiebreak

    def __repr__(self):
        return (f"Filters(player={self.player}, game={self.game}, "
                f"set={self.set}, tiebreak={self.tiebreak})")

class FilterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Filter Options")

        layout = QVBoxLayout()

        # Player selection
        player_layout = QHBoxLayout()
        player_label = QLabel("Player:")
        self.player_combo = QComboBox()
        self.player_combo.addItems(["All", "Player 1", "Player 2"])
        player_layout.addWidget(player_label)
        player_layout.addWidget(self.player_combo)
        layout.addLayout(player_layout)

        # Game selection
        game_layout = QHBoxLayout()
        game_label = QLabel("Game:")
        self.game_combo = QComboBox()
        self.game_combo.addItems(["All", "Custom"])
        self.game_custom = QLineEdit()
        self.game_custom.setPlaceholderText("Enter game number")
        self.game_custom.setEnabled(False)
        self.game_custom.setValidator(QIntValidator())
        self.game_combo.currentIndexChanged.connect(self.toggle_game_custom)
        game_layout.addWidget(game_label)
        game_layout.addWidget(self.game_combo)
        game_layout.addWidget(self.game_custom)
        layout.addLayout(game_layout)

        # Set selection
        set_layout = QHBoxLayout()
        set_label = QLabel("Set:")
        self.set_combo = QComboBox()
        self.set_combo.addItems(["All", "Custom"])
        self.set_custom = QLineEdit()
        self.set_custom.setPlaceholderText("Enter set number")
        self.set_custom.setEnabled(False)
        self.set_custom.setValidator(QIntValidator())
        self.set_combo.currentIndexChanged.connect(self.toggle_set_custom)
        set_layout.addWidget(set_label)
        set_layout.addWidget(self.set_combo)
        set_layout.addWidget(self.set_custom)
        layout.addLayout(set_layout)

        # Tiebreak selection
        tiebreak_layout = QHBoxLayout()
        tiebreak_label = QLabel("Tiebreak:")
        self.tiebreak_combo = QComboBox()
        self.tiebreak_combo.addItems(["All", "Yes", "No"])
        tiebreak_layout.addWidget(tiebreak_label)
        tiebreak_layout.addWidget(self.tiebreak_combo)
        layout.addLayout(tiebreak_layout)

        # Buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.validate_and_accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def toggle_game_custom(self, index):
        is_custom = self.game_combo.currentText() == "Custom"
        self.game_custom.setEnabled(is_custom)

    def toggle_set_custom(self, index):
        is_custom = self.set_combo.currentText() == "Custom"
        self.set_custom.setEnabled(is_custom)

    def validate_and_accept(self):
        if self.game_combo.currentText() == "Custom":
            if not self.game_custom.text().isdigit():
                QMessageBox.warning(self, "Input Error", "Game number must be an integer.")
                return
        if self.set_combo.currentText() == "Custom":
            if not self.set_custom.text().isdigit():
                QMessageBox.warning(self, "Input Error", "Set number must be an integer.")
                return
        self.accept()

    def get_filters(self) -> Filters:
        player_mapping = {
            "All": 0,
            "Player 1": 1,
            "Player 2": 2
        }
        tiebreak_mapping = {
            "All": None,
            "Yes": True,
            "No": False
        }

        player = player_mapping[self.player_combo.currentText()]
        tiebreak = tiebreak_mapping[self.tiebreak_combo.currentText()]

        if self.game_combo.currentText() == "Custom":
            game = int(self.game_custom.text())
        else:
            game = 0

        if self.set_combo.currentText() == "Custom":
            set = int(self.set_custom.text())
        else:
            set = 0

        return Filters(
            player=player,
            game=game,
            set=set,
            tiebreak=tiebreak
        )