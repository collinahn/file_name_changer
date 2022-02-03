# 최신 버전 api로부터 정보를 얻어온다

import json
import requests
import asyncio
from requests.exceptions import (
    ConnectionError,
    Timeout,
    HTTPError,
)

from .log_gongik import Logger
from .__PRIVATE import IP, PORT_API, DOWNLOAD_KEY
from qWrapper import elapsed

class VersionTeller(object):
    def __init__(self):
        self.log = Logger()

        # host='127.0.0.1'
        host = IP
        port = PORT_API
        self.key = DOWNLOAD_KEY

        self._url_get_version = f'http://{host}:{port}/api/v1/version-info'
        self.url_download_exe = f'http://{host}:{port}/api/v1/download-latest'

        self.result = self._init_get_data()


    def _init_get_data(self) -> dict:
        try:
            res = requests.get(self._url_get_version, timeout=1.5).text
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
    
    @elapsed # 소요 시간 6~12초
    def _download_latest_version(self):
        try:
            return requests.post(self.url_download_exe, data={'pw':DOWNLOAD_KEY})
        except (requests.exceptions.ChunkedEncodingError, ConnectionError, Timeout, HTTPError) as es:
            self.log.ERROR(es)
            return None

    @elapsed # 소요시간 0.1 ~ 0.2초
    def write_latest_version(self, byteStream) -> bool:
        try:
            with open(self.new_version + '.exe', 'wb') as f:
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