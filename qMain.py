# v1.3
# 다음 보는 버튼이 사진에 가려서 안보임 레이아웃 조정 완료(v1.3.1)
# 같은 위치에 찍힌 사진 수량 보여주기 -완료(v1.3.1)
# 스펙시트 보여주기(v1.3.1)
# 시간순으로 정렬, 같은 시간대에 찍힌거면 맨 처음 지정한 위치로 통일 - 완료(v1.3.2)

# v1.4
# 파일이 없으면 지정된 경로에서 파일을 옮겨옴(ppadb 이용)(v1.4.0)
# 같은 폴더에 exif정보가 없는 사진이 있으면 예외처리를 못하던 문제 수정(v1.4.1)
# 연결 전 adb 서버를 가동하여 USB footprint를 pc에 저장한다.(v1.4.2)
# 충돌 있는 키보드 단축키 변경(v1.4.3)
# Logger 추가(v1.4.3)
# 1호차 구분이 제대로 되지 않는 버그 수정(v1.4.4)
# 안내장부착 버튼 추가(v1.4.5)

# v1.5
# 하단 상태바에 현재 진행 중인 작업 표시(v1.5.0) --> cancelled
# 로딩 중일 시 알려주는 다이얼로그와 프로그레스 바를 띄워준다(v1.5.0)
# 카카오API로 주소를 받아온다(v1.5.1)
# 계고장 부착(v1.5.1)
# 파일명 미리보기 기능 추가(v1.5.2)
# 사진 상세에서 제목이 가운데 정렬 되지 않는 버그 수정(v1.5.2)
# QLineEdit입력 시 즉시 미리보기 업데이트되도록 수정(v1.5.3)
# 호차 관련 오류 수정(v1.5.4)
# 파일 옮기기에 프로그레스 바 표시 (v1.5.5)
# 파일 이름 변경에 프로그레스 바 표시 -> QTimer 이용 (v1.5.5)
# GPS 정보 보낼 때 바로 보내지 않고 인터넷 연결을 확인하고 보내도록 수정(v1.5.6)

# 파일을 옮겨온 후에 다시 실행할 필요 없이 바로 초기화하도록 수정(v1.6.0b)
# 최초 실행시 유의사항 띄우기(v1.6.1)
# adb 연결 체크 시 따로 쉘을 열지 않고도 실행하도록 수정(v1.6.2)
# 좀 더 다양한 에러 사항을 유저에게 전달하여 대처할 수 있도록 안내 세분화(v1.6.3)
# 긴급패치) 오프라인 상황에서 Undefined로 나오는 문제 수정 (v1.6.4)
# 긴급패치) 주소 없는 이미지가 엉뚱한 주소로 나오는 문제 수정 (v1.6.5)
# keyError 예외처리하여 크래시 나지 않도록 수정(v1.6.6)

# 주소 수정 가능하도록 기능 추가(v1.7.0b)
# 주소 수정을 세부사항 수정으로 수정, 그 외 코드 간소화(v1.7.1b)
# 사진을 클릭하면 열리는 기능 추가(v1.7.1b)

# api 기능 추가(v2.0)
# 버전 정보 판별 기능 추가 (v2.0.1b)
# 최신 버전 다운로드 기능 추가(v2.0.1b)
# 버튼(수거 전, 수거 후) 추가(v2.0.1)

# MVC구조로 수정(파일 미리보기 구조). 양방향 탐색 기능 추가(v2.1.0)
# MVC구조로 전면 수정(파일 속성 데이터), '더 자세히'선택권 부여 (v2.1.1)
# 보정된 위치로 표시되도록 수정(v2.1.2)
# 위치 병합 및 수정 기능 추가(v2.2.0b)
# 최종 실행 전 묻는 팝업창 띄우기(v2.2.0b)
# 위치 추가 기능 추가 및 안정화(v2.2.1)
# 버그fix) 1개의 위치군만 남아있는 상태에서 모든 사진을 선택 후 다른데로 옮기면 크래시, 추후 리팩토링 예정(v2.2.2)
# 기능추가) 사진 일괄 선택 기능 -> 해당 다이얼로그의 취지와 맞지 않아서 취소

# 기능 수정) 현재 커서는 건드리지 않도록 아예 렌더링 시 빼버림(v2.2.3)
# 다운로드 피드백 시각화 (v2.2.4)

# 기능 추가) 초기 경로 설정 추가, 초기 로딩화면에서 업데이트 내역 알림

# pip3 install pyproj pillow requests haversine pyinstaller pyqt5 pure-python-adb paramiko pytesseract

import sys
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import (
    Qt,
)
from PyQt5.QtWidgets import (
    QApplication, 
    QGridLayout, 
    QLabel, 
    QAction,
    QMessageBox, 
    QPushButton, 
    qApp
)
from lib.file_copy import BridgePhone

import lib.utils as utils
import qWordBook as const
from lib.file_property import FileProp
from lib.queue_order import MstQueue
from lib.version_info import VersionTeller
from lib.log_gongik import Logger
from lib.file_detect import FileDetector
from lib.base_folder import WorkingDir
from qMainWidget import GongikWidget
from qVersionDialog import VersionDialog
from qDraggable import ( #custom qobjects
    QDialog, 
    QMainWindow, 
    QWidget,
)
from qDialog import (
    ProgressDialog,
    ProgressDialog4Start,
    InitInfoDialogue,
    FolderDialog
)
from qWrapper import (
    catch_except,
    elapsed
)
from qRestoreDialog import RestoreDialog

'''
exe 빌드하기
pyinstaller -F --clean qMain.spec
pyinstaller -w -F --clean --add-data "db/addr.db;./db" --add-data "img/frog.ico;./img" --add-data "img/developer.ico;./img" --add-data "img/exit.ico;./img" --add-data "img/final.ico;./img" --add-data "platform-tools;./platform-tools" --add-data "tesseract-ocr;./tesseract-ocr" --icon=img/final.ico qMain.py
'''

VERSION_INFO = '(release-beta)gongik_v2.4.4'

INSTRUCTION = '''현재 디렉토리에 처리할 수 있는 파일이 없습니다.
연결된 핸드폰에서 금일 촬영된 사진을 불러옵니다.

**주의사항**
파일 전송 전 핸드폰을 "잠금이 해제된 상태"로 유지하세요.
'''


class Gongik(QMainWindow):
    def __init__(self):
        self.log = Logger()
        self.log.INFO('')
        self.log.INFO('')
        self.log.INFO('')
        self.log.INFO('==============program started=================')
        self.log.INFO('version:', VERSION_INFO)
        self.log.INFO('==============program started=================')
        self.log.INFO('')
        self.log.INFO('')
        self.log.INFO('')


        self.progressDlg = ProgressDialog4Start('기본 정보를 가져오는 중')
        self.progressDlg.show()
        self.progressDlg.mark_progress(10)

        super().__init__()

        self.title = 'Gongik'
        self.main_icon_path = utils.resource_path(const.IMG_FROG)
        self.final_icon_path = utils.resource_path(const.IMG_FROG2)
        self.exit_icon_path = utils.resource_path(const.IMG_EXIT)
        self.dev_icon_path = utils.resource_path(const.IMG_DEV)

        self.progressDlg.mark_progress(20, '로딩 중')

        self.folderDialog = FolderDialog() # 파일 경로 확인 다이얼로그
        self.folderDialog.exec_()
        self.targetFolder = WorkingDir(
            self.folderDialog.path, 
            utils.get_relative_path(self.folderDialog.path)
        )
        self.log.INFO(self.targetFolder)

        self.clsFD = FileDetector(self.targetFolder.rel_path) # '.'는 초기 파일 체크용
        self.files = self.clsFD.file_list

        self.progressDlg.mark_progress(30, '파일 검사 중')
        
        if not self.files:
            self.log.WARNING('current folder empty')
            if not self._get_files_fm_phone():
                sys.exit()

        self.progressDlg.mark_progress(80, '파일 분석 중')

        self._init_ui()
        self._init_main_widget()
        
        self.progressDlg.mark_progress(100, '무결성 검사 중', True)

        self.progressDlg.close()
        del self.progressDlg

    def _init_main_widget(self):
        # 메인 위젯 설정
        qw = GongikWidget(self.targetFolder.abs_path)
        self.setCentralWidget(qw)

    def _get_files_fm_phone(self) -> bool:
        failDlg = InitInfoDialogue(INSTRUCTION, btn=('확인', '다음에'))
        failDlg.exec_()

        self.progressDlg.show()

        if not failDlg.answer:
            QMessageBox.information(self, 'EXIT_PLAIN', const.MSG_INFO['EXIT_PLAIN'])
            return False

        from lib.file_copy import BridgePhone
        clsBP = BridgePhone()
        self._handle_ADB_failure(clsBP)

        self.progressDlg.mark_progress(50, '파일 복사 중')

        if not clsBP.transfer_files():
            QMessageBox.information(self, 'TRANSFER_FAIL', const.MSG_INFO['TRANSFER_FAIL'])
            return False
        
        self.progressDlg.mark_progress(70, '이상 감지 중')

        # QMessageBox.information(self, 'TRANSFER_SUCCESS', const.MSG_INFO['TRANSFER_SUCCESS'])

        return True

    def _handle_ADB_failure(self, clsBridgePhone: BridgePhone):
        if not clsBridgePhone.connected:
            self._pop_warn_msg('CONNECTION_ERROR')

        if not clsBridgePhone.executable:
            self._pop_warn_msg('MULTI_CONNECTION_ERROR')

        if not clsBridgePhone.files:
            self._pop_warn_msg('EMPTY_FILE_ERROR')


    def _pop_warn_msg(self, code):
        self.log.WARNING(repr(const.MSG_WARN[code]))
        QMessageBox.warning(self, code, const.MSG_WARN[code])
        sys.exit()

    def _init_ui(self):
        # 상단 정보 설정
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon(self.main_icon_path))
        self.setStyleSheet(const.QSTYLE_SHEET)
        self.setWindowFlags(Qt.FramelessWindowHint)

        #메뉴 바 - progMenu - Exit
        exitAction = QAction(QIcon(self.exit_icon_path), '퇴근하기', self)
        exitAction.setShortcut(const.MSG_SHORTCUT['EXIT'])
        exitAction.setStatusTip(const.MSG_TIP['EXIT'])
        exitAction.triggered.connect(qApp.quit)

        # (베타) 이미지에서 텍스트 추출
        recommendAction = QAction(QIcon(self.dev_icon_path), '텍스트 추출(베타)', self)
        recommendAction.setShortcut(const.MSG_SHORTCUT['RECOMMEND'])
        recommendAction.setStatusTip(const.MSG_TIP['RECOMMEND'])
        recommendAction.triggered.connect(self.onModalRecommend)

        # 작업 복구 메뉴
        restoreAction = QAction(QIcon(self.dev_icon_path), '복구하기', self)
        restoreAction.setShortcut(const.MSG_SHORTCUT['RESTORE'])
        restoreAction.setStatusTip(const.MSG_TIP['RESTORE'])
        restoreAction.triggered.connect(self.onModalRestore)

        #메뉴 바 - info
        infoAction = QAction(QIcon(self.dev_icon_path), '프로그램 정보', self)
        infoAction.setShortcut(const.MSG_SHORTCUT['INFO'])
        infoAction.setStatusTip(const.MSG_TIP['INFO'])
        infoAction.triggered.connect(self.onModalDeveloperInfo)

        # 참고 정보 표시
        checkAction = QAction(QIcon(self.main_icon_path), '위치 목록 확인', self)
        checkAction.setShortcut(const.MSG_SHORTCUT['LIST'])
        checkAction.setStatusTip(const.MSG_TIP['LIST'])
        checkAction.triggered.connect(self.onModalAddrInfo)

        updateAction = QAction(QIcon(self.final_icon_path), '업데이트 확인', self)
        updateAction.setShortcut(const.MSG_SHORTCUT['UPDATE'])
        updateAction.setStatusTip(const.MSG_TIP['UPDATE'])
        updateAction.triggered.connect(self.onModalUpdateApp)

        self.statusBar()

        menu = self.menuBar()
        menu.setNativeMenuBar(False)
        progMenu = menu.addMenu('&실행')
        additionalMenu = menu.addMenu('&정보')
        
        progMenu.addAction(restoreAction)
        progMenu.addAction(recommendAction)
        progMenu.addAction(exitAction)
        additionalMenu.addAction(infoAction)
        additionalMenu.addAction(checkAction)
        additionalMenu.addAction(updateAction)

        self.show()

    def onModalRestore(self):
        # rdlg = RestoreDialog()
        # rdlg.exec_()
        InitInfoDialogue('프로그램 실행 초기 체크박스에 표시하고 진행하면 접근할 수 있습니다.', ('확인', )).exec_()

    def onModalDeveloperInfo(self):
        dlg = DeveloperInfoDialog()
        dlg.exec_()

    def onModalAddrInfo(self):
        alg = AddrInfoDialog()
        alg.exec_()

    def onModalUpdateApp(self):
        vlg = VersionDialog()
        vlg.exec_()

    def onModalRecommend(self):
        rlg = RecommendDialog()
        rlg.exec_()

class DeveloperInfoDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.log = Logger()
        self.log.INFO('Developer Info Dialog')

        self.title = '프로그램 정보'
        self.iconPath = utils.resource_path(const.IMG_DEV)

        self.setupUI()

    def setupUI(self):
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon(self.iconPath))
        self.setStyleSheet(const.QSTYLE_SHEET_POPUP)
        self.setWindowFlags(Qt.FramelessWindowHint)

        label0 = QLabel('버전:')
        label0.setAlignment(Qt.AlignTop)
        label0_a = QLabel(f'{VERSION_INFO}')
        label1 = QLabel('개발자:')
        label1.setAlignment(Qt.AlignTop)
        label1_a = QLabel('안태영(Collin Ahn)')
        label2 = QLabel('연락처:')
        label2.setAlignment(Qt.AlignTop)
        label2_a = QLabel('collinahn@gmail.com')
        label3 = QLabel('참고사항:')
        label3.setAlignment(Qt.AlignTop)
        label3_a = QLabel(const.PROGRAM_INFO)
        label4 = QLabel('License:')
        label4.setAlignment(Qt.AlignTop)
        label4_a = QLabel('MIT License \nCopyright (c) 2021 Collin Ahn')

        self.pushBtnExit= QPushButton('확인')
        self.pushBtnExit.clicked.connect(self.onBtnClicked)

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(label0, 0, 0)
        layout.addWidget(label0_a, 0, 1)
        layout.addWidget(label1, 1, 0)
        layout.addWidget(label1_a, 1, 1)
        layout.addWidget(label2, 2, 0)
        layout.addWidget(label2_a, 2, 1)
        layout.addWidget(label3, 3, 0)
        layout.addWidget(label3_a, 3, 1)
        layout.addWidget(label4, 4, 0)
        layout.addWidget(label4_a, 4, 1)
        layout.addWidget(self.pushBtnExit, 4, 2)

    def onBtnClicked(self):
        self.log.INFO('Developer Info Dialog closed')
        self.close()


class AddrInfoDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.log = Logger()
        self.log.INFO('Addr Info Dialog')

        self.title = '사진 상세'
        self.iconPath = utils.resource_path(const.IMG_FROG)

        self.setupUI()

    def setupUI(self):
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon(self.iconPath))
        self.setStyleSheet(const.QSTYLE_SHEET_POPUP)
        self.setWindowFlags(Qt.FramelessWindowHint)

        mq = MstQueue()

        lstNameAddrTime = [(
            QLabel(' 파일 이름'), 
            QLabel(' 도로명 주소'),
            QLabel(' 지번 주소'),
            QLabel(' '),
            QLabel('처리 위치'), 
            QLabel('촬영 시각'), 
            QLabel('최종 이름'),
            QLabel('현재 커서'))]
        for label in lstNameAddrTime[-1]:
            label.setAlignment(Qt.AlignCenter)

        # QLabel 객체 삽입
        for name in FileProp.get_names():
            fProp = FileProp(name)
            lstNameAddrTime.append((
                QLabel(f'{fProp.name}'),
                QLabel(f'{fProp.locationFmDB}'),
                QLabel(f'{fProp.locationFmAPI}'),
                QLabel('->'),
                QLabel(f'{fProp._locationDB}'),
                QLabel(f'{fProp.time.strftime("%Y-%m-%d %H:%M:%S")}'),
                QLabel(f'{fProp.final_full_name}'),
                QLabel('<<') if mq.current_preview.current_preview.name == fProp.name else QLabel('')
            ))
            
        lstNameAddrTime.sort(key=lambda x: x[1].text()) #주소 기준 정렬

        # 확인버튼
        self.pushButton1= QPushButton('확인')
        self.pushButton1.clicked.connect(self.onBtnClicked)

        layout = QGridLayout()

        for gridLoc, tplNameAddrTime in enumerate(lstNameAddrTime):
            for idx, data in enumerate(tplNameAddrTime):
                layout.addWidget(data, gridLoc, idx)

        layout.addWidget(self.pushButton1, len(lstNameAddrTime)+1, 0, -1, -1)

        self.setLayout(layout)

    def onBtnClicked(self):
        self.log.INFO('Addr Info Dialog closed')
        self.close()


class RecommendDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.log = Logger()
        self.log.INFO('Addr Info Dialog')

        self.title = '텍스트 추천'
        self.iconPath = utils.resource_path(const.IMG_DEV)

        self.setupUI()

    def setupUI(self):
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon(self.iconPath))
        self.setStyleSheet(const.QSTYLE_SHEET_POPUP)
        self.setWindowFlags(Qt.FramelessWindowHint)

        mq = MstQueue()
        fProp = mq.current_preview.current_preview

        from lib.file_translate import ImageOCR

        labelName = QLabel('파일 이름')
        labelName.setAlignment(Qt.AlignTop)
        dataName = QLabel(f'{fProp.name}')
        labelTxt = QLabel('추출 텍스트:')
        labelTxt.setAlignment(Qt.AlignTop)
        # dataTxt = QLabel(f'{ImageOCR(fProp.name).text}')
        dataTxt = QLabel('개발 중인 기능입니다.')

        self.pushBtnExit= QPushButton('확인')
        self.pushBtnExit.clicked.connect(self.onBtnClicked)

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(labelName, 0, 0)
        layout.addWidget(dataName, 0, 1)
        layout.addWidget(labelTxt, 1, 0)
        layout.addWidget(dataTxt, 1, 1)
        layout.addWidget(self.pushBtnExit, 4, 2)

    def onBtnClicked(self):
        self.log.INFO('Addr Info Dialog closed')
        self.close()



if __name__ == '__main__':
    app = QApplication(sys.argv)

    ex = Gongik()

    try:
        sys.exit(app.exec_())
    except Exception as e:
        from qDialog import InitInfoDialogue
        from lib.new_mail_service import SendMail2Admin
        import traceback
        InitInfoDialogue('예기치 않은 에러가 발생하였습니다.\n로그 보내기를 누르면 로그를 수집합니다.\n파일 이동 중 발생한 오류라면 수동으로 옮기고 프로그램을 다시 실행해 주세요.',('로그 보내기', '취소')).exec_()
        sm = SendMail2Admin()
        sm.send_mail(
            sm.create_mail(
                title='System Malfunction',
                html_contents=f'{traceback.format_exc()}<br><br>{e}<br>System Failed Due to Unexpected Exception'
            )
        )