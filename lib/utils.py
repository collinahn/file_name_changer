import contextlib
import sys
import os
import re
from datetime import datetime
from collections import defaultdict
from PIL import Image
from PIL import UnidentifiedImageError


def get_today_date_formated(separator:str=None) -> str:
    if separator is None:
        separator = ""
    return datetime.now().strftime(f'%Y{separator}%m{separator}%d')

def get_year_month_day() -> tuple[str, str, str]:
    sep = '-'
    date = get_today_date_formated(sep)
    year, month, day = date.split(sep)
    return year, str(int(month)), str(int(day))

# 취급하는 파일 확장자 표시
def get_valid_file_ext():
    return ( r'.jpg', r'.jpeg', r'.JPG', r'.JPEG' )

def get_car_candidates():
    return ( '6', '2', '3', '4' )

def get_handled_suffix():
    return tuple( f'{_}_' for _ in get_car_candidates() )

def is_korean_included(target_str: str) -> bool:
    '''
    한글이 들어가 있는지 정규식으로 판별한다.
    '''
    return bool(len(re.findall(u'[\u3130-\u318F\uAC00-\uD7A3]+', target_str)))

def extract_dir(winDir=False):
    return os.getcwd() if winDir else os.getcwd().replace('\\', '/')

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

def extract_parent_folder(dir) -> str:
    with contextlib.suppress(Exception):
        return dir.rsplit('/', 1)[1]
    return '2구역'

def get_car_no_from_parent_dir() -> str:
    from lib.base_folder import WorkingDir

    gubun = '2'
    parentFolderName: str = extract_parent_folder(WorkingDir().abs_path)

    #호차 구분
    if parentFolderName.startswith('1'):
        gubun = '6' #1조는 6으로
    elif parentFolderName.startswith('2'):
        gubun = '2'

    return gubun

def open_image(filePath) -> Image:
    image: Image = None
    try:
        image = Image.open(filePath)
    except UnidentifiedImageError as ue:
        from lib.log_gongik import Logger
        Logger().ERROR('Unidentified Image', ue)
        return None
    except Exception as e:
        from lib.log_gongik import Logger
        Logger().ERROR('Unexpected Error', e)
        return None

    return image

def get_relative_path(originPath: str) -> str:
    return originPath.replace(extract_dir(), '.')


if __name__ == '__main__':
    print(extract_dir())
    print(extract_dir(True))
    print(resource_path(''))
    print(f'{get_handled_suffix() = }')

    # print(rf'{extract_dir(True)}\tesseract')

    # open_image('1.jpg')

    print(get_relative_path(extract_dir()))