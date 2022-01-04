import sys
from PyQt5.QtWidgets import QApplication, QDialog, QGridLayout, QLabel, QMainWindow, QAction, QPushButton, qApp
from PyQt5.QtGui import QIcon

from qCenterWid import GongikWidget
import utils

# exe 빌드하기
# pyinstaller -w -F --add-data 'db/addr.db;./db' --add-data 'img/frog.ico;./img' --add-data 'img/developer.ico;./img' --add-data 'img/exit.ico;,./img' --icon=img/frog.ico qApp.py

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
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('프로그램을 종료합니다. 완료 버튼을 누르지 않았다면 진행 상황이 저장되지 않습니다.')
        exitAction.triggered.connect(qApp.quit)

        #메뉴 바 - info
        infoAction = QAction(QIcon(self.main_icon_path), '프로그램 정보', self)
        infoAction.setShortcut('Ctrl+I')
        infoAction.setStatusTip('프로그램의 정보를 확인합니다.')
        infoAction.triggered.connect(self.view_developer_info)

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

    def view_developer_info(self):
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

        label1 = QLabel('version 1.1(2022-01-05)')
        label2 = QLabel('개발자: 안태영\n연락처: collinahn@gmail.com\n참고사항: 오프라인에서 로컬DB를 사용하여 위치를 추적하는 방식으로,\n부정확할 수 있습니다. 개선 예정입니다.')

        self.pushButton1= QPushButton('확인')
        self.pushButton1.clicked.connect(self.pushButtonClicked)

        layout = QGridLayout()
        layout.addWidget(label1, 0, 0)
        layout.addWidget(label2, 1, 0, 1, -1)
        layout.addWidget(self.pushButton1, 2, 2)

        self.setLayout(layout)

    def pushButtonClicked(self):
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())