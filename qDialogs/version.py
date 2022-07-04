
import sys
import asyncio
from PyQt5.QtNetwork import (
    QNetworkAccessManager, 
    QNetworkReply, 
    QNetworkRequest,
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import (
    Qt,
    QUrl,
    QByteArray,
    pyqtSlot,
)
from PyQt5.QtWidgets import (
    QApplication, 
    QGridLayout, 
    QLabel, 
    QPushButton, 
)

import lib.utils as utils
import qWordBook as const
from lib.version_info import VersionTeller
from lib.log_gongik import Logger
from qDraggable import ( #custom qobjects
    QDialog, 
    QMainWindow, 
    QWidget,
)
from qDialogs.info_dialog import InitInfoDialogue
from qWidgets.progress_display import ProgressWidgetThreaded
from qWordBook import VERSION_INFO
from lib.__PRIVATE import DOWNLOAD_KEY



class VersionDialog(QDialog):
    def __init__(self, parent=None):
        super(VersionDialog, self).__init__(parent)

        self.log = Logger()
        self.log.INFO('Version Info Dialog')

        self.clsVI = VersionTeller()
        self.latest = self.clsVI.new_version

        self.title = '업데이트 정보'
        self.iconPath = utils.resource_path(const.IMG_DEV)

        self.netManager = QNetworkAccessManager()
        self.netManager.finished.connect(self.onFinishedNetManager)

        
        self._setup_UI()

    def _setup_UI(self):
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon(self.iconPath))
        self.setStyleSheet(const.QSTYLE_SHEET_POPUP)
        self.setWindowFlags(Qt.FramelessWindowHint)

        currentVersion_a = QLabel('현재 버전:')
        currentVersion_a.setAlignment(Qt.AlignTop)
        currentVersion_b = QLabel(f'{VERSION_INFO}')

        latestVersion_a = QLabel('최신 버전:')
        if self.latest and '0.0.0' not in self.latest:
            latestVersion_b = QLabel(f'{self.latest}')
        else:
            latestVersion_b = QLabel('서버에 연결할 수 없습니다.')

        if self.latest and self.latest != VERSION_INFO:
            comment_a = QPushButton('다운로드')
            comment_a.clicked.connect(self.onBtnDownload)
            comment_b = QLabel('새로운 버전이 있습니다.')
        elif self.latest == VERSION_INFO:
            comment_a = QPushButton('다운로드')
            comment_a.setEnabled(False)
            comment_b = QLabel('최신 버전입니다.')
        else:
            comment_a = QPushButton('다운로드')
            comment_a.setEnabled(False)
            comment_b = QLabel('')
            

        self.pushBtnExit= QPushButton('확인')
        self.pushBtnExit.clicked.connect(self.onBtnClickConfirm)

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(currentVersion_a, 0, 0)
        layout.addWidget(currentVersion_b, 0, 1)
        layout.addWidget(latestVersion_a, 1, 0)
        layout.addWidget(latestVersion_b, 1, 1)
        layout.addWidget(comment_a, 2, 0)
        layout.addWidget(comment_b, 2, 1)
        layout.addWidget(self.pushBtnExit, 3, 2)


    def onBtnClickConfirm(self):
        self.log.INFO('Developer Info Dialog closed')
        self.close()

    def onBtnDownload(self):
        self.down_progress_dlg = ProgressWidgetThreaded()
        self.down_progress_dlg.show()
        self.down_progress_dlg.raise_()
        self.down_progress_dlg.update(18, '다운로드 요청 보내는 중')
        
        self.request_new_file(self.clsVI.url_download_exe)

    def request_new_file(self, url):
        request = QNetworkRequest(QUrl(url))
        request.setHeader(QNetworkRequest.ContentTypeHeader, 'application/x-www-form-urlencoded')
        request.setRawHeader(QByteArray(b'auth'), QByteArray(DOWNLOAD_KEY.encode('utf-8')))

        data = QByteArray()
        self.netManager.post(request, data)

    @pyqtSlot(QNetworkReply)
    def onFinishedNetManager(self, reply): 
        self.down_progress_dlg.update(40, '서버로부터 파일 받는 중')

        target = reply.attribute(QNetworkRequest.RedirectionTargetAttribute)
        if reply.error():
            self.log.ERROR(reply.errorString())
            self.down_progress_dlg.close()
            InitInfoDialogue('서버의 문제로 다운로드가 실패하였습니다. 다시 시도해 주세요.', ('나가기', )).exec_()
            return

        byteStr = reply.readAll()
        self.down_progress_dlg.update(39, '파일 저장 중')
        
        self.clsVI.write_latest_version(byteStr)
        self.log.INFO(len(byteStr), 'byte downloaded')
        self.log.INFO('download complete')
        self.down_progress_dlg.close()
        finishInfo = InitInfoDialogue(f'현재 폴더에 다운로드가 완료되었습니다.\n({utils.extract_dir()})', ('예', ))
        finishInfo.exec_() 





if __name__ == '__main__':
    from PyQt5.QtWebEngineWidgets import (
        QWebEngineView, 
        QWebEnginePage,
    )
    app = QApplication(sys.argv)

    VersionDialog().exec_()

    sys.exit(app.exec_())