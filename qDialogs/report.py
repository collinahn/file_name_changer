from PyQt5.QtGui import QIcon
from PyQt5.QtCore import (
    Qt,
)
from PyQt5.QtWidgets import (
    QApplication, 
    QGridLayout, 
    QLabel, 
    QPushButton, 
    QAbstractButton,
    QGroupBox,
    QButtonGroup

)

import lib.utils as utils
import qWordBook as const
from lib.send_file import LogFileSender
from lib.log_gongik import Logger
from lib.file_detect import (
    LogFileDetector
)
from qDraggable import ( #custom qobjects
    QDialog, 
    QMainWindow, 
    QWidget,
)
from qDialogs.info_dialog import InitInfoDialogue
from qDialogs.folder_dialog import FolderDialog

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
        
        self.buttonGroup = QButtonGroup()
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
