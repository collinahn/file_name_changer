# 바이너리를 저장하고 불러온다
# TODO: 클래스 분리할 것

import os
import pickle
import secrets

from lib.log_gongik import Logger 
from lib.file_property import FileProp
from lib.file_detect import BackupFileDetector # 파일 탐지
from lib.utils import (
    get_today_date_formated,
    extract_dir
)

class BackupRestore(object):
    def __init__(self) -> None:
        self.log = Logger()

        self.savePath = f'{extract_dir()}/.gongik/restore'
        if not os.path.exists(self.savePath):
            os.mkdir(self.savePath)

        self.clsFD = BackupFileDetector(self.savePath)
        
        self.log.INFO(f'{self.savePath} init')

    def save_result(self, filePath: str, fPropData: dict[str,FileProp]) -> bool:
        '''
        데이터를 바이너리 파일로 저장한다.\n
        규칙: {'이전파일이름':<FileProp객체>}.
        '''
        try:
            with open(filePath, 'wb') as bf:
                pickle.dump(fPropData, bf)
            self.log.INFO(f'binary file for restore saved, {filePath = }')
        except Exception as e:
            self.log.ERROR(f'{e} / failed to save binary file {filePath}')
            return False

        return True

    def load_result(self, filePath: str) -> dict or None:
        try:
            with open(filePath, 'rb') as bf:
                data: dict = pickle.load(bf)

        except Exception as e:
            self.log.ERROR(f'{e} / failed to load from binary file {filePath}')
            return None

        return data

    def create_file_path(self, carNo: int):
        '''
        저장할 파일의 이름(경로포함)을 생성한다\n
        규칙: (지역번호-호차)_(8자리실행날짜)_(4바이트랜덤토큰).gongik
        '''
        fPath = f'{self.savePath}/{carNo}_{get_today_date_formated()}_{secrets.token_hex(4)}.gongik'
        self.log.INFO(f'file name for future restore has set: {fPath}')

        return f'{fPath}'

    

if __name__ == '__main__':

    br = BackupRestore()

    (br.create_file_path(1))
    (br.create_file_path(1))
    (br.create_file_path(1))
    (br.create_file_path(2))
    (br.create_file_path(2))