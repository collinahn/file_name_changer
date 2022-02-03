# 파일의 메타데이터를 이용한 범용 업무 자동화 프로그램

### Description
사진에서 위치 정보와 시간 정보를 추출하여
일정 시간 이내 찍힌 일정 반경 이내의 사진들을 
특정 도로명 주소와 함께 입력받은 추가 정보를 바탕으로 
파일의 이름을 바꿔주는 GUI 윈도우 프로그램.

이름을 바꾸기 전 기존 폴더의 이름을 기준으로 파일들을 핸들링해서
같은 이름이 허용되는 다른OS에서는 정상작동하지 않을 수 있다.

### Environment
* Windows 10 이상

### Prerequisite
* Python 3.9
* PyQt5 5.15.6
* pyinstaller 4.7

### Usage
exe 빌드하기 
```
pyinstaller -w -F --clean --add-data "db/addr.db;./db" --add-data "img/frog.ico;./img" --add-data "img/developer.ico;./img" --add-data "img/exit.ico;./img" --add-data "img/final.ico;./img" --add-data "platform-tools;./platform-tools" --icon=img/final.ico qMain.py
```

* 실행 파일이 있는 폴더에 사진 파일이 없는 경우
  * 연결된 핸드폰 기본 사진 폴더(/sdcard/DCIM/Camera)에서 오늘 찍은 사진을 가져온다.
* 사진 파일이 있는 경우
  * 사진의 위치와 시간을 고려하여 특정 기준으로 분류한 뒤 GUI프로그램 실행

