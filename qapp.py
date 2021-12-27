from PyQt5.QtWidgets import (
    QWidget, QApplication, QGridLayout,
    QPushButton, QLabel, QLineEdit
)
import sys

class MyApp(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle("Gongik")

        # QVBox Layout
        layout = QGridLayout()
        self.setLayout(layout)
 
        self.label = QLabel("분류")
        layout.addWidget(self.label, 0, 0)
 
        self.nameInput =QLineEdit()
        self.nameInput.setPlaceholderText("enter your name")
        self.nameInput.setMaxLength(10)
        self.nameInput.returnPressed.connect(self.returnPressed)
        layout.addWidget(self.nameInput, 0, 1)

        self.labelO = QLabel()
        layout.addWidget(self.labelO, 1, 1)

        self.button = QPushButton("미리보기")
        self.button.clicked.connect(self.returnPressed)
        layout.addWidget(self.button, 1, 0)


    def returnPressed(self):
        text = self.nameInput.text()
        print(text)
        self.labelO.setText(text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    screen = MyApp()
    screen.resize(320, 200)
    screen.show()
 
    sys.exit(app.exec_())