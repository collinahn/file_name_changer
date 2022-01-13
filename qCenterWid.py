import sys
from PyQt5.QtGui import (
    QPixmap,
    QFont
)
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QGroupBox, 
    QHBoxLayout, 
    QMessageBox, 
    QRadioButton,
    QToolTip, 
    QWidget, 
    QApplication, 
    QGridLayout,
    QPushButton, 
    QLabel, 
    QLineEdit, 
    QSizePolicy
)

from lib.change_name import NameChanger
from lib.meta_data import GPSInfo, TimeInfo
from lib.utils import (
    extract_dir, 
    get_today_date_formated
)

TIME_GAP = 180 #이 시간 내에 찍힌 사진들은 전부 같은 장소 취급

class QPushButton(QPushButton):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

class QLabel(QLabel):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

class GongikWidget(QWidget):
    def __init__(self, parent = None):
        super(GongikWidget, self).__init__(parent)

        self.clsNc = NameChanger()
        self.clsGI = GPSInfo()
        self.clsTI = TimeInfo()
        self.dctName2AddrStorage = self.clsNc.dctName2Change
        self.dctName2Time = self.clsTI.time # {이름:초로 나타낸 시간}
        self.lstOldName = list(self.dctName2AddrStorage.keys())
        self._correct_road_addr_with_time() # 위치 보정

        self.lstTempNamePool = [] # 파일 미리보기를 위한 임시 리스트
        self.currentPos4Preview = 0 # 파일 미리보기 인덱스
        self.dctLoc2LocNumber = {}
        lstLocations = list(self.dctName2AddrStorage.values())
        for loc in lstLocations:
            if loc not in self.dctLoc2LocNumber:
                self.dctLoc2LocNumber[loc] = 1
            else:
                locCallCnt = self.dctLoc2LocNumber[loc] + 1
                self.dctLoc2LocNumber[loc] = locCallCnt
        print(f'{self.dctName2AddrStorage = }\n{self.dctLoc2LocNumber = }')

        self.dctLocation2Details = {}
        self.setProcessedName = set()
        self.setProcessedAddr = set()
        self.dctOldName2BeforeAfter = {}
        self.carNumber = '2' # 호차 구분 (1호차: 6, 2호차: 2)

        self.currentPreview = self.lstOldName[0]
        self.tempImgPreview = self.currentPreview # 장소별/같은 장소 내의 임시 프리뷰 통합 관리/ currentPreview는 다음 장소 업데이트를 위해.. temp는 같은 장소 내에서.
        
        self.init_ui()
        
    def init_ui(self):

        QToolTip.setFont(QFont('SansSerif', 10))
        layout = QGridLayout()
        self.setLayout(layout)

        # 0번 레이아웃
        self.currentPath = QLabel(f'실행 경로: {extract_dir()}')
        layout.addWidget(self.currentPath, 0, 0, 1, 2)
        self.totalPics = QLabel(f'총 사진 개수: {len(self.dctName2AddrStorage)}')
        self.totalPics.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.totalPics, 0, 2)

        self.instruction = QLabel('상세 입력')
        self.instruction.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.instruction, 1, 0)

        self.nameInput = QLineEdit()
        self.nameInput.setPlaceholderText('상세 정보 입력')
        self.nameInput.setMaxLength(100)
        self.nameInput.setMinimumWidth(250)
        self.nameInput.setMinimumHeight(50)
        self.nameInput.returnPressed.connect(self.onBtnRegName)
        layout.addWidget(self.nameInput, 1, 1)

        # 전 후 선택 라디오버튼
        self.radioGroupBox = QGroupBox('파일 이름 개별지정')
        layout.addWidget(self.radioGroupBox, 1, 2)

        self.radioBoxLayout = QHBoxLayout()
        self.radioGroupBox.setLayout(self.radioBoxLayout)

        shortCut = ['Alt+A', 'Alt+S', 'Alt+D']
        txtRadioBtn = [f'전({shortCut[0]})', f'후({shortCut[1]})', f'지정안함({shortCut[2]})']
        self.radioBtnBefore = self._make_radio_btn_for_footer(txtRadioBtn, shortCut, 0)
        self.radioBtnAfter = self._make_radio_btn_for_footer(txtRadioBtn, shortCut, 1)
        self.radioBtnDefault = self._make_radio_btn_for_footer(txtRadioBtn, shortCut, 2)
        self.radioBtnDefault.setChecked(True)
        self.radioBoxLayout.addStretch()


        self.btnPreview = QPushButton('파일명 등록\n(Alt+N)')
        self.btnPreview.setShortcut('Alt+N')
        self.btnPreview.setToolTip('텍스트 박스에 입력된 텍스트가 파일명의 일부로 저장됩니다.')
        self.btnPreview.clicked.connect(self.onBtnRegName)
        layout.addWidget(self.btnPreview, 2, 0)

        self.fileNamePreview = QLabel() # 변환된 파일명의 미리보기
        layout.addWidget(self.fileNamePreview, 2, 1)

        self.picPreview = QLabel('사진 미리보기')
        self.picPreview.resize(540, 540)
        self.picPreview.setAlignment(Qt.AlignCenter)
        self.picPreview.setPixmap(QPixmap(self.currentPreview).scaled(540, 360))#, Qt.KeepAspectRatio))
        layout.addWidget(self.picPreview, 2, 2, 3, -1)

        self.btnNextAddr = QPushButton('다음 장소 보기\n(Alt+F)')
        self.btnNextAddr.setShortcut('Alt+F')
        self.btnNextAddr.setToolTip('같은 장소에서 찍힌 사진들은 상기 등록된 이름 형식으로 저장되고, 다른 장소에서 찍은 사진을 불러옵니다.')
        self.btnNextAddr.clicked.connect(self.onBtnShowNextAddr)
        layout.addWidget(self.btnNextAddr, 3, 0)

        # 같은 위치 preview 갯수 세기
        self.textPointer4SameLoc = self._generate_text_for_indicator()
        self.labelPointer4SameLoc = QLabel(self.textPointer4SameLoc)
        self.labelPointer4SameLoc.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.labelPointer4SameLoc, 3,1)

        # 1호차2호차 선택 라디오버튼
        self.radioGroupCar = QGroupBox('호차 선택')
        layout.addWidget(self.radioGroupCar, 4, 0, 1, 2)

        self.radioBoxCarLayout = QHBoxLayout()
        self.radioGroupCar.setLayout(self.radioBoxCarLayout)

        self.radioBtn1stCar = QRadioButton('1호차(Alt+1)', self)
        self.radioBtn1stCar.clicked.connect(self.onRadioBtnCar)
        self.radioBtn1stCar.setShortcut('Alt+1')
        self.radioBoxCarLayout.addWidget(self.radioBtn1stCar, alignment=Qt.AlignTop)
        self.radioBtn2ndCar = QRadioButton('2호차(Alt+2)', self)
        self.radioBtn2ndCar.clicked.connect(self.onRadioBtnCar)
        self.radioBtn2ndCar.setShortcut('Alt+2')
        self.radioBoxCarLayout.addWidget(self.radioBtn2ndCar, alignment=Qt.AlignTop)
        if self.clsNc.gubun == '2': self.radioBtn2ndCar.setChecked(True)
        else: self.radioBtn1stCar.setChecked(True)
        self.radioBoxCarLayout.addStretch()

        self.btn2Change = QPushButton('완료 및 이름 바꾸기\n(Ctrl+Shift+E)')
        self.btn2Change.setShortcut('Ctrl+Shift+E')
        self.btn2Change.setMinimumHeight(70)
        self.btn2Change.setToolTip('현재 폴더에서의 모든 작업을 종료하고 설정한 대로 이름을 변경합니다.')
        self.btn2Change.clicked.connect(self.onBtnChangeLocation)
        layout.addWidget(self.btn2Change, 5, 0, -1, 2)

        self.btnNextPicSameAddr = QPushButton('같은 장소 다른 사진 보기\n(Alt+W)')
        self.btnNextPicSameAddr.setShortcut('Alt+W')
        self.btnNextPicSameAddr.setToolTip('같은 장소에서 찍힌 사진 중 다른 사진으로 미리보기를 교체합니다.')
        self.btnNextPicSameAddr.clicked.connect(self.onBtnNextPreview)
        layout.addWidget(self.btnNextPicSameAddr, 5, 2)

    # 이름 뒤 구분 명칭을 결정하는 라디오 버튼을 만든다
    def _make_radio_btn_for_footer(self, tplRadioBtn, tplShortCut, seq):
        result = QRadioButton(tplRadioBtn[seq], self)
        result.clicked.connect(self.onRadioBtnBeforeAfter)
        result.setShortcut(tplShortCut[seq])
        self.radioBoxLayout.addWidget(result, alignment=Qt.AlignTop)
        return result

    # 초기화 시 시간을 기준으로 주소를 교정한다.
    def _correct_road_addr_with_time(self):
        lstTimePicTakenSorted = sorted(list(self.dctName2Time.values()))
        dctTimeLaps: dict[int,str] = {} # 기준이 되는 시간과 주소를 기록한다
        timeStandard = 0 # for루프를 돌 때 기준이 되는 시간점
        todaysDate = get_today_date_formated(':')

        # 시간 기준으로 첫 사진이 찍히고 상당 기간 내에 사진이 찍히지 않을 경우 
        # 첫 사진의 주소로 상당 기간 내에 찍힌 그 이후 사진들의 주소를 대체한다 
        for timePic in lstTimePicTakenSorted:
            if timePic - timeStandard > TIME_GAP:
                timeStandard = timePic # 다시 반복문을 돌 때 계산을 위하여
                for fName4Init, time4Init in self.dctName2Time.items():
                    if time4Init == timeStandard:
                        dctTimeLaps[timeStandard] = self.dctName2AddrStorage[fName4Init] # 기준들 저장

        for fName, time in self.dctName2Time.items():
            if todaysDate not in self.clsTI.dctTimeFilesMade[fName]:
                continue # 오늘 날짜가 아니면 시간 제한을 적용하지 않는다
            for tMin, roadAddr in dctTimeLaps.items():
                if time - tMin < TIME_GAP and time - tMin >= 0: # 기준점을 기준으로 기준 시간 내에 드는경우
                    self.dctName2AddrStorage[fName] = roadAddr

        # 여기서 바꾸면 잘 동작하나 테스트코드
        # 아무거나 = self.dctName2AddrStorage[list(self.dctName2AddrStorage.keys())[0]]
        # for 파일이름 in list(self.dctName2AddrStorage.keys()):
        #     self.dctName2AddrStorage[파일이름] = 아무거나


    def _generate_text_for_indicator(self, pos='1'):
        return f'현재 위치: {self.dctName2AddrStorage[self.currentPreview]} \
               \n해당 위치 개수: {pos} / {self.dctLoc2LocNumber[self.dctName2AddrStorage[self.currentPreview]]}'

    @staticmethod
    def find_same_loc(dctData, loc) -> list[str]:
        return [key for key, value in dctData.items() if value == loc]

    #파일 이름을 업데이트한다(다음 파일로 커서 이동)
    def _point_file_name(self) -> str or None:
        res = None
        try:
            lstNameToBeRemoved = self.find_same_loc(self.dctName2AddrStorage, self.dctName2AddrStorage[self.currentPreview])
            for target in lstNameToBeRemoved:
                self.setProcessedName.add(target)

            for target in self.lstOldName:
                if target not in self.setProcessedName:
                    res = target

        except AttributeError as ae:
            print(ae)

        print(f'point_file_name ret val: {res}')
        return res


    # 추적 흔적을 남긴다, 추후 조회하여 다시 리뷰할 것인지 판단할 때 사용.
    def store_preview_history(self, name, storeEntireLoc=True):
        self.setProcessedName.add(name)
        if storeEntireLoc:
            self.setProcessedAddr.add(self.dctName2AddrStorage[name])

    def register_unmanaged_filenames(self):
        # 현재 커서의 지정 이름 저장
        targetFileName = self.currentPreview
        self.store_preview_history(targetFileName)
        self.dctLocation2Details[self.dctName2AddrStorage[targetFileName]] = self.clsNc.get_final_name(targetFileName, self.nameInput.text())
        print(f'(register_unmanaged_filenames) filename = {targetFileName}: {self.dctLocation2Details[self.dctName2AddrStorage[targetFileName]]}')

    # 사진과 설명을 업데이트한다.
    def update_pixmap(self, srcName):
        self.picPreview.setPixmap(QPixmap(srcName).scaled(540, 360))# , Qt.KeepAspectRatio))
    
    def onBtnRegName(self):
        oldFileName = self.currentPreview
        self.store_preview_history(oldFileName)

        text = self.nameInput.text()
        newFileName = self.clsNc.get_final_name(oldFileName, text)
        print(f'등록됨 {newFileName =} ')

        self.dctLocation2Details[self.dctName2AddrStorage[oldFileName]] = newFileName # {주소: 바뀔 이름}
        
        self.fileNamePreview.setText(f'{newFileName} (으)로 등록완료')

    def onBtnShowNextAddr(self):
        self.lstTempNamePool = [] # 장소 단위 리스트 초기화
        self.currentPos4Preview = 0

        self.register_unmanaged_filenames() # 처리되지 않은 파일 이름들 처리

        nextFileName = self._point_file_name()
        if not nextFileName:
            QMessageBox.warning(self, '경고', '마지막 장소입니다.')
            return

        self.currentPreview = nextFileName
        self.tempImgPreview = nextFileName

        # 강제로 임시대기열 업데이트 후 현재 프리뷰로 나가는 파일 목록에서 삭제
        currentLoc = self.dctName2AddrStorage[self.currentPreview]
        if not self.lstTempNamePool: #이 리스트가 비어있으면 업데이트
            for oldName, roadAddr in self.dctName2AddrStorage.items():
                if currentLoc == roadAddr:
                    self.lstTempNamePool.append(oldName)
            print('temp list updated')
            self.lstTempNamePool.remove(self.currentPreview)

        self.update_pixmap(self.currentPreview)
        self.fileNamePreview.setText('')
        self.textPointer4SameLoc = self._generate_text_for_indicator()
        self.labelPointer4SameLoc.setText(self.textPointer4SameLoc)
        self.radioBtnDefault.setChecked(True) # 라디오 버튼 기본값으로 
        self.nameInput.setText('') # 입력 필드 초기화

        print(f'onChange {self.tempImgPreview = }')


    #라디오버튼의 위치를 기억했다가 다시 차례가 오면 채워준다
    def setRadioBtnAsChecked(self):
        if self.tempImgPreview not in self.dctOldName2BeforeAfter:
            self.radioBtnDefault.setChecked(True)
            return

        if self.dctOldName2BeforeAfter[self.tempImgPreview] == '전':
            self.radioBtnBefore.setChecked(True)
        elif self.dctOldName2BeforeAfter[self.tempImgPreview] == '후':
            self.radioBtnAfter.setChecked(True)


    def onBtnNextPreview(self):
        self.store_preview_history(self.currentPreview, storeEntireLoc=False)
        currentLoc = self.dctName2AddrStorage[self.currentPreview]
        if not self.lstTempNamePool: #이 리스트가 비어있으면 업데이트
            for oldName, roadAddr in self.dctName2AddrStorage.items():
                if currentLoc == roadAddr:
                    self.lstTempNamePool.append(oldName)
            print('temp list updated')

        self.tempImgPreview = self.lstTempNamePool.pop()

        self.update_pixmap(self.tempImgPreview)

        # 라디오버튼 기억
        self.setRadioBtnAsChecked()

        # 사진 개수 트래킹
        self.currentPos4Preview = (self.currentPos4Preview + 1) % self.dctLoc2LocNumber[self.dctName2AddrStorage[self.currentPreview]] # 0부터 시작
        position = self.currentPos4Preview + 1
        self.textPointer4SameLoc = self._generate_text_for_indicator(position)
        self.labelPointer4SameLoc.setText(self.textPointer4SameLoc)

        print(f'onChangePreview {self.tempImgPreview = }')

    def onBtnChangeLocation(self):
        self.register_unmanaged_filenames() # 처리되지 않고 넘어간 파일 이름 처리

        while True: # 디테일을 전부 다 지정하지 않고 넘어가는 경우
            self.currentPreview = self._point_file_name()
            if not self.currentPreview:
                break
            self.dctLocation2Details[self.dctName2AddrStorage[self.currentPreview]] = self.clsNc.get_final_name(self.currentPreview, '') # {주소: 바뀔 이름(초기화)}

        if self.clsNc.change_name_on_btn(self.dctLocation2Details, self.dctOldName2BeforeAfter, self.carNumber):
            QMessageBox.information(self, '알림', '처리가 완료되었습니다.')
        else:
            QMessageBox.warning(self, '경고', '문제가 있어 일부 파일을 처리하지 못했습니다.(수동 확인 필요)')

        QMessageBox.information(self, '알림', '프로그램을 종료합니다.\n일부 중복된 장소를 확인해주세요.')
        sys.exit()


    #선택한 라디오 버튼에 맞춰서 {현 썸네일 이름: 전.후 정보}를 업데이트한다.
    def onRadioBtnBeforeAfter(self):
        if self.radioBtnBefore.isChecked():
            print(f'{self.tempImgPreview = }, 전')
            self.dctOldName2BeforeAfter[self.tempImgPreview] = '전'
        elif self.radioBtnAfter.isChecked():
            print(f'{self.tempImgPreview = }, 후')
            self.dctOldName2BeforeAfter[self.tempImgPreview] = '후'
        elif self.radioBtnDefault.isChecked():
            print(f'{self.tempImgPreview = }, 전/후정보 제거')
            self.dctOldName2BeforeAfter[self.tempImgPreview] = ''

        print(f'onRadio {self.dctOldName2BeforeAfter = }')
        

    def onRadioBtnCar(self):
        if self.radioBtn1stCar.isChecked():
            print('1호차 선택됨')
            self.carNumber = '6'
        elif self.radioBtn2ndCar.isChecked():
            print('2호차 선택됨')
            self.carNumber = '2'

if __name__ == '__main__':
    app = QApplication(sys.argv)
    screen = GongikWidget()
    screen.resize(540, 100)
    screen.show()
 
    sys.exit(app.exec_())