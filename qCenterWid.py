from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtWidgets import (
    QGroupBox, QHBoxLayout, QMessageBox, QRadioButton, QSizePolicy,
    QToolTip, QWidget, QApplication, QGridLayout,
    QPushButton, QLabel, QLineEdit
)
import sys

import utils
from change_name import NameChanger

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
        self.dctNameStorage = self.clsNc.dctName2Change
        self.lstOldName = list(self.dctNameStorage.keys())
        self.dctLocation2Details = {}
        self.idxPointer = 0
        self.setProcessedName = set()
        self.setProcessedAddr = set()
        self.lstTempNamePool = [] # 파일 미리보기를 위한 임시 리스트
        self.dctOldName2BeforeAfter = {}

        if not self.dctNameStorage:
            #TODO: 잘못된 경로(temp)로 읽히는 원인 파악하기 
            currentDir = 'exe 파일이 위치한 곳' # utils.extract_parent_dir()
            QMessageBox.warning(self, '경고', f'현재 디렉토리\n({currentDir})\n에 처리할 수 있는 파일이 없습니다.\n종료합니다.')
            sys.exit()

        self.currentPreview = self.lstOldName[0]
        self.tempImgPreview = self.currentPreview # 장소별/같은 장소 내의 임시 프리뷰 통합 관리
        self.init_ui()
        
    def init_ui(self):
        currentDir = utils.extract_parent_dir()

        QToolTip.setFont(QtGui.QFont('SansSerif', 10))
        layout = QGridLayout()
        self.setLayout(layout)

        #TODO: 메뉴바

        self.dirInfo = QLabel('현재 디렉토리: ')
        layout.addWidget(self.dirInfo, 0, 0)

        self.startingDir = QLabel(currentDir)
        layout.addWidget(self.startingDir, 0, 1)

        self.labelLoc4Preview = QLabel(f'사진 위치: {self.dctNameStorage[self.currentPreview]}')
        self.labelLoc4Preview.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.labelLoc4Preview, 0,2)

        self.instruction = QLabel('상세 입력')
        layout.addWidget(self.instruction, 1, 0)

        self.nameInput = QLineEdit()
        self.nameInput.setPlaceholderText('상세 정보 입력')
        self.nameInput.setMaxLength(30)
        self.nameInput.returnPressed.connect(self.onBtnRegName)
        layout.addWidget(self.nameInput, 1, 1)

        # 전 후 선택 라디오버튼
        self.radioGroupBox = QGroupBox('')
        layout.addWidget(self.radioGroupBox, 1, 2)

        self.radioBoxLayout = QHBoxLayout()
        self.radioGroupBox.setLayout(self.radioBoxLayout)

        self.radioBtnBefore = QRadioButton('전', self)
        self.radioBtnBefore.clicked.connect(self.onRadioBtn)
        self.radioBoxLayout.addWidget(self.radioBtnBefore, alignment=QtCore.Qt.AlignTop)
        self.radioBtnAfter = QRadioButton('후', self)
        self.radioBtnAfter.clicked.connect(self.onRadioBtn)
        self.radioBoxLayout.addWidget(self.radioBtnAfter, alignment=QtCore.Qt.AlignTop)
        self.radioBtnDefault = QRadioButton('지정안함', self)
        self.radioBtnDefault.clicked.connect(self.onRadioBtn)
        self.radioBoxLayout.addWidget(self.radioBtnDefault, alignment=QtCore.Qt.AlignTop)
        self.radioBtnDefault.setChecked(True)
        self.radioBoxLayout.addStretch()


        self.btnPreview = QPushButton('파일명 등록')
        self.btnPreview.setToolTip('텍스트 박스에 입력된 텍스트가 파일명의 일부로 저장됩니다.')
        self.btnPreview.clicked.connect(self.onBtnRegName)
        layout.addWidget(self.btnPreview, 2, 0)

        self.fileNamePreview = QLabel() # 변환된 파일명의 미리보기
        layout.addWidget(self.fileNamePreview, 2, 1)

        self.picPreview = QLabel('사진 미리보기')
        self.picPreview.resize(540, 540)
        self.picPreview.setAlignment(QtCore.Qt.AlignCenter)
        self.picPreview.setPixmap(QtGui.QPixmap(self.currentPreview).scaled(540, 360))#, QtCore.Qt.KeepAspectRatio))
        layout.addWidget(self.picPreview, 2, 2, -1, -1)

        self.btnNextAddr = QPushButton('다음 장소 보기')
        self.btnNextAddr.setToolTip('같은 장소에서 찍힌 사진들은 상기 등록된 이름 형식으로 저장되고, 다른 장소에서 찍은 사진을 불러옵니다.')
        self.btnNextAddr.clicked.connect(self.onBtnShowNextAddr)
        layout.addWidget(self.btnNextAddr, 3, 0)

        self.finalResult = QLabel()
        layout.addWidget(self.finalResult, 3, 1)

        self.btn2Change = QPushButton('완료 및 이름 바꾸기')
        self.btn2Change.setToolTip('현재 폴더에서의 모든 작업을 종료하고 설정한 대로 이름을 변경합니다.')
        self.btn2Change.clicked.connect(self.onBtnChange)
        layout.addWidget(self.btn2Change, 4, 0, -1, 2)

        self.btnNextPicSameAddr = QPushButton('같은 장소 다른 사진 보기')
        self.btnNextPicSameAddr.setToolTip('같은 장소에서 찍힌 사진 중 다른 사진으로 미리보기를 교체합니다.')
        self.btnNextPicSameAddr.clicked.connect(self.onBtnNextThumbnail)
        layout.addWidget(self.btnNextPicSameAddr, 4, 2)


    @staticmethod
    def find_same_loc(dctData, loc) -> list[str]:
        return [key for key, value in dctData.items() if value == loc]

    def point_file_name(self) -> str or None:
        res = None
        try:
            lstNameToBeRemoved = self.find_same_loc(self.dctNameStorage, self.dctNameStorage[self.currentPreview])
            for target in lstNameToBeRemoved:
                self.setProcessedName.add(target)

            for target in self.lstOldName:
                if target not in self.setProcessedName:
                    res = target

        except AttributeError as ae:
            print(ae)

        return res


    # 추적 흔적을 남긴다, 추후 조회하여 다시 리뷰할 것인지 판단할 때 사용.
    def store_preview_history(self, name, storeEntireLoc=True):
        self.setProcessedName.add(name)
        if storeEntireLoc:
            self.setProcessedAddr.add(self.dctNameStorage[name])

    # 사진과 설명을 업데이트한다.
    def update_pixmap(self, srcName):
        self.labelLoc4Preview.setText(f'사진 위치: {self.dctNameStorage[srcName]}')
        self.picPreview.setPixmap(QtGui.QPixmap(srcName).scaled(540, 360))# , QtCore.Qt.KeepAspectRatio))
    
    def onBtnRegName(self):
        self.lstTempNamePool = [] # 장소 단위 리스트 초기화

        oldFileName = self.currentPreview

        self.store_preview_history(oldFileName)

        text = self.nameInput.text()
        newFileName = self.clsNc.get_final_name(oldFileName, text)
        print(f'등록됨 {newFileName =} ')

        self.dctLocation2Details[self.dctNameStorage[oldFileName]] = newFileName # {주소: 바뀔 이름}
        
        self.fileNamePreview.setText(f'{newFileName} (으)로 등록되었습니다.')

    def onBtnShowNextAddr(self):
        self.lstTempNamePool = [] # 장소 단위 리스트 초기화

        oldFileName = self.point_file_name()
        if not oldFileName:
            QMessageBox.warning(self, '경고', '마지막 장소입니다')
            return

        self.fileNamePreview.setText('')
        self.update_pixmap(oldFileName)


    def onBtnNextThumbnail(self):
        self.store_preview_history(self.currentPreview, storeEntireLoc=False)
        currentLoc = self.dctNameStorage[self.currentPreview]
        if not self.lstTempNamePool: #이 리스트가 비어있으면 업데이트
            for oldName, roadAddr in self.dctNameStorage.items():
                if currentLoc == roadAddr:
                    self.lstTempNamePool.append(oldName)
            print('temp list updated')

        self.tempImgPreview = self.lstTempNamePool.pop()

        self.update_pixmap(self.tempImgPreview)

        # 라디오버튼 기억
        if self.tempImgPreview in self.dctOldName2BeforeAfter:
            if self.dctOldName2BeforeAfter[self.tempImgPreview] == '전':
                self.radioBtnBefore.setChecked(True)
            elif self.dctOldName2BeforeAfter[self.tempImgPreview] == '후':
                self.radioBtnAfter.setChecked(True)
        else:
            self.radioBtnDefault.setChecked(True)

    #TODO: 리팩토링좀
    def onBtnChange(self):
        # 현재 커서의 지정 이름 저장
        oldFileName = self.currentPreview
        self.dctLocation2Details[self.dctNameStorage[oldFileName]] = self.clsNc.get_final_name(oldFileName, self.nameInput.text())
        while True: # 디테일을 전부 다 지정하지 않고 넘어가는 경우
            oldFileName = self.point_file_name()
            if not oldFileName:
                break
            self.dctLocation2Details[self.dctNameStorage[oldFileName]] = self.clsNc.get_final_name(oldFileName, '') # {주소: 바뀔 이름(초기화)}

        if self.clsNc.change_name_on_btn(self.dctLocation2Details, self.dctOldName2BeforeAfter):
            QMessageBox.information(self, '알림', '처리가 완료되었습니다.')
        else:
            QMessageBox.warning(self, '경고', '이미 완료되었습니다.')

        QMessageBox.information(self, '알림', '프로그램을 종료하고 퇴근합니다.')
        sys.exit()


    #선택한 라디오 버튼에 맞춰서 {현 썸네일 이름: 전.후 정보}를 업데이트한다.
    def onRadioBtn(self):
        if self.radioBtnBefore.isChecked():
            print(f'{self.tempImgPreview = }, 전')
            self.dctOldName2BeforeAfter[self.tempImgPreview] = '전'
        elif self.radioBtnAfter.isChecked():
            print(f'{self.tempImgPreview = }, 후')
            self.dctOldName2BeforeAfter[self.tempImgPreview] = '후'
        elif self.radioBtnDefault.isChecked():
            print(f'{self.tempImgPreview = }, 전/후정보 제거')
            try:
                del self.dctOldName2BeforeAfter[self.tempImgPreview]
            except AttributeError as ae:
                print(ae)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    screen = GongikWidget()
    screen.resize(540, 100)
    screen.show()
 
    sys.exit(app.exec_())