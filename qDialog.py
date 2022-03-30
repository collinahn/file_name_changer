import sys
import time
from PyQt5.QtWidgets import (
    QGridLayout, 
    QLabel, 
    QProgressBar,
    QPushButton,
    QFileDialog,
    QCheckBox
)
from PyQt5.QtCore import (
    Qt,
    QTimer
)
from PyQt5.QtGui import QIcon

import lib.utils as utils
from lib.version_info import VersionTeller
import qWordBook as const
from lib.log_gongik import Logger
from lib.check_online import ConnectionCheck
from qDraggable import (
    QMainWindow,
    QDialog, 
    QWidget
)

class ProgressDialog(QDialog):
    def __init__(self, labelMsg:str='        '):
        super(ProgressDialog, self).__init__()

        self.log = Logger()
        self.log.INFO('init')

        self.title = '알림'
        self.icon_path = utils.resource_path('img/developer.ico')
        self.label = labelMsg

        self.__setupUI()

    def __setupUI(self):
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon(self.icon_path))
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.comment = QLabel(self.label)
        self.comment.setAlignment(Qt.AlignTop)

        self.pbar = QProgressBar(self)
        self.pbar.setAlignment(Qt.AlignCenter)
        self.__progress = 0
        self.__interval = 0.005

        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.comment, 0, 0)
        self.layout.addWidget(self.pbar, 1, 0)

    def mark_progress(self, percentage, labelMsg=None, speed=False):
        if labelMsg:
            self.label = labelMsg
            self.comment.setText(self.label)
        if speed:
            self.__interval = 0.01

        for i in range(self.__progress, percentage):
            self.pbar.setValue(int(i))
            self.__progress = percentage
            time.sleep(self.__interval) # 좋지 않은 시각효과 TODO: 타이머로 변경

            if i%5 == 0:
                self.comment.setText(self.label+'....'[:(i%4+1)])


class ProgressDialog4Start(ProgressDialog):
    def __init__(self, labelMsg:str=''):
        super(ProgressDialog4Start, self).__init__(labelMsg)
        
        clsCC = ConnectionCheck()
        if not clsCC.check_online():
            return

        clsVI = VersionTeller() # 온라인일 때 실행
        if not clsVI.is_latest:
            self.setup_ui() # 최신파일이 아니면 업데이트 하라고 안내 멘트

    def setup_ui(self):
        self.labelNeedUpdate = QLabel('업데이트가 있습니다.\n실행 후 정보>업데이트 확인 탭에서 새 버전을 다운받아 주세요.')
        self.layout.addWidget(self.labelNeedUpdate, 2, 0)

class ProgressTimerDialog(QDialog):
    def __init__(self, labelMsg:str='', Parent=None):
        super(ProgressTimerDialog, self).__init__(Parent)

        self.log = Logger()

        self.title = '알림'
        self.iconPath = utils.resource_path('img/developer.ico')
        self.label = labelMsg

        self._setup_UI()

        self.timer = QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self._update)
        self.timer.start()

        self.log.INFO('progress timer dialog init')

    def _setup_UI(self):
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon(self.iconPath))
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.comment = QLabel(self.label)
        self.comment.setAlignment(Qt.AlignTop)

        self.pbar = QProgressBar(self)
        self.pbar.setAlignment(Qt.AlignCenter)
        self._progress = 0
        self._percentageInput = 0

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.comment, 0, 0)
        layout.addWidget(self.pbar, 1, 0)


    def _update(self):
        if self._progress >= self._percentageInput:
            self.timer.stop()
            return
        else:
            if not self.timer.isActive():
                self.timer.start()

        self._progress = self.pbar.value()
        self._progress += 1
        self.pbar.setValue(self._progress)

    def mark_progress(self, percentage, labelMsg=None):
        if labelMsg:
            self.label = labelMsg
            self.comment.setText(self.label)

        self._percentageInput = percentage
        self.log.INFO('setting percentage =', percentage, ', msg =', labelMsg)


class InitInfoDialogue(QDialog):
    def __init__(self, msg:str, btn:tuple=None):
        super().__init__()

        self.log = Logger()
        self.log.INFO('Info Dialogue,', repr(msg))

        self.title = '알림'
        self.mainMsg = msg
        self.btn = btn
        self.iconPath = utils.resource_path('img/frog.ico')

        self.answer: bool = False

        self.setupUI()

    def setupUI(self):
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon(self.iconPath))
        self.setStyleSheet(const.QSTYLE_SHEET_POPUP)
        # self.setWindowFlags(Qt.FramelessWindowHint)
        self.setMinimumWidth(200)

        label0 = QLabel(self.mainMsg, self)
        label0.setAlignment(Qt.AlignCenter)
        label0.setMinimumHeight(30)

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(label0)

        if not self.btn:
            return

        self.pushYesBtn= QPushButton(f'{self.btn[0]}(y)', self)
        self.pushYesBtn.setMinimumHeight(30)
        self.pushYesBtn.clicked.connect(self.onBtnYesClicked)
        self.pushYesBtn.setShortcut('Y')
        layout.addWidget(self.pushYesBtn)

        if len(self.btn) > 1:
            self.pushNoBtn= QPushButton(f'{self.btn[1]}(n)', self)
            self.pushNoBtn.setMinimumHeight(30)
            self.pushNoBtn.clicked.connect(self.onBtnNoClicked)
            self.pushNoBtn.setShortcut('N')
            layout.addWidget(self.pushNoBtn)

    def onBtnYesClicked(self):  # sourcery skip: class-extract-method
        self.answer = True
        self.log.INFO('User Selected Yes')
        self.close()

    def onBtnNoClicked(self):
        self.answer = False
        self.log.INFO('User Selected No')
        self.close()


class FolderDialog(QDialog):
    #최초 실행 시 파일의 디렉토리 정보를 찾아서 이후 절차에 사용한다.
    def __init__(self, labelMsg:str=''):
        super(FolderDialog, self).__init__()

        self.log = Logger()
        self.log.INFO('dir setter init')

        self.title = '알림'
        self.iconPath = utils.resource_path('img/developer.ico')

        sep = '.'
        self.date = utils.get_today_date_formated(sep)
        year, month, day = self.date.split(sep)

        self.path = utils.extract_dir()
        self.setup_ui()

        self.proceed = False

    def setup_ui(self):
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon(self.iconPath))
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.layout = QGridLayout()
        self.setLayout(self.layout)
        
        self.labelExplain = QLabel('경로를 지정합니다. 확인을 눌러 경로를 확정합니다.')
        self.labelInfoPath = QLabel('경로:')
        self.labelInfoPath.setFixedWidth(50)
        self.labelInfoDate = QLabel('일자:')
        self.labelInfoDate.setFixedWidth(50)

        self.labelDisplayDate = QLabel(self.date)

        currentDir = utils.extract_dir() # TODO: 초기값은 현재 폴더
        self.btnDirectory = QPushButton(currentDir)
        self.btnDirectory.clicked.connect(self.onBtnPushDir)

        #TODO: 여기에 복원모드로 여는 체크박스 
        self.checkboxRestoreMode = QCheckBox('복구모드 열기')
        self.checkboxRestoreMode.stateChanged.connect(self.onStateChangeRestoreMode)

        self.btnOK = QPushButton('확인')
        self.btnOK.setMaximumWidth(50)
        self.btnOK.clicked.connect(self.onBtnClose)

        # self.layout.addWidget(QLabel(''), 0, 0)
        self.layout.addWidget(self.labelExplain, 1, 0, -1, -1, Qt.AlignTop)
        self.layout.addWidget(QLabel(''), 2, 0)
        self.layout.addWidget(self.labelInfoDate, 3, 0)
        self.layout.addWidget(self.labelDisplayDate, 3, 1)
        self.layout.addWidget(QLabel(''), 4, 0)
        self.layout.addWidget(self.labelInfoPath, 5, 0)
        self.layout.addWidget(self.btnDirectory, 5, 1)
        self.layout.addWidget(self.checkboxRestoreMode, 6, 0, -1, -1, alignment=Qt.AlignCenter)
        self.layout.addWidget(QLabel(''), 7, 0)
        self.layout.addWidget(self.btnOK, 8, 1, alignment=Qt.AlignRight)

    def onBtnPushDir(self):
        self.log.INFO('dir clicked')

        self.path = str(QFileDialog.getExistingDirectory(self, "폴더를 선택하세요")) or self.path
        self.log.INFO(f'path selected = {self.path}')

        self.btnDirectory.setText(self.path)

    def onStateChangeRestoreMode(self):
        if self.checkboxRestoreMode.isChecked():
            self.btnDirectory.setDisabled(True)
            self.log.INFO('restoreMode checkbox checked')
        else:
            self.btnDirectory.setEnabled(True)
            self.log.INFO('restoreMode checkbox unchecked')

    def onBtnClose(self):
        if not self.checkboxRestoreMode.isChecked():
            self.log.INFO('closing')
            self.close()
            return

        from qRestoreDialog import RestoreDialog
        rdlg = RestoreDialog()
        rdlg.exec_()
        
        self.log.INFO('restore dialog closing')
        self.close() # TODO: 싱글턴 메모리 공유 분리 문제 때문에 지금은 일단 실행 후 바로 닫는다
        sys.exit()

if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    # InitInfoDialogue('test', ('test', 'test')).exec_()
    # pdlg1 = ProgressDialog('sleep')
    # pdlg1.show()
    # pdlg1.mark_progress(100)
    # pdlg1.close()
    # pdlg = ProgressTimerDialog('test')
    # pdlg.show()
    # pdlg.mark_progress(80)
    # pdlg.close()

    # ProgressDialog4Start('test').exec_()
    FolderDialog().exec_()
    sys.exit(app.exec_())