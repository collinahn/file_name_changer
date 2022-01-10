# v1.3
# 시간순으로 정렬, 같은 시간대에 찍힌거면 맨 처음 지정한 위치로 통일 - 완료(v1.3)
# 다음 보는 버튼이 사진에 가려서 안보임 레이아웃 조정 완료(v1.3)
# 같은 위치에 찍힌 사진 수량 보여주기 -완료(v1.3)
# 스펙시트 보여주기

# v1.3a
# 파일이 없으면 지정된 경로에서 파일을 옮겨옴

import sys
from PyQt5.QtWidgets import (
    QApplication, 
    QDialog, 
    QGridLayout, 
    QLabel, 
    QMainWindow, 
    QAction,
    QMessageBox, 
    QPushButton, 
    qApp
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from qCenterWid import GongikWidget
from change_name import NameChanger
from meta_data import GPSInfo
import utils

'''
exe 빌드하기
pyinstaller -w -F --add-data "db/addr.db;./db" --add-data "img/frog.ico;./img" --add-data "img/developer.ico;./img" --add-data "img/exit.ico;./img" --icon=img/frog.ico qMain.py
'''

VERSION_INFO = 'v1.3b(2022-01-10)'

class Gongik(QMainWindow):
    def __init__(self):
        super().__init__()

        self.title = 'Gongik'
        self.main_icon_path = utils.resource_path('img/frog.ico')
        self.exit_icon_path = utils.resource_path('img/exit.ico')
        
        self.clsNc = NameChanger()
        self.dctNameStorage = self.clsNc.dctName2Change
        
        if not self.dctNameStorage:
            failDlg = InitFailDialogue()
            failDlg.exec_()
            if failDlg.result:
                QMessageBox.warning(self, '경고', f'개발중인 기능입니다.\n수동으로 사진을 옮기세요.')
                sys.exit()
            else:
                QMessageBox.warning(self, '경고', f'종료합니다.')
                sys.exit()

        self.init_ui()

    def init_ui(self):
        # 기본 설정
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon(self.main_icon_path))

        # 메인 위젯 설정
        qw = GongikWidget()
        self.setCentralWidget(qw)

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

        # 참고 정보 표시
        checkAction = QAction(QIcon(self.main_icon_path), '위치 목록 확인', self)
        checkAction.setShortcut('Ctrl+G')
        checkAction.setStatusTip('사진 정보 목록을 불러옵니다.')
        checkAction.triggered.connect(self.onModalAddrInfo)

        self.statusBar()

        menu = self.menuBar()
        menu.setNativeMenuBar(False)
        progMenu = menu.addMenu('&실행')
        additionalMenu = menu.addMenu('&정보')
        
        progMenu.addAction(exitAction)
        additionalMenu.addAction(infoAction)
        additionalMenu.addAction(checkAction)

        # self.setGeometry(540, 300, 300, 200)
        self.show()

    def onModalDeveloperInfo(self):
        dlg = DeveloperInfoDialog()
        dlg.exec_()

    def onModalAddrInfo(self):
        alg = AddrInfoDialog()
        alg.exec_()


class InitFailDialogue(QDialog):
    def __init__(self):
        super().__init__()

        self.title = '알림'
        self.icon_path = utils.resource_path('img/frog.ico')

        self.result: bool = False

        self.setupUI()

    def setupUI(self):
        # self.setGeometry(1100, 200, 300, 100)
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon(self.icon_path))

        label0 = QLabel('현재 디렉토리에 처리할 수 있는 파일이 없습니다.\n연결된 핸드폰에서 금일 촬영된 사진을 불러오겠습니까?')
        label0.setAlignment(Qt.AlignTop)
        
        self.pushYesBtn= QPushButton('네(y)')
        self.pushYesBtn.clicked.connect(self.onBtnYesClicked)
        self.pushYesBtn.setShortcut('Y')

        self.pushNoBtn= QPushButton('아니오(n)')
        self.pushNoBtn.clicked.connect(self.onBtnNoClicked)
        self.pushNoBtn.setShortcut('N')

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(label0, 0, 0)
        layout.addWidget(self.pushYesBtn)
        layout.addWidget(self.pushNoBtn)


    def onBtnYesClicked(self):
        self.result = True
        self.close()

    def onBtnNoClicked(self):
        self.result = False
        self.close()

class DeveloperInfoDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.title = '프로그램 정보'
        self.icon_path = utils.resource_path('img/developer.ico')

        self.setupUI()

    def setupUI(self):
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

        self.pushBtnExit= QPushButton('확인')
        self.pushBtnExit.clicked.connect(self.onBtnClicked)

        layout = QGridLayout()
        self.setLayout(layout)
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
        layout.addWidget(self.pushBtnExit, 4, 2)


    def onBtnClicked(self):
        self.close()

class AddrInfoDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.title = '사진 상세'
        self.icon_path = utils.resource_path('img/frog.ico')

        self.clsNc = NameChanger()
        self.clsGI = GPSInfo()
        self.dctName2AddrStorage = self.clsNc.dctName2Change
        self.dctName2Time = self.clsGI.time_as_str

        self.setupUI()

    def setupUI(self):
        # self.setGeometry(1100, 200, 300, 100)
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon(self.icon_path))

        lstNameAddrTime = [(QLabel('파일 이름'), QLabel('사진 위치'), QLabel('촬영 시각'))]
        lstNameAddrTime[-1][0].setAlignment(Qt.AlignCenter)
        lstNameAddrTime[-1][1].setAlignment(Qt.AlignCenter)
        lstNameAddrTime[-1][2].setAlignment(Qt.AlignCenter)

        # QLabel 객체 삽입
        for name, addr in self.dctName2AddrStorage.items():
            lstNameAddrTime.append((QLabel(f'{name}'), QLabel(f'{addr}'), QLabel(f'{self.dctName2Time[name]}')))
        lstNameAddrTime.sort(key=lambda x: x[0].text()) #라벨 이름 기준 정렬

        # 확인버튼
        self.pushButton1= QPushButton('확인')
        self.pushButton1.clicked.connect(self.onBtnClicked)

        layout = QGridLayout()

        for gridLoc, tplNameAddrTime in enumerate(lstNameAddrTime):
            for idx, data in enumerate(tplNameAddrTime):
                layout.addWidget(data, gridLoc, idx)

        layout.addWidget(self.pushButton1, len(lstNameAddrTime)+1, 0, -1, -1)

        self.setLayout(layout)

    def onBtnClicked(self):
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Gongik()
    sys.exit(app.exec_())