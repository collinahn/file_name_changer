# 파일의 이름을 받아와 원래 파일명을 바꿀 파일명으로 변경함

import os


from . import utils
from .log_gongik import Logger
from .get_name import Name

class NameChanger(object):
    def __new__(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
            cls.log = Logger()

        cls.log.INFO(cls._instance)
        return cls._instance

    def __init__(self):
        cls = type(self)
        if not hasattr(cls, '_init'):
            self.clsName: Name = Name()
            self.dctName2Change: dict[str,str] = self.clsName.new_name 

            self.dctFinalResult: dict[str, str] = {} #최종 결과 담아놓기

            cls._init = True

    @staticmethod
    def extract_parent_folder(dir) -> str:
        try:
            return dir.rsplit('/', 1)[1]
        except (IndexError, AttributeError) as es:
            Logger.ERROR(es)
        except Exception as e:
            Logger.CRITICAL(e, 'input =', dir)
        return '2구역'

    def _get_car_no_from_parent_dir(self) -> str:
        gubun = '2'
        parentFolderName = self.extract_parent_folder(utils.extract_dir())

        #호차 구분
        if '1' in parentFolderName:
            gubun = '6' #1조는 6으로
        elif '2' in parentFolderName:
            gubun = '2'

        return str(gubun)

    def get_final_name(self, gubun, oldName, detailInput):
        res = gubun + '_' + self.dctName2Change[oldName]
        if detailInput:
            res += ' ' + detailInput
            
        self.dctFinalResult[oldName] = res
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
            except (AttributeError, IndexError, KeyError) as es:
                self.log.ERROR(es)
                ret = False
            except Exception as e:
                self.log.CRITICAL(e)
                ret = False
        return ret

    @property
    def gubun(self):
        return self._get_car_no_from_parent_dir()

if __name__ == '__main__':
    cn = NameChanger()


    # header = os.path.abspath(__file__)
    # print(header.parent)
    # print(str(header).split('\\', -1)[-2])



