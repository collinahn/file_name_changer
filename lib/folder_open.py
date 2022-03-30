# 실행이 끝나고 확인용으로 폴더를 오픈해주는 클래스

import webbrowser
from lib.log_gongik import Logger

class FolderOpener(object):
    def __init__(self) -> None:
        self.log = Logger()

    def open_file_browser(self, *, absPath):
        '''
        새 파일 브라우저를 띄운다
        '''
        if not webbrowser.open(f'file://{absPath}'):
            self.log.ERROR(f'failed to open file browser {absPath = }')
            return False

        self.log.INFO(f'opening {absPath} success')
        return True