
import sys
import time
from PyQt5.QtWidgets import (
    QWidget,
    QProgressBar,
    QApplication,
    QBoxLayout,
    QLabel,
)
from PyQt5.QtCore import (
    Qt,
    QThread,
    pyqtSignal,
    QWaitCondition,
    QMutex,
    pyqtSlot,
)
from PyQt5.QtGui import QIcon

import qWordBook as const
import lib.utils as utils
from lib.log_gongik import Logger
from lib.progress_counter import ProgressSignalSingleton
from lib.version_info import VersionTeller
from lib.check_online import ConnectionCheck

class ProgressCounterThead(QThread):
    """
    단순히 0부터 100까지 카운트만 하는 쓰레드
    값이 변경되면 그 값을 change_value 시그널에 값을 emit 한다.
    """
    # 사용자 정의 시그널
    counter_value = pyqtSignal(int)
    hint_value = pyqtSignal(str)

    def __init__(self):
        QThread.__init__(self)
        self.log = Logger()
        self.cond = QWaitCondition()
        self.mutex = QMutex()
        self._pusher = ProgressSignalSingleton()
        self._status = False # 처음엔 대기
        self._cnt = 0

    def __del__(self):
        self.wait()

    def run(self):
        max_val = 1
        while True:
            self.mutex.lock()
            if not self._status:
                self.cond.wait(self.mutex)

            self.counter_value.emit(max_val)
            self.msleep(100)
            self.mutex.unlock()
                
    @property
    def status(self):
        return self._status

    def toggle_status(self):
        self._status = not self._status
        if self._status:
            self.cond.wakeAll()


class ProgressWidgetThreaded(QWidget):
    def __init__(self):
        QWidget.__init__(self, flags=Qt.Widget)
        self.log = Logger()
        self.counter_thread = ProgressCounterThead()

        self.title = '진행률 알림'
        self.icon_path = utils.resource_path(const.IMG_DEV)

        self.init_widget()
        self.counter_thread.start()
        self.counter_thread.counter_value.connect(self.update_progress)
        self.counter_thread.hint_value.connect(self.update_hint)
        self.log.INFO('counter thread start')

    def init_widget(self):
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon(self.icon_path))
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.box_layout = QBoxLayout(QBoxLayout.TopToBottom, parent=self)
        self.setLayout(self.box_layout)

        self.progress_hint = QLabel()
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setAlignment(Qt.AlignCenter)

        self.box_layout.addWidget(self.progress_hint)
        self.box_layout.addWidget(self.progress_bar)
        self.center()

    def center(self):
        self.move(QApplication.desktop().screen().rect().center() - self.rect().center()/2)

    def update_progress(self, max_val: int):
        for _ in range(max_val):
            self.progress_bar.setValue(self.progress_bar.value() + 1)
            time.sleep(0.01)

        if max_val == 0:
            self.progress_bar.setValue(100)

    def update_hint(self, hint: str):
        self.progress_hint.setText(hint)

    def update(self, max_val: int, hint: str):
        self.counter_thread.toggle_status()
        self.update_hint(hint)
        self.update_progress(max_val)
        self.counter_thread.toggle_status()


class ProgressWidgetThreaded4Start(ProgressWidgetThreaded):
    def __init__(self):
        ProgressWidgetThreaded.__init__(self)

        conn_check = ConnectionCheck()
        if not conn_check.check_online():
            return
        
        version = VersionTeller()
        if not version.is_latest:
            self.add_instruction()
        
    def add_instruction(self):
        need_update = QLabel(const.MSG_INFO.get('UPDATE_POSSIBLE'))
        self.box_layout.addWidget(need_update)

if __name__ == "__main__":
    from PyQt5.QtWebEngineWidgets import (
        QWebEngineView, 
        QWebEnginePage,
    )
    from lib.progress_counter import ProgressSignalSingleton
    app = QApplication(sys.argv)
    
    # signal = ProgressSignalSingleton()
    # signal.hint = 'first 30'
    # signal.current = 30
    bar = ProgressWidgetThreaded4Start()
    bar.show()

    bar.update(30, '2a')
    time.sleep(1)
    bar.update(1, 'b')
    time.sleep(1)
    bar.update(3, 'c')
    time.sleep(1)
    bar.update(4, 'd')
    time.sleep(1)
    bar.update(2, 'a')
    time.sleep(1)
    bar.update(1, 'f')
    time.sleep(1)



    exit(app.exec_())