import sys
from PyQt5.QtGui import (
    QPixmap,
    QFont,
    QIcon,
    QMouseEvent,
)
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QGroupBox, 
    QHBoxLayout, 
    QVBoxLayout,
    QCheckBox,
    QRadioButton,
    QToolTip, 
    QApplication, 
    QGridLayout,
    QPushButton, 
    QLabel, 
    QScrollArea,
    QButtonGroup,
    QAbstractButton,
    QDialog,
    QWidget, 
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
        self.dctPreviewInstance: dict[str, QLabel] = {} # 레이블 클릭 여부 추적

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
            # picPreview.mouseReleaseEvent = self.onClickReleasePic
            self.dctPreviewInstance[prop.name] = picPreview

            picLoc = QLabel(prop.locationDB)
            picSelect = QCheckBox()
            self.dctCheckBoxInstance[prop.name] = picSelect
            picSelect.stateChanged.connect(self.onCheckPicSelect)

            singleInstanceLayout.addWidget(picPreview, 0, 0, 1, -1)
            singleInstanceLayout.addWidget(picSelect, 1, 0, 1, 1)
            singleInstanceLayout.addWidget(picLoc, 1, 1, 1, 1)

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


        #-------------도착지 선택 창-------------
        # Container Widget
        widget4ChooseDest = QWidget()
        widget4ChooseDestLayout = QVBoxLayout()
        widget4ChooseDestLayout.setContentsMargins(0, 0, 0, 0)
        widget4ChooseDest.setLayout(widget4ChooseDestLayout)

        self.buttonGroup = QButtonGroup() #버튼들 추적
        self.buttonGroup.buttonClicked[QAbstractButton].connect(self.onBtnModifyClassification)
        for btnIdx, qProps in enumerate(self.mstQueue.queue): # 1칸 = 같은 위치 사진들 깔아놓기
            qProps: PropsQueue

            if qProps == self.mstQueue.current_preview:
                continue # 현재 선택중인 큐는 생성안함

            singleLocBox = QGroupBox()
            singleLocBoxLayout = QGridLayout()
            singleLocBox.setLayout(singleLocBoxLayout)

            btnModifyClassification = QPushButton(f'{qProps.name}')
            self.buttonGroup.addButton(btnModifyClassification, btnIdx)
            btnModifyClassification.setMaximumWidth(150)

            singleLocBoxLayout.addWidget(btnModifyClassification, 0, 0, 1, 1)

            for widgetIdx, fProp in enumerate(qProps.queue, start=1):
                fProp: FileProp
                
                picPreview4Candidate = QLabel(fProp.name)
                picPreview4Candidate.resize(200, 150)
                picPreview4Candidate.setPixmap(QPixmap(fProp.name).scaled(200, 150))

                picLoc = QLabel(fProp.locationDB)
                
                singleLocBoxLayout.addWidget(picPreview4Candidate, 0, widgetIdx, 1, 1)
                singleLocBoxLayout.addWidget(picLoc, 1, widgetIdx, 1, 15)

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
        
    # def onClickReleasePic(self, event: QMouseEvent):
    #     self.log.DEBUG(event.pos())
    #     for fName, preview in self.dctPreviewInstance.items():
    #         if self.childAt(event.pos()) == preview:
    #             self.log.INFO('clicked', fName)
    #             self.dctCheckBoxInstance[fName].toggle()

    def onCheckPicSelect(self):
        lstCheckedCheckBox = [ 
            name for name, checkbox in self.dctCheckBoxInstance.items() 
            if checkbox.isChecked() 
        ]
        self.log.DEBUG(lstCheckedCheckBox, 'checked')

    def onBtnModifyClassification(self, btn): 
        removeRet = 0
        addRet = 0
        location = btn.text()
        self.log.DEBUG(location, 'pressed')

        fileCnt = 0

        for fName, checkbox in self.dctCheckBoxInstance.items():
            fName:str #파일이름

            if checkbox.isChecked():
                removeRet += self.mstQueue.current_preview.remove(FileProp(fName))
                addRet += self.mstQueue.add(location, fName)
                fileCnt += 1

        if fileCnt == 0:
            InitInfoDialogue('이동할 사진을 선택해주세요.', ('확인',)).exec_()
            return

        if removeRet + addRet == 0:
            InitInfoDialogue(f'{fileCnt}개의 사진 이동 완료하였습니다.', ('확인', )).exec_()
        else:
            InitInfoDialogue('완료하지 못했습니다. 다시 시도해주세요.', ('확인', )).exec_()
            
    
        if __name__ != '__main__': self.close()
        else: self.log.DEBUG(self.mstQueue.current_preview.queue)


    def onBtnAddNew(self):
        isExecutable = False

        tplNamesChecked = tuple(
            fName 
            for fName, checkBox in self.dctCheckBoxInstance.items()
            if checkBox.isChecked()
        ) # 체크되어있는 목록 반환(파일 이름 리스트)

        dctLocationPool = FileProp.name2AddrDBCorrected()
        setLocationPool = set(dctLocationPool.values()) # init 정보 클래스 변수는 어떨까?

        self.log.DEBUG(f'{dctLocationPool = }')
        self.log.DEBUG(f'{set(dctLocationPool.values()) = }')
        self.log.DEBUG(f'{len(set(dctLocationPool.values())) = }')

        for fName in tplNamesChecked:
            prop = FileProp(fName)
            self.log.DEBUG(f'{prop.locationDB, setLocationPool}')
            if prop.locationDB not in setLocationPool: # 점유 이름과 같으면 생성하지 않음
                isExecutable = True

                self.mstQueue.new(prop.locationDB, tplNamesChecked)
                self.mstQueue.current_preview.remove_many(tplNamesChecked)
                break
        
        if isExecutable:
            InitInfoDialogue(f'{len(tplNamesChecked)}개의 파일을 맨 뒤로 이동하였습니다.', ('확인', )).exec_()
            self.close()
        else:
            InitInfoDialogue('선택한 사진의 위치가 기존 사진의 위치와 정확히 일치하는 사진은 신규로 카테고리를 생성할 수 없습니다.', ('확인', )).exec_()

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