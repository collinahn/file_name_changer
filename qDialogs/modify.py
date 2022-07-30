from sys import prefix
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import (
    Qt,
)
from PyQt5.QtWidgets import (
    QApplication, 
    QGridLayout,
    QVBoxLayout,
    QHBoxLayout,
    QLabel, 
    QGroupBox,
    QPushButton, 
    QLineEdit
)

import lib.utils as utils
from qDialogs.info_dialog import InitInfoDialogue
import qWordBook as const
from lib.file_property import FileProp
from lib.queue_order import MstQueue
from lib.log_gongik import Logger
from lib.word_settings import ( 
    WordSettings,
    IncompleteValueError
)
from qDraggable import ( #custom qobjects
    QDialog, 
    QMainWindow, 
    QWidget,
)

class QLineEdit(QLineEdit):
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(50)
        self.setMinimumWidth(240)

class ModifyButtonTextDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.log = Logger()
        self.log.INFO('Modify Button Dialog')

        self.title = '버튼 편집'
        self.iconPath = utils.resource_path(const.IMG_DEV)
        self.word_settings = WordSettings()
        self.base_data = self.word_settings.load_data()

        self.prefix_input_pool: list[tuple[str]] = []
        self.suffix_input_pool: list[tuple[str]] = []

        self.setup_ui()
        self._fill_in_text()

    def setup_ui(self):
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon(self.iconPath))
        self.setStyleSheet(const.QSTYLE_SHEET_POPUP)
        self.setWindowFlags(Qt.FramelessWindowHint)

        layout = QVBoxLayout()

        label = QLabel('버튼의 표시 이름은 중복될 수 없습니다.\n버튼의 표시 이름을 지정하지 않는 경우 기본값으로 대체됩니다.')
        layout.addWidget(label)

        prefix_group = QGroupBox('prefix')
        prefix_group_layout = QGridLayout()
        prefix_group.setLayout(prefix_group_layout)

        suffix_group = QGroupBox('suffix')
        suffix_group_layout = QGridLayout()
        suffix_group.setLayout(suffix_group_layout)

        layout.addWidget(prefix_group)
        layout.addWidget(suffix_group)

        for idx, _ in enumerate(self.base_data.get('prefix')):
            self.prefix_input_pool.append(
                (QLineEdit(), QLineEdit())
            )
            self.prefix_input_pool[-1][0].textChanged.connect( self.on_input_btn_text )
            self.prefix_input_pool[-1][1].setEnabled(False)
            prefix_group_layout.addWidget(self.prefix_input_pool[-1][0], idx, 0)
            prefix_group_layout.addWidget(self.prefix_input_pool[-1][1], idx, 1)


        for idx, _ in enumerate(self.base_data.get('suffix')):
            self.suffix_input_pool.append(
                (QLineEdit(), QLineEdit())
            )
            self.suffix_input_pool[-1][0].textChanged.connect( self.on_input_btn_text )
            self.suffix_input_pool[-1][1].setEnabled(False)
            suffix_group_layout.addWidget(self.suffix_input_pool[-1][0], idx, 0)
            suffix_group_layout.addWidget(self.suffix_input_pool[-1][1], idx, 1)

        self.btn_group = QGroupBox()
        self.btn_group_layout = QHBoxLayout()
        self.btn_group.setLayout(self.btn_group_layout)
        self.btn_group.setStyleSheet('QGroupBox {border:0px}')
        layout.addWidget(self.btn_group)

        self.btn_modify = QPushButton('변경')
        self.btn_modify.setMinimumHeight(50)
        self.btn_modify.clicked.connect(self.on_btn_modify)
        self.btn_init = QPushButton('초기화')
        self.btn_init.setMinimumHeight(50)
        self.btn_init.clicked.connect(self.on_btn_init)
        self.btn_cancel = QPushButton('나가기')
        self.btn_cancel.setMinimumHeight(50)
        self.btn_cancel.clicked.connect(self.on_btn_cancel)

        self.btn_group_layout.addWidget(self.btn_modify)
        self.btn_group_layout.addWidget(self.btn_init)
        self.btn_group_layout.addWidget(self.btn_cancel)
        self.setLayout(layout)

    def _fill_in_text(self):
        self.word_settings = WordSettings()
        self.base_data = self.word_settings.load_data()

        for idx, (name, value) in enumerate(self.prefix_input_pool):
            name: QLineEdit
            value: QLineEdit
            name.setPlaceholderText(f'버튼의 표시 이름({self.base_data.get("prefix")[idx][0]})')
            value.setPlaceholderText(f'실제 값({self.base_data.get("prefix")[idx][1]})')
        
        for idx, (name, value) in enumerate(self.suffix_input_pool):
            name: QLineEdit
            value: QLineEdit
            name.setPlaceholderText(f'버튼의 표시 이름({self.base_data.get("suffix")[idx][0]})')
            value.setPlaceholderText(f'실제 값({self.base_data.get("suffix")[idx][1]})')

    def _wipe_all_input(self):
        for (name_input, value_input) in self.prefix_input_pool + self.suffix_input_pool:
            name_input: QLineEdit
            value_input: QLineEdit
            name_input.clear()
            value_input.clear()

    def _no_blank_input(self, new_data: dict[str, list[tuple[str, str]]]) -> bool:
        for (name, _) in new_data.get('prefix'):
            if name.count(' ') == len(name):
                return False
        for (name, _) in new_data.get('suffix'):
            if name.count(' ') == len(name):
                return False 
        return True
    
    def _no_input_overlap(self, new_data: dict[str, list[tuple[str, str]]]) -> bool:
        inspect_pool = []
        for (name, _) in new_data.get('prefix'):
            if name in inspect_pool:
                return False
            inspect_pool.append(name)
        
        inspect_pool.clear()
        for (name, _) in new_data.get('suffix'):
            if name in inspect_pool:
                return False
            inspect_pool.append(name)
        return True

    def _verify_input(self, new_data) -> bool:
        if self._no_blank_input(new_data) and self._no_input_overlap(new_data):
            return True
        return False

    def get_result_data(self) -> dict[str, list[tuple[str, str]]]:
        latest_prefix = self.base_data.get('prefix')
        latest_suffix = self.base_data.get('suffix')
        return {
            'prefix': [
                (name.text(), value.text()) if name.text() else latest_prefix[idx]
                for idx, (name, value) in enumerate(self.prefix_input_pool)
            ],
            'suffix': [
                (name.text(), value.text()) if name.text() else latest_suffix[idx]
                for idx, (name, value) in enumerate(self.suffix_input_pool)
            ]
        }

    def on_btn_modify(self):
        mod = InitInfoDialogue('입력한 내용을 기반으로 버튼의 설정값을 변경합니다.', ('예', '아니오'))
        mod.exec_()
        if not mod.answer:
            return

        new_data = self.get_result_data()
        self.log.INFO(f'change from {self.base_data} to {new_data}')
        if not self._verify_input(new_data):
            InitInfoDialogue('1. 중복된 이름이 있으면 안됩니다.\n2. 공백만으로 이름을 지정할 수 없습니다.', ('다시 시도',)).exec_()
            return
        
        try:
            self.word_settings.save_data(new_data)
            self._fill_in_text()
        except IncompleteValueError: # not saved
            InitInfoDialogue('입력값이 올바르지 않습니다.', ('예',)).exec_()
            return

        InitInfoDialogue('변경이 완료되었습니다. 프로그램 재시작시 변경된 내용이 반영됩니다.', ('확인',)).exec_()


    def on_btn_init(self):
        init = InitInfoDialogue('초기화를 진행하겠습니까?', ('예', '아니오'))
        init.exec_()
        if not init.answer:
            return

        self.word_settings = WordSettings()
        self.word_settings.initialize()
        self.base_data = self.word_settings.load_data()
        self._fill_in_text()
        self._wipe_all_input()
        self.log.INFO('initialized btn texts')

    def on_input_btn_text(self):
        target_input = self.sender()
        for (name_input, value_input) in self.prefix_input_pool + self.suffix_input_pool:
            if target_input == name_input and not name_input.text():
                value_input.setEnabled(False)
                return
            if name_input.text():
                value_input.setEnabled(True)

    def on_btn_cancel(self):
        self.log.INFO('Modify Button Dialog canceled')
        self.close()

            


if __name__ == '__main__':

    import sys
    app = QApplication(sys.argv)
    dlg = ModifyButtonTextDialog()
    # screen.resize(540, 100)
    dlg.show()
 
    sys.exit(app.exec_())