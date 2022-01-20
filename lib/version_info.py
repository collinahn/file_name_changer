# 최신 버전 api로부터 정보를 얻어온다

import json
import requests
from requests.exceptions import (
    ConnectionError,
    Timeout,
    HTTPError,
)

from .log_gongik import Logger
from .__PRIVATE import IP, PORT_API, DOWNLOAD_KEY

class VersionTeller(object):
    def __init__(self):
        self.log = Logger()

        # host='127.0.0.1'
        host=IP
        port=PORT_API

        self._url_get_version = f'http://{host}:{port}/api/v1/version-info'
        self._url_download_exe = f'http://{host}:{port}/api/v1/download-latest'

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

    def download_latest(self):
        res = None
        try:
            res = requests.post(self._url_download_exe, data={'pw':DOWNLOAD_KEY})
            if res.status_code != 200:
                return None

            with open(self.new_version + '.exe', 'wb') as f:
                f.write(res.content)

        except (requests.exceptions.ChunkedEncodingError, ConnectionError, Timeout, HTTPError) as es:
            self.log.ERROR(es)
            res = None

        return res


if __name__ == '__main__':
    vt = VersionTeller()

    print('end')