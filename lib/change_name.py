# 파일의 이름을 받아와 원래 파일명을 바꿀 파일명으로 변경함

import os
import traceback

import qWordBook as const
from lib.file_property import FileProp
from lib.log_gongik import Logger


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
            self.name_counter = {}

            cls._init = True


    def change_name_on_btn(self, name_type:int) -> int:
        ret: int = 0 # 정상 코드
        self.name_counter = {} # 이름 저장
        
        try:
            for name in FileProp.get_names():
                props = FileProp(name)
                if name_type == const.USE_BOTH:
                    new_name = props.final_full_name
                elif name_type == const.USE_ROAD:
                    new_name = props.final_road_name
                else:
                    new_name = props.final_normal_name

                if new_name not in self.name_counter:
                    self.name_counter[new_name] = 0 # 먼저 위치해야 비교가 가능해짐
                    new_name = ''.join((new_name, '.jpg'))
                else:
                    self.name_counter[new_name] += 1 # 먼저 위치해야 비교가 가능해짐
                    new_name = ''.join((new_name, f' ({self.name_counter[new_name]}).jpg'))
                    
                new_full_path = f'{props.abs_path[:-len(props.name)]}{new_name}'

                self.log.INFO(f'renaming {props.abs_path} to {new_full_path}')
                if os.path.exists(props.abs_path):
                    os.rename(props.abs_path, new_full_path)
                else:
                    self.log.WARNING(f'ignoring {props.abs_path} - doesnt exist(failed to rename)')
                props.new_path = new_full_path # 이때 처음 초기화
        except FileExistsError as fe:
            self.log.WARNING(fe)
            ret = 1 # 파일 이미 있음
        except (AttributeError, IndexError, KeyError) as es:
            self.log.ERROR(es)
            self.log.ERROR(f'{traceback.format_exc()}')
            ret = 2 # 처리 오류(로그 참조)
        except Exception as e:
            self.log.CRITICAL(e)
            ret = 99 # 기타 오류(로그 참조)
            self.log.ERROR(f'{traceback.format_exc()}')

        return ret


    def change_name_designated(self, *, src_name: str, dst_name: str) -> bool:
        try:
            self.log.INFO(f'renaming {src_name} to {dst_name}')
            os.rename(src_name, dst_name)
            self.log.INFO(f'{dst_name} restored')
        except Exception as e:
            self.log.CRITICAL(f'{e} / failed while restoring {src_name}')
            import traceback
            self.log.ERROR(f'{traceback.format_exc()}')
            return False
        
        return True

if __name__ == '__main__':
    cn = NameChanger()


    # header = os.path.abspath(__file__)
    # print(header.parent)
    # print(str(header).split('\\', -1)[-2])



