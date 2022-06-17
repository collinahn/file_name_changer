import sys
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QGroupBox, 
    QHBoxLayout, 
    QCheckBox,
    QToolTip, 
    QWidget, 
    QApplication,
)
from PIL.ImageQt import ImageQt


import lib.utils as utils
import qWordBook as const
from lib.log_gongik import Logger
from lib.file_property import FileProp
from lib.picture_stamp import TimeStamp
from lib.picture_stamp import LocalStamp
from lib.picture_stamp import CommentStamp
from lib.base_folder import WorkingDir
from lib.queue_order import MstQueue
from lib.queue_order import PropsQueue

class StampWidget(QWidget):
    '''
    사진에 스탬프 추가 여부를 결정하는 위젯
    '''
    def __init__(self, parent=None, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)

        self.log = Logger()

        self.mst_queue = MstQueue()
        self.init_ui()

    
    def init_ui(self):
        self.setWindowTitle('Stamp Widget')

        widget_layout = QHBoxLayout(self)
        self.setContentsMargins(0,0,0,0)
        self.setLayout(widget_layout)

        self.checkbox_group = QGroupBox('사진에 스탬프 추가(개발중)')
        widget_layout.addWidget(self.checkbox_group)

        self.group_layout = QHBoxLayout()
        self.checkbox_group.setLayout(self.group_layout)

        self.checkbox_timestamp = QCheckBox('타임스탬프')
        self.checkbox_locationstamp = QCheckBox('장소스탬프')
        self.checkbox_detailstamp = QCheckBox('상세정보스탬프')
        self.group_layout.addWidget(self.checkbox_timestamp)
        self.group_layout.addWidget(self.checkbox_locationstamp)
        self.group_layout.addWidget(self.checkbox_detailstamp)
        self.checkbox_timestamp.clicked.connect(self.on_checked)
        self.checkbox_locationstamp.clicked.connect(self.on_checked)
        self.checkbox_detailstamp.clicked.connect(self.on_checked)

    def on_checked(self):
        status = self.checkbox_status()
        current_loc: PropsQueue = self.mst_queue.current_preview
        self.log.INFO(f'user checked ! checkbox {status = }')

        if status == (False, False, False):
            for prop in current_loc.queue:
                prop: FileProp
                prop.pixmap = QPixmap(prop.abs_path).scaled(*const.PIXMAP_SCALE)
        elif status == (True, False, False):
            for prop in current_loc.queue:
                prop: FileProp
                ts = TimeStamp(prop) 
                ts.stamp() # -> 이때 사진
                prop.pixmap = QPixmap.fromImage(ImageQt(ts.img)).scaled(*const.PIXMAP_SCALE)
        # elif status == (False, True, False):
        # elif status == (False, False, True):
        # elif status == (True, True, False):
        # elif status == (False, True, True):
        # elif status == (True, False, True):
        # elif status == (True, True, True):


    def checkbox_status(self):
        return ( 
            self.checkbox_timestamp.isChecked(), 
            self.checkbox_locationstamp.isChecked(), 
            self.checkbox_detailstamp.isChecked()
        )

if __name__ == '__main__':
    app = QApplication(sys.argv)
    wd = WorkingDir(utils.extract_dir(),'.')
    screen = StampWidget()
    screen.resize(540, 100)
    screen.show()
 
    sys.exit(app.exec_())