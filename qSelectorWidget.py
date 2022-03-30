#폴더를 결정한다.

import sys
from PyQt5.QtGui import (
    QPixmap,
    QFont,
    QMouseEvent,
)
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, 
    QApplication, 
    QGridLayout,
    QPushButton, 
    QLabel, 
    QLineEdit, 
    QSizePolicy
)


import lib.utils as utils
import qWordBook as const
from lib.get_location import LocationInfo
from lib.file_property import FileProp
from lib.queue_order import (
    MstQueue, 
    PropsQueue
)
from lib.log_gongik import Logger
from lib.change_name import NameChanger
from lib.meta_data import (
    GPSInfo, 
    TimeInfo
)
from qDistributorDialog import DistributorDialog
from qDialog import InitInfoDialogue

class QPushButton(QPushButton):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

class QLabel(QLabel):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

class SelectorWidget(QWidget):
    def __init__(self, parent = None):
        super(SelectorWidget, self).__init__(parent)

        self.log = Logger()

        self.selectorWidgetLayout = QGridLayout()
        self.setLayout(self.selectorWidgetLayout)
        self.setStyleSheet(const.QSTYLE_SHEET)

        self.btnShowAddr = QPushButton('불러오기')
        self.btnShowAddr.clicked.connect(self.onBtnShowPrevAddr)
        self.selectorWidgetLayout.addWidget(self.btnShowAddr, 0, 0)

    def onBtnShowPrevAddr(self): pass