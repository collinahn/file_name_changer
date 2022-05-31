# pip3 install pyproj pillow requests haversine pyinstaller pyqt5 pure-python-adb paramiko pytesseract

import sys
import time
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import (
    Qt,
)
from PyQt5.QtWidgets import (
    QApplication, 
    QGridLayout, 
    QLabel, 
    QAction,
    QMessageBox, 
    QPushButton, 
    QDesktopWidget,
    QButtonGroup,
    QAbstractButton,
    QGroupBox,
    qApp
)

import lib.utils as utils
import qWordBook as const
from lib.file_copy import BridgePhone
from lib.file_property import FileProp
from lib.queue_order import MstQueue
from lib.send_file import LogFileSender
from lib.log_gongik import Logger
from lib.base_folder import WorkingDir
from qMainWidget import GongikWidget
from qVersionDialog import VersionDialog
from qRestoreDialog import RestoreDialog
from qWidgets.progress_display import ProgressWidgetThreaded4Start
from lib.file_detect import (
    FileDetector, 
    LogFileDetector
)
from qDraggable import ( #custom qobjects
    QDialog, 
    QMainWindow, 
    QWidget,
)
from qDialog import (
    InitInfoDialogue,
    FolderDialog
)

'''
exe 빌드하기
pyinstaller -F --clean qMain.spec
pyinstaller -w -F --clean --add-data "db/addr.db;./db" --add-data "img/frog.ico;./img" --add-data "img/developer.ico;./img" --add-data "img/exit.ico;./img" --add-data "img/final.ico;./img" --add-data "platform-tools;./platform-tools" --add-data "tesseract-ocr;./tesseract-ocr" --icon=img/final.ico qMain.py
'''

VERSION_INFO = '(release)gongik_v2.6.6'

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


        self.progress_dlg = ProgressWidgetThreaded4Start()
        self.progress_dlg.update(5, 'init')
        self.progress_dlg.show()
        self.progress_dlg.update(10, '기본 정보를 가져오는 중')

        super().__init__()

        self.title = 'Gongik'
        self.main_icon_path = utils.resource_path(const.IMG_FROG)
        self.final_icon_path = utils.resource_path(const.IMG_FROG2)
        self.exit_icon_path = utils.resource_path(const.IMG_EXIT)
        self.dev_icon_path = utils.resource_path(const.IMG_DEV)

        self.progress_dlg.update(5, '위치를 탐색하는 중')

        self.folderDialog = FolderDialog() # 파일 경로 확인 다이얼로그
        self.folderDialog.exec_()
        self.targetFolder = WorkingDir(
            self.folderDialog.path, 
            utils.get_relative_path(self.folderDialog.path)
        )
        self.log.INFO(f'{self.targetFolder = }')

        self.clsFD = FileDetector(self.targetFolder.rel_path) # '.'는 초기 파일 체크용
        self.files = self.clsFD.file_list

        self.progress_dlg.update(5, '파일 불러오는 중')
        
        if not self.files:
            self.log.WARNING('current folder empty')
            if not self._get_files_fm_phone():
                sys.exit()

        self.progress_dlg.update(10, '파일 분석 중')

        self._init_ui()
        self._init_main_widget()
        
        self.progress_dlg.update(10, '무결성 검사 중')
        self.progress_dlg.close()

    def _init_main_widget(self):
        # 메인 위젯 설정
        qw = GongikWidget(self.targetFolder.abs_path)
        self.setCentralWidget(qw)

    def _get_files_fm_phone(self) -> bool:
        failDlg = InitInfoDialogue(const.NO_FILE_INSTRUCTION, btn=('확인', '다음에'))
        failDlg.exec_()

        self.progress_dlg.show()

        if not failDlg.answer:
            QMessageBox.information(self, 'EXIT_PLAIN', const.MSG_INFO['EXIT_PLAIN'])
            return False

        from lib.file_copy import BridgePhone
        clsBP = BridgePhone()
        self._handle_ADB_failure(clsBP)

        self.progress_dlg.update(20, '파일 복사 중')

        if not clsBP.transfer_files():
            QMessageBox.information(self, 'TRANSFER_FAIL', const.MSG_INFO['TRANSFER_FAIL'])
            return False
        
        self.progress_dlg.update(10, '이상 감지 중')
        return True

    def _handle_ADB_failure(self, clsBridgePhone: BridgePhone):
        if not clsBridgePhone.connected:
            self._pop_warn_msg('CONNECTION_ERROR')

        if not clsBridgePhone.executable:
            self._pop_warn_msg('MULTI_CONNECTION_ERROR')

        if not clsBridgePhone.files:
            self._pop_warn_msg('EMPTY_FILE_ERROR')


    def _pop_warn_msg(self, code):
        self.log.WARNING(repr(const.MSG_WARN[code]))
        QMessageBox.warning(self, code, const.MSG_WARN[code])
        sys.exit()

    def _init_ui(self):
        # 상단 정보 설정
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon(self.main_icon_path))
        self.setStyleSheet(const.QSTYLE_SHEET)
        self.setWindowFlags(Qt.FramelessWindowHint)

        #메뉴 바 - progMenu - Exit
        exitAction = QAction(QIcon(self.exit_icon_path), '퇴근하기', self)
        exitAction.setShortcut(const.MSG_SHORTCUT['EXIT'])
        exitAction.setStatusTip(const.MSG_TIP['EXIT'])
        exitAction.triggered.connect(qApp.quit)

        # (베타) 이미지에서 텍스트 추출
        recommendAction = QAction(QIcon(self.dev_icon_path), '텍스트 추출(베타)', self)
        recommendAction.setShortcut(const.MSG_SHORTCUT['RECOMMEND'])
        recommendAction.setStatusTip(const.MSG_TIP['RECOMMEND'])
        recommendAction.triggered.connect(self.onModalRecommend)

        # 작업 복구 메뉴
        restoreAction = QAction(QIcon(self.dev_icon_path), '복구하기', self)
        restoreAction.setShortcut(const.MSG_SHORTCUT['RESTORE'])
        restoreAction.setStatusTip(const.MSG_TIP['RESTORE'])
        restoreAction.triggered.connect(self.onModalRestore)

        #메뉴 바 - info
        infoAction = QAction(QIcon(self.dev_icon_path), '프로그램 정보', self)
        infoAction.setShortcut(const.MSG_SHORTCUT['INFO'])
        infoAction.setStatusTip(const.MSG_TIP['INFO'])
        infoAction.triggered.connect(self.onModalDeveloperInfo)

        # 참고 정보 표시
        checkAction = QAction(QIcon(self.main_icon_path), '위치 목록 확인', self)
        checkAction.setShortcut(const.MSG_SHORTCUT['LIST'])
        checkAction.setStatusTip(const.MSG_TIP['LIST'])
        checkAction.triggered.connect(self.onModalAddrInfo)

        # 업데이트
        updateAction = QAction(QIcon(self.final_icon_path), '업데이트 확인', self)
        updateAction.setShortcut(const.MSG_SHORTCUT['UPDATE'])
        updateAction.setStatusTip(const.MSG_TIP['UPDATE'])
        updateAction.triggered.connect(self.onModalUpdateApp)

        logReportAction = QAction(QIcon(self.dev_icon_path), '로그 보고하기', self)
        logReportAction.triggered.connect(self.onReportRecentLog)

        self.statusBar()

        menu = self.menuBar()
        menu.setNativeMenuBar(False)
        progMenu = menu.addMenu('실행')
        additionalMenu = menu.addMenu('정보')
        logMenu = menu.addMenu('보고')
        
        progMenu.addAction(restoreAction)
        progMenu.addAction(recommendAction)
        progMenu.addAction(exitAction)
        additionalMenu.addAction(infoAction)
        additionalMenu.addAction(checkAction)
        additionalMenu.addAction(updateAction)
        logMenu.addAction(logReportAction)

        # self.center()
        self.move(120, 250)
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def onModalRestore(self):
        rdlg = RestoreDialog()
        rdlg.exec_()

    def onModalDeveloperInfo(self):
        dlg = DeveloperInfoDialog()
        dlg.exec_()

    def onModalAddrInfo(self):
        alg = AddrInfoDialog()
        alg.exec_()

    def onModalUpdateApp(self):
        vlg = VersionDialog()
        vlg.exec_()

    def onModalRecommend(self):
        rlg = RecommendDialog()
        rlg.exec_()

    def onReportRecentLog(self):
        rllg = ReportLogDialog()
        rllg.exec_()

class DeveloperInfoDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.log = Logger()
        self.log.INFO('Developer Info Dialog')

        self.title = '프로그램 정보'
        self.iconPath = utils.resource_path(const.IMG_DEV)

        self.setupUI()

    def setupUI(self):
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon(self.iconPath))
        self.setStyleSheet(const.QSTYLE_SHEET_POPUP)
        self.setWindowFlags(Qt.FramelessWindowHint)

        lVersion = QLabel('버전:')
        lVersionInfo = QLabel(f'{VERSION_INFO}')
        lDeveloper = QLabel('개발자:')
        lDeveloperInfo = QLabel('안태영(Collin Ahn)')
        lSourceCode = QLabel('소스코드:')
        lSourceCodeUrl = QLabel('https://github.com/collinahn/file_name_changer')
        lContact = QLabel('연락처:')
        lContactInfo = QLabel('collinahn@gmail.com')
        lRef = QLabel('참고사항:')
        lRefInfo = QLabel(const.PROGRAM_INFO)
        lLicense = QLabel('License:')
        lLicenseInfo = QLabel('MIT License \nCopyright (c) 2021 Collin Ahn')

        
        self.pushBtnExit= QPushButton('확인')
        self.pushBtnExit.clicked.connect(self.onBtnClicked)

        lVersion.setAlignment(Qt.AlignTop)
        lDeveloper.setAlignment(Qt.AlignTop)
        lSourceCode.setAlignment(Qt.AlignTop)
        lContact.setAlignment(Qt.AlignTop)
        lRef.setAlignment(Qt.AlignTop)
        lLicense.setAlignment(Qt.AlignTop)

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(lVersion, 0, 0)
        layout.addWidget(lVersionInfo, 0, 1)
        layout.addWidget(lDeveloper, 1, 0)
        layout.addWidget(lDeveloperInfo, 1, 1)
        layout.addWidget(lSourceCode, 2, 0)
        layout.addWidget(lSourceCodeUrl, 2, 1)
        layout.addWidget(lContact, 3, 0)
        layout.addWidget(lContactInfo, 3, 1)
        layout.addWidget(lRef, 4, 0)
        layout.addWidget(lRefInfo, 4, 1)
        layout.addWidget(lLicense, 5, 0)
        layout.addWidget(lLicenseInfo, 5, 1)
        layout.addWidget(self.pushBtnExit, 5, 2)

    def onBtnClicked(self):
        self.log.INFO('Developer Info Dialog closed')
        self.close()


class AddrInfoDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.log = Logger()
        self.log.INFO('Addr Info Dialog')

        self.title = '사진 상세'
        self.iconPath = utils.resource_path(const.IMG_FROG)

        self.setupUI()

    def setupUI(self):
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon(self.iconPath))
        self.setStyleSheet(const.QSTYLE_SHEET_POPUP)
        self.setWindowFlags(Qt.FramelessWindowHint)

        mq = MstQueue()

        lstNameAddrTime = [(
            QLabel(' 파일 이름'), 
            QLabel(' 도로명 주소'),
            QLabel(' 지번 주소'),
            QLabel(' '),
            QLabel('처리 위치'), 
            QLabel('촬영 시각'), 
            QLabel('최종 이름'),
            QLabel('현재 커서'))]
        for label in lstNameAddrTime[-1]:
            label.setAlignment(Qt.AlignCenter)

        # QLabel 객체 삽입
        for name in FileProp.get_names():
            fProp = FileProp(name)
            lstNameAddrTime.append((
                QLabel(f'{fProp.name}'),
                QLabel(f'{fProp.locationFmDB}'),
                QLabel(f'{fProp.locationFmAPI}'),
                QLabel('->'),
                QLabel(f'{fProp._locationDB}'),
                QLabel(f'{fProp.time.strftime("%Y-%m-%d %H:%M:%S")}'),
                QLabel(f'{fProp.final_full_name}'),
                QLabel('<<') if mq.current_preview.current_preview.name == fProp.name else QLabel('')
            ))
            
        lstNameAddrTime.sort(key=lambda x: x[1].text()) #주소 기준 정렬

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
        self.log.INFO('Addr Info Dialog closed')
        self.close()


class RecommendDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.log = Logger()
        self.log.INFO('Recommend Dialog')

        self.title = '텍스트 추천'
        self.iconPath = utils.resource_path(const.IMG_DEV)

        self.setupUI()

    def setupUI(self):
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon(self.iconPath))
        self.setStyleSheet(const.QSTYLE_SHEET_POPUP)
        self.setWindowFlags(Qt.FramelessWindowHint)

        mq = MstQueue()
        fProp = mq.current_preview.current_preview

        # from lib.file_translate import ImageOCR

        labelName = QLabel('파일 이름')
        labelName.setAlignment(Qt.AlignTop)
        dataName = QLabel(f'{fProp.name}')
        labelTxt = QLabel('추출 텍스트:')
        labelTxt.setAlignment(Qt.AlignTop)
        # dataTxt = QLabel(f'{ImageOCR(fProp.name).text}')
        dataTxt = QLabel('개발 중인 기능입니다.')

        self.pushBtnExit= QPushButton('확인')
        self.pushBtnExit.clicked.connect(self.onBtnClicked)

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(labelName, 0, 0)
        layout.addWidget(dataName, 0, 1)
        layout.addWidget(labelTxt, 1, 0)
        layout.addWidget(dataTxt, 1, 1)
        layout.addWidget(self.pushBtnExit, 4, 2)

    def onBtnClicked(self):
        self.log.INFO('Recommend Dialog closed')
        self.close()


class ReportLogDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.log = Logger()
        self.log.INFO('Report Logfile Dialog')

        self.title = '오류 보고'
        self.iconPath = utils.resource_path(const.IMG_DEV)

        self.log_detector = LogFileDetector()
        self.log_files = self.log_detector.file_list

        self.setupUI()

    def setupUI(self):
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon(self.iconPath))
        self.setStyleSheet(const.QSTYLE_SHEET_POPUP)
        self.setWindowFlags(Qt.FramelessWindowHint)

        layout = QGridLayout()
        self.setLayout(layout)

        self.buttonGroup = QButtonGroup() #버튼들 추적
        self.buttonGroup.buttonClicked[QAbstractButton].connect(self.onBtnSendLogFile)
        for btnIdx, log in enumerate(self.log_files): # 1칸 = 같은 위치 사진들 깔아놓기

            TextAndBtnBox = QGroupBox()
            TextAndBtnBoxLayout = QGridLayout()
            TextAndBtnBox.setLayout(TextAndBtnBoxLayout)

            labelReport = QLabel('보고하기')

            btnSendLogFile = QPushButton(log)
            self.buttonGroup.addButton(btnSendLogFile, btnIdx)
            btnSendLogFile.setFixedWidth(100)
            btnSendLogFile.setFixedHeight(40)
            
            TextAndBtnBoxLayout.addWidget(btnSendLogFile, btnIdx, 0)
            TextAndBtnBoxLayout.addWidget(labelReport, btnIdx, 1)
            layout.addWidget(TextAndBtnBox)

        self.pushBtnExit = QPushButton('취소')
        self.pushBtnExit.setFixedHeight(40)
        self.pushBtnExit.clicked.connect(self.onBtnExit)

        layout.addWidget(self.pushBtnExit, 11, 0)

    def onBtnExit(self):
        self.log.INFO('Report Logfile Dialog closed')
        self.close()

    def onBtnSendLogFile(self, btn):
        target_log_file = f'{self.log_detector.log_file_dir}/{btn.text()}'
        self.log.INFO(f'preparing to send {target_log_file}')

        sender = LogFileSender(target_log_file)
        if sender.report():
            InitInfoDialogue('성공', ('확인',)).exec_()
        else:
            InitInfoDialogue('로그 전송에 실패하였습니다.', ('다시시도',)).exec_()


if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        ex = Gongik()
        sys.exit(app.exec_())
    except Exception as e:
        Logger().CRITICAL(e)
        log_detector = LogFileDetector()
        sender = LogFileSender(f'{log_detector.log_file_dir}/gongik.log')
        sender.report()