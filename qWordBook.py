VERSION_INFO = '(release)gongik_v2.7.1'

NO_FILE_INSTRUCTION = '''현재 디렉토리에 처리할 수 있는 파일이 없습니다.
이미 처리한 파일은 프로그램이 인식하지 않습니다.
연결된 핸드폰에서 금일 촬영된 사진을 불러옵니다.

**주의사항**
파일 전송 전 핸드폰을 "잠금이 해제된 상태"로 유지하세요.
'''

PROGRAM_INFO = '''1. 최초 실행시 실행 폴더에 파일이 없을 경우 연결된 핸드폰 기본 카메라 폴더에서 오늘 생성된 파일만을 가져옵니다.
2. 파일 이름에 한글이 포함된 경우, 사진 파일(jpg)이 아닌 경우, 혹은 사진에 메타데이터가 없는 경우 인식하지 않습니다.
3. 장소와 무관하게 3분 이내에 찍힌 사진들은 같은 장소로 취급됩니다.
4. 사진을 찍은 장소에서 가장 가까운 건물 번호를 기준으로 삼아 파일들을 분류합니다. 부정확하다면 우측의 지도를 클릭해 보정하세요.
5. 본 프로그램의 실행 중에 발생한 이용자의 귀책사유로 인한 피해는 개발자가 책임지지 않습니다.'''

TIME_GAP = 180 #이 시간 내에 찍힌 사진들은 전부 같은 장소 취급
PIXMAP_SCALE = (1100, 825)

BEFORE_FIX = '전후정비 전'
AFTER_FIX = '전후정비 후'
ATTACH_FLYER = '안내장 부착'
WARN_1ST = '1차 계고장 부착'
WARN_2ND = '2차 계고장 부착'
BEFORE_FETCH = '수거 전'
AFTER_FETCH = '수거 후'
EMPTY_STR = ''

#img src
IMG_FROG = 'img/frog.ico'
IMG_FROG2 = 'img/final.ico'
IMG_EXIT = 'img/exit.ico'
IMG_DEV = 'img/developer.ico'

#이름 타입
USE_BOTH = 0
USE_ROAD = 1
USE_NORMAL = 2


#Interact Msg
MSG_INFO = {
    'COMPLETE':'처리가 완료되었습니다.\n결과를 확인하여 주세요.',
    'SOF':'시작 장소입니다.',
    'EOF':'마지막 장소입니다.',
    'EXIT_END':'프로그램을 종료합니다.\n일부 중복된 장소를 확인하여 주세요.',
    'EXIT_PLAIN':'종료합니다.',
    'TRANSFER_FAILURE':'연결이 불안정하여 사진을 옮기지 못하였습니다.\n1) user/.adroid폴더 내부 adbkey를 확인해주세요.\n2) 핸드폰에 표시된 팝업창에서 "이 컴퓨터에서 항상 허용"을 체크하고 다시 실행해주세요.\n',
    'TRANSFER_SUCCESS':'사진 옮기기가 완료되었습니다.',
    'TRANSFER_RETRY_SUCCESS':'다시 시도했는데 성공하였습니다.',
    'TRANSFER_RETRY_FAILURE':'다시 시도하였는데 실패하였습니다.\n다시 시도하거나 사진을 수동으로 옮겨 주세요.',
    'UPDATE_POSSIBLE':'업데이트가 있습니다.\n실행 후 정보>업데이트 확인 탭에서 새 버전을 다운받아 주세요.'
}

MSG_WARN = {
    'FILE_NAME_ERROR':'중복된 파일 이름이 있습니다. 이름 변경 후 다시 시도하세요',
    'OS_ERROR':'문제가 있어 일부 파일을 처리하지 못했습니다.(수동 확인 필요, 로그를 확인하세요.)',
    'CONNECTION_ERROR':'연결된 기기가 없거나 USB디버깅 모드가 활성화되지 않았습니다.\n종료합니다.',
    'MULTI_CONNECTION_ERROR':'연결된 기기가 하나 이상입니다.\n종료합니다.',
    'EMPTY_FILE_ERROR':'금일 생성된 파일이 없거나 권한이 없어 파일을 인식하지 못하였습니다.\nUSB 디버깅을 위해 컴퓨터의 RSA지문을 항상 허용해주세요.',
}

MSG_TIP = {
    'EXIT':'프로그램을 종료합니다. 진행 상황이 저장되지 않습니다.',
    'RECOMMEND':'이미지에서 텍스트를 추출해 키워드를 추천합니다.',
    'RESTORE':'이전에 완료했던 작업들을 복구합니다.',
    'INFO':'프로그램의 정보를 확인합니다.',
    'UPDATE':'버전정보를 확인하고 새 버전을 다운받습니다. 온라인에서만 동작합니다.',
    'LIST':'사진 정보 목록을 불러옵니다.',
    'MODIFY':'텍스트 박스에 입력된 텍스트로 등록하거나 수정합니다.\n다음 위치를 보면 자동으로 저장됩니다.',
    'FORWARD':f'다른 장소에서 {TIME_GAP}초 이내에 찍은 사진을 불러옵니다.',
    'BACKWARD':'이전 장소를 불러옵니다.',
    '1CAR':'',
    '2CAR':'',
    'FINISH':'현재 폴더에서의 모든 작업을 종료하고 설정한 대로 이름을 변경합니다.',
    'NEXT':'비슷한 장소에서 찍힌 사진 중 다음 사진으로 미리보기를 교체합니다.',
    'PREVIOUS':'비슷한 장소에서 찍힌 사진 중 이전 사진으로 미리보기를 교체합니다.',
    'PHOTO':'사진을 크게 보시려면 더블 클릭하세요.',
    'SEQUENCE':'사진 분류를 수정하려면 클릭하세요.',
}

MSG_SHORTCUT = {
    'EXIT':'Ctrl+Shift+Q',
    'RECOMMEND':'Ctrl+E',
    'RESTORE':'Ctrl+R',
    'INFO':'Ctrl+I',
    'UPDATE':'Ctrl+U',
    'LIST':'Ctrl+G',
    'MODIFY':'Alt+M',
    'FORWARD':'Alt+Down', # 다음 위치 보기
    'BACKWARD':'Alt+Up',
    '1CAR':'Ctrl+1',
    '2CAR':'Ctrl+2',
    'FINISH':'Ctrl+Shift+E',
    'NEXT':'Alt+Right',    # 다음 사진 보기
    'PREVIOUS':'Alt+Left',
    'BEFORE_FIX':'Alt+A', 
    'AFTER_FIX':'Alt+S', 
    'BEFORE_FETCH':'Alt+F',
    'WARN_1ST':'Alt+1', 
    'WARN_2ST':'Alt+2', 
    'AFTER_FETCH':'Alt+G',
    'ATTACH_FLYER':'Alt+D', 
    'SET_NONE':'Alt+X',
}


QSTYLE_SHEET = '''
QWidget {
    background-color: rgb(37, 37, 38);
    color: rgb(255, 255, 255);
}
QWidget .QPushButton {
    color: yellow;
    background-color: rgb(37, 37, 38);
    border: 2px solid yellow;
    border-radius: 5px;
}
QWidget .QPushButton:hover {
    border:0px;
    background-color: yellow;
    color: black
}
QWidget .QPushButton:disabled {
    border:2px solid rgb(67, 67, 70);
    color: rgb(67, 67, 70)
}

QLineEdit {
    border:2px solid rgb(67, 67, 70);
    background-color: rgb(51, 51, 55);
    color: rgb(255, 255, 255);
}
QLineEdit:disabled {
    border:1px solid rgb(67, 67, 70);
    background-color: rgb(45, 45, 48);
    color: rgb(255, 255, 255);
}

'''

QSTYLE_NO_BORDER_BOX = '''
QGroupBox { border: 0px; }
'''

QSTYLE_SHEET_POPUP = '''
QWidget {
    background-color: rgb(82, 82, 83);
    color: rgb(255, 255, 255);
}
QWidget .QPushButton {
    color: yellow;
    background-color: rgb(82, 82, 83);
    border: 2px solid yellow;
    border-radius: 5px;
}
QWidget .QPushButton:hover {
    border:0px;
    background-color: yellow;
    color: black
}
QWidget .QPushButton:disabled {
    border: 2px solid grey;
    background-color: rgb(82, 82, 83);
    color: yellow
}

QComboBox {
    text-align: center;
    border: 1px solid darkgray;
    border-radius: 0px;
    padding-right: 20px;
    min-width: 6em;
    color: white;
}

'''