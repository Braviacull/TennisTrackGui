from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QSlider
from PySide6.QtCore import Qt

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

        # Creazione di un QSlider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(0)
        # self.slider.setTickPosition(QSlider.TicksBelow)
        # self.slider.setTickInterval(10)

        # Creazione di una QLabel per mostrare il valore del QSlider
        self.label = QLabel("Valore: 0")
        
        # Collegamento del segnale valueChanged del QSlider a uno slot
        self.slider.valueChanged.connect(self.updateLabel)

        # Aggiunta del QSlider e della QLabel al layout
        self.layout.addWidget(self.slider)
        self.layout.addWidget(self.label)

        self.setLayout(self.layout)
        self.setWindowTitle('QSlider Example')
        self.show()

    def updateLabel(self, value):
        self.label.setText(f"Valore: {value}")

if __name__ == '__main__':
    app = QApplication([])
    window = MyWindow()
    app.exec_()