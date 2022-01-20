from ctypes import alignment
import sys
from PyQt5.QtGui import (
    QPixmap,
    QFont
)
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QGroupBox, 
    QHBoxLayout, 
    QVBoxLayout,
    QCheckBox,
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

import lib.utils as utils
from lib.log_gongik import Logger
from lib.change_name import NameChanger
from lib.meta_data import GPSInfo, TimeInfo
from qDialog import InitInfoDialogue
import qWordBook as const

# TIME_GAP

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

        self.log = Logger()

        self.clsNc = NameChanger()
        self.clsGI = GPSInfo()
        self.clsTI = TimeInfo()
        self.dctName2AddrStorage = self.clsNc.dctName2Change
        self.dctName2Time = self.clsTI.time # {이름:초로 나타낸 시간}
        self.lstOldName = list(self.dctName2AddrStorage.keys())
        self._correct_addr_with_time() # 위치 보정

        if not self.dctName2AddrStorage:
            fDlg = InitInfoDialogue('해당 디렉토리에 GPS정보를 가진 파일이 없거나 이미 처리된 파일들 입니다.\n종료합니다.', btn=('확인',))
            fDlg.exec_()
            sys.exit()

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

        self.dctLocation2Details = {}
        self.setProcessedName = set()
        self.setProcessedAddr = set()
        self.dctOldName2Suffix = {}
        self.prefix = self.clsNc.gubun # 호차 구분 (1호차: 6, 2호차: 2)

        self.currentPreview = self.lstOldName[0]
        self.tempImgPreview = self.currentPreview # 장소별/같은 장소 내의 임시 프리뷰 통합 관리/ currentPreview는 다음 장소 업데이트를 위해.. temp는 같은 장소 내에서.

        self.dctName2Details2Modify = {} #{이름:개별수정사안}
        
        self.init_ui()
        self.log.INFO('init complete')
        
    def init_ui(self):

        QToolTip.setFont(QFont('SansSerif', 10))
        layout = QGridLayout()
        self.setLayout(layout)

        # 0번 레이아웃
        self.currentPath = QLabel(f'실행 경로: {utils.extract_dir()}')
        layout.addWidget(self.currentPath, 0, 0, 1, 2)
        self.totalPics = QLabel(f'총 사진 개수: {len(self.dctName2AddrStorage)}')
        self.totalPics.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.totalPics, 0, 2)

        self.instruction = QLabel('상세 입력')
        self.instruction.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.instruction, 1, 0)

        self.nameInput = QLineEdit()
        self.nameInput.setPlaceholderText('상세 정보 입력(예> "불법적치물"만 입력)')
        self.nameInput.setMaxLength(100)
        self.nameInput.setMinimumWidth(500)
        self.nameInput.setMinimumHeight(50)
        self.nameInput.textChanged.connect(self._update_file_name_preview)
        self.nameInput.returnPressed.connect(self.onBtnRegName)
        layout.addWidget(self.nameInput, 1, 1)

        # 전 후 선택 라디오버튼
        self.radioGroupBox = QGroupBox('파일 이름 개별지정')
        layout.addWidget(self.radioGroupBox, 1, 2)

        self.radioBoxLayout = QHBoxLayout()
        self.radioGroupBox.setLayout(self.radioBoxLayout)

        txtRadioBtn = [
            f'정비 전\n({const.MSG_SHORTCUT["BEFORE_FIX"]})', 
            f'정비 후\n({const.MSG_SHORTCUT["AFTER_FIX"]})',
            f'안내장\n({const.MSG_SHORTCUT["ATTACH_FLYER"]})',
            f'1차계고장\n({const.MSG_SHORTCUT["WARN_1ST"]})',
            f'2차계고장\n({const.MSG_SHORTCUT["WARN_2ST"]})',
            f'수거 전\n({const.MSG_SHORTCUT["BEFORE_FETCH"]})',
            f'수거 후\n({const.MSG_SHORTCUT["AFTER_FETCH"]})',
            f'지정안함\n({const.MSG_SHORTCUT["SET_NONE"]})'
        ]
        self.radioBtnBefore = self._make_suffix_radio_btn(txtRadioBtn, 'BEFORE_FIX', 0)
        self.radioBtnAfter = self._make_suffix_radio_btn(txtRadioBtn, 'AFTER_FIX', 1)
        self.radioBtnAttached = self._make_suffix_radio_btn(txtRadioBtn, 'ATTACH_FLYER', 2)
        self.radioBtn1stWarn = self._make_suffix_radio_btn(txtRadioBtn, 'WARN_1ST', 3)
        self.radioBtn2ndWarn = self._make_suffix_radio_btn(txtRadioBtn, 'WARN_2ST', 4)
        self.radioBtnBeforeFetch = self._make_suffix_radio_btn(txtRadioBtn, 'BEFORE_FIX', 5)
        self.radioBtnAfterFetch = self._make_suffix_radio_btn(txtRadioBtn, 'AFTER_FIX', 6)
        self.radioBtnDefault = self._make_suffix_radio_btn(txtRadioBtn, 'SET_NONE', 7)
        self.radioBtnDefault.setChecked(True)
        self.radioBoxLayout.addStretch()

        self.btnPreview = QPushButton(f'파일명 등록 및 수정\n({const.MSG_SHORTCUT["MODIFY"]})')
        self.btnPreview.setShortcut(const.MSG_SHORTCUT['MODIFY'])
        self.btnPreview.setToolTip(const.MSG_TIP['MODIFY'])
        self.btnPreview.clicked.connect(self.onBtnRegName)
        layout.addWidget(self.btnPreview, 2, 0)

        self.fileNamePreview = QLabel() # 변환된 파일명의 미리보기
        self.fileNamePreview.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.fileNamePreview, 2, 1)

        self.picPreview = QLabel('사진 미리보기')
        self.picPreview.resize(540, 540)
        self.picPreview.setAlignment(Qt.AlignCenter)
        self.picPreview.setPixmap(QPixmap(self.currentPreview).scaled(1280//2, 720//2))#, Qt.KeepAspectRatio))
        self.picPreview.setToolTip(const.MSG_TIP['PHOTO'])
        self.picPreview.mouseDoubleClickEvent = self.onClickShowImage
        layout.addWidget(self.picPreview, 2, 2, 3, -1)

        self.btnNextAddr = QPushButton(f'다음 장소 보기\n({const.MSG_SHORTCUT["FORWARD"]})')
        self.btnNextAddr.setShortcut(const.MSG_SHORTCUT['FORWARD'])
        self.btnNextAddr.setToolTip(const.MSG_TIP['FORWARD'])
        self.btnNextAddr.clicked.connect(self.onBtnShowNextAddr)
        layout.addWidget(self.btnNextAddr, 3, 0)

        # 같은 위치 preview 갯수 세기 & 주소 변경 체크박스
        self.locationGroupInfo = QGroupBox()
        layout.addWidget(self.locationGroupInfo, 3, 1)

        self.locationBoxInfoLayout = QVBoxLayout()
        self.locationGroupInfo.setLayout(self.locationBoxInfoLayout)

        self.textPointer4SameLoc = self._generate_text_for_indicator()
        self.labelPointer4SameLoc = QLabel(self.textPointer4SameLoc)
        self.locationBoxInfoLayout.addWidget(self.labelPointer4SameLoc, alignment=Qt.AlignCenter)

        self.changeGroupAddr = QGroupBox() #그룹박스 내부 그룹박스
        self.changeGroupAddr.setStyleSheet('QGroupBox { border: 0px }')
        self.locationBoxInfoLayout.addWidget(self.changeGroupAddr, alignment=Qt.AlignCenter)

        self.changeLocLayout = QHBoxLayout()
        self.changeGroupAddr.setLayout(self.changeLocLayout)

        self.checkChangeCurrentLoc = QCheckBox()
        self.changeLocLayout.addWidget(self.checkChangeCurrentLoc)
        self.checkChangeCurrentLoc.stateChanged.connect(self.onCheckModifyLoc)
        self.inputChangeCurrentLoc = QLineEdit()
        self.inputChangeCurrentLoc.setDisabled(True)
        self.inputChangeCurrentLoc.setPlaceholderText('상세 정보를 바꾸려면 체크 후 입력')
        self.inputChangeCurrentLoc.setMinimumWidth(300)
        self.inputChangeCurrentLoc.textChanged.connect(self.onTextLocationModify)
        self.inputChangeCurrentLoc.returnPressed.connect(self.onTextLocationModify)
        self.changeLocLayout.addWidget(self.inputChangeCurrentLoc)

        # 1호차2호차 선택 라디오버튼
        self.radioGroupCar = QGroupBox('호차 선택')
        layout.addWidget(self.radioGroupCar, 4, 0, 1, 2)

        self.radioBoxCarLayout = QHBoxLayout()
        self.radioGroupCar.setLayout(self.radioBoxCarLayout)

        self.radioBtn1stCar = QRadioButton(f'1호차({const.MSG_SHORTCUT["1CAR"]})', self)
        self.radioBtn1stCar.clicked.connect(self.onRadioBtnCar)
        self.radioBtn1stCar.setShortcut(const.MSG_SHORTCUT['1CAR'])
        self.radioBoxCarLayout.addWidget(self.radioBtn1stCar, alignment=Qt.AlignTop)
        self.radioBtn2ndCar = QRadioButton(f'2호차({const.MSG_SHORTCUT["2CAR"]})', self)
        self.radioBtn2ndCar.clicked.connect(self.onRadioBtnCar)
        self.radioBtn2ndCar.setShortcut(const.MSG_SHORTCUT["2CAR"])
        self.radioBoxCarLayout.addWidget(self.radioBtn2ndCar, alignment=Qt.AlignTop)
        if self.prefix == '2': self.radioBtn2ndCar.setChecked(True)
        else: self.radioBtn1stCar.setChecked(True)
        self.radioBoxCarLayout.addStretch()

        self.btn2Change = QPushButton(f'완료 및 이름 바꾸기\n({const.MSG_SHORTCUT["FINISH"]})')
        self.btn2Change.setShortcut(const.MSG_SHORTCUT['FINISH'])
        self.btn2Change.setMinimumHeight(70)
        self.btn2Change.setToolTip(const.MSG_TIP['FINISH'])
        self.btn2Change.clicked.connect(self.onBtnChangeFileName)
        layout.addWidget(self.btn2Change, 5, 0, -1, 2)

        self.btnNextPicSameAddr = QPushButton(f'같은 장소 다른 사진 보기\n({const.MSG_SHORTCUT["NEXT"]})')
        self.btnNextPicSameAddr.setShortcut(const.MSG_SHORTCUT['NEXT'])
        self.btnNextPicSameAddr.setToolTip(const.MSG_TIP['NEXT'])
        self.btnNextPicSameAddr.clicked.connect(self.onBtnNextPreview)
        layout.addWidget(self.btnNextPicSameAddr, 5, 2)

    # 이름 뒤 구분 명칭을 결정하는 라디오 버튼을 만든다
    def _make_suffix_radio_btn(self, tplRadioBtn, shortcutCode, seq):
        result = QRadioButton(tplRadioBtn[seq], self)
        result.clicked.connect(self.onRadioBtnSuffix)
        result.setShortcut(const.MSG_SHORTCUT[shortcutCode])
        self.radioBoxLayout.addWidget(result, alignment=Qt.AlignTop)
        return result

    # 초기화 시 시간을 기준으로 주소를 교정한다.
    def _correct_addr_with_time(self):
        lstTimePicTakenSorted = sorted(list(self.dctName2Time.values()))
        dctTimeLaps: dict[int,str] = {} # 기준이 되는 시간과 주소를 기록한다
        timeStandard = 0 # for루프를 돌 때 기준이 되는 시간점
        todaysDate = utils.get_today_date_formated(':')

        # 시간 기준으로 첫 사진이 찍히고 상당 기간 내에 사진이 찍히지 않을 경우 
        # 첫 사진의 주소로 상당 기간 내에 찍힌 그 이후 사진들의 주소를 대체한다 
        for timePic in lstTimePicTakenSorted:
            if timePic - timeStandard > const.TIME_GAP:
                timeStandard = timePic # 다시 반복문을 돌 때 계산을 위하여
                for fName4Init, time4Init in self.dctName2Time.items():
                    if time4Init == timeStandard:
                        dctTimeLaps[timeStandard] = self.dctName2AddrStorage[fName4Init] # 기준들 저장

        for fName, time in self.dctName2Time.items():
            if todaysDate not in self.clsTI.dctTimeFilesMade[fName]:
                self.log.WARNING('different datetime', fName, self.clsTI.dctTimeFilesMade[fName])
                continue # 오늘 날짜가 아니면 시간 제한을 적용하지 않는다
            for tMin, roadAddr in dctTimeLaps.items():
                if time - tMin < const.TIME_GAP and time - tMin >= 0: # 기준점을 기준으로 기준 시간 내에 드는경우
                    try:
                        tmpOldAddr = self.dctName2AddrStorage[fName]
                        self.dctName2AddrStorage[fName] = roadAddr
                        self.log.INFO(fName, tmpOldAddr, '->', roadAddr)
                    except KeyError as ke:
                        self.log.ERROR(ke, fName, '/** while correcting location')

        # 여기서 바꾸면 잘 동작하나 테스트코드
        # 아무거나 = self.dctName2AddrStorage[list(self.dctName2AddrStorage.keys())[0]]
        # for 파일이름 in list(self.dctName2AddrStorage.keys()):
        #     self.dctName2AddrStorage[파일이름] = 아무거나


    def _generate_text_for_indicator(self, pos='1'):
        return f'\n해당 위치 개수: {pos} / {self.dctLoc2LocNumber[self.dctName2AddrStorage[self.currentPreview]]} \
            \n현재 위치: {self.dctName2AddrStorage[self.currentPreview]}'

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
            self.log.ERROR(ae)

        self.log.INFO('Preview Pointer Set: ', res)
        return res


    # 추적 흔적을 남긴다, 추후 조회하여 다시 리뷰할 것인지 판단할 때 사용.
    def _store_preview_history(self, name, storeEntireLoc=True):
        self.setProcessedName.add(name)
        if storeEntireLoc:
            self.setProcessedAddr.add(self.dctName2AddrStorage[name])

    def _register_unmanaged_names(self):
        # 현재 커서의 지정 이름 저장
        targetFileName = self.currentPreview
        self._store_preview_history(targetFileName)
        self.dctLocation2Details[self.dctName2AddrStorage[targetFileName]] = self.nameInput.text()
        self.log.INFO('filename =', targetFileName, ':', self.dctLocation2Details[self.dctName2AddrStorage[targetFileName]])

    # 사진과 설명을 업데이트한다.
    def _update_pixmap(self, srcName):
        self.picPreview.setPixmap(QPixmap(srcName).scaled(1280//2, 720//2))# , Qt.KeepAspectRatio))
    
    @staticmethod
    def _check_registered(dctDataSet, key) -> str:
        try:
            return dctDataSet[key]
        except (KeyError, AttributeError, TypeError):
            return ''

    def onBtnRegName(self):
        oldFileName = self.currentPreview
        self._store_preview_history(oldFileName)

        inputTxtDetails = self.nameInput.text()
        inputTxtDetails = inputTxtDetails.strip()

        self.dctLocation2Details[self.dctName2AddrStorage[oldFileName]] = inputTxtDetails

        namePreview = f'{self.prefix}_{self.dctName2AddrStorage[self.tempImgPreview]} {inputTxtDetails} {self._check_registered(self.dctOldName2Suffix, oldFileName)}'
        
        self.fileNamePreview.setText(f'<미리보기>\n{namePreview}')
        self.log.INFO(oldFileName, '->', namePreview)

    def onBtnShowNextAddr(self):
        self.lstTempNamePool = [] # 장소 단위 리스트 초기화
        self.currentPos4Preview = 0

        self._register_unmanaged_names() # 처리되지 않은 파일 이름들 처리
        self.clsNc.store_models(
            self.prefix, 
            self.dctName2AddrStorage, 
            self.dctLocation2Details, 
            self.dctOldName2Suffix, 
            self.dctName2Details2Modify
        )

        nextFileName = self._point_file_name()
        if not nextFileName:
            QMessageBox.information(self, 'EOF', const.MSG_INFO['EOF'])
            return

        self.currentPreview = nextFileName #같은 위치의 대표(1번 사진)
        self.tempImgPreview = nextFileName #같은 위치 프리뷰의 기준점

        # 강제로 임시대기열 업데이트 후 현재 프리뷰로 나가는 파일 목록에서 삭제
        currentLoc = self.dctName2AddrStorage[self.currentPreview]
        if not self.lstTempNamePool: #이 리스트가 비어있으면 업데이트
            for oldName, roadAddr in self.dctName2AddrStorage.items():
                if currentLoc == roadAddr:
                    self.lstTempNamePool.append(oldName)
            self.log.INFO('preview list updated')
            self.lstTempNamePool.remove(self.currentPreview)

        self._update_pixmap(self.currentPreview)
        self.fileNamePreview.setText('')
        self.textPointer4SameLoc = self._generate_text_for_indicator()
        self.labelPointer4SameLoc.setText(self.textPointer4SameLoc)
        # self.radioBtnDefault.setChecked(True) # 라디오 버튼 기본값으로 
        self._setRadioBtnAsChecked()
        self._setModifyLocAsChecked()
        self.nameInput.setText('') # 입력 필드 초기화


        self.log.INFO('Location:', currentLoc, 'Next File:', nextFileName)


    #라디오버튼의 위치를 기억했다가 다시 차례가 오면 채워준다
    def _setRadioBtnAsChecked(self):
        if self.tempImgPreview not in self.dctOldName2Suffix:
            self.radioBtnDefault.setChecked(True)
            return

        if self.dctOldName2Suffix[self.tempImgPreview] == const.BEFORE_FIX:
            self.radioBtnBefore.setChecked(True)
        elif self.dctOldName2Suffix[self.tempImgPreview] == const.AFTER_FIX:
            self.radioBtnAfter.setChecked(True)
        elif self.dctOldName2Suffix[self.tempImgPreview] == const.ATTACH_FLYER:
            self.radioBtnAttached.setChecked(True)
        elif self.dctOldName2Suffix[self.tempImgPreview] == const.WARN_1ST:
            self.radioBtn1stWarn.setChecked(True)   
        elif self.dctOldName2Suffix[self.tempImgPreview] == const.WARN_2ND:
            self.radioBtn2ndWarn.setChecked(True)
        elif self.dctOldName2Suffix[self.tempImgPreview] == const.BEFORE_FETCH:
            self.radioBtnBeforeFetch.setChecked(True)   
        elif self.dctOldName2Suffix[self.tempImgPreview] == const.AFTER_FETCH:
            self.radioBtnAfterFetch.setChecked(True)

        self.log.DEBUG(self.dctOldName2Suffix)

    #위치 변경 여부를 기억한다
    def _setModifyLocAsChecked(self):
        if self.tempImgPreview in self.dctName2Details2Modify:
            self.checkChangeCurrentLoc.setChecked(True)
            self.inputChangeCurrentLoc.setEnabled(True)
            self.inputChangeCurrentLoc.setText(self.dctName2Details2Modify[self.tempImgPreview])
        else:
            self.checkChangeCurrentLoc.setChecked(False)
            self.inputChangeCurrentLoc.setText('')
            self.inputChangeCurrentLoc.setEnabled(False)

        self.log.DEBUG(self.dctName2Details2Modify)


    def onBtnNextPreview(self):
        self._store_preview_history(self.currentPreview, storeEntireLoc=False)
        currentLoc = self.dctName2AddrStorage[self.currentPreview]
        if not self.lstTempNamePool: #이 리스트가 비어있으면 업데이트
            for oldName, roadAddr in self.dctName2AddrStorage.items():
                if currentLoc == roadAddr:
                    self.lstTempNamePool.append(oldName)
            self.log.INFO('preview list updated')

        self.tempImgPreview = self.lstTempNamePool.pop()

        self._update_pixmap(self.tempImgPreview)

        # 라디오버튼 기억
        self._setRadioBtnAsChecked()
        # 위치 변경 기억
        self._setModifyLocAsChecked()

        # 사진 개수 트래킹
        self.currentPos4Preview = (self.currentPos4Preview + 1) % self.dctLoc2LocNumber[self.dctName2AddrStorage[self.currentPreview]] # 0부터 시작
        position = self.currentPos4Preview + 1
        self.textPointer4SameLoc = self._generate_text_for_indicator(position)
        self.labelPointer4SameLoc.setText(self.textPointer4SameLoc)
        self._update_file_name_preview()

        self.log.INFO('onBtnNextPreview', self.tempImgPreview, 'Location =', currentLoc)

    def onBtnChangeFileName(self):
        from qDialog import ProgressTimerDialog
        progDlg = ProgressTimerDialog()
        progDlg.show()
        progDlg.mark_progress(10, '준비 중')
        self._register_unmanaged_names() # 처리되지 않고 넘어간 파일 이름 처리
        progDlg.mark_progress(30, '미완료 값 처리 중')
        while True: # 디테일을 전부 다 지정하지 않고 넘어가는 경우
            self.currentPreview = self._point_file_name()
            if not self.currentPreview:
                break
            self.dctLocation2Details[self.dctName2AddrStorage[self.currentPreview]] = '' #없는 애 취급

        progDlg.mark_progress(80, '이름 변경 중')
        
        retChangeName = self.clsNc.change_name_on_btn(self.prefix, self.dctLocation2Details, self.dctOldName2Suffix, self.dctName2Details2Modify)

        if retChangeName == 0:
            self.log.INFO('mission complete')
            QMessageBox.information(self, 'COMPLETE', const.MSG_INFO['COMPLETE'])
        elif retChangeName == 1:
            QMessageBox.warning(self, 'FILE_NAME_ERROR', const.MSG_WARN['FILE_NAME_ERROR'])
        else:
            self.log.ERROR('mission fail')
            QMessageBox.warning(self, 'OS_ERROR', const.MSG_WARN['OS_ERROR'])

        progDlg.mark_progress(100, '마무리 중')

        QMessageBox.information(self, 'EXIT_END', const.MSG_INFO['EXIT_END'])
        self.log.INFO('==================================')
        self.log.INFO('program exit')
        self.log.INFO('==================================')
        sys.exit()

    def _get_new_name(self, imgName):
        return f'{self.prefix}_{self.dctName2AddrStorage[imgName]} {self.nameInput.text().strip()} {self._check_registered(self.dctOldName2Suffix, imgName)}'
    
    def _update_file_name_preview(self):
        self.fileNamePreview.setText(f'<미리보기>\n{self._get_new_name(self.tempImgPreview)}')
    
    def _update_suffix(self, suffix):
        self.log.INFO(f'{self.tempImgPreview = }, "{suffix}"')
        self.dctOldName2Suffix[self.tempImgPreview] = suffix
        self._update_file_name_preview()

    #선택한 라디오 버튼에 맞춰서 {현 썸네일 이름: 전.후 정보}를 업데이트한다.
    def onRadioBtnSuffix(self):
        if self.radioBtnBefore.isChecked(): self._update_suffix(const.BEFORE_FIX)
        elif self.radioBtnAfter.isChecked(): self._update_suffix(const.AFTER_FIX)
        elif self.radioBtnAttached.isChecked(): self._update_suffix(const.ATTACH_FLYER)
        elif self.radioBtn1stWarn.isChecked(): self._update_suffix(const.WARN_1ST)
        elif self.radioBtn2ndWarn.isChecked(): self._update_suffix(const.WARN_2ND)
        elif self.radioBtnBeforeFetch.isChecked(): self._update_suffix(const.BEFORE_FETCH)
        elif self.radioBtnAfterFetch.isChecked(): self._update_suffix(const.AFTER_FETCH)
        elif self.radioBtnDefault.isChecked(): self._update_suffix(const.EMPTY_STR)

    def onRadioBtnCar(self):
        if self.radioBtn1stCar.isChecked():
            self.log.INFO('selected 1호차')
            self.prefix = '6'
        elif self.radioBtn2ndCar.isChecked():
            self.log.INFO('selected 2호차')
            self.prefix = '2'
        self._update_file_name_preview()

    def onCheckModifyLoc(self):
        if self.checkChangeCurrentLoc.isChecked():
            self.log.INFO('checkbox checked')
            self.inputChangeCurrentLoc.setEnabled(True)            

        else:
            self.log.INFO('checkbox unchecked')
            self.inputChangeCurrentLoc.setDisabled(True)
            if self.tempImgPreview in self.dctName2Details2Modify:
                self.dctName2Details2Modify.pop(self.tempImgPreview)

    def onTextLocationModify(self):
        if self.checkChangeCurrentLoc.isChecked():
            self.dctName2Details2Modify[self.tempImgPreview] = self.inputChangeCurrentLoc.text()
            # self.log.DEBUG(self.tempImgPreview, self.dctLoc2Modify[self.tempImgPreview])

    def onClickShowImage(self, event):
        self.clsGI.show_image(self.tempImgPreview)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    screen = GongikWidget()
    # screen.resize(540, 100)
    screen.show()
 
    sys.exit(app.exec_())