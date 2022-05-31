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
from lib.queue_order import MstQueue
from lib.log_gongik import Logger
from qDraggable import ( #custom qobjects
    QDialog, 
    QMainWindow, 
    QWidget,
)

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
