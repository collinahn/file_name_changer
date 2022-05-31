# 폴더 설정 후 그룹 설정 바꾸는 다이얼로그

import sys
from PyQt5.QtGui import (
    QPixmap,
    QFont,
    QIcon,
    QMouseEvent,
)
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QGroupBox, 
    QHBoxLayout, 
    QVBoxLayout,
    QCheckBox,
    QRadioButton,
    QToolTip, 
    QApplication, 
    QGridLayout,
    QPushButton, 
    QLabel, 
    QScrollArea,
    QAbstractButton,
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
from qDialogs.info_dialog import InitInfoDialogue
from qDraggable import QDialog

class LocatorWidget(QDialog):
    def __init__(self, parent=None) -> None:
        super(LocatorWidget, self).__init__(parent)
        
        self.log = Logger()
        
        self.title = '위치군 사전조정'
        self.icon_path = utils.resource_path(const.IMG_DEV)

        self.mstQueue = MstQueue()

        self._init_ui()
        
        self.log.INFO('LocatorWidget init')

    def _init_ui(self):
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon(self.icon_path))

        QToolTip.setFont(QFont('SansSerif', 10))
        self.layout = QGridLayout()
        self.setLayout(self.layout)

if __name__ == '__main__':

    app = QApplication(sys.argv)
    screen = LocatorWidget()
    screen.show()
 
    sys.exit(app.exec_())