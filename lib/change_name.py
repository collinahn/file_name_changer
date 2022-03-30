# 파일의 이름을 받아와 원래 파일명을 바꿀 파일명으로 변경함

import os
import copy

import qWordBook as const
from lib.file_property import FileProp
from .log_gongik import Logger


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

            cls._init = True


    def change_name_on_btn(self, nameType:int) -> int:
        ret: int = 0 # 정상 코드
        
        try:
            for idx, name in enumerate(FileProp.get_names()):
                props = FileProp(name)
                if nameType == const.USE_BOTH:
                    newName = props.final_full_name
                elif nameType == const.USE_ROAD:
                    newName = props.final_road_name
                else:
                    newName = props.final_normal_name

                newName = ''.join((newName, f' ({idx}).jpg'))
                newPath = f'{props.abs_path[:-len(props.name)]}{newName}'

                self.log.INFO(f'renaming {props.abs_path} to {newPath}')
                os.rename(props.abs_path, newPath)
                props.new_path = newPath # 이때 처음 초기화
        except FileExistsError as fe:
            self.log.WARNING(fe)
            ret = 1 # 파일 이미 있음
        except (AttributeError, IndexError, KeyError) as es:
            self.log.ERROR(es)
            import traceback
            self.log.ERROR(f'{traceback.format_exc()}')
            ret = 2 # 처리 오류(로그 참조)
        except Exception as e:
            self.log.CRITICAL(e)
            ret = 99 # 기타 오류(로그 참조)
            import traceback
            self.log.ERROR(f'{traceback.format_exc()}')

        return ret


    def change_name_designated(self, *, fromName: str, toName: str) -> bool:
        try:
            self.log.INFO(f'renaming {fromName} to {toName}')
            os.rename(fromName, toName)
            self.log.INFO(f'{toName} restored')
        except Exception as e:
            self.log.CRITICAL(f'{e} / failed while restoring {fromName}')
            import traceback
            self.log.ERROR(f'{traceback.format_exc()}')
            return False
        
        return True

if __name__ == '__main__':
    cn = NameChanger()


    # header = os.path.abspath(__file__)
    # print(header.parent)
    # print(str(header).split('\\', -1)[-2])



