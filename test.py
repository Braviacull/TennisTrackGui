import sys
import vlc
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from PySide6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("VLC Video Player")
        self.resize(800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.vlc_instance = vlc.Instance()
        self.media_player = self.vlc_instance.media_player_new()

        self.video_frame = QWidget(self)
        self.video_frame.setAttribute(Qt.WA_OpaquePaintEvent)
        self.layout.addWidget(self.video_frame)

        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.play_video)
        self.layout.addWidget(self.play_button)

        self.start_frame = 100  # Imposta il frame di inizio desiderato

    def play_video(self):
        media = self.vlc_instance.media_new("sinner10sec.mp4")
        self.media_player.set_media(media)

        if sys.platform.startswith('linux'):  # for Linux using the X Server
            self.media_player.set_xwindow(self.video_frame.winId())
        elif sys.platform == "win32":  # for Windows
            self.media_player.set_hwnd(self.video_frame.winId())
        elif sys.platform == "darwin":  # for MacOS
            self.media_player.set_nsobject(int(self.video_frame.winId()))

        self.media_player.play()

        # Attendi che il media sia pronto
        self.media_player.event_manager().event_attach(vlc.EventType.MediaPlayerPlaying, self.set_start_position)

    def set_start_position(self, event):
        # Ottieni il frame rate del video
        fps = self.media_player.get_fps()
        if fps > 0:
            # Converti il numero di frame in millisecondi
            start_time_ms = int((self.start_frame / fps) * 1000)
            self.media_player.set_time(start_time_ms)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())