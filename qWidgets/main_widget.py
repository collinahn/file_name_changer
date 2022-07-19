import sys
from PyQt5.QtGui import (
    QPixmap,
    QFont,
    QMouseEvent,
)
from PyQt5.QtCore import (
    Qt,
    QTimer,
)
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
from lib.base_folder import WorkingDir


import lib.utils as utils
import qWordBook as const
from qWidgets.car_radiobtn import CarWidget
from lib.get_location import LocationInfo
from lib.file_property import FileProp
from lib.log_gongik import Logger
from lib.change_name import NameChanger
from lib.folder_open import FolderOpener
from lib.queue_order import (
    MstQueue, 
    PropsQueue
)
from lib.meta_data import (
    GPSInfo, 
    TimeInfo
)
from lib.restore_result import BackupRestore
from qWidgets.stamp_chkbox import StampWidget
from qDialogs.distributor import DistributorDialog
from qDialogs.info_dialog import InitInfoDialogue
from qWidgets.progress_display import ProgressWidgetThreaded
from qWidgets.web_engine import QWebEngineInstalled

class QPushButton(QPushButton):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

class QLabel(QLabel):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

class GongikWidget(QWidget):
    def __init__(self, targetFolder, parent = None):
        super(GongikWidget, self).__init__(parent)

        self.log = Logger()

        self.targetFolderAbsPath = targetFolder
        clsLoc = LocationInfo(targetFolder) #질의를 한 후 그 결과로 FileProp클래스 인스턴스의 정보를 초기화 
        clsTI = TimeInfo(targetFolder) #시간 정보를 초기화한다.(FileProp 인스턴스 이용)


        if not FileProp.name2AddrAPIOrigin() or not FileProp.name2AddrDBOrigin():
            fDlg = InitInfoDialogue('해당 디렉토리에 GPS정보를 가진 파일이 없거나 이미 처리된 파일들 입니다.\n종료합니다.', btn=('확인',))
            fDlg.exec_()
            sys.exit()

        FileProp.self_correct_address()
        # FileProp.debug_info()

        self.mst_queue = MstQueue() # 위치에 따라 큐를 생성하고 초기화시 자기자신에 삽입
        self.current_loc: PropsQueue = self.mst_queue.current_preview

        self._use_name:int = const.USE_ROAD # 도로명주소 우선

        self._init_ui()
        self._refresh_widget(self.current_loc.current_preview)

        timer = QTimer(self)
        timer.timeout.connect(self.onTimerFlash)
        timer.start(100)
        self.timerCnt = 0
        
        self.log.INFO('init complete')
        
    def _init_ui(self):
        QToolTip.setFont(QFont('SansSerif', 10))
        self.mainWidgetLayout = QGridLayout()
        self.setLayout(self.mainWidgetLayout)
        self.setStyleSheet(const.QSTYLE_SHEET)

        # 0번 레이아웃
        self.currentPath = QLabel(f'실행 경로: {self.targetFolderAbsPath}')
        self.mainWidgetLayout.addWidget(self.currentPath, 0, 0, 1, 2)
        self.totalPics = QLabel(f'총 사진 개수: {self.mst_queue.total_size}')
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
            f'정비 전\n({const.MSG_SHORTCUT.get("BEFORE_FIX")})',
            f'정비 후\n({const.MSG_SHORTCUT.get("AFTER_FIX")})',
            f'안내장\n({const.MSG_SHORTCUT.get("ATTACH_FLYER")})',
            f'1차계고\n({const.MSG_SHORTCUT.get("WARN_1ST")})',
            f'2차계고\n({const.MSG_SHORTCUT.get("WARN_2ST")})',
            f'수거 전\n({const.MSG_SHORTCUT.get("BEFORE_FETCH")})',
            f'수거 후\n({const.MSG_SHORTCUT.get("AFTER_FETCH")})',
            f'지정안함\n({const.MSG_SHORTCUT.get("SET_NONE")})',
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

        self.btnPreviousAddr = QPushButton(f'이전 장소 보기\n({const.MSG_SHORTCUT.get("BACKWARD")})')
        self.btnPreviousAddr.setShortcut(const.MSG_SHORTCUT.get('BACKWARD'))
        self.btnPreviousAddr.setToolTip(const.MSG_TIP.get('BACKWARD', 'BACKWARD'))
        self.btnPreviousAddr.clicked.connect(self.onBtnShowPrevAddr)
        self.mainWidgetLayout.addWidget(self.btnPreviousAddr, 2, 0)

        # 파일 이름 미리보기 & 주소 종류 설정 라디오버튼
        self.fileNameGroup = QGroupBox()
        self.mainWidgetLayout.addWidget(self.fileNameGroup, 2, 1)

        self.fileNameBoxLayout = QVBoxLayout()
        self.fileNameGroup.setLayout(self.fileNameBoxLayout)

        self.fileNamePreview = QLabel() # 변환된 파일명의 미리보기
        self.fileNamePreview.setAlignment(Qt.AlignCenter)
        self.fileNamePreview.setStyleSheet('font-weight: bold; color: yellow')
        self.fileNameBoxLayout.addWidget(self.fileNamePreview)
        self.bgFlash = False

        self.changeAddrGroupType = QGroupBox('') # 그룹박스 내 그룹박스(라디오버튼)
        self.changeAddrGroupType.setStyleSheet(const.QSTYLE_NO_BORDER_BOX)
        self.fileNameBoxLayout.addWidget(self.changeAddrGroupType, alignment=Qt.AlignCenter)

        self.changeAddrTypeLayout = QHBoxLayout()
        self.changeAddrGroupType.setLayout(self.changeAddrTypeLayout)
        
        self.radioBtnAddrTypeBoth = QRadioButton('자세히', self)
        self.radioBtnAddrTypeNormal = QRadioButton('지번주소', self)        
        self.radioBtnAddrTypeRoad = QRadioButton('도로명주소(기본)', self)
        self.radioBtnAddrTypeBoth.clicked.connect(self.onCheckRadioAddrType)
        self.radioBtnAddrTypeNormal.clicked.connect(self.onCheckRadioAddrType)
        self.radioBtnAddrTypeRoad.clicked.connect(self.onCheckRadioAddrType)
        self.changeAddrTypeLayout.addWidget(self.radioBtnAddrTypeBoth)
        self.changeAddrTypeLayout.addWidget(self.radioBtnAddrTypeNormal)
        self.changeAddrTypeLayout.addWidget(self.radioBtnAddrTypeRoad)
        self.radioBtnAddrTypeRoad.setChecked(True)

        self.picPreview = QLabel('Pixmap preview')
        self.picPreview.resize(540, 540)
        self.picPreview.setAlignment(Qt.AlignCenter)
        self.picPreview.setPixmap(self.current_loc.current_preview.pixmap.scaled(1280//2, 720//2))#, Qt.KeepAspectRatio))
        self.picPreview.setToolTip(const.MSG_TIP.get('PHOTO', 'PHOTO'))
        self.picPreview.mouseDoubleClickEvent = self.onClickShowImage
        self.mainWidgetLayout.addWidget(self.picPreview, 2, 2, 3, 1)

        self.btnNextAddr = QPushButton(f'다음 장소 보기\n({const.MSG_SHORTCUT.get("FORWARD")})')
        self.btnNextAddr.setShortcut(const.MSG_SHORTCUT.get('FORWARD'))
        self.btnNextAddr.setToolTip(const.MSG_TIP.get('FORWARD', 'FORWARD'))
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
        self.inputPriorityDetails.setPlaceholderText('개별 상세 정보를 등록하려면 체크 후 입력')
        self.inputPriorityDetails.setMinimumWidth(300)
        self.inputPriorityDetails.textChanged.connect(self.onModifyDetailsPrior)
        self.inputPriorityDetails.returnPressed.connect(self.onModifyDetailsPrior)
        self.changeDetailsLayout.addWidget(self.inputPriorityDetails)

        # 1호차2호차 선택 라디오버튼
        self.car_widget = CarWidget()
        self.mainWidgetLayout.addWidget(self.car_widget, 4, 0)
        self.car_widget.radio_btn_1st.clicked.connect(self.on_btn_refresh)
        self.car_widget.radio_btn_2nd.clicked.connect(self.on_btn_refresh)

        #사진에 스탬프 추가 체크박스
        self.stamp_widget = StampWidget()
        self.mainWidgetLayout.addWidget(self.stamp_widget, 4, 1)
        self.stamp_widget.checkbox_timestamp.clicked.connect(self.on_btn_refresh_preview)
        self.stamp_widget.checkbox_locationstamp.clicked.connect(self.on_btn_refresh_preview)
        self.stamp_widget.checkbox_detailstamp.clicked.connect(self.on_btn_refresh_preview)

        self.btn2Change = QPushButton(f'완료 및 이름 바꾸기\n({const.MSG_SHORTCUT.get("FINISH")})')
        self.btn2Change.setShortcut(const.MSG_SHORTCUT.get('FINISH'))
        self.btn2Change.setMinimumHeight(70)
        self.btn2Change.setToolTip(const.MSG_TIP.get('FINISH', 'FINISH'))
        self.btn2Change.clicked.connect(self.onBtnChangeFileName)
        self.mainWidgetLayout.addWidget(self.btn2Change, 5, 0, -1, 2)

        btnGroupOtherPics = QGroupBox()
        btnGroupOtherPics.setStyleSheet(const.QSTYLE_NO_BORDER_BOX)
        self.mainWidgetLayout.addWidget(btnGroupOtherPics, 5, 2)
        
        btnBoxOtherPicsLayout = QHBoxLayout()
        btnBoxOtherPicsLayout.setContentsMargins(0,0,0,0)
        btnGroupOtherPics.setLayout(btnBoxOtherPicsLayout)

        self.btnPreviousPicSameAddr = QPushButton(f'같은 장소 이전 사진 보기\n({const.MSG_SHORTCUT.get("PREVIOUS")})')
        self.btnPreviousPicSameAddr.setShortcut(const.MSG_SHORTCUT.get('PREVIOUS'))
        self.btnPreviousPicSameAddr.setToolTip(const.MSG_TIP.get('PREVIOUS', 'PREVIOUS'))
        self.btnPreviousPicSameAddr.clicked.connect(self.onBtnPrevPreview)
        btnBoxOtherPicsLayout.addWidget(self.btnPreviousPicSameAddr)

        self.btnLabelPicSeqInfo = QPushButton(self._generate_text_pic_indicator())
        self.btnLabelPicSeqInfo.setToolTip(const.MSG_TIP.get('SEQUENCE'))
        self.btnLabelPicSeqInfo.clicked.connect(self.onBtnDistributePics)
        btnBoxOtherPicsLayout.addWidget(self.btnLabelPicSeqInfo)

        self.btnNextPicSameAddr = QPushButton(f'같은 장소 다음 사진 보기\n({const.MSG_SHORTCUT.get("NEXT")})')
        self.btnNextPicSameAddr.setShortcut(const.MSG_SHORTCUT.get('NEXT'))
        self.btnNextPicSameAddr.setToolTip(const.MSG_TIP.get('NEXT', 'NEXT'))
        self.btnNextPicSameAddr.clicked.connect(self.onBtnNextPreview)
        btnBoxOtherPicsLayout.addWidget(self.btnNextPicSameAddr)

        # 웹엔진 관련 기능 위젯
        self.webEngineWidget = QWebEngineInstalled()
        self.webEngineWidget.init_page(*self.current_loc.current_preview.coord)
        self.webEngineWidget.btnRenewLocation.clicked.connect(self.on_btn_refresh)
        self.webEngineWidget.newLocFmPic.valueChanged.connect(self.on_btn_refresh) # 지도 클릭시 값이 변경되고 바로 반영
        self.mainWidgetLayout.addWidget(self.webEngineWidget, 0, 3, -1, -1)


    # 이름 뒤 구분 명칭을 결정하는 라디오 버튼을 만든다
    def _make_suffix_radio_btn(self, tplRadioBtn, shortcutCode, seq):
        result = QRadioButton(tplRadioBtn[seq], self)
        result.clicked.connect(self.onRadioBtnSuffix)
        result.setShortcut(const.MSG_SHORTCUT.get(shortcutCode))
        self.radioBoxLayout.addWidget(result, alignment=Qt.AlignTop)
        return result

    def _generate_text_pic_indicator(self):
        return f'{self.current_loc.current_pos} / {self.current_loc.size}'

    def _generate_text_loc_indicator(self):
        return f'\n완료율: {self.mst_queue.current_pos} / {self.mst_queue.size} \
            \n촬영 위치: {self.current_loc.name}'

    def _register_input(self):
        # 현재 커서의 지정 이름 저장
        text = self.nameInput.text().strip()
        self.current_loc.set_common_details(text)

        self.log.INFO('filename =', self.current_loc.current_preview, 'details=', text)

    # 사진과 설명을 업데이트한다.
    def _update_pixmap(self, file_props: FileProp):
        self.picPreview.setPixmap(file_props.pixmap.scaled(1280//2, 720//2))# , Qt.KeepAspectRatio))
    
    @staticmethod
    def _check_registered(dctDataSet, key) -> str:
        try:
            return dctDataSet[key]
        except (KeyError, AttributeError, TypeError):
            return ''

    #suffix라디오버튼의 위치를 기억했다가 다시 차례가 오면 채워준다
    def _set_radio_btn_as_checked(self):
        currentPreview: FileProp = self.current_loc.current_preview

        if   currentPreview.suffix == const.EMPTY_STR:    self.radioBtnDefault.setChecked(True)
        elif currentPreview.suffix == const.BEFORE_FIX:   self.radioBtnBefore.setChecked(True)
        elif currentPreview.suffix == const.AFTER_FIX:    self.radioBtnAfter.setChecked(True)
        elif currentPreview.suffix == const.ATTACH_FLYER: self.radioBtnAttached.setChecked(True)
        elif currentPreview.suffix == const.WARN_1ST:     self.radioBtn1stWarn.setChecked(True)   
        elif currentPreview.suffix == const.WARN_2ND:     self.radioBtn2ndWarn.setChecked(True)
        elif currentPreview.suffix == const.BEFORE_FETCH: self.radioBtnBeforeFetch.setChecked(True)   
        elif currentPreview.suffix == const.AFTER_FETCH:  self.radioBtnAfterFetch.setChecked(True)

        self.log.DEBUG('name:', currentPreview.name, 'suffix:', currentPreview.suffix)

    #개별 설명란 사용 여부를 기억한다
    def _set_modify_loc_still(self):
        fProp: FileProp = self.current_loc.current_preview
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
        self._update_pixmap(props)
        self._update_file_name_preview()
        self._set_radio_btn_as_checked()
        self._set_modify_loc_still()
        self.btnLabelPicSeqInfo.setText(self._generate_text_pic_indicator())
        self.labelPointer4SameLoc.setText(self._generate_text_loc_indicator())
        self.webEngineWidget.init_page(*props.coord) # 웹뷰 변경
        self.stamp_widget.set_status()

        self.log.INFO(props.name, 'refreshed')

    def onEnterRegisterCommonDetails(self):
        current_view: FileProp = self.current_loc.current_preview
        self._register_input()
        self._update_file_name_preview()

        self.log.INFO(current_view.name, '->', f'{current_view.prefix}_{current_view.locationFmAPI}-{current_view.locationFmDB} {self.nameInput.text().strip()} {current_view.suffix}')

    def onBtnShowPrevAddr(self):
        if self.mst_queue.current_pos == 1:
            InitInfoDialogue(const.MSG_INFO.get('SOF', 'start'), ('확인', )).exec_()
            return
            
        # 변경되어 현재 큐에 아무것도 없는 경우 리프레시, 아니면 장소 변경
        self.current_loc: PropsQueue = self.mst_queue.view_previous() if self.current_loc.queue else self.mst_queue.refresh()

        nextFile: FileProp = self.current_loc.current_preview
        self._refresh_widget(nextFile)
        self.log.INFO('Location:', self.current_loc.name, 'Next File:', nextFile.name)

    def onBtnShowNextAddr(self):
        if self.mst_queue.current_pos >= self.mst_queue.size:
            InitInfoDialogue(const.MSG_INFO.get('EOF', 'end'), ('확인', )).exec_()
            return

        # 변경되어 현재 큐에 아무것도 없는 경우 리프레시, 아니면 장소 변경
        self.current_loc: PropsQueue = self.mst_queue.view_next() if self.current_loc.queue else self.mst_queue.refresh()

        nextFile: FileProp = self.current_loc.current_preview
        self._refresh_widget(nextFile)
        self.log.INFO('Location:', self.current_loc.name, 'Next File:', nextFile.name)

    def onBtnPrevPreview(self):
        if not self.current_loc.queue:
            infoDlg = InitInfoDialogue('이동된 파일입니다. 다음/이전 장소 보기를 누르면 새로고침 됩니다.', ('확인', ))
            infoDlg.exec_()
            return

        nextFile: FileProp = self.current_loc.view_previous()
        self._refresh_widget(nextFile)
        self.log.INFO('file = ', nextFile, 'location =', self.current_loc)


    def onBtnNextPreview(self):
        if not self.current_loc.queue:
            infoDlg = InitInfoDialogue('이동된 파일입니다. 다음/이전 장소 보기를 누르면 새로고침 됩니다.', ('확인', ))
            infoDlg.exec_()
            return

        nextFile: FileProp = self.current_loc.view_next()
        self._refresh_widget(nextFile)
        self.log.INFO('file = ', nextFile, 'location =', self.current_loc)

    def onBtnChangeFileName(self):
        progress_dlg = ProgressWidgetThreaded()
        progress_dlg.show()
        progress_dlg.update(10, '준비 중')

        self._register_input() # 처리되지 않고 넘어간 현재 파일 이름 처리

        confirm_dlg = InitInfoDialogue('현재까지의 진행 상황을 파일 이름에 반영합니다.\n변환 후 프로그램은 종료됩니다.', ('예', '아니오'))
        confirm_dlg.exec_()

        if not confirm_dlg.answer:
            progress_dlg.close()
            return

        progress_dlg.update(80, '이름 변경 중')

        name_changer = NameChanger()
        ret_val = name_changer.change_name_on_btn(self._use_name)

        if ret_val == 0:
            self.log.INFO('mission complete')
            complete_dlg = InitInfoDialogue(const.MSG_INFO.get('COMPLETE', 'COMPLETE'), ('확인', ))
            complete_dlg.exec_()
        elif ret_val == 1:
            self.log.ERROR('file name error')
            error_dlg = InitInfoDialogue(const.MSG_WARN.get('FILE_NAME_ERROR', 'FILE_NAME_ERROR'), ('확인', ))
            error_dlg.exec_()
            return
        else:
            self.log.ERROR('mission fail')
            error_dlg = InitInfoDialogue(const.MSG_WARN.get('OS_ERROR', 'OS_ERROR'), ('확인', ))
            error_dlg.exec_()

        progress_dlg.update(10, '내역 저장 중')

        backup = BackupRestore()
        name4save = backup.create_file_path(self.current_loc.current_preview.prefix)
        FileProp.delete_pixmap_to_save() # 저장 공간 최적화를 위해 사진 정보는 빼고 저장한다.
        backup.save_result(name4save, FileProp.props())

        folder_opener = FolderOpener()
        folder_opener.open_file_browser(abs_path=self.targetFolderAbsPath)

        self.log.INFO('==================================')
        self.log.INFO('program exit')
        self.log.INFO('==================================')
        sys.exit()

    def _get_new_name(self):
        if self._use_name == const.USE_BOTH:
            return self.current_loc.current_preview.final_full_name
        elif self._use_name == const.USE_ROAD:
            return self.current_loc.current_preview.final_road_name
        return self.current_loc.current_preview.final_normal_name


    def _set_file_name_preview_text(self, text: str = None):
        if text is None:
            text = f'<미리보기>\n{self._get_new_name()}'
        self.fileNamePreview.setText(text)
    
    def _update_file_name_preview(self):
        self.timerCnt = 0 # 깜빡이기
        self.bgFlash = False
        self._set_file_name_preview_text()
    
    def _update_suffix(self, suffix):
        self.current_loc.current_preview.suffix = suffix
        self._update_file_name_preview()
        self.log.INFO(f'{self.current_loc.current_preview.name = }, "{suffix}"')

    def onTextCommonDetailsModified(self):
        self.current_loc.set_common_details(self.nameInput.text().strip()) # 공통 부분으로 업데이트
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

    def onCheckModifyLoc(self):
        fProps: FileProp = self.current_loc.current_preview

        if self.checkChangeCurrentLoc.isChecked():
            self.inputPriorityDetails.setEnabled(True)            
        else:
            self.inputPriorityDetails.setDisabled(True)
            self.inputPriorityDetails.setText('')
            fProps.specific_details = ''
            self.log.INFO('priority details deleted')

        self._update_file_name_preview()


    def onModifyDetailsPrior(self):
        fProps: FileProp = self.current_loc.current_preview

        if self.checkChangeCurrentLoc.isChecked():
            fProps.specific_details = self.inputPriorityDetails.text()

        self._update_file_name_preview()

    def onClickShowImage(self, event: QMouseEvent):
        fProp:FileProp = self.current_loc.current_preview
        fileOpener = FolderOpener()
        fileOpener.open_file_browser(abs_path=fProp.abs_path)
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
        
        if not self.current_loc.queue:
            self.log.WARNING('Deleting vacant mstQueue element')
            self.mst_queue.remove_location(self.mst_queue.current_preview)

        if dWidget.isChanged:
            self.current_loc = self.mst_queue.refresh()
            self._refresh_widget(self.current_loc.current_preview)

    def on_btn_refresh(self):
        self._update_file_name_preview()

    def on_btn_refresh_preview(self):
        current_loc: PropsQueue = self.mst_queue.current_preview
        self._update_pixmap(current_loc.current_preview)

    def onTimerFlash(self):
        if self.timerCnt > 3: 
            # 2번 이상 했으면 깜빡이지 않는다.
            return
        if self.bgFlash:
            self._set_file_name_preview_text()
            self.bgFlash = False
        else:
            self._set_file_name_preview_text('')
            self.bgFlash = True
        self.timerCnt += 1

if __name__ == '__main__':
    app = QApplication(sys.argv)
    wd = WorkingDir(utils.extract_dir(),'.')
    screen = GongikWidget(utils.extract_dir())
    # screen.resize(540, 100)
    screen.show()
 
    sys.exit(app.exec_())