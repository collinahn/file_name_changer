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
from lib.word_settings import WordSettings

class CarWidget(QWidget):
    '''
    사진에 스탬프 추가 여부를 결정하는 위젯
    '''
    def __init__(self, parent=None, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)

        self.log = Logger()

        self.mst_queue = MstQueue()
        self.current_loc: PropsQueue = self.mst_queue.current_preview
        word_setting = WordSettings()
        self.base_data = word_setting.load_data().get('prefix')
        self.first_name = self.base_data[0][0]
        self.first_value = self.base_data[0][1]
        self.sec_name = self.base_data[1][0]
        self.sec_value = self.base_data[1][1]
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

        self.radio_btn_1st = QRadioButton(self.first_name, self)
        self.radio_btn_2nd = QRadioButton(self.sec_name, self)
        self.radio_btn_1st.clicked.connect(self.on_radio_btn)
        self.radio_btn_2nd.clicked.connect(self.on_radio_btn)
        self.radio_btn_1st.setShortcut(const.MSG_SHORTCUT.get('1CAR'))
        self.radio_btn_2nd.setShortcut(const.MSG_SHORTCUT.get("2CAR"))
        self.radio_btns_layout_hbox.addWidget(self.radio_btn_1st, alignment=Qt.AlignCenter)
        self.radio_btns_layout_hbox.addWidget(self.radio_btn_2nd, alignment=Qt.AlignCenter)
        if self.current_loc.current_preview.prefix == self.first_value: self.radio_btn_1st.setChecked(True)
        elif self.current_loc.current_preview.prefix == self.sec_value: self.radio_btn_2nd.setChecked(True)
        self.radio_btns_layout_hbox.addStretch()

    def on_radio_btn(self):
        if self.radio_btn_1st.isChecked():
            self.log.INFO(f'selected {self.first_name}')
            for instance in FileProp.props().values():
                instance: FileProp
                instance.prefix = self.first_value

        elif self.radio_btn_2nd.isChecked():
            self.log.INFO(f'selected {self.sec_name}')
            for instance in FileProp.props().values():
                instance: FileProp
                instance.prefix = self.sec_value

if __name__ == '__main__':
    app = QApplication(sys.argv)
    wd = WorkingDir(utils.extract_dir(),'.')
    screen = CarWidget()
    screen.resize(540, 100)
    screen.show()
 
    sys.exit(app.exec_())