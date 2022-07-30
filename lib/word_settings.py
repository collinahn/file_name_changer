# 바이너리를 저장하고 불러온다
# TODO: 클래스 분리할 것

import os
import pickle
from time import sleep

from lib.log_gongik import Logger 
from lib.utils import extract_dir

class IncompleteValueError(Exception):
    pass

class WordSettings:
    def __init__(self) -> None:
        self.log = Logger()

        self.save_path = f'{extract_dir()}/.gongik/settings'
        self.save_file = f'{self.save_path}/gongik.save'
        if not os.path.exists(self.save_path):
            os.mkdir(self.save_path)

        self.initialize_if_file_missing()
        self.log.INFO(f'{self.save_path} init')

    @staticmethod
    def make_init_data() -> dict[str, list[tuple]]:
        return {
            'prefix': [
                ('1','1호차'),
                ('2','2호차'),
            ],
            'suffix': [
                ('정비 전','전후정비 전'),
                ('정비 후','전후정비 후'),
                ('안내장','안내장 부착'),
                ('1차 계고','1차 계고장 부착'),
                ('2차 계고','2차 계고장 부착'),
                ('수거 전','수거 전'),
                ('수거 후','수거 후'),
                ('지정안함',''),
            ]
        }
    
    @staticmethod
    def shortcut_info() -> dict[str,list]:
        return {
            'prefix': [
                'Ctrl+1',
                'Ctrl+2',
            ],
            'suffix': [
                'Alt+A', 
                'Alt+S', 
                'Alt+D',
                'Alt+1', 
                'Alt+2', 
                'Alt+F',
                'Alt+G', 
                'Alt+X'
            ]
        }

    def initialize_if_file_missing(self):
        if not os.path.exists(self.save_file):
            self.initialize()

    def initialize(self):
        init_data = self.make_init_data() 
        return self.save_data(init_data)

    def _verify_data(self, input: dict):
        sample_data = self.make_init_data()
        if input.keys() != sample_data.keys():
            raise IncompleteValueError()
        for key, value in sample_data.items():
            if input.get(key) is None:
                raise IncompleteValueError()
            if len(input.get(key)) != len(value):
                raise IncompleteValueError()

    def save_data(self, data: dict[str, list[tuple]]) -> bool:
        '''
        데이터를 바이너리 파일로 저장한다.\n
        형식에 맞지 않는 데이터를 저장하면 IncompleteValueError 예외를 내보냄.
        '''
        self._verify_data(data) # throws IncompleteValueError

        try:
            with open(self.save_file, 'wb') as bf:
                pickle.dump(data, bf)
            self.log.INFO(f'binary file for restore saved, {self.save_file = }')
        except Exception as e:
            self.log.ERROR(f'{e} / failed to save binary file {self.save_file}')
            return False
        return True

    def load_data(self) -> dict[str, list[tuple]] or None:
        self.initialize_if_file_missing()
        try:
            with open(self.save_file, 'rb') as bf:
                data: dict = pickle.load(bf)
        except Exception as e:
            self.log.ERROR(f'{e} / failed to load from binary file {self.save_file}')
            return None

        return data

if __name__ == '__main__':
    from pprint import pprint
    ws = WordSettings()
    pprint(ws.load_data())

    # ws.save_data({'1':'', '2':''})
    ws.save_data({'prefix':'', 'suffix':''})
