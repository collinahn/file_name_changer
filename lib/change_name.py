# 파일의 이름을 받아와 원래 파일명을 바꿀 파일명으로 변경함

import os

from . import utils
from .get_name import Name

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
            self.dctName2Change: dict[str,str] = self.clsName.new_name 

            self.dctFinalResult: dict[str, str] = {} #최종 결과 담아놓기

            processedFileNames = set(self.dctName2Change.keys())
            currentDirFileNames = set(utils.extract_file_name_sorted())

            if not processedFileNames.issubset(currentDirFileNames):
                print('init failed - file unstable')
                return

            cls._init = True

    @staticmethod
    def _change_name(oldName, addr, cnt, header='2'):
        newName = header + '_' + addr + ' ' + str(oldName.split('.')[0]) + ' (' + str(cnt) + ')' + '.jpg'
        os.rename(oldName, newName)

    # 이미 필터링된 주소를 넘기는 것으로 수정
    @staticmethod
    def _simplify_address(origin):
        return origin

    @staticmethod
    def extract_parent_dir(dir):
        try:
            return dir.rsplit('/', 1)[1]
        except (IndexError, AttributeError) as e:
            print(e)
        return '2'


    def get_car_no_from_parent_dir(self) -> str:
        gubun = 2
        parentFolderName = self.extract_parent_dir(utils.extract_dir())

        #호차 구분
        if '1' in parentFolderName:
            gubun = 6 #1조는 6으로
        elif '2' in parentFolderName:
            gubun = 2

        return str(gubun)

    def process_cli(self):
        gubun = self.get_car_no_from_parent_dir()

        for cnt, (oldName, addr) in enumerate(self.dctName2Change.items(), start=1):
            self._change_name(oldName, addr, cnt, gubun)


    def get_final_name(self, oldName, detailInput):
        gubun = self.get_car_no_from_parent_dir()

        self.dctFinalResult[oldName] = gubun + '_' + self.dctName2Change[oldName] + ' ' + detailInput
        
        return self.dctFinalResult[oldName]


    def change_name_on_btn(self, dctLoc2Name, dctName2BeforeAfter, carSpec='2') -> bool:
        ret = True
        
        i = 0
        for target, loc in self.dctName2Change.items():
            frontName = carSpec + dctLoc2Name[loc][1:]
            try:
                if target in dctName2BeforeAfter:
                    newName = frontName + ' ' + dctName2BeforeAfter[target] + ' (' + str(i) + ').jpg'
                else: 
                    newName = frontName + ' (' + str(i) + ').jpg' 
                os.rename(target, newName)
                i += 1
            except Exception as e:
                print(e, 'exception')
                ret = False
        return ret

    @property
    def gubun(self):
        return self.get_car_no_from_parent_dir()

if __name__ == '__main__':
    cn = NameChanger()


    # header = os.path.abspath(__file__)
    # print(header.parent)
    # print(str(header).split('\\', -1)[-2])

    cn.process_cli()

