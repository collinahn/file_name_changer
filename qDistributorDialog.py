import sys
from PyQt5.QtGui import (
    QPixmap,
    QFont,
    QIcon,
)
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QGroupBox, 
    QHBoxLayout, 
    QVBoxLayout,
    QCheckBox,
    QRadioButton,
    QToolTip, 
    QWidget, 
    QApplication, 
    QGridLayout,
    QPushButton, 
    QLabel, 
    QDialog,
    QScrollArea,
    QButtonGroup,
    QAbstractButton
)

import lib.utils as utils
import qWordBook as const
from lib.get_location import LocationInfo
from lib.file_property import FileProp
from lib.queue_order import MstQueue, PropsQueue
from lib.log_gongik import Logger
from qDialog import InitInfoDialogue

class DistributorDialog(QDialog):
    def __init__(self, parent = None):
        super(DistributorDialog, self).__init__(parent)

        self.log = Logger()

        self.title = '위치군 조정'
        self.icon_path = utils.resource_path(const.IMG_DEV)
    
        self.mstQueue = MstQueue()
        self.dctCheckBoxInstance: dict[str, QCheckBox] = {} # 체크된 객체 추적

        self.init_ui()

        self.log.INFO('init complete')
        
    def init_ui(self):
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon(self.icon_path))

        QToolTip.setFont(QFont('SansSerif', 10))
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        # 0번 레이아웃
        self.currentPath = QLabel(f'"{self.mstQueue.current_preview.name}"으로 분류된 사진에서 다른 위치로 병합할 사진을 선택하세요.')
        self.layout.addWidget(self.currentPath, 0, 0)


        #-------------현재 파일 선택 창-------------
        # Container Widget
        widget4ChoosePic = QWidget()
        widget4ChoosePicLayout = QHBoxLayout()
        widget4ChoosePicLayout.setContentsMargins(0, 5, 0, 0)
        widget4ChoosePic.setLayout(widget4ChoosePicLayout)
        for prop in self.mstQueue.current_preview.queue:
            prop: FileProp
            
            singleInstanceBox = QGroupBox(f'{prop.name}')
            singleInstanceLayout = QGridLayout()
            singleInstanceBox.setLayout(singleInstanceLayout)
            
            picPreview = QLabel(prop.name)
            picPreview.resize(200, 150)
            picPreview.setPixmap(QPixmap(prop.name).scaled(200, 150))

            picLoc = QLabel(prop.locationAPI)
            picSelect = QCheckBox()
            self.dctCheckBoxInstance[prop.name] = picSelect
            picSelect.stateChanged.connect(self.onCheckPicSelect)
            
            singleInstanceLayout.addWidget(picPreview, 0, 0, 1, -1)
            singleInstanceLayout.addWidget(picSelect, 1, 0)
            singleInstanceLayout.addWidget(picLoc, 1, 1)

            widget4ChoosePicLayout.addWidget(singleInstanceBox)

        # Scroll Area Properties
        scrollAreaChoosePic = QScrollArea()
        # scroll.setFrameShape(frame)
        scrollAreaChoosePic.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scrollAreaChoosePic.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scrollAreaChoosePic.setWidgetResizable(True)
        scrollAreaChoosePic.setWidget(widget4ChoosePic)
        scrollAreaChoosePic.setMinimumHeight(250)
        scrollAreaChoosePic.setMinimumWidth(800)

        self.layout.addWidget(scrollAreaChoosePic, 1, 0, 1, -1)


        #-------------후보 선택 창-------------
        # Container Widget
        widget4ChooseDest = QWidget()
        widget4ChooseDestLayout = QVBoxLayout()
        widget4ChooseDestLayout.setContentsMargins(0, 0, 0, 0)
        widget4ChooseDest.setLayout(widget4ChooseDestLayout)

        self.buttonGroup = QButtonGroup() #버튼들 추적
        self.buttonGroup.buttonClicked[QAbstractButton].connect(self.onBtnModifyClassification)
        for btnIdx, qProps in enumerate(self.mstQueue.queue): # 1칸 = 같은 위치 사진들 깔아놓기
            qProps: PropsQueue

            singleLocBox = QGroupBox()
            singleLocBoxLayout = QGridLayout()
            singleLocBox.setLayout(singleLocBoxLayout)

            btnModifyClassification = QPushButton(f'{qProps.name}')
            # btnModifyClassification.clicked.connect(self.onBtnModifyClassification)
            self.buttonGroup.addButton(btnModifyClassification, btnIdx)
            btnModifyClassification.setMaximumWidth(150)
            
            singleLocBoxLayout.addWidget(btnModifyClassification, 0, 0, 1, 1)

            for widgetIdx, fProp in enumerate(qProps.queue, start=1):
                fProp: FileProp

                picPreview = QLabel(fProp.name)
                picPreview.resize(200, 150)
                picPreview.setPixmap(QPixmap(fProp.name).scaled(200, 150))

                picLoc = QLabel(fProp.locationDB)
                
                singleLocBoxLayout.addWidget(picPreview, 0, widgetIdx)
                singleLocBoxLayout.addWidget(picLoc, 1, widgetIdx)

            widget4ChooseDestLayout.addWidget(singleLocBox)

        # Scroll Area Properties
        scrollAreaChooseDest = QScrollArea()
        # scroll.setFrameShape(frame)
        scrollAreaChooseDest.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scrollAreaChooseDest.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scrollAreaChooseDest.setWidgetResizable(True)
        scrollAreaChooseDest.setWidget(widget4ChooseDest)
        scrollAreaChooseDest.setMinimumHeight(400)
        
        self.layout.addWidget(scrollAreaChooseDest, 2, 0, 1, -1)

        btnAddNew = QPushButton(f'따로 생성')
        btnAddNew.clicked.connect(self.onBtnAddNew)
        self.layout.addWidget(btnAddNew, 3, 2)

        btnCancel = QPushButton(f'취소')
        btnCancel.clicked.connect(self.onBtnCancel)
        self.layout.addWidget(btnCancel, 3, 3)
        

    def onCheckPicSelect(self):
        for name, checkbox in self.dctCheckBoxInstance.items():
            if checkbox.isChecked():
                self.log.DEBUG(name, 'checked')

    def onBtnModifyClassification(self, btn): # 1. mstQueue에서 조작 
        location = btn.text()
        self.log.DEBUG(location, 'pressed')

        for fName, checkbox in self.dctCheckBoxInstance.items():
            fName:str #파일이름

            if checkbox.isChecked():
                self.mstQueue.current_preview.remove(FileProp(fName))
                self.mstQueue.add(location, fName)

                if not self.mstQueue.current_preview.queue:
                    self.log.WARNING('Vacant mstQueue element')
                    self.mstQueue.remove(self.mstQueue.current_preview)

        self.close()


    def onBtnAddNew(self):
        self.mstQueue.new()

    def onBtnCancel(self):
        self.log.INFO('User Canceled Distribution')
        self.close()

if __name__ == '__main__':
            
    from lib.meta_data import TimeInfo
    from lib.get_location import LocationInfo
    TimeInfo()
    LocationInfo() 

    app = QApplication(sys.argv)
    screen = DistributorDialog()
    # screen.resize(540, 100)
    screen.show()
 
    sys.exit(app.exec_())