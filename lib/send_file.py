import requests
import json
from requests.exceptions import (
    ConnectionError,
    Timeout,
    HTTPError,
)

from lib.json_parser import TextParser
from lib.log_gongik import Logger
from lib.__PRIVATE import IP, PORT_API, DOWNLOAD_KEY

class LogFileSender(object):
    def __init__(self, target_file_dir: str) -> None:
        self.log = Logger()

        host = IP
        port = PORT_API

        self.server_url: str = f'http://{host}:{port}/api/v1/log-report'
        self.target_dir: str = target_file_dir

    def _send_server(self) -> requests.Response or None:
        try:
            self.log.INFO(f'putting {self.target_dir} to memory')
            whole_log_file: str = TextParser(self.target_dir).value
            self.log.INFO(f'sending {self.target_dir} to server, size = {len(whole_log_file)}')
            
            requset_header = {
                'auth':DOWNLOAD_KEY
            }
            post_data = json.dumps({
                'log': whole_log_file
            })

            return requests.post(self.server_url, data=post_data, headers=requset_header)
        except (requests.exceptions.ChunkedEncodingError, ConnectionError, Timeout, HTTPError) as networkerror:
            self.log.ERROR(f'network error occurred {networkerror}')
            return None

    def report(self) -> bool:
        res = self._send_server()
        if res.status_code != 200:
            self.log.ERROR(f'{res.content = }')
            return False

        self.log.INFO('log report complete')
        return True