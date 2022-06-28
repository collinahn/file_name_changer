import sys
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QGroupBox, 
    QHBoxLayout, 
    QPushButton,
    QCheckBox,
    QToolTip, 
    QWidget, 
    QApplication,
)
from PIL import Image
from PIL.ImageQt import ImageQt
from lib.continuous_image import ContinuousImage


import lib.utils as utils
from qDialogs.info_dialog import InitInfoDialogue
import qWordBook as const
from lib.log_gongik import Logger
from lib.file_property import FileProp
from lib.picture_stamp import TimeStamp
from lib.picture_stamp import LocalStamp
from lib.picture_stamp import DetailStamp
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

        self.imageqt_pool = []

    
    def init_ui(self):
        self.setWindowTitle('Stamp Widget')

        widget_layout = QHBoxLayout(self)
        self.setContentsMargins(0,0,0,0)
        self.setLayout(widget_layout)

        self.checkbox_group = QGroupBox('사진에 스탬프 추가(개발중)')
        widget_layout.addWidget(self.checkbox_group)

        self.group_layout = QHBoxLayout()
        self.checkbox_group.setLayout(self.group_layout)

        self.checkbox_timestamp = QCheckBox('촬영시각')
        self.checkbox_locationstamp = QCheckBox('촬영장소')
        self.checkbox_detailstamp = QCheckBox('상세정보')
        self.btn_store = QPushButton('저장하기')
        self.group_layout.addWidget(self.checkbox_timestamp)
        self.group_layout.addWidget(self.checkbox_locationstamp)
        self.group_layout.addWidget(self.checkbox_detailstamp)
        self.group_layout.addWidget(self.btn_store)
        self.checkbox_timestamp.clicked.connect(self.on_checked)
        self.checkbox_locationstamp.clicked.connect(self.on_checked)
        self.checkbox_detailstamp.clicked.connect(self.on_checked)
        self.btn_store.clicked.connect(self.on_store_stamped_pic)
        self.btn_store.setMinimumHeight(30)

    def on_checked(self):
        self.imageqt_pool = []
        status = self.checkbox_status()
        current_loc: PropsQueue = self.mst_queue.current_preview
        current_loc.chkbox_status = status # 상태 저장
        self.log.INFO(f'user checked ! checkbox {status = }')

        time_flag, loc_flag, detail_flag = status
        for prop in current_loc.queue:
            prop: FileProp
            ContinuousImage.refresh(prop.abs_path)
            img_file = None
            
            if time_flag:
                ts = TimeStamp(prop)
                ts.stamp()
                img_file = ts.img
            if loc_flag:
                ls = LocalStamp(prop)
                ls.stamp()
                img_file = ls.img
            if detail_flag:
                df = DetailStamp(prop)
                df.stamp()
                img_file = df.img

            if not img_file: # 아무것도 체크하지 않은 경우
                prop.pixmap = QPixmap(prop.abs_path).scaled(*const.PIXMAP_SCALE)
                continue

            iqt = ImageQt(img_file)
            self.imageqt_pool.append(iqt)
            prop.pixmap = QPixmap.fromImage(iqt).scaled(*const.PIXMAP_SCALE)

    def checkbox_status(self):
        return ( 
            self.checkbox_timestamp.isChecked(), 
            self.checkbox_locationstamp.isChecked(), 
            self.checkbox_detailstamp.isChecked()
        )

    def set_status(self):
        current_loc: PropsQueue = self.mst_queue.current_preview
        self.checkbox_timestamp.setChecked(current_loc.chkbox_status[0])
        self.checkbox_locationstamp.setChecked(current_loc.chkbox_status[1])
        self.checkbox_detailstamp.setChecked(current_loc.chkbox_status[2])

    def on_store_stamped_pic(self):
        self.log.INFO('storing stamped')
        current_loc: PropsQueue = self.mst_queue.current_preview

        ask_save = InitInfoDialogue(
            f'현재 보이는 미리보기로 사진을 교체하여 저장합니다.\n현재 위치군에 있는 사진 {current_loc.size}장이 전부 변경됩니다.\n이 작업은 되돌릴 수 없습니다.', 
            ('예', '아니오')
        )
        ask_save.exec_()

        if not ask_save.answer or self.checkbox_status() == (False, False, False):
            self.log.INFO('user chose not to save')
            return

        for prop in current_loc.queue:
            prop: FileProp
            original_size = Image.open(prop.abs_path).size

            try:
                prop.pixmap.scaled(*original_size).save(prop.abs_path, 'jpg', 100)
                self.log.INFO(f'{prop.name} saved with it\'s original size {original_size}, {self.checkbox_status() = }')
            except Exception as e:
                self.log.CRITICAL(e)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    wd = WorkingDir(utils.extract_dir(),'.')
    screen = StampWidget()
    screen.resize(540, 100)
    screen.show()
 
    sys.exit(app.exec_())