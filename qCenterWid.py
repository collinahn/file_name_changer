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
import qWordBook as const
from lib.queue_order import QueueReadOnly
from lib.log_gongik import Logger
from lib.change_name import NameChanger
from lib.meta_data import GPSInfo, TimeInfo
from qDialog import InitInfoDialogue

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
        self._correct_addr_with_time() # 위치 보정

        if not self.dctName2AddrStorage:
            fDlg = InitInfoDialogue('해당 디렉토리에 GPS정보를 가진 파일이 없거나 이미 처리된 파일들 입니다.\n종료합니다.', btn=('확인',))
            fDlg.exec_()
            sys.exit()

        
        lstSingleLocQueue = []
        self.dctLoc2Names = utils.invert_dict(self.dctName2AddrStorage)
        for loc, nameList in self.dctLoc2Names.items():
            lstSingleLocQueue.append(QueueReadOnly(loc, tuple(nameList)))

        self.masterQueue = QueueReadOnly('master', tuple(lstSingleLocQueue)) # 위치에 따른 이름 리스트 저장
        self.currentLoc: QueueReadOnly = self.masterQueue.current_preview
        self.log.DEBUG(self.currentLoc.name)

        self.dctLocation2Details = {}
        self.setProcessedName = set()
        self.setProcessedAddr = set()
        self.dctName2Suffix = {}
        self.prefix = self.clsNc.gubun # 호차 구분 (1호차: 6, 2호차: 2)

        self.dctName2Details2Modify = {} #{이름:개별수정사안}
        
        self.init_ui()
        self.log.INFO('init complete')
        
    def init_ui(self):

        QToolTip.setFont(QFont('SansSerif', 10))
        self.mainWidgetLayout = QGridLayout()
        self.setLayout(self.mainWidgetLayout)

        # 0번 레이아웃
        self.currentPath = QLabel(f'실행 경로: {utils.extract_dir()}')
        self.mainWidgetLayout.addWidget(self.currentPath, 0, 0, 1, 2)
        self.totalPics = QLabel(f'총 사진 개수: {len(self.dctName2AddrStorage)}')
        self.totalPics.setAlignment(Qt.AlignCenter)
        self.mainWidgetLayout.addWidget(self.totalPics, 0, 2)

        self.instruction = QLabel('상세 입력')
        self.instruction.setAlignment(Qt.AlignCenter)
        self.mainWidgetLayout.addWidget(self.instruction, 1, 0)

        self.nameInput = QLineEdit()
        self.nameInput.setPlaceholderText('상세 정보 입력(예> "불법적치물"만 입력)')
        self.nameInput.setMaxLength(100)
        self.nameInput.setMinimumWidth(500)
        self.nameInput.setMinimumHeight(50)
        self.nameInput.textChanged.connect(self._update_file_name_preview)
        self.nameInput.returnPressed.connect(self.onEnterRegName)
        self.mainWidgetLayout.addWidget(self.nameInput, 1, 1)

        # 전 후 선택 라디오버튼
        self.radioGroupBox = QGroupBox('파일 이름 개별지정')
        self.mainWidgetLayout.addWidget(self.radioGroupBox, 1, 2)

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
        self.radioBtnBeforeFetch = self._make_suffix_radio_btn(txtRadioBtn, 'BEFORE_FETCH', 5)
        self.radioBtnAfterFetch = self._make_suffix_radio_btn(txtRadioBtn, 'AFTER_FETCH', 6)
        self.radioBtnDefault = self._make_suffix_radio_btn(txtRadioBtn, 'SET_NONE', 7)
        self.radioBtnDefault.setChecked(True)
        self.radioBoxLayout.addStretch()

        self.btnPreviousAddr = QPushButton(f'이전 장소 보기\n({const.MSG_SHORTCUT["BACKWARD"]})')
        self.btnPreviousAddr.setShortcut(const.MSG_SHORTCUT['BACKWARD'])
        self.btnPreviousAddr.setToolTip(const.MSG_TIP['BACKWARD'])
        self.btnPreviousAddr.clicked.connect(self.onBtnShowPrevAddr)
        self.mainWidgetLayout.addWidget(self.btnPreviousAddr, 2, 0)

        self.fileNamePreview = QLabel() # 변환된 파일명의 미리보기
        self.fileNamePreview.setAlignment(Qt.AlignCenter)
        self.mainWidgetLayout.addWidget(self.fileNamePreview, 2, 1)

        self.picPreview = QLabel('사진 미리보기')
        self.picPreview.resize(540, 540)
        self.picPreview.setAlignment(Qt.AlignCenter)
        self.picPreview.setPixmap(QPixmap(self.currentLoc.current_preview).scaled(1280//2, 720//2))#, Qt.KeepAspectRatio))
        self.picPreview.setToolTip(const.MSG_TIP['PHOTO'])
        self.picPreview.mouseDoubleClickEvent = self.onClickShowImage
        self.mainWidgetLayout.addWidget(self.picPreview, 2, 2, 3, -1)

        self.btnNextAddr = QPushButton(f'다음 장소 보기\n({const.MSG_SHORTCUT["FORWARD"]})')
        self.btnNextAddr.setShortcut(const.MSG_SHORTCUT['FORWARD'])
        self.btnNextAddr.setToolTip(const.MSG_TIP['FORWARD'])
        self.btnNextAddr.clicked.connect(self.onBtnShowNextAddr)
        self.mainWidgetLayout.addWidget(self.btnNextAddr, 3, 0)

        # 같은 위치 preview 갯수 세기 & 주소 변경 체크박스
        self.locationGroupInfo = QGroupBox()
        self.mainWidgetLayout.addWidget(self.locationGroupInfo, 3, 1)

        self.locationBoxInfoLayout = QVBoxLayout()
        self.locationGroupInfo.setLayout(self.locationBoxInfoLayout)

        self.labelPointer4SameLoc = QLabel(self._generate_text_loc_indicator())
        self.labelPointer4SameLoc.setAlignment(Qt.AlignCenter)
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
        self.inputChangeCurrentLoc.textChanged.connect(self.onModifyTextLocation)
        self.inputChangeCurrentLoc.returnPressed.connect(self.onModifyTextLocation)
        self.changeLocLayout.addWidget(self.inputChangeCurrentLoc)

        # 1호차2호차 선택 라디오버튼
        self.radioGroupCar = QGroupBox('호차 선택')
        self.mainWidgetLayout.addWidget(self.radioGroupCar, 4, 0, 1, 2)

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
        self.mainWidgetLayout.addWidget(self.btn2Change, 5, 0, -1, 2)


        btnGroupOtherPics = QGroupBox()
        self.mainWidgetLayout.addWidget(btnGroupOtherPics, 5, 2)
        
        btnBoxOtherPicsLayout = QHBoxLayout()
        btnGroupOtherPics.setLayout(btnBoxOtherPicsLayout)

        self.btnPreviousPicSameAddr = QPushButton(f'같은 장소 이전 사진 보기\n({const.MSG_SHORTCUT["PREVIOUS"]})')
        self.btnPreviousPicSameAddr.setShortcut(const.MSG_SHORTCUT['PREVIOUS'])
        self.btnPreviousPicSameAddr.setToolTip(const.MSG_TIP['PREVIOUS'])
        self.btnPreviousPicSameAddr.clicked.connect(self.onBtnPrevPreview)
        btnBoxOtherPicsLayout.addWidget(self.btnPreviousPicSameAddr)

        self.labelPicSeqInfo = QLabel(self._generate_text_pic_indicator())
        self.labelPicSeqInfo.setAlignment(Qt.AlignCenter)
        btnBoxOtherPicsLayout.addWidget(self.labelPicSeqInfo)

        self.btnNextPicSameAddr = QPushButton(f'같은 장소 다음 사진 보기\n({const.MSG_SHORTCUT["NEXT"]})')
        self.btnNextPicSameAddr.setShortcut(const.MSG_SHORTCUT['NEXT'])
        self.btnNextPicSameAddr.setToolTip(const.MSG_TIP['NEXT'])
        self.btnNextPicSameAddr.clicked.connect(self.onBtnNextPreview)
        btnBoxOtherPicsLayout.addWidget(self.btnNextPicSameAddr)

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

    def _generate_text_pic_indicator(self):
        return f'{self.currentLoc.current_pos} / {self.currentLoc.queue_size}'

    def _generate_text_loc_indicator(self):
        return f'\n완료율: {self.masterQueue.current_pos} / {self.masterQueue.queue_size} \
            \n현재 위치: {self.dctName2AddrStorage[self.currentLoc.current_preview]}'


    def _register_input(self):
        # 현재 커서의 지정 이름 저장
        currentPreview = self.currentLoc.current_preview
        self.dctLocation2Details[self.dctName2AddrStorage[currentPreview]] = self.nameInput.text().strip()
        self.log.INFO('filename =', currentPreview, ':', self.dctLocation2Details[self.dctName2AddrStorage[currentPreview]])

    # 사진과 설명을 업데이트한다.
    def _update_pixmap(self, srcName):
        self.picPreview.setPixmap(QPixmap(srcName).scaled(1280//2, 720//2))# , Qt.KeepAspectRatio))
    
    @staticmethod
    def _check_registered(dctDataSet, key) -> str:
        try:
            return dctDataSet[key]
        except (KeyError, AttributeError, TypeError):
            return ''


    #라디오버튼의 위치를 기억했다가 다시 차례가 오면 채워준다
    def _setRadioBtnAsChecked(self):
        currentPreview = self.currentLoc.current_preview
        if currentPreview not in self.dctName2Suffix:
            self.radioBtnDefault.setChecked(True)
            return

        if self.dctName2Suffix[currentPreview] == const.BEFORE_FIX:
            self.radioBtnBefore.setChecked(True)
        elif self.dctName2Suffix[currentPreview] == const.AFTER_FIX:
            self.radioBtnAfter.setChecked(True)
        elif self.dctName2Suffix[currentPreview] == const.ATTACH_FLYER:
            self.radioBtnAttached.setChecked(True)
        elif self.dctName2Suffix[currentPreview] == const.WARN_1ST:
            self.radioBtn1stWarn.setChecked(True)   
        elif self.dctName2Suffix[currentPreview] == const.WARN_2ND:
            self.radioBtn2ndWarn.setChecked(True)
        elif self.dctName2Suffix[currentPreview] == const.BEFORE_FETCH:
            self.radioBtnBeforeFetch.setChecked(True)   
        elif self.dctName2Suffix[currentPreview] == const.AFTER_FETCH:
            self.radioBtnAfterFetch.setChecked(True)

        self.log.DEBUG(self.dctName2Suffix)

    #위치 변경 여부를 기억한다
    def _setModifyLocAsChecked(self):
        if self.currentLoc.current_preview in self.dctName2Details2Modify:
            self.checkChangeCurrentLoc.setChecked(True)
            self.inputChangeCurrentLoc.setEnabled(True)
            self.inputChangeCurrentLoc.setText(self.dctName2Details2Modify[self.currentLoc.current_preview])
        else:
            self.checkChangeCurrentLoc.setChecked(False)
            self.inputChangeCurrentLoc.setEnabled(False)
            self.inputChangeCurrentLoc.setText('')

        self.log.DEBUG(self.dctName2Details2Modify)


    def onEnterRegName(self):
        currentPreview = self.currentLoc.current_preview
        self._register_input()
        self._update_file_name_preview()
        self.clsNc.store_models(
            self.prefix, 
            self.dctName2AddrStorage, 
            self.dctLocation2Details, 
            self.dctName2Suffix, 
            self.dctName2Details2Modify
        )

        self.log.INFO(currentPreview, '->', f'{self.prefix}_{self.dctName2AddrStorage[currentPreview]} {self.nameInput.text().strip()} {self._check_registered(self.dctName2Suffix, currentPreview)}')

    def onBtnShowPrevAddr(self):
        self._register_input() # 처리되지 않은 파일 이름들 처리
        self.clsNc.store_models(
            self.prefix, 
            self.dctName2AddrStorage, 
            self.dctLocation2Details, 
            self.dctName2Suffix, 
            self.dctName2Details2Modify
        )

        if self.masterQueue.current_pos == 1:
            QMessageBox.information(self, 'SOF', const.MSG_INFO['SOF'])
            return
        
        self.currentLoc = self.masterQueue.view_previous() # 장소 변경
        nextFileName = self.currentLoc.current_preview # 같은 장소의 사진 변경

        self.nameInput.setText(self._check_registered(self.dctLocation2Details, self.currentLoc.name)) # 입력 필드 불러오기
        self._update_pixmap(nextFileName)
        self._setRadioBtnAsChecked()
        self._setModifyLocAsChecked()
        self._update_file_name_preview()
        self.labelPicSeqInfo.setText(self._generate_text_pic_indicator())
        self.labelPointer4SameLoc.setText(self._generate_text_loc_indicator())

        self.log.INFO('Location:', self.currentLoc.name, 'Next File:', nextFileName)

    def onBtnShowNextAddr(self):
        self._register_input() # 처리되지 않은 파일 이름들 처리
        self.clsNc.store_models(
            self.prefix, 
            self.dctName2AddrStorage, 
            self.dctLocation2Details, 
            self.dctName2Suffix, 
            self.dctName2Details2Modify
        )
        if self.masterQueue.current_pos == self.masterQueue.queue_size:
            QMessageBox.information(self, 'EOF', const.MSG_INFO['EOF'])
            return

        self.currentLoc = self.masterQueue.view_next() # 장소 변경
        nextFileName = self.currentLoc.current_preview # 같은 장소의 사진 변경

        self.nameInput.setText(self._check_registered(self.dctLocation2Details, self.currentLoc.name)) # 입력 필드 초기화
        self._update_pixmap(nextFileName)
        self._setRadioBtnAsChecked()
        self._setModifyLocAsChecked()
        self._update_file_name_preview()
        self.labelPicSeqInfo.setText(self._generate_text_pic_indicator())
        self.labelPointer4SameLoc.setText(self._generate_text_loc_indicator())

        self.log.INFO('Location:', self.currentLoc, 'Next File:', nextFileName)

    def onBtnPrevPreview(self):
        currentPreview = self.currentLoc.view_previous()

        self._update_pixmap(currentPreview)
        self._setRadioBtnAsChecked()  # 라디오버튼 기억        
        self._setModifyLocAsChecked() # 위치 변경 기억
        self._update_file_name_preview()
        self.labelPicSeqInfo.setText(self._generate_text_pic_indicator())
        # self.labelPointer4SameLoc.setText(self._generate_text_loc_indicator())

        self.log.INFO('file =', currentPreview, 'location =', self.currentLoc)


    def onBtnNextPreview(self):
        currentPreview = self.currentLoc.view_next()

        self._update_pixmap(currentPreview)
        self._setRadioBtnAsChecked()  # 라디오버튼 기억        
        self._setModifyLocAsChecked() # 위치 변경 기억
        self._update_file_name_preview()
        self.labelPicSeqInfo.setText(self._generate_text_pic_indicator())
        # self.labelPointer4SameLoc.setText(self._generate_text_loc_indicator())

        self.log.INFO('file = ', currentPreview, 'location =', self.currentLoc)

    def onBtnChangeFileName(self):
        from qDialog import ProgressTimerDialog
        progDlg = ProgressTimerDialog()
        progDlg.show()
        progDlg.mark_progress(10, '준비 중')

        progDlg.mark_progress(30, '미완료 값 처리 중')
        
        self._register_input() # 처리되지 않고 넘어간 현재 파일 이름 처리
        lstVirtualLocObj = self.masterQueue.queue   # 이후에 혹시 처리되지 않은 파일 이름 있으면 처리
        for locInstance in lstVirtualLocObj:
            if locInstance.name not in self.dctLocation2Details:
                self.dctLocation2Details[locInstance.name] = ''

        progDlg.mark_progress(80, '이름 변경 중')

        retChangeName = self.clsNc.change_name_on_btn(self.prefix, self.dctLocation2Details, self.dctName2Suffix, self.dctName2Details2Modify)

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
        return f'{self.prefix}_{self.dctName2AddrStorage[imgName]} {self.nameInput.text().strip()} {self._check_registered(self.dctName2Suffix, imgName)}'
    
    def _update_file_name_preview(self):
        self.fileNamePreview.setText(f'<미리보기>\n{self._get_new_name(self.currentLoc.current_preview)}')
    
    def _update_suffix(self, suffix):
        self.log.INFO(f'{self.currentLoc.current_preview = }, "{suffix}"')
        self.dctName2Suffix[self.currentLoc.current_preview] = suffix
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
            if self.currentLoc.current_preview in self.dctName2Details2Modify:
                self.dctName2Details2Modify.pop(self.currentLoc.current_preview)

    def onModifyTextLocation(self):
        if self.checkChangeCurrentLoc.isChecked():
            self.dctName2Details2Modify[self.currentLoc.current_preview] = self.inputChangeCurrentLoc.text()
            # self.log.DEBUG(self.tempImgPreview, self.dctLoc2Modify[self.tempImgPreview])

    def onClickShowImage(self, event):
        self.clsGI.show_image(self.currentLoc.current_preview)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    screen = GongikWidget()
    # screen.resize(540, 100)
    screen.show()
 
    sys.exit(app.exec_())