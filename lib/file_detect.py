# 현재 위치에서 파일 목록을 찾아서 보유한다.

from . import utils
from .log_gongik import Logger


class FileDetector(object):
    __dctArg2Instance: dict = {}
    __setIsInit: set = set()

    def __new__(cls, targetDir=utils.extract_dir(), *args):
        if targetDir in cls.__dctArg2Instance:
            return cls.__dctArg2Instance[targetDir]

        cls._instance: FileDetector = super().__new__(cls) 
        cls.__dctArg2Instance[targetDir] = cls._instance

        cls.log = Logger()
        cls.log.INFO(cls._instance, f'{targetDir = }')
        return cls._instance

    def __init__(self, targetDir=utils.extract_dir(), *args):
        cls = type(self)
        if targetDir not in cls.__setIsInit:
            self.lstPic: list[str] = utils.extract_file_name_sorted(targetDir)
            self.log.INFO(f'file list in {targetDir}\n')
            self.log.INFO('list:', self.lstPic)

            cls.__setIsInit.add(targetDir)

    @property
    def file_list(self):
        return self.lstPic


if __name__ == '__main__':
    dt = FileDetector()


