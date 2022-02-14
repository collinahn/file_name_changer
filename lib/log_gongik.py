# 로그를 설정하고 생성하는 클래스(싱글턴)
# 모듈 파일명, 함수명, 등의 정보를 포함하여 로그를 출력한다.
# 함수명 등의 디버그 정보는 Python3.8 이상에서 동작한다.

# 사용법
# 로그를 레벨별로 세분화한다.
"""
DEBUG   상세한 정보가 필요할 때, 보통 문제 분석, 디버깅할 때 사용
INFO    동작이 절차에 따라서 진행되고 있는지 관찰 할 때
WARNING 어떤 문제가 조만간 발생할 조짐이 있을 때. 예) 디스크 용량이 부족 할 때
ERROR   프로그램에 문제가 발생해서 기능의 일부가 동작하지 않을 때
CRITICAL    심각한 문제가 발생해서 도저히 시스템이 정상적으로 동작할 수 없을 때

출처: https://wikidocs.net/17747
"""

# 사용예
'''
from LoggerLT import Logger

#인스턴스 가져옴
log = Logger()

#로그 기록(로그 레벨에 따라 파일 및 콘솔 출력)
log.DEBUG("msg")
'''

# 2021.11.09. created by 안태영


import os
import logging
import logging.handlers

LOG_FOLDER_PATH = './.gongik/'
LOG_FILE_NAME = 'gongik.log'
LOG_FILE_PATH = LOG_FOLDER_PATH + LOG_FILE_NAME
STACK_LV = 2
MAX_BYTES_PER_FILE = 10*1024*1024
BACKUP_FILE_CNT = 10


class Logger:

    def __new__(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)

            #폴더가 없는 경우
            if os.path.exists(LOG_FOLDER_PATH) == False:
                os.mkdir(LOG_FOLDER_PATH)
            #파일이 없는 경우
            if os.path.exists(LOG_FILE_PATH) == False:
                f = open(LOG_FILE_PATH, 'w', encoding='UTF-8')
                f.close()

        return cls._instance

  
    def __init__(self) :
        cls = type(self)
        if not hasattr(cls, "_init"):
            cls._logger = logging.getLogger('LoggerGongik')
            cls._logger.setLevel(logging.DEBUG)

            cls.formatter = logging.Formatter('%(asctime)s [%(filename)-25s:%(funcName)-25s:%(lineno)-5s] [%(levelname)s] >> %(message)s')
            cls.fileHandler = logging.handlers.RotatingFileHandler(
                LOG_FILE_PATH, 
                maxBytes=MAX_BYTES_PER_FILE, 
                backupCount=BACKUP_FILE_CNT, 
                encoding='UTF-8'
            )
            cls.streamHandler = logging.StreamHandler()
            cls.fileHandler.setFormatter(cls.formatter)
            cls.streamHandler.setFormatter(cls.formatter)

            cls._logger.addHandler(cls.fileHandler)
            cls._logger.addHandler(cls.streamHandler)

            #콘솔엔 전부 출력하고 파일엔 info 이상부터 기록
            cls.fileHandler.setLevel(logging.INFO)
            cls.streamHandler.setLevel(logging.DEBUG)
            
            cls._init = True

    @staticmethod
    def assemble_msg(msg):
        return ''.join(str(word) + ' ' for word in msg)

    @classmethod
    def DEBUG(cls, *message):
        ret = cls.assemble_msg(message)
        cls._logger.debug(ret, stacklevel=STACK_LV)

    @classmethod
    def INFO(cls, *message):
        ret = cls.assemble_msg(message)
        cls._logger.info(ret, stacklevel=STACK_LV)

    @classmethod
    def WARNING(cls, *message):
        ret = cls.assemble_msg(message)
        cls._logger.warning(ret, stacklevel=STACK_LV)

    @classmethod
    def ERROR(cls, *message):
        ret = cls.assemble_msg(message)
        cls._logger.error(ret, stacklevel=STACK_LV)

    @classmethod
    def CRITICAL(cls, *message):
        ret = cls.assemble_msg(message)
        cls._logger.critical(ret, stacklevel=STACK_LV)

    #logLv 10(debug) 20 30 40 50(critical)
    @classmethod
    def set_log_lv(cls, logLv: int):
        if logLv in {10, 20, 30, 40, 50}:
            cls.fileHandler.setLevel(logLv)


if __name__ == "__main__":
    log = Logger()

    sMsg = "LogMessage"

    log.CRITICAL(sMsg, 1)
    log.ERROR(sMsg, 2)
    log.WARNING(sMsg, 3)
    log.INFO(sMsg, 4)
    log.DEBUG(sMsg, 5)