import sys
from PyQt5.QtWidgets import (
    QGridLayout, 
    QLabel, 
    QPushButton,
    QFileDialog,
    QCheckBox
)
from PyQt5.QtCore import (
    Qt,
)
from PyQt5.QtGui import QIcon

import lib.utils as utils
from lib.log_gongik import Logger
from qDraggable import (
    QMainWindow,
    QDialog, 
    QWidget
)

class FolderDialog(QDialog):
    #최초 실행 시 파일의 디렉토리 정보를 찾아서 이후 절차에 사용한다.
    def __init__(self, labelMsg:str=''):
        super(FolderDialog, self).__init__()

        self.log = Logger()
        self.log.INFO('dir setter init')

        self.title = '알림'
        self.iconPath = utils.resource_path('img/developer.ico')

        sep = '.'
        self.date = utils.get_today_date_formated(sep)
        year, month, day = self.date.split(sep)

        self.path = utils.extract_dir()
        self.setup_ui()

        self.proceed = False

    def setup_ui(self):
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon(self.iconPath))
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.layout = QGridLayout()
        self.setLayout(self.layout)
        
        self.labelExplain = QLabel('경로를 지정합니다. 확인을 눌러 경로를 확정합니다.')
        self.labelInfoPath = QLabel('경로:')
        self.labelInfoPath.setFixedWidth(50)
        self.labelInfoDate = QLabel('일자:')
        self.labelInfoDate.setFixedWidth(50)

        self.labelDisplayDate = QLabel(self.date)

        currentDir = utils.extract_dir() # TODO: 초기값은 현재 폴더
        self.btnDirectory = QPushButton(currentDir)
        self.btnDirectory.clicked.connect(self.onBtnPushDir)

        #TODO: 여기에 복원모드로 여는 체크박스 
        self.checkboxRestoreMode = QCheckBox('복구모드 열기')
        self.checkboxRestoreMode.stateChanged.connect(self.onStateChangeRestoreMode)

        self.btnOK = QPushButton('확인')
        self.btnOK.setMaximumWidth(50)
        self.btnOK.clicked.connect(self.onBtnClose)

        # self.layout.addWidget(QLabel(''), 0, 0)
        self.layout.addWidget(self.labelExplain, 1, 0, -1, -1, Qt.AlignTop)
        self.layout.addWidget(QLabel(''), 2, 0)
        self.layout.addWidget(self.labelInfoDate, 3, 0)
        self.layout.addWidget(self.labelDisplayDate, 3, 1)
        self.layout.addWidget(QLabel(''), 4, 0)
        self.layout.addWidget(self.labelInfoPath, 5, 0)
        self.layout.addWidget(self.btnDirectory, 5, 1)
        self.layout.addWidget(self.checkboxRestoreMode, 6, 0, -1, -1, alignment=Qt.AlignCenter)
        self.layout.addWidget(QLabel(''), 7, 0)
        self.layout.addWidget(self.btnOK, 8, 1, alignment=Qt.AlignRight)

    def onBtnPushDir(self):
        self.log.INFO('dir clicked')

        self.path = str(QFileDialog.getExistingDirectory(self, "폴더를 선택하세요")) or self.path
        self.log.INFO(f'path selected = {self.path}')

        self.btnDirectory.setText(self.path)

    def onStateChangeRestoreMode(self):
        if self.checkboxRestoreMode.isChecked():
            self.btnDirectory.setDisabled(True)
            self.log.INFO('restoreMode checkbox checked')
        else:
            self.btnDirectory.setEnabled(True)
            self.log.INFO('restoreMode checkbox unchecked')

    def onBtnClose(self):
        if not self.checkboxRestoreMode.isChecked():
            self.log.INFO('closing')
            self.close()
            return

        from qDialogs.restore import RestoreDialog
        rdlg = RestoreDialog()
        rdlg.exec_()
        
        self.log.INFO('restore dialog closing')
        self.close() # TODO: 싱글턴 메모리 공유 분리 문제 때문에 지금은 일단 실행 후 바로 닫는다
        sys.exit()

if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)

    FolderDialog().exec_()
    sys.exit(app.exec_())