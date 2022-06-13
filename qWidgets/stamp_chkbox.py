import sys
from PyQt5.QtWidgets import (
    QGroupBox, 
    QHBoxLayout, 
    QCheckBox,
    QToolTip, 
    QWidget, 
    QApplication, 
)
from lib.base_folder import WorkingDir


import lib.utils as utils
import qWordBook as const
from lib.log_gongik import Logger
from lib.file_property import FileProp
from lib.picture_stamp import TimeStamp
from lib.picture_stamp import LocalStamp
from lib.picture_stamp import CommentStamp
from lib.queue_order import MstQueue
from lib.queue_order import PropsQueue

class StampWidget(QWidget):
    '''
    사진에 스탬프 추가 여부를 결정하는 위젯
    '''
    def __init__(self, parent=None, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)

        self.log = Logger()

        self.init_ui()

    
    def init_ui(self):
        self.setWindowTitle('Stamp Widget')

        widgetLayout = QHBoxLayout(self)
        self.setContentsMargins(0,0,0,0)
        self.setLayout(widgetLayout)

        self.checkboxGroupStamp = QGroupBox('사진에 스탬프 추가(개발중)')
        widgetLayout.addWidget(self.checkboxGroupStamp)

        self.checkboxStampLayout = QHBoxLayout()
        self.checkboxGroupStamp.setLayout(self.checkboxStampLayout)

        self.checkboxTimeStamp = QCheckBox('타임스탬프')
        self.checkboxLocationStamp = QCheckBox('장소스탬프')
        self.checkboxDetailStamp = QCheckBox('상세정보스탬프')
        self.checkboxTimeStamp.setCheckable(False)
        self.checkboxLocationStamp.setCheckable(False)
        self.checkboxDetailStamp.setCheckable(False)
        self.checkboxStampLayout.addWidget(self.checkboxTimeStamp)
        self.checkboxStampLayout.addWidget(self.checkboxLocationStamp)
        self.checkboxStampLayout.addWidget(self.checkboxDetailStamp)
        self.checkboxTimeStamp.clicked.connect(self.on_checked_time)
        self.checkboxLocationStamp.clicked.connect(self.on_checked_loc)
        self.checkboxDetailStamp.clicked.connect(self.on_checked_detail)

    def on_checked_time(self):
        ts = TimeStamp()

    def on_checked_loc(self):
        ...

    def on_checked_detail(self):
        ...

if __name__ == '__main__':
    app = QApplication(sys.argv)
    wd = WorkingDir(utils.extract_dir(),'.')
    screen = StampWidget()
    screen.resize(540, 100)
    screen.show()
 
    sys.exit(app.exec_())