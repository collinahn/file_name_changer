from PyQt5.QtGui import QIcon
from PyQt5.QtCore import (
    Qt,
)
from PyQt5.QtWidgets import (
    QApplication, 
    QGridLayout, 
    QLabel, 
    QPushButton, 
)

import lib.utils as utils
import qWordBook as const
from lib.log_gongik import Logger
from qDraggable import ( #custom qobjects
    QDialog, 
    QMainWindow, 
    QWidget,
)
from qWordBook import VERSION_INFO



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

