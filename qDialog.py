import sys
import time
from PyQt5.QtWidgets import (
    QDialog, 
    QGridLayout, 
    QLabel, 
    QProgressBar,
    QPushButton,
    QMainWindow,
    QWidget
)
from PyQt5.QtCore import (
    Qt,
    QTimer
)
from PyQt5.QtGui import QIcon

import lib.utils as utils
import qWordBook as const
from lib.log_gongik import Logger

class ProgressDialog(QDialog):
    def __init__(self, labelMsg:str='        '):
        super(ProgressDialog, self).__init__()

        self.log = Logger()
        self.log.INFO('init')

        self.title = '알림'
        self.icon_path = utils.resource_path('img/developer.ico')
        self.label = labelMsg

        self.setupUI()

    def setupUI(self):
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon(self.icon_path))
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.comment = QLabel(self.label)
        self.comment.setAlignment(Qt.AlignTop)

        self.pbar = QProgressBar(self)
        self.pbar.setAlignment(Qt.AlignCenter)
        self.__progress = 0
        self.__interval = 0.005

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.comment, 0, 0)
        layout.addWidget(self.pbar, 1, 0)

    def mark_progress(self, percentage, labelMsg=None, speed=False):
        if labelMsg:
            self.label = labelMsg
            self.comment.setText(self.label)
        if speed:
            self.__interval = 0.01

        for i in range(self.__progress, percentage):
            self.pbar.setValue(int(i))
            self.__progress = percentage
            time.sleep(self.__interval) # 좋지 않은 시각효과 TODO: 타이머로 변경

            if i%5 == 0:
                self.comment.setText(self.label+'....'[:(i%4+1)])

class ProgressTimerDialog(QWidget):
    def __init__(self, labelMsg:str='', Parent=None):
        super(ProgressTimerDialog, self).__init__(Parent)

        self.log = Logger()
        self.log.INFO('init')

        self.title = '알림'
        self.icon_path = utils.resource_path('img/developer.ico')
        self.label = labelMsg

        self.setupUI()

    def setupUI(self):
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon(self.icon_path))
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.comment = QLabel(self.label)
        self.comment.setAlignment(Qt.AlignTop)

        self.pbar = QProgressBar(self)
        self.pbar.setAlignment(Qt.AlignCenter)
        self.__progress = 0
        self.__percentageInput = 0

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.comment, 0, 0)
        layout.addWidget(self.pbar, 1, 0)

        self.timer = QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.__update)
        self.timer.start()

    def __update(self):
        if self.__progress >= self.__percentageInput:
            self.timer.stop()
            return
        else:
            if not self.timer.isActive():
                self.timer.start()

        self.__progress = self.pbar.value()
        self.__progress += 1
        self.pbar.setValue(self.__progress)

    def mark_progress(self, percentage, labelMsg=None):
        if labelMsg:
            self.label = labelMsg
            self.comment.setText(self.label)

        self.__percentageInput = percentage


class InitInfoDialogue(QDialog):
    def __init__(self, msg:str, btn:tuple=None):
        super().__init__()

        self.log = Logger()
        self.log.INFO('Info Dialogue', msg)

        self.title = '알림'
        self.main_msg = msg
        self.btn = btn
        self.icon_path = utils.resource_path('img/frog.ico')

        self.answer: bool = False

        self.setupUI()

    def setupUI(self):
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon(self.icon_path))
        self.setStyleSheet(const.QSTYLE_SHEET)
        # self.setWindowFlags(Qt.FramelessWindowHint)
        self.setMinimumWidth(200)

        label0 = QLabel(self.main_msg, self)
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

    def mousePressEvent(self, event) :
        if event.button() == Qt.LeftButton :
            self.offset = event.pos()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event) :
        try:
            if self.offset is not None and event.buttons() == Qt.LeftButton:
                self.move(self.pos() + event.pos() - self.offset)
            else:
                super().mouseMoveEvent(event)
        except:
            pass

    def mouseReleaseEvent(self, event) :
        self.offset = None
        super().mouseReleaseEvent(event)



if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    InitInfoDialogue('test', ('test', 'test')).exec_()
    pdlg1 = ProgressDialog('sleep')
    pdlg1.show()
    pdlg1.mark_progress(100)
    pdlg1.close()
    pdlg = ProgressTimerDialog('test')
    pdlg.show()
    pdlg.mark_progress(80)
    sys.exit(app.exec_())