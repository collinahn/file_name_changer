import sys
from PyQt5.QtWidgets import (
    QGridLayout, 
    QLabel, 
    QPushButton,
)
from PyQt5.QtCore import (
    Qt,
)
from PyQt5.QtGui import QIcon

import lib.utils as utils
import qWordBook as const
from lib.log_gongik import Logger
from qDraggable import (
    QMainWindow,
    QDialog, 
    QWidget
)

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

if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)

    InitInfoDialogue('',('','')).exec_()
    sys.exit(app.exec_())