# TODO: DICT객체 참조 시 get 메소드를 이용

import sys
from PyQt5.QtGui import (
    QPixmap,
    QFont,
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
from lib.get_location import LocationInfo
from lib.file_property import FileProp
from lib.log_gongik import Logger
from lib.change_name import NameChanger
from lib.queue_order import (
    MstQueue, 
    PropsQueue
)
from lib.meta_data import (
    GPSInfo, 
    TimeInfo
)
from qDistributorDialog import DistributorDialog
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

        clsLoc = LocationInfo() #질의를 한 후 그 결과로 FileProp클래스 인스턴스의 정보를 초기화 
        clsTI = TimeInfo() #시간 정보를 초기화한다.(FileProp 인스턴스 이용)


        if not FileProp.name2AddrAPIOrigin() or not FileProp.name2AddrDBOrigin():
            fDlg = InitInfoDialogue('해당 디렉토리에 GPS정보를 가진 파일이 없거나 이미 처리된 파일들 입니다.\n종료합니다.', btn=('확인',))
            fDlg.exec_()
            sys.exit()

        FileProp.self_correct_address()
        if __name__ == '__main__':
            FileProp.debug_info()

        self.masterQueue = MstQueue() # 위치에 따라 큐를 생성하고 초기화시 자기자신에 삽입
        self.currentLoc: PropsQueue = self.masterQueue.current_preview

        self._use_name:int = const.USE_BOTH

        self._init_ui()
        self._refresh_widget(self.currentLoc.current_preview)
        self.log.INFO('init complete')
        
    def _init_ui(self):
        QToolTip.setFont(QFont('SansSerif', 10))
        self.mainWidgetLayout = QGridLayout()
        self.setLayout(self.mainWidgetLayout)
        self.setStyleSheet(const.QSTYLE_SHEET)

        # 0번 레이아웃
        self.currentPath = QLabel(f'실행 경로: {utils.extract_dir()}')
        self.mainWidgetLayout.addWidget(self.currentPath, 0, 0, 1, 2)
        self.totalPics = QLabel(f'총 사진 개수: {self.masterQueue.total_size}')
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
        self.nameInput.textChanged.connect(self.onTextCommonDetailsModified)
        self.nameInput.returnPressed.connect(self.onEnterRegisterCommonDetails)
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

        # 파일 이름 미리보기 & 주소 종류 설정 라디오버튼
        self.fileNameGroup = QGroupBox()
        self.mainWidgetLayout.addWidget(self.fileNameGroup, 2, 1)

        self.fileNameBoxLayout = QVBoxLayout()
        self.fileNameGroup.setLayout(self.fileNameBoxLayout)

        self.fileNamePreview = QLabel() # 변환된 파일명의 미리보기
        self.fileNamePreview.setAlignment(Qt.AlignCenter)
        self.fileNameBoxLayout.addWidget(self.fileNamePreview)

        self.changeAddrGroupType = QGroupBox('') # 그룹박스 내 그룹박스(라디오버튼)
        self.changeAddrGroupType.setStyleSheet(const.QSTYLE_NO_BORDER_BOX)
        self.fileNameBoxLayout.addWidget(self.changeAddrGroupType, alignment=Qt.AlignCenter)

        self.changeAddrTypeLayout = QHBoxLayout()
        self.changeAddrGroupType.setLayout(self.changeAddrTypeLayout)
        
        self.radioBtnAddrTypeBoth = QRadioButton('자세히', self)
        self.radioBtnAddrTypeNormal = QRadioButton('지번주소', self)        
        self.radioBtnAddrTypeRoad = QRadioButton('도로명주소(인터넷 연결 없을 시)', self)
        self.radioBtnAddrTypeBoth.clicked.connect(self.onCheckRadioAddrType)
        self.radioBtnAddrTypeNormal.clicked.connect(self.onCheckRadioAddrType)
        self.radioBtnAddrTypeRoad.clicked.connect(self.onCheckRadioAddrType)
        self.changeAddrTypeLayout.addWidget(self.radioBtnAddrTypeBoth)
        self.changeAddrTypeLayout.addWidget(self.radioBtnAddrTypeNormal)
        self.changeAddrTypeLayout.addWidget(self.radioBtnAddrTypeRoad)
        self.radioBtnAddrTypeBoth.setChecked(True)

        self.picPreview = QLabel('사진 미리보기')
        self.picPreview.resize(540, 540)
        self.picPreview.setAlignment(Qt.AlignCenter)
        self.picPreview.setPixmap(QPixmap(self.currentLoc.current_preview.name).scaled(1280//2, 720//2))#, Qt.KeepAspectRatio))
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

        self.changeGroupSpecificDetail = QGroupBox() #그룹박스 내부 그룹박스
        self.changeGroupSpecificDetail.setStyleSheet(const.QSTYLE_NO_BORDER_BOX)
        self.locationBoxInfoLayout.addWidget(self.changeGroupSpecificDetail, alignment=Qt.AlignCenter)

        self.changeDetailsLayout = QHBoxLayout()
        self.changeDetailsLayout.setContentsMargins(0,0,0,0)
        self.changeGroupSpecificDetail.setLayout(self.changeDetailsLayout)

        self.checkChangeCurrentLoc = QCheckBox()
        self.changeDetailsLayout.addWidget(self.checkChangeCurrentLoc)
        self.checkChangeCurrentLoc.stateChanged.connect(self.onCheckModifyLoc)
        self.inputPriorityDetails = QLineEdit()
        self.inputPriorityDetails.setDisabled(True)
        self.inputPriorityDetails.setPlaceholderText('상세 정보를 바꾸려면 체크 후 입력')
        self.inputPriorityDetails.setMinimumWidth(300)
        self.inputPriorityDetails.textChanged.connect(self.onModifyDetailsPrior)
        self.inputPriorityDetails.returnPressed.connect(self.onModifyDetailsPrior)
        self.changeDetailsLayout.addWidget(self.inputPriorityDetails)

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
        if self.currentLoc.current_preview.prefix == '6': self.radioBtn1stCar.setChecked(True)
        elif self.currentLoc.current_preview.prefix == '2': self.radioBtn2ndCar.setChecked(True)
        self.radioBoxCarLayout.addStretch()

        self.btn2Change = QPushButton(f'완료 및 이름 바꾸기\n({const.MSG_SHORTCUT["FINISH"]})')
        self.btn2Change.setShortcut(const.MSG_SHORTCUT['FINISH'])
        self.btn2Change.setMinimumHeight(70)
        self.btn2Change.setToolTip(const.MSG_TIP['FINISH'])
        self.btn2Change.clicked.connect(self.onBtnChangeFileName)
        self.mainWidgetLayout.addWidget(self.btn2Change, 5, 0, -1, 2)

        btnGroupOtherPics = QGroupBox()
        btnGroupOtherPics.setStyleSheet(const.QSTYLE_NO_BORDER_BOX)
        self.mainWidgetLayout.addWidget(btnGroupOtherPics, 5, 2)
        
        btnBoxOtherPicsLayout = QHBoxLayout()
        btnBoxOtherPicsLayout.setContentsMargins(0,0,0,0)
        btnGroupOtherPics.setLayout(btnBoxOtherPicsLayout)

        self.btnPreviousPicSameAddr = QPushButton(f'같은 장소 이전 사진 보기\n({const.MSG_SHORTCUT["PREVIOUS"]})')
        self.btnPreviousPicSameAddr.setShortcut(const.MSG_SHORTCUT['PREVIOUS'])
        self.btnPreviousPicSameAddr.setToolTip(const.MSG_TIP['PREVIOUS'])
        self.btnPreviousPicSameAddr.clicked.connect(self.onBtnPrevPreview)
        btnBoxOtherPicsLayout.addWidget(self.btnPreviousPicSameAddr)

        self.btnLabelPicSeqInfo = QPushButton(self._generate_text_pic_indicator())
        self.btnLabelPicSeqInfo.setToolTip(const.MSG_TIP['SEQUENCE'])
        self.btnLabelPicSeqInfo.clicked.connect(self.onBtnDistributePics)
        btnBoxOtherPicsLayout.addWidget(self.btnLabelPicSeqInfo)

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

    def _generate_text_pic_indicator(self):
        return f'{self.currentLoc.current_pos} / {self.currentLoc.size}'

    def _generate_text_loc_indicator(self):
        return f'\n완료율: {self.masterQueue.current_pos} / {self.masterQueue.size} \
            \n현재 위치: {self.currentLoc.name}'

    def _register_input(self):
        # 현재 커서의 지정 이름 저장
        text = self.nameInput.text().strip()
        self.currentLoc.common_details(text)

        self.log.INFO('filename =', self.currentLoc.current_preview, 'details=', text)

    # 사진과 설명을 업데이트한다.
    def _update_pixmap(self, srcName):
        self.picPreview.setPixmap(QPixmap(srcName).scaled(1280//2, 720//2))# , Qt.KeepAspectRatio))
    
    @staticmethod
    def _check_registered(dctDataSet, key) -> str:
        try:
            return dctDataSet[key]
        except (KeyError, AttributeError, TypeError):
            return ''

    #suffix라디오버튼의 위치를 기억했다가 다시 차례가 오면 채워준다
    def _setRadioBtnAsChecked(self):
        currentPreview = self.currentLoc.current_preview

        if   currentPreview.suffix == const.EMPTY_STR:    self.radioBtnDefault.setChecked(True)
        elif currentPreview.suffix == const.BEFORE_FIX:   self.radioBtnBefore.setChecked(True)
        elif currentPreview.suffix == const.AFTER_FIX:    self.radioBtnAfter.setChecked(True)
        elif currentPreview.suffix == const.ATTACH_FLYER: self.radioBtnAttached.setChecked(True)
        elif currentPreview.suffix == const.WARN_1ST:     self.radioBtn1stWarn.setChecked(True)   
        elif currentPreview.suffix == const.WARN_2ND:     self.radioBtn2ndWarn.setChecked(True)
        elif currentPreview.suffix == const.BEFORE_FETCH: self.radioBtnBeforeFetch.setChecked(True)   
        elif currentPreview.suffix == const.AFTER_FETCH:  self.radioBtnAfterFetch.setChecked(True)

        self.log.DEBUG('name:', currentPreview.name, 'suffix:', currentPreview.suffix)

    #위치 변경 여부를 기억한다
    def _setModifyLocStill(self):
        fProp: FileProp = self.currentLoc.current_preview
        if fProp.specific_details:
            self.checkChangeCurrentLoc.setChecked(True)
            self.inputPriorityDetails.setEnabled(True)
            self.inputPriorityDetails.setText(fProp.specific_details)
        else:
            self.checkChangeCurrentLoc.setChecked(False)
            self.inputPriorityDetails.setEnabled(False)
            self.inputPriorityDetails.setText('')

        self.log.INFO(f'{fProp.name = } {fProp.specific_details = }')

    def _refresh_widget(self, props: FileProp):

        self.nameInput.setText(props.details) # 입력 필드 불러오기
        self._update_pixmap(props.name)
        self._update_file_name_preview()
        self._setRadioBtnAsChecked()
        self._setModifyLocStill()
        self.btnLabelPicSeqInfo.setText(self._generate_text_pic_indicator())
        self.labelPointer4SameLoc.setText(self._generate_text_loc_indicator())
        
        self.log.INFO(props.name, 'refreshed')

    def onEnterRegisterCommonDetails(self):
        currentPreview: FileProp = self.currentLoc.current_preview
        self._register_input()
        self._update_file_name_preview()

        self.log.INFO(currentPreview.name, '->', f'{currentPreview.prefix}_{currentPreview.locationAPI}-{currentPreview.locationDB} {self.nameInput.text().strip()} {currentPreview.suffix}')

    def onBtnShowPrevAddr(self):
        if self.masterQueue.current_pos == 1:
            InitInfoDialogue(const.MSG_INFO['SOF'], ('확인', )).exec_()
            return
        
        if not self.currentLoc.queue: #변경되어 현재 큐에 아무것도 없을 경우
            self.currentLoc = self.masterQueue.refresh()
        else:
            self.currentLoc = self.masterQueue.view_previous() # 장소 변경
        
        nextFile: FileProp = self.currentLoc.current_preview
        self._refresh_widget(nextFile)
        self.log.INFO('Location:', self.currentLoc.name, 'Next File:', nextFile.name)

    def onBtnShowNextAddr(self):

        if self.masterQueue.current_pos >= self.masterQueue.size:
            InitInfoDialogue(const.MSG_INFO['EOF'], ('확인', )).exec_()
            return

        if not self.currentLoc.queue: #변경되어 현재 큐에 아무것도 없는 경우
            self.currentLoc = self.masterQueue.refresh()
        else:
            self.currentLoc = self.masterQueue.view_next() # 장소 변경

        nextFile: FileProp = self.currentLoc.current_preview
        self._refresh_widget(nextFile)
        self.log.INFO('Location:', self.currentLoc.name, 'Next File:', nextFile.name)

    def onBtnPrevPreview(self):
        if not self.currentLoc.queue:
            infoDlg = InitInfoDialogue('이동된 파일입니다. 다음/이전 장소 보기를 누르면 새로고침 됩니다.', ('확인', ))
            infoDlg.exec_()
            return

        nextFile: FileProp = self.currentLoc.view_previous()
        self._refresh_widget(nextFile)
        self.log.INFO('file = ', nextFile, 'location =', self.currentLoc)


    def onBtnNextPreview(self):
        if not self.currentLoc.queue:
            infoDlg = InitInfoDialogue('이동된 파일입니다. 다음/이전 장소 보기를 누르면 새로고침 됩니다.', ('확인', ))
            infoDlg.exec_()
            return

        nextFile: FileProp = self.currentLoc.view_next()
        self._refresh_widget(nextFile)
        self.log.INFO('file = ', nextFile, 'location =', self.currentLoc)

    def onBtnChangeFileName(self):
        from qDialog import ProgressTimerDialog
        progDlg = ProgressTimerDialog()
        progDlg.show()
        progDlg.mark_progress(10, '준비 중')

        self._register_input() # 처리되지 않고 넘어간 현재 파일 이름 처리

        confirmDlg = InitInfoDialogue('현재까지의 진행 상황을 파일 이름에 반영합니다.\n변환 후 프로그램은 종료됩니다.', ('예', '아니오'))
        confirmDlg.exec_()

        if not confirmDlg.answer:
            progDlg.close()
            return

        progDlg.mark_progress(80, '이름 변경 중')

        clsNc = NameChanger()
        retChangeName = clsNc.change_name_on_btn(self._use_name)

        if retChangeName == 0:
            self.log.INFO('mission complete')
            completeDlg = InitInfoDialogue(const.MSG_INFO['COMPLETE'], ('확인', ))
            completeDlg.exec_()
        elif retChangeName == 1:
            self.log.ERROR('file name error')
            errorDlg = InitInfoDialogue(const.MSG_WARN['FILE_NAME_ERROR'], ('확인', ))
            errorDlg.exec_()
        else:
            self.log.ERROR('mission fail')
            errorDlg = InitInfoDialogue(const.MSG_WARN['OS_ERROR'], ('확인', ))
            errorDlg.exec_()

        progDlg.mark_progress(100, '마무리 중')

        InitInfoDialogue(const.MSG_INFO['EXIT_END'], ('확인', )).exec_()
        self.log.INFO('==================================')
        self.log.INFO('program exit')
        self.log.INFO('==================================')
        sys.exit()

    def _get_new_name(self):
        if self._use_name == const.USE_BOTH:
            return self.currentLoc.current_preview.final_full_name
        elif self._use_name == const.USE_ROAD:
            return self.currentLoc.current_preview.final_road_name
        return self.currentLoc.current_preview.final_normal_name
    
    def _update_file_name_preview(self):
        self.fileNamePreview.setText(f'<미리보기>\n{self._get_new_name()}')
    
    def _update_suffix(self, suffix):
        self.currentLoc.current_preview.suffix = suffix
        self._update_file_name_preview()
        self.log.INFO(f'{self.currentLoc.current_preview.name = }, "{suffix}"')

    def onTextCommonDetailsModified(self):
        self.currentLoc.common_details(self.nameInput.text().strip()) # 공통 부분으로 업데이트
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
        currentFile = self.currentLoc.current_preview
        if self.radioBtn1stCar.isChecked():
            self.log.INFO('selected 1호차')
            currentFile.prefix = '6'

        elif self.radioBtn2ndCar.isChecked():
            self.log.INFO('selected 2호차')
            currentFile.prefix = '2'
            
        self._update_file_name_preview()

    def onCheckModifyLoc(self):
        fProps: FileProp = self.currentLoc.current_preview

        if self.checkChangeCurrentLoc.isChecked():
            self.inputPriorityDetails.setEnabled(True)            
        else:
            self.inputPriorityDetails.setDisabled(True)
            self.inputPriorityDetails.setText('')
            fProps.specific_details = ''
            self.log.INFO(f'priority details deleted')

        self._update_file_name_preview()


    def onModifyDetailsPrior(self):
        fProps: FileProp = self.currentLoc.current_preview

        if self.checkChangeCurrentLoc.isChecked():
            fProps.specific_details = self.inputPriorityDetails.text()

        self._update_file_name_preview()

    def onClickShowImage(self, event: QMouseEvent):
        clsGI = GPSInfo()
        fProp:FileProp = self.currentLoc.current_preview
        clsGI.show_image(fProp.name)
        self.log.INFO('opening', fProp.name)

    def onCheckRadioAddrType(self):
        if self.radioBtnAddrTypeBoth.isChecked():
            self._use_name = const.USE_BOTH
        if self.radioBtnAddrTypeNormal.isChecked():
            self._use_name = const.USE_NORMAL
        if self.radioBtnAddrTypeRoad.isChecked():
            self._use_name = const.USE_ROAD

        self._update_file_name_preview()


    def onBtnDistributePics(self):
        dWidget = DistributorDialog()
        dWidget.exec_()
        
        if not self.currentLoc.queue:
            self.log.WARNING('Deleting vacant mstQueue element')
            self.masterQueue.remove_location(self.masterQueue.current_preview)

        self.currentLoc = self.masterQueue.refresh()

        self._refresh_widget(self.currentLoc.current_preview)
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    screen = GongikWidget()
    # screen.resize(540, 100)
    screen.show()
 
    sys.exit(app.exec_())