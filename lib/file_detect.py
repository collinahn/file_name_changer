# 현재 위치에서 파일 목록을 찾아서 보유한다.

from . import utils

class FileDetector(object):
    def __new__(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)

        print('FILE_DECTECTOR', cls._instance)
        return cls._instance

    def __init__(self):
        cls = type(self)
        if not hasattr(cls, '_init'):
            self.lstPic: list[str] = utils.extract_file_name_sorted()

            # for indv in self.lstPic:
                # print("debug:", indv)

            cls._init = True


    @property
    def fileList(self):
        return self.lstPic


if __name__ == '__main__':
    dt = FileDetector()

    print(dt.fileList)

