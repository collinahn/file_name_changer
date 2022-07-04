# 서버에 흔적을 남긴다

import json
import requests
from requests.exceptions import (
    ConnectionError,
    Timeout,
    HTTPError,
)
from lib.log_gongik import Logger
from lib.check_online import ConnectionCheck
from lib.meta_classes import MetaSingletonThreaded
from lib.__PRIVATE import IP, PORT_API, DOWNLOAD_KEY

class GSLogger(metaclass=MetaSingletonThreaded):
    def __init__(self) -> None:
        self.log = Logger()
        self._server_ip = IP
        self._server_port = PORT_API
        self._url = f'http://{self._server_ip}:{self._server_port}/api/v1/report'
        self._key = DOWNLOAD_KEY
        self._header = {'Auth':self._key}
        self.conn = ConnectionCheck()
        self.connected = self.conn.check_server()
        if not self.connected:
            self.log.WARNING('server not connected')

    def serverlog(self, **kwargs) -> bool:
        if not self.connected:
            return False

        res = self._snitch(**kwargs)

        if res:
            return res.status_code == 200 

        return False

        


    def _snitch(self, **kwargs) -> requests.Response or None:
        try:
            data = json.dumps(kwargs)
            return requests.post(self._url, data=data, headers=self._header, timeout=3)
        except (requests.exceptions.ChunkedEncodingError, ConnectionError, Timeout, HTTPError) as networkerror:
            self.log.ERROR(f'network error occurred {networkerror}')
            return None
        
if __name__ == '__main__':

    gslogger = GSLogger()
    gslogger.serverlog(apple=1, Return_val=3)