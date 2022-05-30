# 파일/폴더를 오픈해주는 클래스

import webbrowser
from lib.log_gongik import Logger

class FolderOpener(object):
    def __init__(self) -> None:
        self.log = Logger()

    def open_file_browser(self, *, abs_path):
        '''
        새 파일 브라우저를 띄운다
        '''
        if not webbrowser.open(f'file://{abs_path}'):
            self.log.ERROR(f'failed to open file browser {abs_path = }')
            return False

        self.log.INFO(f'opening {abs_path} success')
        return True