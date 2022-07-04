# 최신 버전 api로부터 정보를 얻어온다

import json
import requests
from requests.exceptions import (
    ConnectionError,
    Timeout,
    HTTPError,
)

from lib.log_gongik import Logger
from lib.__PRIVATE import IP, PORT_API, DOWNLOAD_KEY
from qWordBook import VERSION_INFO
from qWrapper import elapsed

class VersionTeller(object):
    def __new__(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        
        return cls._instance

    def __init__(self):
        cls = type(self)
        if not hasattr(cls, '_init'):
            self.log = Logger()

            # host='127.0.0.1'
            host = IP
            port = PORT_API

            self._url_get_version = f'http://{host}:{port}/api/v1/version-info'
            self.url_download_exe = f'http://{host}:{port}/api/v1/download-latest'

            self.result = self._init_get_data()

            cls._init = True


    def _init_get_data(self) -> dict:
        try:
            request_header = {
                'auth':DOWNLOAD_KEY
            }
            res = requests.get(self._url_get_version, headers=request_header, timeout=3).text
            res = json.loads(res)
            self.log.INFO('version info request received', f'{res = } ')
        except (ConnectionError, Timeout, HTTPError) as ce:
            res = None
            self.log.ERROR(ce)
        return res

    @property
    def new_version(self) -> str:
        if self.result and 'document' in self.result and 'new_version' in self.result['document']:
            return self.result['document']['new_version']

        return ''

    @property
    def is_latest(self) -> bool:
        self.log.INFO(f'checking current version {VERSION_INFO} and new version from server {self.new_version}')
        return self.new_version == VERSION_INFO
    
    @elapsed # 소요 시간 6~12초
    def _download_latest_version(self):
        try:
            self.log.INFO('requesting server latest version')
            return requests.post(self.url_download_exe, data={'pw':DOWNLOAD_KEY})
        except (requests.exceptions.ChunkedEncodingError, ConnectionError, Timeout, HTTPError) as es:
            self.log.ERROR(es)
            return None

    @elapsed # 소요시간 0.1 ~ 0.2초
    def write_latest_version(self, byteStream) -> bool:
        try:
            with open(f'{self.new_version}.exe', 'wb') as f:
                self.log.INFO(f'writing {self.new_version}.exe')
                f.write(byteStream)
        except Exception as e:
            self.log.CRITICAL(e, '/ file write failure')
            return False
        return True
            
    # @elapsed
    def get_latest_version_current_dir(self) -> bool:
        ret = False
        try:
            postResponse = self._download_latest_version()
            self.log.INFO(f'download request result = {postResponse.text}')
            if not postResponse or postResponse.status_code != 200:
                return ret 
    
            if not self.new_version:
                return ret

            ret = self.write_latest_version(postResponse.content)

        except Exception as e:
            self.log.ERROR(e)
            ret = False

        return ret


if __name__ == '__main__':
    vt = VersionTeller()

    print('end')