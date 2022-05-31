import socket
from threading import Lock

from lib.log_gongik import Logger

class ConnectionCheck(object):
    lock = Lock()
    def __new__(cls):
        with cls.lock:
            if not hasattr(cls, '_instance'):
                cls.log = Logger()
                cls._instance = super().__new__(cls)
            
            cls.log.INFO('calling singleton class', cls._instance)
            return cls._instance

    def __init__(self) -> None:
        cls = type(self)
        if not hasattr(cls, '_init'):
            self.log.INFO('init')

            cls._init = True

    def check_online(self, host="8.8.8.8", port=53, timeout=3):
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            self.log.INFO('Online')
            return True
        except socket.error as ex:
            self.log.WARNING(ex)
            return False
        except Exception as e:
            self.log.ERROR(e)
            return False

if __name__ == '__main__':
    on = ConnectionCheck()
    print(f'{on.check_online() = }')