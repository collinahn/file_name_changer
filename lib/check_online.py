import socket
import requests
from threading import Lock

from lib.log_gongik import Logger
from lib.__PRIVATE import IP, PORT_API, DOWNLOAD_KEY

class ConnectionCheck(object):
    lock = Lock()
    def __new__(cls):
        with cls.lock:
            if not hasattr(cls, '_instance'):
                cls.log = Logger()
                cls._instance = super().__new__(cls)
            
            return cls._instance

    def __init__(self) -> None:
        cls = type(self)
        if not hasattr(cls, '_init'):
            self.log.INFO('init')
            self.server_connected = None
            self._url_server_health_check =  f'http://{IP}:{PORT_API}/api/v1/server-health-check'

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

    def check_server(self, *, timeout=3):
        '''
        check server is alive
        response from server is cached
        '''
        if self.server_connected is not None:
            return self.server_connected
        return self._server_health_check(timeout)
    
    def _server_health_check(self, timeout) -> bool:
        try:
            request_header = {
                'Auth':DOWNLOAD_KEY
            }
            status = requests.get(self._url_server_health_check, headers=request_header, timeout=timeout).status_code
            if status == 200:
                self.server_connected = True
                self.log.INFO('Server Online')
                return True
        except socket.error as ex:
            self.server_connected = False
            self.log.WARNING(ex)
            return False
        except Exception as e:
            self.server_connected = False
            self.log.ERROR(e)
            return False
        self.log.WARNING('Auth Failed')
        return False


if __name__ == '__main__':
    on = ConnectionCheck()
    print(f'{on.check_online() = }')
    print(f'{on.check_server() = }')