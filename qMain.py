# v1.3
# 다음 보는 버튼이 사진에 가려서 안보임 레이아웃 조정 완료(v1.3.1)
# 같은 위치에 찍힌 사진 수량 보여주기 -완료(v1.3.1)
# 스펙시트 보여주기(v1.3.1)
# 시간순으로 정렬, 같은 시간대에 찍힌거면 맨 처음 지정한 위치로 통일 - 완료(v1.3.2)

# v1.4
# 파일이 없으면 지정된 경로에서 파일을 옮겨옴(ppadb 이용)(v1.4.0)
# 같은 폴더에 exif정보가 없는 사진이 있으면 예외처리를 못하던 문제 수정(v1.4.1)
# 연결 전 adb 서버를 가동하여 USB footprint를 pc에 저장한다.(v1.4.2)
# 충돌 있는 키보드 단축키 변경(v1.4.3)
# Logger 추가(v1.4.3)
# 1호차 구분이 제대로 되지 않는 버그 수정(v1.4.4)
# 안내장부착 버튼 추가(v1.4.5)

# v1.5(예정)
# 하단 상태바에 현재 진행 중인 작업 표시(v1.5.0) --> cancelled
# 로딩 중일 시 알려주는 다이얼로그와 프로그레스 바를 띄워준다(v1.5.0)
# 카카오API로 주소를 받아온다(v1.5.1)
# 계고장 부착(v1.5.1)
# 파일명 미리보기 기능 추가(v1.5.2)
# 사진 상세에서 제목이 가운데 정렬 되지 않는 버그 수정(v1.5.2)
# QLineEdit입력 시 즉시 미리보기 업데이트되도록 수정(v1.5.3)


# pip install pyproj pillow requests haversine pyinstaller pyqt5 pure-python-adb

import sys
import time
from PyQt5.QtWidgets import (
    QApplication, 
    QDialog, 
    QGridLayout, 
    QLabel, 
    QMainWindow, 
    QAction,
    QMessageBox, 
    QPushButton, 
    QProgressBar,
    qApp
)
from PyQt5.QtCore import (
    Qt,
    QTimer
)
from PyQt5.QtGui import QIcon

import lib.utils as utils
from lib.log_gongik import Logger
from lib.change_name import NameChanger
from lib.meta_data import GPSInfo, TimeInfo
from qCenterWid import GongikWidget
import qWordBook as const

'''
exe 빌드하기
pyinstaller -F --clean qMain.spec
pyinstaller -w -F --add-data "db/addr.db;./db" --add-data "img/frog.ico;./img" --add-data "img/developer.ico;./img" --add-data "img/exit.ico;./img" --add-data "platform-tools;./platform-tools" --icon=img/frog.ico qMain.py
'''

VERSION_INFO = 'v1.5.3(2022-01-17)'


class Gongik(QMainWindow):
    def __init__(self):
        self.log = Logger()
        self.log.INFO('')
        self.log.INFO('')
        self.log.INFO('')
        self.log.INFO('==============program started=================')
        self.log.INFO('version:', VERSION_INFO)
        self.log.INFO('==============program started=================')
        self.log.INFO('')
        self.log.INFO('')
        self.log.INFO('')

        self.progressDlg = ProgressDialog()
        self.progressDlg.show()

        super().__init__()

        self.title = 'Gongik'
        self.main_icon_path = utils.resource_path('img/frog.ico')
        self.exit_icon_path = utils.resource_path('img/exit.ico')

        self.progressDlg.mark_progress(30)


        self.clsNc = NameChanger()
        self.dctNameStorage = self.clsNc.dctName2Change

        self.progressDlg.mark_progress(80)
        
        if not self.dctNameStorage:
            self.log.WARNING('current folder empty')
            self._handle_failure()
            sys.exit()

        self.progressDlg.mark_progress(100)

        self.init_ui()

        self.progressDlg.close()

    def _handle_failure(self) -> bool:
        failDlg = InitFailDialogue()
        failDlg.exec_()

        if not failDlg.getFilesFmPhone:
            QMessageBox.information(self, 'EXIT_PLAIN', const.MSG_INFO['EXIT_PLAIN'])
            return False

        from lib.file_copy import BridgePhone
        clsBP = BridgePhone()
        self._handle_ADB_failure(clsBP)
        if not clsBP.transfer_files():
            QMessageBox.information(self, 'TRANSFER_FAIL', const.MSG_INFO['TRANSFER_FAIL'])
            return False
            
        QMessageBox.information(self, 'TRANSFER_SUCCESS', const.MSG_INFO['TRANSFER_SUCCESS'])

        return True

    def _handle_ADB_failure(self, clsBridgePhone):
        if not clsBridgePhone.connected:
            self._pop_warn_msg('CONNECTION_ERROR')

        if not clsBridgePhone.executable:
            self._pop_warn_msg('MULTI_CONNECTION_ERROR')

    def _pop_warn_msg(self, code):
        self.log.WARNING(const.MSG_WARN[code])
        QMessageBox.warning(self, code, const.MSG_WARN[code])
        sys.exit()

    def init_ui(self):
        # 상단 정보 설정
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon(self.main_icon_path))

        # 메인 위젯 설정
        qw = GongikWidget()
        self.setCentralWidget(qw)

        #메뉴 바 - progMenu - Exit
        exitAction = QAction(QIcon(self.exit_icon_path), '퇴근하기', self)
        exitAction.setShortcut(const.MSG_SHORTCUT['EXIT'])
        exitAction.setStatusTip(const.MSG_TIP['EXIT'])
        exitAction.triggered.connect(qApp.quit)

        #메뉴 바 - progMenu - info
        infoAction = QAction(QIcon(self.main_icon_path), '프로그램 정보', self)
        infoAction.setShortcut(const.MSG_SHORTCUT['INFO'])
        infoAction.setStatusTip(const.MSG_TIP['INFO'])
        infoAction.triggered.connect(self.onModalDeveloperInfo)

        # 참고 정보 표시
        checkAction = QAction(QIcon(self.main_icon_path), '위치 목록 확인', self)
        checkAction.setShortcut(const.MSG_SHORTCUT['LIST'])
        checkAction.setStatusTip(const.MSG_TIP['LIST'])
        checkAction.triggered.connect(self.onModalAddrInfo)

        self.statusBar()

        menu = self.menuBar()
        menu.setNativeMenuBar(False)
        progMenu = menu.addMenu('&실행')
        additionalMenu = menu.addMenu('&정보')
        
        progMenu.addAction(exitAction)
        additionalMenu.addAction(infoAction)
        additionalMenu.addAction(checkAction)

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

        self.log = Logger()
        self.log.INFO('Fail Info Dialogue')

        self.title = '알림'
        self.icon_path = utils.resource_path('img/frog.ico')

        self.getFilesFmPhone: bool = False

        self.setupUI()

    def setupUI(self):
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


    def onBtnYesClicked(self):  # sourcery skip: class-extract-method
        self.getFilesFmPhone = True
        self.log.INFO('User Selected Getting Files From Phone')
        self.close()

    def onBtnNoClicked(self):
        self.getFilesFmPhone = False
        self.log.INFO('User Selected Not to Transfer')
        self.close()

class DeveloperInfoDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.log = Logger()
        self.log.INFO('Developer Info Dialog')

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
        label1_a = QLabel("안태영(Collin Ahn)")
        label2 = QLabel('연락처:')
        label2.setAlignment(Qt.AlignTop)
        label2_a = QLabel('collinahn@gmail.com')
        # labelSrc = QLabel('소스코드:')
        # labelSrc.setAlignment(Qt.AlignTop)
        # labelSrc_a = QLabel('https://github.com/collinahn/file_name_changer')
        label3 = QLabel('참고사항:')
        label3.setAlignment(Qt.AlignTop)
        label3_a = QLabel('카카오맵 API를 이용하여 주소를 받아옵니다.(인터넷 필요)\n오프라인에서 실행 시 내장된 DB를 이용하므로 부정확한 결과를 얻을 수 있습니다.')
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
        self.log.INFO('Developer Info Dialog closed')
        self.close()

class AddrInfoDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.log = Logger()
        self.log.INFO('Addr Info Dialog')

        self.title = '사진 상세'
        self.icon_path = utils.resource_path('img/frog.ico')

        self.clsNc = NameChanger()
        self.clsGI = GPSInfo()
        self.clsTI = TimeInfo()
        self.dctName2AddrStorage = self.clsNc.dctName2Change
        self.dctName2Time = self.clsTI.time_as_dct
        self.dctFinalResult = self.clsNc.dctFinalResult
        self.dctName2RealAddr = self.clsNc.dctName2Change

        self.setupUI()

    def setupUI(self):
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon(self.icon_path))

        lstNameAddrTime = [(
            QLabel('파일 이름'), 
            QLabel('실제 위치'),
            QLabel(' '),
            QLabel('처리 위치'), 
            QLabel('촬영 시각'), 
            QLabel('최종 이름'))]
        for label in lstNameAddrTime[-1]:
            label.setAlignment(Qt.AlignCenter)

        # QLabel 객체 삽입
        for name, addr in self.dctName2AddrStorage.items():
            lstNameAddrTime.append((
                QLabel(f'{name}'),
                QLabel(f'{self.check_key_error(self.dctName2RealAddr, name)}'),
                QLabel('->'),
                QLabel(f'{addr}'),
                QLabel(f'{self.check_key_error(self.dctName2Time, name)}'),
                QLabel(f'{self.check_key_error(self.dctFinalResult, name)}')
            ))

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

    @staticmethod
    def check_key_error(dctDataSet: dict[str, str], key: str) -> str:
        try:
            return dctDataSet[key]
        except KeyError:
            return '지정되지 않음'

    def onBtnClicked(self):
        self.log.INFO('Addr Info Dialog closed')
        self.close()

class ProgressDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.log = Logger()
        self.log.INFO('init')

        self.title = '알림'
        self.icon_path = utils.resource_path('img/developer.ico')

        self.setupUI()

    def setupUI(self):
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon(self.icon_path))

        comment = QLabel('로딩 중입니다. 잠시만 기다려 주세요.')
        comment.setAlignment(Qt.AlignTop)

        self.pushBtnExit= QPushButton('확인')

        self.pbar = QProgressBar(self)
        self.pbar.setAlignment(Qt.AlignCenter)
        self.__progress = 0

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(comment, 0, 0)
        layout.addWidget(self.pbar, 1, 0)

    def mark_progress(self, percentage):
        for i in range(self.__progress, percentage):
            self.pbar.setValue(int(i))
            self.__progress = percentage
            time.sleep(0.01) # 좋지 않은 시각효과
            






if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Gongik()
    sys.exit(app.exec_())