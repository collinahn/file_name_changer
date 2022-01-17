import time
from PyQt5.QtWidgets import (
    QDialog, 
    QGridLayout, 
    QLabel, 
    QProgressBar,
)
from PyQt5.QtCore import (
    Qt,
)
from PyQt5.QtGui import QIcon

import lib.utils as utils
from lib.log_gongik import Logger


class ProgressDialog(QDialog):
    def __init__(self, labelMsg:str='        '):
        super().__init__()

        self.log = Logger()
        self.log.INFO('init')

        self.title = '알림'
        self.icon_path = utils.resource_path('img/developer.ico')
        self.label = labelMsg

        self.setupUI()

    def setupUI(self):
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon(self.icon_path))

        self.comment = QLabel(self.label)
        self.comment.setAlignment(Qt.AlignTop)

        self.pbar = QProgressBar(self)
        self.pbar.setAlignment(Qt.AlignCenter)
        self.__progress = 0

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.comment, 0, 0)
        layout.addWidget(self.pbar, 1, 0)


    def mark_progress(self, percentage, labelMsg=None):
        if labelMsg:
            self.label = labelMsg
            self.comment.setText(self.label)

        for i in range(self.__progress, percentage):
            self.pbar.setValue(int(i))
            self.__progress = percentage
            time.sleep(0.01) # 좋지 않은 시각효과 TODO: 타이머로 변경

            if i%5 == 0:
                self.comment.setText(self.label+'....'[:(i%4+1)])
