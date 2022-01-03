from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtWidgets import (
    QWidget, QApplication, QGridLayout,
    QPushButton, QLabel, QLineEdit
)
import sys

import utils
from change_name import NameChanger

class MyApp(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle("Gongik")
        self.clsNc = NameChanger()
        self.nameList = self.clsNc.dctName2Change
        

        # QVBox Layout
        layout = QGridLayout()
        self.setLayout(layout)


        self.init = QLabel("현재 위치: ")
        layout.addWidget(self.init, 0, 0)

        currentLoc = utils.extract_parent_dir()
        self.initLoc = QLabel(currentLoc)
        layout.addWidget(self.initLoc, 0, 1)

        self.picPreview = QLabel("사진 미리보기")
        self.picPreview.setPixmap(QtGui.QPixmap(list(self.nameList.keys())[0]).scaled(200, 200, QtCore.Qt.KeepAspectRatio))
        layout.addWidget(self.picPreview, 0, 3, -1, 5)
 
        self.label = QLabel("상세 입력")
        layout.addWidget(self.label, 1, 0)
 
        self.nameInput = QLineEdit()
        self.nameInput.setPlaceholderText("상세 정보 입력")
        self.nameInput.setMaxLength(30)
        self.nameInput.returnPressed.connect(self.returnPressedPreview)
        layout.addWidget(self.nameInput, 1, 1)

        self.btnPreview = QPushButton("파일명 등록하기")
        self.btnPreview.clicked.connect(self.returnPressedPreview)
        layout.addWidget(self.btnPreview, 2, 0)

        self.labelPreview = QLabel()
        layout.addWidget(self.labelPreview, 2, 1)

        self.btnPreview = QPushButton("파일 이름 및 주소 보기")
        self.btnPreview.clicked.connect(self.returnPressedResult)
        layout.addWidget(self.btnPreview, 3, 0)

        self.finalResult = QLabel()
        layout.addWidget(self.finalResult, 3, 1)

        self.btnNext = QPushButton("다음 장소 보기")
        self.btnNext.clicked.connect(self.onBtnNext)
        layout.addWidget(self.btnNext, 4, 0)

        self.btn2Change = QPushButton("이름 바꾸기")
        self.btn2Change.clicked.connect(self.onBtnChange)
        layout.addWidget(self.btn2Change, 4, 1)



    def returnPressedPreview(self):
        text = self.nameInput.text()
        print(text)
        self.labelPreview.setText(text)

    def returnPressedResult(self):
        print(f'setText = {self.nameList}')
        self.finalResult.setText(str(self.nameList).replace(', ',',\n'))

    def onBtnNext(self):
        self.picPreview.setPixmap(QtGui.QPixmap(list(self.nameList.keys())[1]).scaled(200, 200, QtCore.Qt.KeepAspectRatio))



    def onBtnChange(self):
        self.clsNc.process_cli()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    screen = MyApp()
    screen.resize(540, 100)
    screen.show()
 
    sys.exit(app.exec_())