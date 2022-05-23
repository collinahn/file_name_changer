# 현재 위치에서 파일 목록을 찾아서 보유한다.

import os 

from . import utils
from .log_gongik import Logger


class FileDetector(object):
    __dctArg2Instance: dict = {}
    __setIsInit: set = set()

    def __new__(cls, targetDir:str=utils.extract_dir(), *args, **kwargs):
        if targetDir in cls.__dctArg2Instance:
            return cls.__dctArg2Instance[targetDir]

        cls._instance: FileDetector = super().__new__(cls) 
        cls.__dctArg2Instance[targetDir] = cls._instance

        cls.log = Logger()
        cls.log.INFO(cls._instance, f'{targetDir = }')
        return cls._instance

    def __init__(self, targetDir:str=utils.extract_dir(), isBackup:bool=False, *args):
        cls = type(self)
        if targetDir not in cls.__setIsInit:
            
            if isBackup:
                self.lstFile: list[str] = self.sort_out_backup_file(targetDir)
                self.log.INFO('detecting backup files in backup mode')
            else:
                self.lstFile: list[str] = self.sort_out_pics_name(targetDir)
                self.log.INFO('detecting pictures in normal mode')

            self.log.INFO(f'file list in {targetDir}\n')
            self.log.INFO('list:', self.lstFile)

            cls.__setIsInit.add(targetDir)

    @property
    def file_list(self):
        return self.lstFile

    # 파일 목록 추출
    # jpg 확장자가 아니거나 이미 바꾼 목록은 건들지 않음
    def sort_out_pics_name(self, dir='.') -> list:
        fileExt = utils.get_valid_file_ext()
        alreadyHandled = utils.get_handled_suffix()
        touchedFileName = utils.get_touched_char()

        files: list[str] = os.listdir(dir)
        return [
            _ for _ in files 
            if _.endswith(fileExt) # 확장자 거름
            and not _.startswith(alreadyHandled) # 이미 프로그램으로 다뤄진 파일들 거름
            and all(ch not in _ for ch in touchedFileName) # 수동으로 다뤄진 파일들 거름
        ]

    def sort_out_backup_file(self, dir='./.gongik/restore') -> list:
        '''
        형식에 맞는 파일들의 이름들을 가져온다.
        '''
        fileExt = ('gongik', )
        validHeaders = ('2', '6', )
        try:
            lstRes: list[str] = os.listdir(dir)
        except FileNotFoundError as fe:
            self.log.ERROR(fe)
            return []
        return sorted([
            _ for _ in lstRes
            if _.endswith(fileExt) and _.startswith(validHeaders) and _.count('_')==2
        ], reverse=True)

if __name__ == '__main__':
    dt = FileDetector('.')
    dt = FileDetector(f'{utils.extract_dir()}\\.gongik/restore', isBackup=True)


