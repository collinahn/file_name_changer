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

# v1.5
# 하단 상태바에 현재 진행 중인 작업 표시(v1.5.0) --> cancelled
# 로딩 중일 시 알려주는 다이얼로그와 프로그레스 바를 띄워준다(v1.5.0)
# 카카오API로 주소를 받아온다(v1.5.1)
# 계고장 부착(v1.5.1)
# 파일명 미리보기 기능 추가(v1.5.2)
# 사진 상세에서 제목이 가운데 정렬 되지 않는 버그 수정(v1.5.2)
# QLineEdit입력 시 즉시 미리보기 업데이트되도록 수정(v1.5.3)
# 호차 관련 오류 수정(v1.5.4)
# 파일 옮기기에 프로그레스 바 표시 (v1.5.5)
# 파일 이름 변경에 프로그레스 바 표시 -> QTimer 이용 (v1.5.5)
# GPS 정보 보낼 때 바로 보내지 않고 인터넷 연결을 확인하고 보내도록 수정(v1.5.6)

# 파일을 옮겨온 후에 다시 실행할 필요 없이 바로 초기화하도록 수정(v1.6.0b)
# 최초 실행시 유의사항 띄우기(v1.6.1)
# adb 연결 체크 시 따로 쉘을 열지 않고도 실행하도록 수정(v1.6.2)
# 좀 더 다양한 에러 사항을 유저에게 전달하여 대처할 수 있도록 안내 세분화(v1.6.3)

# pip install pyproj pillow requests haversine pyinstaller pyqt5 pure-python-adb

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
from PyQt5.QtCore import (
    Qt,
)
from PyQt5.QtGui import QIcon

import lib.utils as utils
from lib.log_gongik import Logger
from lib.file_detect import FileDetector
from lib.change_name import NameChanger
from lib.meta_data import (
    GPSInfo, 
    TimeInfo
)
from qCenterWid import GongikWidget
from qDialog import (
    ProgressDialog,
    InitInfoDialogue
)
import qWordBook as const


'''
exe 빌드하기
pyinstaller -F --clean qMain.spec
pyinstaller -w -F --clean --add-data "db/addr.db;./db" --add-data "img/frog.ico;./img" --add-data "img/developer.ico;./img" --add-data "img/exit.ico;./img" --add-data "platform-tools;./platform-tools" --icon=img/frog.ico qMain.py
'''

VERSION_INFO = 'v1.6.3(2022-01-18)'

INSTRUCTION = '''현재 디렉토리에 처리할 수 있는 파일이 없습니다.
연결된 핸드폰에서 금일 촬영된 사진을 불러옵니다.

**주의사항**
파일 전송 전 핸드폰을 "잠금이 해제된 상태"로 유지하세요.
'''


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

        self.progressDlg.mark_progress(20, '로딩 중')


        self.clsFD = FileDetector('.') # '.'는 초기 파일 체크용
        self.files = self.clsFD.fileList

        self.progressDlg.mark_progress(30, '파일 분석 중')
        
        if not self.files:
            self.log.WARNING('current folder empty')
            if not self._handle_failure():
                sys.exit()

        self.progressDlg.mark_progress(100, '파일 검사 중', True)

        self.init_ui()

        self.progressDlg.close()

    def _handle_failure(self) -> bool:
        failDlg = InitInfoDialogue(INSTRUCTION, \
                                    btn=('확인', '다음에'))
        failDlg.exec_()

        self.progressDlg.show()

        if not failDlg.answer:
            QMessageBox.information(self, 'EXIT_PLAIN', const.MSG_INFO['EXIT_PLAIN'])
            return False

        from lib.file_copy import BridgePhone
        clsBP = BridgePhone()
        self._handle_ADB_failure(clsBP)

        self.progressDlg.mark_progress(50, '파일 복사 중')

        if not clsBP.transfer_files():
            QMessageBox.information(self, 'TRANSFER_FAIL', const.MSG_INFO['TRANSFER_FAIL'])
            return False
        
        self.progressDlg.mark_progress(70, '이상 감지 중')

        # QMessageBox.information(self, 'TRANSFER_SUCCESS', const.MSG_INFO['TRANSFER_SUCCESS'])

        return True

    def _handle_ADB_failure(self, clsBridgePhone):
        if not clsBridgePhone.connected:
            self._pop_warn_msg('CONNECTION_ERROR')

        if not clsBridgePhone.executable:
            self._pop_warn_msg('MULTI_CONNECTION_ERROR')

        if not clsBridgePhone.files:
            self._pop_warn_msg('EMPTY_FILE_ERROR')


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
        label3_a = QLabel(const.PROGRAM_INFO)
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
        import copy

        self.log = Logger()
        self.log.INFO('Addr Info Dialog')

        self.title = '사진 상세'
        self.icon_path = utils.resource_path('img/frog.ico')

        self.clsNc = NameChanger()
        self.clsGI = GPSInfo()
        self.clsTI = TimeInfo()
        self.dctName2AddrStorage = self.clsNc.dctName2Change
        self.dctName2Time = self.clsTI.time_as_dct
        self.dctName2RealAddr = self.clsNc.dctName2Change
        self.dctFinalResult = copy.deepcopy(self.clsNc.dctFinalResult)

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
        from qCenterWid import GongikWidget
        for name, addr in self.dctName2AddrStorage.items():
            lstNameAddrTime.append((
                QLabel(f'{name}'),
                QLabel(f'{self.check_key_error(self.dctName2RealAddr, name)}'),
                QLabel('->'),
                QLabel(f'{addr}'),
                QLabel(f'{self.check_key_error(self.dctName2Time, name)}'),
                QLabel(f'{self.check_key_error(self.dctFinalResult, name)}')
            ))
            print(f'{self.dctFinalResult = }')
            print(f'{self.dctName2AddrStorage = }')
            print(f'{self.dctName2RealAddr = }')

        lstNameAddrTime.sort(key=lambda x: x[0].text()) #라벨 이름 기준 정렬

        # 확인버튼
        self.pushButton1= QPushButton('확인(개발 중인 기능입니다)')
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


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # warnDlg = InitInfoDialogue(INSTRUCTION, btn=('확인했습니다.', ))
    # warnDlg.exec_()
    # del warnDlg

    ex = Gongik()
    sys.exit(app.exec_())