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
from lib.file_property import FileProp
from lib.queue_order import MstQueue
from lib.log_gongik import Logger
from qDraggable import ( #custom qobjects
    QDialog, 
    QMainWindow, 
    QWidget,
)

class AddrInfoDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.log = Logger()
        self.log.INFO('Addr Info Dialog')

        self.title = '사진 상세'
        self.iconPath = utils.resource_path(const.IMG_FROG)

        self.setupUI()

    def setupUI(self):
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon(self.iconPath))
        self.setStyleSheet(const.QSTYLE_SHEET_POPUP)
        self.setWindowFlags(Qt.FramelessWindowHint)

        mq = MstQueue()

        lstNameAddrTime = [(
            QLabel(' 파일 이름'), 
            QLabel(' 도로명 주소'),
            QLabel(' 지번 주소'),
            QLabel(' '),
            QLabel('처리 위치'), 
            QLabel('촬영 시각'), 
            QLabel('최종 이름'),
            QLabel('현재 커서'))]
        for label in lstNameAddrTime[-1]:
            label.setAlignment(Qt.AlignCenter)

        # QLabel 객체 삽입
        for name in FileProp.get_names():
            fProp = FileProp(name)
            lstNameAddrTime.append((
                QLabel(f'{fProp.name}'),
                QLabel(f'{fProp.locationFmDB}'),
                QLabel(f'{fProp.locationFmAPI}'),
                QLabel('->'),
                QLabel(f'{fProp._locationDB}'),
                QLabel(f'{fProp.time.strftime("%Y-%m-%d %H:%M:%S")}'),
                QLabel(f'{fProp.final_full_name}'),
                QLabel('<<') if mq.current_preview.current_preview.name == fProp.name else QLabel('')
            ))
            
        lstNameAddrTime.sort(key=lambda x: x[1].text()) #주소 기준 정렬

        # 확인버튼
        self.pushButton1= QPushButton('확인')
        self.pushButton1.clicked.connect(self.onBtnClicked)

        layout = QGridLayout()

        for gridLoc, tplNameAddrTime in enumerate(lstNameAddrTime):
            for idx, data in enumerate(tplNameAddrTime):
                layout.addWidget(data, gridLoc, idx)

        layout.addWidget(self.pushButton1, len(lstNameAddrTime)+1, 0, -1, -1)

        self.setLayout(layout)

    def onBtnClicked(self):
        self.log.INFO('Addr Info Dialog closed')
        self.close()
