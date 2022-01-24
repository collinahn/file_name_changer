import sys
import os
from datetime import datetime
from collections import defaultdict

def get_today_date_formated(separator) -> str:
    return datetime.now().strftime(f'%Y{separator}%m{separator}%d')

# 취급하는 파일 확장자 표시
def get_valid_file_ext():
    return ( r'.jpg', r'.jpeg' )

# 파일 목록 추출
# jpg 확장자가 아니거나 이미 바꾼 목록은 건들지 않음
def extract_file_name_sorted(dir='.'):
    fileExt = get_valid_file_ext()
    alreadyHandled = ( r'6_', r'2_', r'3_', r'4_' )

    lstRes: list[str] = os.listdir(dir)
    return [ _ for _ in lstRes if _.endswith(fileExt) and not _.startswith(alreadyHandled) ]


def extract_dir(): # 부모 디렉터리 추출
    return os.getcwd().replace('\\', '/')

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# key: value형태를 value: key list 형태로 변환한다
def invert_dict(originDct):
    resDct = defaultdict(list)
    for key, value in originDct.items():
        resDct[value].append(key)
    
    return dict(resDct)


if __name__ == '__main__':
    print(extract_dir())