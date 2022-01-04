from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtWidgets import (
    QMessageBox, QSizePolicy,
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
        self.currentPreview = self.lstOldName[0]

        if not self.dctNameStorage:
            QMessageBox.warning(self, '경고', f'현재 디렉토리\n({utils.extract_parent_dir()})\n에 처리할 수 있는 파일이 없습니다.')
            sys.exit()

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

        self.picPreview = QLabel('사진 미리보기')
        self.picPreview.resize(540, 540)
        self.picPreview.setAlignment(QtCore.Qt.AlignCenter)
        self.picPreview.setPixmap(QtGui.QPixmap(self.currentPreview).scaled(540, 360))#, QtCore.Qt.KeepAspectRatio))
        layout.addWidget(self.picPreview, 1, 2, -1, -1)

        self.btnPreview = QPushButton('파일명 등록')
        self.btnPreview.setToolTip('텍스트 박스에 입력된 텍스트가 파일명의 일부로 저장됩니다.')
        self.btnPreview.clicked.connect(self.onBtnRegName)
        layout.addWidget(self.btnPreview, 2, 0)

        self.labelPreview = QLabel()
        layout.addWidget(self.labelPreview, 2, 1)

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
        
        self.labelPreview.setText(f'{newFileName} (으)로 등록되었습니다.')

    def onBtnShowNextAddr(self):
        self.lstTempNamePool = [] # 장소 단위 리스트 초기화

        oldFileName = self.point_file_name()
        if not oldFileName:
            QMessageBox.warning(self, '경고', '마지막 장소입니다')
            return

        self.labelPreview.setText('')
        self.update_pixmap(oldFileName)


    def onBtnNextThumbnail(self):
        self.store_preview_history(self.currentPreview, storeEntireLoc=False)
        currentLoc = self.dctNameStorage[self.currentPreview]
        if not self.lstTempNamePool: #이 리스트가 비어있으면 업데이트
            for oldName, roadAddr in self.dctNameStorage.items():
                if currentLoc == roadAddr:
                    self.lstTempNamePool.append(oldName)
            print('temp list updated')

        tempPreview = self.lstTempNamePool.pop()

        self.update_pixmap(tempPreview)


    def onBtnChange(self):
        while True: # 디테일을 전부 다 지정하지 않고 넘어가는 경우
            OldFileName = self.point_file_name()
            if not OldFileName:
                break
            self.dctLocation2Details[self.dctNameStorage[OldFileName]] = self.clsNc.get_final_name(OldFileName, '') # {주소: 바뀔 이름(초기화)}

        if self.clsNc.change_name_on_btn(self.dctLocation2Details):
            QMessageBox.information(self, '알림', '변환이 완료되었습니다.')
        else:
            QMessageBox.warning(self, '경고', '이미 완료되었습니다.')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    screen = GongikWidget()
    screen.resize(540, 100)
    screen.show()
 
    sys.exit(app.exec_())