import sys
from PyQt5.QtCore import (
    Qt,
    QTimer,
)
from PyQt5.QtWidgets import (
    QGroupBox, 
    QHBoxLayout, 
    QRadioButton,
    QToolTip, 
    QWidget, 
    QApplication, 
)

import lib.utils as utils
import qWordBook as const
from lib.base_folder import WorkingDir
from lib.file_property import FileProp
from lib.log_gongik import Logger
from lib.queue_order import (
    MstQueue, 
    PropsQueue
)

class CarWidget(QWidget):
    '''
    사진에 스탬프 추가 여부를 결정하는 위젯
    '''
    def __init__(self, parent=None, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)

        self.log = Logger()

        self.mst_queue = MstQueue()
        self.current_loc: PropsQueue = self.mst_queue.current_preview
        self.init_ui()

    
    def init_ui(self):
        self.setWindowTitle('Car Widget')

        widget_layout = QHBoxLayout(self)
        self.setContentsMargins(0,0,0,0)
        self.setLayout(widget_layout)

        self.groupbox = QGroupBox('호차 선택')
        widget_layout.addWidget(self.groupbox)
        
        self.radio_btns_layout_hbox = QHBoxLayout()
        self.groupbox.setLayout(self.radio_btns_layout_hbox)

        self.radio_btn_1st = QRadioButton(f'1', self)
        self.radio_btn_2nd = QRadioButton(f'2', self)
        self.radio_btn_1st.clicked.connect(self.on_radio_btn)
        self.radio_btn_2nd.clicked.connect(self.on_radio_btn)
        self.radio_btn_1st.setShortcut(const.MSG_SHORTCUT.get('1CAR'))
        self.radio_btn_2nd.setShortcut(const.MSG_SHORTCUT.get("2CAR"))
        self.radio_btns_layout_hbox.addWidget(self.radio_btn_1st, alignment=Qt.AlignTop)
        self.radio_btns_layout_hbox.addWidget(self.radio_btn_2nd, alignment=Qt.AlignTop)
        if self.current_loc.current_preview.prefix == '6': self.radio_btn_1st.setChecked(True)
        elif self.current_loc.current_preview.prefix == '2': self.radio_btn_2nd.setChecked(True)
        self.radio_btns_layout_hbox.addStretch()

    def on_radio_btn(self):
        if self.radio_btn_1st.isChecked():
            self.log.INFO(f'selected 1호차')
            for instance in FileProp.props().values():
                instance: FileProp
                instance.prefix = '6'

        elif self.radio_btn_2nd.isChecked():
            self.log.INFO(f'selected 2호차')
            for instance in FileProp.props().values():
                instance: FileProp
                instance.prefix = '2'

if __name__ == '__main__':
    app = QApplication(sys.argv)
    wd = WorkingDir(utils.extract_dir(),'.')
    screen = CarWidget()
    screen.resize(540, 100)
    screen.show()
 
    sys.exit(app.exec_())