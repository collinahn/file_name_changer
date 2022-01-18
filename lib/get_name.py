# 추출한 파일 정보를 토대로 api요청을 보낸 뒤 {원래 파일 명:바뀔 파일 명} 형식으로 저장한다

from threading import Thread


from .log_gongik import Logger
from .meta_data import GPSInfo
from .local_db_gps import LocalDB
from .reverse_geocode import LocationRequest # 사용안함


class Name(object):
    def __new__(cls, *args):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)

        cls.log = Logger()
        cls.log.INFO('NAME', cls._instance)
        return cls._instance

    def __init__(self, *args):
        cls = type(self)
        if not hasattr(cls, '_init'):
            self.clsGPS = GPSInfo()
            self.clsDB = LocalDB()
            self.clsAPI = LocationRequest()

            self.dctName2GPS4API = self.clsGPS.dctGPSInfoWGS84
            self.dctName2GPS4DB = self.clsGPS.dctGPSInfoGRS80

            self._dctName2Addr = {}
            self._dctName2Addr = self.run_thread_get_name() #스레드로
            # self._dctName2Addr = self.run_seq_get_name() #순차

            cls._init = True

    # 사용안함
    def run_seq_get_name(self):
        online = self.clsAPI.check_online()

        for orginName, tplGPS4API in self.dctName2GPS4API.items():
            self._get_addr_fm_coord(online, orginName, tplGPS4API, self.dctName2GPS4DB[orginName])
        
        return self._dctName2Addr

    # 스레드 재료
    def _get_addr_fm_coord(self, online, orignName, tplGPS4API, tplGPS4DB):
        if not online:
            addr = self.clsDB.get_addr(tplGPS4DB)
            self.log.INFO('got info fm DB')
        else:        
            addr = self.clsAPI.parse_addr_response(tplGPS4API)
            self.log.INFO('got info fm API')
        self._dctName2Addr[orignName] = addr


    # TODO: 적당한 수의 스레드로 나눈다
    def run_thread_get_name(self) -> dict:
        online = self.clsAPI.check_online()

        lstThreads = [
            Thread(target=self._get_addr_fm_coord, args=(online, orginName, tplGPS4API, self.dctName2GPS4DB[orginName]))
            for orginName, tplGPS4API in self.dctName2GPS4API.items()
        ]

        for thread in lstThreads:
            thread.start()

        self.log.INFO('threads started')

        for thread in lstThreads:
            try:
                thread.join()
            except Exception as e:
                self.log.CRITICAL(e, '/ caught error while joining')

        return self._dctName2Addr

    @property
    def new_name(self) -> dict:
        return self._dctName2Addr

if __name__ == '__main__':
    import time
    now = time.time()
    n = Name()
    elapsedTime = time.time() - now

    print(n.new_name)
    print(f'for - not threaded : {elapsedTime = }')

    # now = time.time()
    # n = Name("threaded")
    # elapsedTime = time.time() - now

    # print(n.new_name)
    # print(f'threaded : {elapsedTime = }')
    