# 현재 위치에서 파일 목록을 찾아서 보유한다.

from . import utils


class FileDetector(object):
    __dctArg2Instance: dict = {}
    __setIsInit: set = set()

    def __new__(cls, targetDir=utils.extract_dir(), *args):
        if targetDir in cls.__dctArg2Instance:
            return cls.__dctArg2Instance[targetDir]

        cls._instance: FileDetector = super().__new__(cls) 
        cls.__dctArg2Instance[targetDir] = cls._instance
        print(f'FILE_DECTECTOR {targetDir =}', cls._instance)
        return cls._instance

    def __init__(self, targetDir=utils.extract_dir(), *args):
        cls = type(self)
        if targetDir not in cls.__setIsInit:
            self.lstPic: list[str] = utils.extract_file_name_sorted(targetDir)

            cls.__setIsInit.add(targetDir)

    @property
    def fileList(self):
        return self.lstPic


if __name__ == '__main__':
    dt = FileDetector()

    print(dt.fileList)

