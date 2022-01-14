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

            self._dctName2Addr = {}
            self._dctName2Addr = self.run_thread_get_name()

            cls._init = True

    # 사용안함
    def _get_road_addr_seq(self):
        for orginName, tplGPS in self.clsGPS.gps_GRS80.items():
            self._dctName2Addr[orginName] = self.clsDB.get_addr(tplGPS)
        
        return self._dctName2Addr

    # 스레드 재료
    def _get_road_addr_fm_coord(self, orignName, tplLatLon):
        addr = self.clsDB.get_addr(tplLatLon)

        self._dctName2Addr[orignName] = addr

    # TODO: 적당한 수의 스레드로 나눈다
    def run_thread_get_name(self) -> dict:
        lstThreads = [
            Thread(target=self._get_road_addr_fm_coord, args=(orginName, tplGPS))
            for orginName, tplGPS in self.clsGPS.gps_GRS80.items()
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
    