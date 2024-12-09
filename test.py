from PySide6.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QCheckBox, QPushButton

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

        # Creazione di un layout orizzontale per la checkbox e la label
        h_layout = QHBoxLayout()
        self.checkbox = QCheckBox()
        self.label = QLabel("Label vicino alla checkbox")
        
        # Aggiunta della checkbox e della label al layout orizzontale
        h_layout.addWidget(self.checkbox)
        h_layout.addWidget(self.label)

        # Aggiunta del layout orizzontale al layout principale
        self.layout.addLayout(h_layout)

        # Aggiunta di un pulsante di esempio
        self.button = QPushButton("Esempio Pulsante")
        self.layout.addWidget(self.button)

        self.setLayout(self.layout)
        self.setWindowTitle('Checkbox vicino alla Label')
        self.show()

if __name__ == '__main__':
    app = QApplication([])
    window = MyWindow()
    app.exec_()