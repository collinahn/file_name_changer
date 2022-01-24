# 파일의 이름을 받아와 원래 파일명을 바꿀 파일명으로 변경함

import os
import copy


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
            self.dctName2LocOrigin: dict[str,str] = copy.deepcopy(self.dctName2Change)

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

    def store_models(self, carSpec, dctName2Loc, dctLoc2Detail, dctName2Sufix, dctName2DetailModified):
        for name, loc in dctName2Loc.items():
            try:
                middle = ' ' + dctLoc2Detail[loc]
                if name in dctName2DetailModified and dctName2DetailModified[name]:
                    middle = ' ' + dctName2DetailModified[name]

                suffix = ''
                if name in dctName2Sufix and dctName2Sufix[name]:
                    suffix = ' ' + dctName2Sufix[name]

                res = carSpec + '_' + loc + middle + suffix
                
                self.dctFinalResult[name] = res
                self.log.INFO(name, 'saved as', self.dctFinalResult[name])
            except KeyError as e:
                self.log.DEBUG(e)
        return self.dctFinalResult


    def change_name_on_btn(self, prefix, dctLoc2Detail, dctName2Suffix, dctName2DetailsModify) -> int:
        ret: int = 0 # 정상 코드
        
        idx = 0
        for target, loc in self.dctName2Change.items():
            try:
                middleName = loc + ' '

                if target not in dctName2DetailsModify: # 기본
                    middleName += dctLoc2Detail[loc]

                if target in dctName2DetailsModify:     # 따로 지정한 경우
                    middleName += dctName2DetailsModify[target]

                nameFirstHalf = prefix + '_' + middleName # 2_불법노점

                if target in dctName2Suffix and dctName2Suffix[target]:
                    fullName = nameFirstHalf + ' ' + dctName2Suffix[target] + ' (' + str(idx) + ').jpg'
                else: 
                    fullName = nameFirstHalf + ' (' + str(idx) + ').jpg' 
                
                self.log.INFO('renaming', target, 'to', fullName)
                os.rename(target, fullName)
                idx += 1
            except FileExistsError as fe:
                self.log.WARNING(fe)
                ret = 1 # 파일 이미 있음
            except (AttributeError, IndexError, KeyError) as es:
                self.log.ERROR(es)
                ret = 2 # 처리 오류(로그 참조)
            except Exception as e:
                self.log.CRITICAL(e)
                ret = 99 # 기타 오류(로그 참조)
        return ret

    @property
    def gubun(self):
        return self._get_car_no_from_parent_dir()

if __name__ == '__main__':
    cn = NameChanger()


    # header = os.path.abspath(__file__)
    # print(header.parent)
    # print(str(header).split('\\', -1)[-2])



