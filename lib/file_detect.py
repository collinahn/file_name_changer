# 현재 위치에서 파일 목록을 찾아서 보유한다.

import os 

from lib import utils
from lib.log_gongik import Logger


class Detector(object):
    __dctArg2Instance: dict = {}

    def __new__(cls, target_dir:str=utils.extract_dir(), *args, **kwargs):
        if target_dir in cls.__dctArg2Instance:
            return cls.__dctArg2Instance[target_dir]

        cls._instance: Detector = super().__new__(cls) 
        cls.__dctArg2Instance[target_dir] = cls._instance

        cls.log = Logger()
        cls.log.INFO(cls._instance, f'{target_dir = }')
        return cls._instance

    def __init__(self, *args, **kwargs):
        self._lst_file = []

    @property
    def file_list(self):
        return self._lst_file

    def sort_out(self):
        raise NotImplementedError()

class FileDetector(Detector):
    __setIsInit: set = set()

    def __init__(self, target_dir:str=utils.extract_dir(), *args):
        cls = type(self)
        if target_dir not in cls.__setIsInit:
            super().__init__()
            self._target_dir = target_dir
            self._lst_file: list[str] = self.sort_out(target_dir)
            self.log.INFO(f'pic files from {target_dir} detected')
            self.log.INFO('list:', self._lst_file)

            cls.__setIsInit.add(target_dir)

    def sort_out(self, dir='.') -> list:
        '''
        사진 파일 목록을 추출한다
        jpg 확장자가 아니거나 이미 수정이 된 파일들은 올리지 않는다.
        '''
        file_extention = utils.get_valid_file_ext()
        already_handled = utils.get_handled_suffix()

        files: list[str] = os.listdir(dir)
        return [
            file_name for file_name in files 
            if file_name.endswith(file_extention) # 확장자 거름
            and not file_name.startswith(already_handled) # 이미 프로그램으로 다뤄진 파일들 거름
            and not utils.is_korean_included(file_name)  # 수동으로 다뤄진 파일들 거름
        ]

    def refresh(self):
        self._lst_file = self.sort_out(self._target_dir)
        self.log.INFO(f'pic files from {self._target_dir} refreshed')
        self.log.INFO('list:', self._lst_file)
        
class BackupFileDetector(Detector):
    backup_file_dir = f'{utils.extract_dir()}/.gongik/restore'

    def __new__(cls, *args, **kwargs):
        return super().__new__(BackupFileDetector, cls.backup_file_dir)

    def __init__(self, *args, **kwargs):
        super().__init__()
        self._lst_file: list[str] = self.sort_out()
        self.log.INFO(f'backup files from {self.backup_file_dir} detected')
        self.log.INFO('list:', self._lst_file)

    def sort_out(self) -> list:
        '''
        형식에 맞는 백업 폴더 내부의 파일 이름들을 가져온다.
        '''
        fileExt = ('gongik', )
        validHeaders = ('2', '6', )
        try:
            lstRes: list[str] = os.listdir(self.backup_file_dir)
        except FileNotFoundError as fe:
            self.log.ERROR(fe)
            return []
        return sorted([
            _ for _ in lstRes
            if _.endswith(fileExt) and _.startswith(validHeaders) and _.count('_')==2
        ], reverse=True)


class LogFileDetector(Detector):
    log_file_dir = f'{utils.extract_dir()}/.gongik'

    def __new__(cls, *args, **kwargs):
        return super().__new__(LogFileDetector, cls.log_file_dir)

    def __init__(self, *args, **kwargs):
        super().__init__()
        self._lst_file: list[str] = self.sort_out()
        self.log.INFO(f'log files from {self.log_file_dir} detected')
        self.log.INFO('list:', self._lst_file)

    def sort_out(self):
        '''
        형식에 맞는 로그 폴더 내부의 파일 이름들을 가져온다.
        '''
        validHeaders = ('gongik', )
        try:
            lstRes: list[str] = os.listdir(self.log_file_dir)
        except FileNotFoundError as fe:
            self.log.ERROR(fe)
            return []
        return sorted([
            _ for _ in lstRes
            if _.startswith(validHeaders)
        ])
        


if __name__ == '__main__':
    dt = FileDetector('.')
    dt = FileDetector(f'{utils.extract_dir()}')

    bf = BackupFileDetector()
    lf = LogFileDetector()

