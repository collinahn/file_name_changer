# 파일의 이름을 받아와 원래 파일명을 바꿀 파일명으로 변경함

import utils
import os

from get_name import Name

class NameChanger(object):
    def __new__(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)

        print('GPSINFO', cls._instance)
        return cls._instance

    def __init__(self):
        cls = type(self)
        if not hasattr(cls, '_init'):
            self.clsName: Name = Name()
            self.dctName2Change: dict = self.clsName.new_name 

            processedFileNames = set(self.dctName2Change.keys())
            currentDirFileNames = set(utils.extract_file_name_sorted())

            if not processedFileNames.issubset(currentDirFileNames):
                print('init failed - file unstable')
                return

            cls._init = True

    @staticmethod
    def _change_name(oldName, addr, cnt, header=2):
        newName = str(header) + '_' + addr + ' ' + str(oldName.split('.')[0]) + ' (' + str(cnt) + ')' + '.jpg'
        os.rename(oldName, newName)

    @staticmethod
    def _extract_parent_dir(): # 부모 디렉터리 추출
        currentPath = os.path.abspath(__file__)
        return str(currentPath).split('\\', -1)[-2]

    # 이미 필터링된 주소를 넘기는 것으로 수정
    @staticmethod
    def _simplify_address(origin):
        return origin

    def process(self):
        gubun = 2
        parentFolderName = self._extract_parent_dir()
        print()
        print()
        print(f'{parentFolderName = }')
        print()
        print()
        #호차 구분
        if '1' in parentFolderName:
            gubun = 1
        elif '2' in parentFolderName:
            gubun = 2
        elif '3' in parentFolderName:
            gubun = 3
        elif '4' in parentFolderName:
            gubun = 4

        cnt = 1
        for oldName, addr in self.dctName2Change.items():
            simplifiedAddr = self._simplify_address(addr)
            self._change_name(oldName, simplifiedAddr, cnt, gubun)
            cnt += 1


if __name__ == '__main__':
    cn = NameChanger()


    # header = os.path.abspath(__file__)
    # print(header.parent)
    # print(str(header).split('\\', -1)[-2])

    cn.process()


