import sys
from PyQt5.QtGui import (
    QFont,
    QIcon,
)
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QGroupBox, 
    QHBoxLayout, 
    QToolTip, 
    QApplication, 
    QGridLayout,
    QPushButton, 
    QLabel, 
    QScrollArea,
    QWidget, 
    QComboBox,
)
from lib.folder_open import FolderOpener

import lib.utils as utils
import qWordBook as const
from lib.change_name import NameChanger
from lib.get_location import LocationInfo
from lib.file_property import FileProp
from lib.file_detect import FileDetector
from lib.restore_result import BackupRestore
from lib.log_gongik import Logger
from qDialog import InitInfoDialogue
from qDraggable import (
    QDialog,
)

NEW_LINE = '\n'

class RestoreDialog(QDialog):
    def __init__(self, parent = None):
        super(RestoreDialog, self).__init__(parent)

        self.log = Logger()

        self.title = '내역 복원'
        self.icon_path = utils.resource_path(const.IMG_DEV)

        self.execPath = f'{utils.extract_dir()}/.gongik/restore'
        self.clsFD = FileDetector(self.execPath, isBackup=True)
        self.listBackupFiles: list = self.clsFD.file_list
        self.setBackupDates: set = {_.split('_')[1] for _ in self.listBackupFiles}
        self.log.INFO(f'backup dates extracted = {self.setBackupDates}')

        self.clsBR = BackupRestore() # 복구 데이터 불러오는
        self.targetData: dict[str, FileProp] or None = None # 복구 대상 데이터 
        self.globalPath: str = '' # 현재 위치 공유데이터

        self.init_ui()

        self.log.INFO('init complete')
        
    def init_ui(self):
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon(self.icon_path))        
        self.setStyleSheet(const.QSTYLE_SHEET_POPUP)
        self.setWindowFlags(Qt.FramelessWindowHint)

        QToolTip.setFont(QFont('SansSerif', 10))
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        
        #0번
        self.labelChooseDate = QLabel('복원 일자 선택')
        self.labelChooseDate.setToolTip('실행 일자 기준입니다.')
        self.labelChooseDate.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.labelChooseDate, 0, 0)
        
        self.widgetWrapComboDC = QWidget()
        self.comboChooseDate = QComboBox()
        self.comboChooseDate.addItems(sorted(list(self.setBackupDates),reverse=True)) # 콤보박스에 아이템 추가
        self.comboChooseDate.setToolTip('백업 파일이 있을 경우에만 표시됩니다.')
        self.comboChooseDate.setMaxVisibleItems(10)
        self.comboChooseDate.setMinimumHeight(30)
        self.comboChooseDate.setMinimumWidth(300)
        self.comboChooseDate.activated[str].connect(self.onChooseDate)
        self.layout.addWidget(self.comboChooseDate, 0, 1)

        # 1번 레이아웃
        self.infoChooseFile = QLabel('백업 파일 선택')
        self.infoChooseFile.setToolTip('형식: (호차)_(일자)_(고유식별번호).gongik')
        self.infoChooseFile.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.infoChooseFile, 1, 0)

        self.comboChooseFile = QComboBox()
        self.comboChooseFile.setMinimumHeight(30)
        self.comboChooseFile.setMinimumWidth(300)
        self.comboChooseFile.activated[str].connect(self.onChooseFile)
        self.layout.addWidget(self.comboChooseFile, 1, 1)
        self.update_combobox_file_list(self.comboChooseDate.currentText())


        #-------------파일 확인 창------------- 3번
        # Container Widget
        self.widget4ConfirmFile = QWidget()
        self.widget4ConfirmFileLayout = QHBoxLayout()
        self.widget4ConfirmFileLayout.setContentsMargins(10, 10, 10, 10)
        self.widget4ConfirmFile.setLayout(self.widget4ConfirmFileLayout)
        self.update_backupfile_info()

        # Scroll Area Properties
        self.scrollAreaChoosePic = QScrollArea()
        self.scrollAreaChoosePic.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollAreaChoosePic.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollAreaChoosePic.setWidgetResizable(True)
        self.scrollAreaChoosePic.setWidget(self.widget4ConfirmFile)
        self.scrollAreaChoosePic.setMinimumHeight(250)
        self.scrollAreaChoosePic.setMinimumWidth(800)

        self.layout.addWidget(self.scrollAreaChoosePic, 2, 0, 1, -1)


        # 4번 기능 버튼
        self.btnRestore = QPushButton('복원하기')
        self.btnRestore.setMinimumHeight(40)
        self.btnRestore.clicked.connect(self.onBtnAddNew)
        self.layout.addWidget(self.btnRestore, 3, 2)

        btnCancel = QPushButton('취소')
        btnCancel.setMaximumHeight(40)
        btnCancel.clicked.connect(self.onBtnCancel)
        self.layout.addWidget(btnCancel, 3, 3)
        
        self.set_btn_state()

    def set_btn_state(self):
        '''
        최초 로드시, 날짜 변경시, 파일 변경 시 실행됨 
        '''
        if not self.targetData: self.btnRestore.setDisabled(True)
        else: self.btnRestore.setEnabled(True)

    def onChooseDate(self, dateChosen: str):
        '''
        날짜를 골랐을 때 하단 콤보박스(해당하는 날짜의 백업 파일)를 업데이트한다
        '''
        self.log.INFO(f'usr chose {dateChosen}')
        self.update_combobox_file_list(dateChosen)
        self.set_btn_state()

    def update_combobox_file_list(self, dateChosen:str):
        self.comboChooseFile.clear()
        self.comboChooseFile.addItems((_ for _ in self.listBackupFiles if dateChosen in _ ))
        if hasattr(self, 'widget4ConfirmFileLayout'):
            self.update_backupfile_info()

    def onChooseFile(self, fileChosen: str):
        '''
        파일로부터 바이너리 정보를 읽어와 정보를 업데이트한다
        '''
        self.log.INFO(f'usr chose {fileChosen}')
        self.update_backupfile_info()
        self.set_btn_state()

    def update_backupfile_info(self):
        '''
        지정한 백업 파일을 읽어 정보를 표시하고 전역 변수를 업데이트한다.
        '''
        self.remove_item_from_mem() # 이전 내역 지운다
        if hasattr(self, 'widget4ConfirmFileLayout'):
            self.remove_item_from_layout(self.widget4ConfirmFileLayout)

        if not self.comboChooseFile.currentText():
            self.widget4ConfirmFileLayout.addWidget(QLabel('백업 파일이 존재하지 않습니다.'))
            self.targetData = None # 변경을 위한 공유 변수 초기화
            return
            
        targetFile = f'{self.clsBR.savePath}/{self.comboChooseFile.currentText()}'
        self.targetData: dict[str, FileProp] = self.clsBR.load_result(targetFile)

        try:
            for oldName, fProp in self.targetData.items():
                fProp: FileProp
                newName = fProp.new_path.split('/')[-1]

                singleInstanceBox = QGroupBox(f'{newName} 정보')
                singleInstanceLayout = QGridLayout()
                singleInstanceBox.setLayout(singleInstanceLayout)

                previousName = QLabel(oldName)
                timeCreated = QLabel(str(fProp.time))
                location4Display = QLabel(str(fProp.location4Display))
                locationOriginal = QLabel(str((fProp.locationFmAPI, fProp.locationFmDB)))
                details = QLabel(fProp.specific_details or fProp.details)
                filePath = QLabel(fProp.new_path.removesuffix(newName))
                self.globalPath = filePath.text() # 위치 공유

                singleInstanceLayout.addWidget(QLabel('이전 이름'), 1, 0)
                singleInstanceLayout.addWidget(previousName, 1, 1)
                singleInstanceLayout.addWidget(QLabel('촬영 시각'), 2, 0)
                singleInstanceLayout.addWidget(timeCreated, 2, 1)
                singleInstanceLayout.addWidget(QLabel('처리 위치'), 3, 0)
                singleInstanceLayout.addWidget(location4Display, 3, 1)
                singleInstanceLayout.addWidget(QLabel('실제 위치'), 4, 0)
                singleInstanceLayout.addWidget(locationOriginal, 4, 1)
                singleInstanceLayout.addWidget(QLabel('유저 입력'), 5, 0)
                singleInstanceLayout.addWidget(details, 5, 1)
                singleInstanceLayout.addWidget(QLabel('파일 경로'), 6, 0)
                singleInstanceLayout.addWidget(filePath, 6, 1)

                self.widget4ConfirmFileLayout.addWidget(singleInstanceBox)
        except AttributeError as ae:
            self.log.ERROR(ae)
            self.widget4ConfirmFileLayout.addWidget(QLabel(f'{self.comboChooseFile.currentText()} 파일이 손상되어 진행할 수 없습니다.'))
            self.targetData = None # 공유 변수(최종 데이터)

    def remove_item_from_mem(self) -> bool:
        if not self.targetData:
            return True
        
        FileProp.initialize_instances()
        
        return True


    def remove_item_from_layout(self, layout: QGridLayout or QHBoxLayout or any):
        self.log.INFO(f'layout ready for clear, {layout.count() = }')
        for i in reversed(range(layout.count())): 
            widgetToRemove = layout.itemAt(i).widget()
            # 레이아웃 제거
            layout.removeWidget(widgetToRemove)
            # gui에서 제거
            widgetToRemove.setParent(None)
        
    def onBtnAddNew(self):
        confirmDialog = InitInfoDialogue('***경고***\n 파일 이름을 초기 상태로 되돌립니다.\n이 행위는 되돌릴 수 없습니다.\n진행하시겠습니까?', ('확인했습니다','취소'))
        confirmDialog.exec_()
        if confirmDialog.answer:
            reconfirmDialog = InitInfoDialogue(f'현재 선택된 파일 \n{self.comboChooseFile.currentText()}\n의 데이터로 복구를 진행합니다.\n폴더 위치:{self.globalPath or "(오류_진행하지 않는 것을 권장합니다.)"}', ('알겠다고요','취소'))
            reconfirmDialog.exec_()
            if not reconfirmDialog.answer:
                return

            res = []
            clsNC = NameChanger()
            for fProp in self.targetData.values():
                fProp: FileProp
                if not clsNC.change_name_designated(
                    fromName=fProp.new_path,
                    toName=fProp.abs_path
                ): #오류 발생
                    res.append(fProp.new_path)

            clsFO = FolderOpener()
            clsFO.open_file_browser(absPath=self.globalPath) # 폴더 열기

            if res:
                resultDialog = InitInfoDialogue(f'**알림**\n\n이름 복구 실패 목록을 알려드립니다.\n\n{NEW_LINE.join(res)}\n\n파일이 이동되었거나 삭제되었으면 복구가 불가합니다.', ('네',))
            else:
                resultDialog = InitInfoDialogue('변환이 완료되었습니다. \n확인을 누르면 창을 닫습니다.', ('네',))
            resultDialog.exec_()
            self.close()
        

    def onBtnCancel(self):
        self.log.INFO('User Canceled Distribution')
        self.close()


if __name__ == '__main__':
            
    from lib.meta_data import TimeInfo
    from lib.get_location import LocationInfo
    from lib.utils import extract_dir
    TimeInfo()
    LocationInfo(extract_dir()) 

    app = QApplication(sys.argv)
    screen = RestoreDialog()
    # screen.resize(540, 100)
    screen.show()
 
    sys.exit(app.exec_())