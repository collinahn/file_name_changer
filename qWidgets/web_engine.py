from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWebEngineCore import QWebEngineHttpRequest
from PyQt5.QtWebEngineWidgets import (
    QWebEngineView, 
    QWebEnginePage,
)
from PyQt5 import (
    QtCore, 
    QtWebChannel,
)
from PyQt5.QtCore import (
    QObject,
    pyqtSignal, 
    QUrl,
    Qt,
    QByteArray
)
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QToolTip, 
    QWidget, 
    QApplication, 
    QPushButton, 
    QLabel, 
    QLineEdit, 
)
import json

import lib.utils as utils
import qWordBook as const
from qDialogs.info_dialog import InitInfoDialogue
from lib.queue_order import MstQueue, PropsQueue
from lib.log_gongik import Logger
from lib.__PRIVATE import IP, PORT_API, DOWNLOAD_KEY


class WebEnginePage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        Logger().INFO("javaScriptConsoleMessage: ", level, message, lineNumber, sourceID)

class PassQT2JS(QObject):
    '''JS와 PYTHON 간 데이터 공유를 위한 클래스'''
    valueChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._value = ''

    @QtCore.pyqtProperty(str)
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        self._value = v
        self.valueChanged.emit(v)


class QWebEngineInstalled(QWidget):

    def __init__(self):
        super().__init__()
        self.log = Logger()

        self.initUI()

        self.newLocFmPic = PassQT2JS(self)
        self.newLocFmPic.valueChanged.connect(self.onMapClick)
        self.channel = QtWebChannel.QWebChannel()
        self.channel.registerObject("newLocFmPic", self.newLocFmPic)
        self.mapExplorer.page().setWebChannel(self.channel) #페이지와 통신

        self.init_page()

    def initUI(self):

        mapBoxLayout = QVBoxLayout(self)
        mapBoxLayout.setContentsMargins(5,5,5,5)
        self.setLayout(mapBoxLayout)

        self.labelInfoMapArea = QLabel('위치 정밀 조정')
        self.labelInfoMapArea.setAlignment(Qt.AlignCenter)
        mapBoxLayout.addWidget(self.labelInfoMapArea)

        self.mapExplorer = QWebEngineView()
        self.mapExplorerPage = QWebEnginePage(self.mapExplorer)
        self.mapExplorer.setPage(self.mapExplorerPage)
        self.mapExplorer.setFixedSize(330, 430)
        mapBoxLayout.addWidget(self.mapExplorer, alignment=Qt.AlignCenter)

        self.labelLocationCandidate = QLabel('위치를 조정하려면 지도를 클릭하세요')
        self.labelLocationCandidate.setAlignment(Qt.AlignCenter)
        mapBoxLayout.addWidget(self.labelLocationCandidate)
        
        self.btnRenewLocation = QPushButton('주소 변경하기')
        self.btnRenewLocation.setToolTip('선택한 주소로 변경합니다.')
        self.btnRenewLocation.setMinimumHeight(50)
        self.btnRenewLocation.clicked.connect(self.onBtnChangeLocation)
        mapBoxLayout.addWidget(self.btnRenewLocation)

        self.setGeometry(300, 300, 400, 600)
        self.setWindowTitle('QWebEngineView')


    def init_page(self, latitude:float=37.507441500, longtitude:float=126.721393317):
        self.log.INFO('refreshing webview')
        data = {
            'pw':DOWNLOAD_KEY,
            'lat':latitude,
            'lon':longtitude
        }
        url = QUrl(f"http://{IP}:{PORT_API}/api/v1/map-html")
        req = QWebEngineHttpRequest(url=url, method=QWebEngineHttpRequest.Post)
        req.setHeader(QByteArray(b'Content-Type'),QByteArray(b'application/json'))
        req.setPostData(bytes(json.dumps(data), 'utf-8'))

        self.mapExplorer.load(req)
        self.labelLocationCandidate.setText('위치를 조정하려면 지도를 클릭하세요')

    def onBtnChangeLocation(self):
        self.log.DEBUG(f'{self.newLocFmPic.value = }')
        if not self.newLocFmPic.value:
            InitInfoDialogue('주소가 선택되지 않았습니다.', ('다시 선택하기',)).exec_()
            return

        mstQ = MstQueue()
        currentLoc: PropsQueue = mstQ.current_preview
        currentLoc.set_common_location(self.newLocFmPic.value)
        self.log.INFO(f'location changed to {currentLoc.name} -> {self.newLocFmPic.value}')
        

    @QtCore.pyqtSlot(str)
    def onMapClick(self, value):
        self.labelLocationCandidate.setText(value)
        self.onBtnChangeLocation()
        self.log.INFO(f'user clicked {value = }')
        
        
def main():
    import sys

    app = QApplication(sys.argv)
    ex = QWebEngineInstalled()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()