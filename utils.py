import os

# 파일 목록 추출
# jpg 확장자가 아니거나 이미 바꾼 목록은 건들지 않음
def extract_file_name_sorted():
    fileExt = ( r'.jpg', r'.jpeg' )
    alreadyHandled = ( r'6_', r'2_', r'3_', r'4_' )

    lstRes: list[str] = os.listdir('.')
    return [ _ for _ in lstRes if _.endswith(fileExt) and not _.startswith(alreadyHandled) ] 
