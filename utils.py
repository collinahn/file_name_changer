import sys
import os

# 파일 목록 추출
# jpg 확장자가 아니거나 이미 바꾼 목록은 건들지 않음
def extract_file_name_sorted():
    fileExt = ( r'.jpg', r'.jpeg' )
    alreadyHandled = ( r'6_', r'2_', r'3_', r'4_' )

    lstRes: list[str] = os.listdir('.')
    return [ _ for _ in lstRes if _.endswith(fileExt) and not _.startswith(alreadyHandled) ] 


def extract_parent_dir(): # 부모 디렉터리 추출
    res = None
    try:
        res = resource_path('.').rsplit('\\', 1)[-2]
    except (IndexError, AttributeError) as e:
        print(e)
    
    return res

def resource_path(relative_path=None):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path) if relative_path else base_path[:-1]



if __name__ == '__main__':
    print(extract_parent_dir())