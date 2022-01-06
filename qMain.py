# v1.3
# 시간순으로 정렬, 같은 시간대에 찍힌거면 맨 처음 지정한 위치로 통일 - 완료(v1.3)
# 다음 보는 버튼이 사진에 가려서 안보임 레이아웃 조정 완료(v1.3)
# 같은 위치에 찍힌 사진 수량 보여주기 -완료(v1.3)


import sys
from PyQt5.QtWidgets import QApplication, QDialog, QGridLayout, QLabel, QMainWindow, QAction, QPushButton, qApp
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from qCenterWid import GongikWidget
import utils

# exe 빌드하기
# pyinstaller -w -F --add-data "db/addr.db;./db" --add-data "img/frog.ico;./img" --add-data "img/developer.ico;./img" --add-data "img/exit.ico;./img" --icon=img/frog.ico qMain.py
VERSION_INFO = 'v1.3(2022-01-07)'

class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.title = 'Gongik'
        self.main_icon_path = utils.resource_path('img/frog.ico')
        self.exit_icon_path = utils.resource_path('img/exit.ico')
        
        self.init_ui()

    def init_ui(self):
        #메뉴 바 - progMenu - Exit
        exitAction = QAction(QIcon(self.exit_icon_path), '퇴근하기', self)
        exitAction.setShortcut('Ctrl+Shift+Q')
        exitAction.setStatusTip('프로그램을 종료합니다. 완료 버튼을 누르지 않았다면 진행 상황이 저장되지 않습니다.')
        exitAction.triggered.connect(qApp.quit)

        #메뉴 바 - progMenu - info
        infoAction = QAction(QIcon(self.main_icon_path), '프로그램 정보', self)
        infoAction.setShortcut('Ctrl+I')
        infoAction.setStatusTip('프로그램의 정보를 확인합니다.')
        infoAction.triggered.connect(self.onModalDeveloperInfo)

        self.statusBar()

        menu = self.menuBar()
        menu.setNativeMenuBar(True)
        progMenu = menu.addMenu('&파일')

        progMenu.addAction(infoAction)
        progMenu.addAction(exitAction)

        # 기본 설정
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon(self.main_icon_path))

        # 메인 위젯 설정
        qw = GongikWidget()
        self.setCentralWidget(qw)

        self.setGeometry(540, 300, 300, 200)
        self.show()

    def onModalDeveloperInfo(self):
        dlg = InfoDialog()
        dlg.exec_()


class InfoDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.title = '프로그램 정보'
        self.icon_path = utils.resource_path('img/developer.ico')

        self.setupUI()

    def setupUI(self):
        self.setGeometry(1100, 200, 300, 100)
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon(self.icon_path))

        label0 = QLabel('버전:')
        label0.setAlignment(Qt.AlignTop)
        label0_a = QLabel(VERSION_INFO)
        label1 = QLabel('개발자:')
        label1.setAlignment(Qt.AlignTop)
        label1_a = QLabel("안태영")
        label2 = QLabel('연락처:')
        label2.setAlignment(Qt.AlignTop)
        label2_a = QLabel('collinahn@gmail.com')
        label3 = QLabel('참고사항:')
        label3.setAlignment(Qt.AlignTop)
        label3_a = QLabel('오프라인에서 내장된 로컬DB \n(출처: www.juso.go.kr)를 사용하여 \n위치를 추적하는 방식으로, 다소 부정확할 수 있습니다. \n개선 예정입니다.')
        label4 = QLabel('License:')
        label4.setAlignment(Qt.AlignTop)
        label4_a = QLabel('MIT License \nCopyright (c) 2021 Collin Ahn')

        self.pushButton1= QPushButton('확인')
        self.pushButton1.clicked.connect(self.onBtnClicked)

        layout = QGridLayout()
        layout.addWidget(label0, 0, 0)
        layout.addWidget(label0_a, 0, 1)
        layout.addWidget(label1, 1, 0)
        layout.addWidget(label1_a, 1, 1)
        layout.addWidget(label2, 2, 0)
        layout.addWidget(label2_a, 2, 1)
        layout.addWidget(label3, 3, 0)
        layout.addWidget(label3_a, 3, 1)
        layout.addWidget(label4, 4, 0)
        layout.addWidget(label4_a, 4, 1)
        layout.addWidget(self.pushButton1, 4, 2)

        self.setLayout(layout)

    def onBtnClicked(self):
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())