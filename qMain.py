# pip3 install pyproj pillow requests haversine pyinstaller pyqt5 pure-python-adb paramiko pytesseract

import sys
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import (
    Qt,
)
from PyQt5.QtWidgets import (
    QApplication, 
    QAction,
    qApp
)

import lib.utils as utils
import qWordBook as const
from lib.file_copy import BridgePhone
from lib.send_file import LogFileSender
from lib.log_gongik import Logger
from lib.base_folder import WorkingDir
from qWidgets.main_widget import GongikWidget
from qDialogs.version import VersionDialog
from qDialogs.restore import RestoreDialog
from qDialogs.info_dialog import InitInfoDialogue
from qDialogs.folder_dialog import FolderDialog
from qDialogs.developer import DeveloperInfoDialog
from qDialogs.recommend import RecommendDialog
from qDialogs.report import ReportLogDialog
from qDialogs.summary import AddrInfoDialog
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
from qWordBook import VERSION_INFO


'''
exe 빌드하기
pyinstaller -F --clean qMain.spec
pyinstaller -w -F --clean --add-data "db/addr.db;./db" --add-data "img/frog.ico;./img" --add-data "img/developer.ico;./img" --add-data "img/exit.ico;./img" --add-data "img/final.ico;./img" --add-data "platform-tools;./platform-tools" --add-data "tesseract-ocr;./tesseract-ocr" --icon=img/final.ico qMain.py
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

        self.file_detector = FileDetector(self.targetFolder.rel_path) # '.'는 초기 파일 체크용
        self.files = self.file_detector.file_list

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
            InitInfoDialogue(const.MSG_INFO.get('EXIT_PLAIN', 'EXIT'), ('네', )).exec_()
            return False

        adb_connect = BridgePhone()
        self._handle_ADB_failure(adb_connect)

        self.progress_dlg.update(20, f'{len(adb_connect.files)}개의 파일 복사 중')

        if not adb_connect.transfer_files():
            InitInfoDialogue(const.MSG_INFO.get('TRANSFER_FAILURE', 'TRANSFER_FAILURE'), ('다시 시도', )).exec_()
            self.progress_dlg.update(10, '다시 시도 중')
            if adb_connect.transfer_files(): # 현재는 객체 재활용, 안먹히면 다시 생성
                InitInfoDialogue(const.MSG_INFO.get('TRANSFER_RETRY_SUCCESS', 'TRANSFER_RETRY_SUCCESS'), ('확인',)).exec_()
                return True
            InitInfoDialogue(const.MSG_INFO.get('TRANSFER_RETRY_FAILURE', 'TRANSFER_RETRY_FAILURE'), ('확인', )).exec_()
            return False
        
        self.progress_dlg.update(10, '파일 검사 중')
        return True

    def _handle_ADB_failure(self, adb_conn: BridgePhone):
        if not adb_conn.connected:
            self._pop_warn_msg('CONNECTION_ERROR')

        if not adb_conn.executable:
            self._pop_warn_msg('MULTI_CONNECTION_ERROR')

        if not adb_conn.files:
            self._pop_warn_msg('EMPTY_FILE_ERROR')


    def _pop_warn_msg(self, code):
        self.log.WARNING(f'{code = }')
        InitInfoDialogue(const.MSG_WARN.get(code, code), ('넹', )).exec_()
        sys.exit()

    def _init_ui(self):
        # 상단 정보 설정
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon(self.main_icon_path))
        self.setStyleSheet(const.QSTYLE_SHEET)
        self.setWindowFlags(Qt.FramelessWindowHint)

        #메뉴 바 - progMenu - Exit
        exitAction = QAction(QIcon(self.exit_icon_path), '퇴근하기', self)
        exitAction.setShortcut(const.MSG_SHORTCUT.get('EXIT'))
        exitAction.setStatusTip(const.MSG_TIP.get('EXIT', 'EXIT'))
        exitAction.triggered.connect(qApp.quit)

        # (베타) 이미지에서 텍스트 추출
        recommendAction = QAction(QIcon(self.dev_icon_path), '텍스트 추출(베타)', self)
        recommendAction.setShortcut(const.MSG_SHORTCUT.get('RECOMMEND'))
        recommendAction.setStatusTip(const.MSG_TIP.get('RECOMMEND', 'RECOMMEND'))
        recommendAction.triggered.connect(self.onModalRecommend)

        # 작업 복구 메뉴
        restoreAction = QAction(QIcon(self.dev_icon_path), '복구하기', self)
        restoreAction.setShortcut(const.MSG_SHORTCUT.get('RESTORE'))
        restoreAction.setStatusTip(const.MSG_TIP.get('RESTORE', 'RESTORE'))
        restoreAction.triggered.connect(self.onModalRestore)

        #메뉴 바 - info
        infoAction = QAction(QIcon(self.dev_icon_path), '프로그램 정보', self)
        infoAction.setShortcut(const.MSG_SHORTCUT.get('INFO'))
        infoAction.setStatusTip(const.MSG_TIP.get('INFO', 'INFO'))
        infoAction.triggered.connect(self.onModalDeveloperInfo)

        # 참고 정보 표시
        checkAction = QAction(QIcon(self.main_icon_path), '위치 목록 확인', self)
        checkAction.setShortcut(const.MSG_SHORTCUT.get('LIST'))
        checkAction.setStatusTip(const.MSG_TIP.get('LIST', 'LIST'))
        checkAction.triggered.connect(self.onModalAddrInfo)

        # 업데이트
        updateAction = QAction(QIcon(self.final_icon_path), '업데이트 확인', self)
        updateAction.setShortcut(const.MSG_SHORTCUT.get('UPDATE'))
        updateAction.setStatusTip(const.MSG_TIP.get('UPDATE', 'UPDATE'))
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
        self.move(QApplication.desktop().screen().rect().center() - self.rect().center())

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