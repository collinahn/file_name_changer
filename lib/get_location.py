# 추출한 파일 정보를 토대로 api요청을 보낸 뒤 {원래 파일 명:바뀔 파일 명} 형식으로 저장한다

from threading import Thread



from .check_online import ConnectionCheck
from .log_gongik import Logger
from .meta_data import GPSInfo
from .local_db_gps import LocalDB
from .reverse_geocode import LocationRequest #온라인 체크
from .file_property import FileProp


class LocationInfo(object):
    def __new__(cls, *args):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)

        cls.log = Logger()
        cls.log.INFO('NAME', cls._instance)
        return cls._instance

    def __init__(self, targetFolder, *args):
        cls = type(self)
        if not hasattr(cls, '_init'):
            self.path = targetFolder
            self.clsGPS = GPSInfo(targetFolder)
            self.clsDB = LocalDB()
            self.clsAPI = LocationRequest()

            self._dctName2GPS4API = self.clsGPS._dctGPSInfoWGS84
            self._dctName2GPS4DB = self.clsGPS._dctGPSInfoGRS80

            self.run_thread_get_name() # 온라인이 아닌 경우 둘 다 DB 주소가 된다

            cls._init = True

    def _get_db_addr_fm_coord(self):
        for orginName, tplGPS4DB in self._dctName2GPS4DB.items():
            prop = FileProp(orginName, path=self.path)

            prop.locationFmDB = self.clsDB.get_addr(tplGPS4DB)
            self.log.INFO(f'got info fm DB, {orginName} {tplGPS4DB} -> {prop.locationFmDB}')
        

    # 스레드 재료
    def _get_api_addr_fm_coord(self, originName, tplGPS4API):
        prop = FileProp(originName, path=self.path)
        prop.locationFmAPI = self.clsAPI.parse_addr_response(tplGPS4API)
        prop.coord = tuple(list(tplGPS4API)[::-1]) # 후에 써먹기 유리하도록 순서를 뒤집는다
        self.log.INFO(f'got info fm API, {originName} {tplGPS4API} -> {prop.locationFmAPI}')


    # TODO: 적당한 수의 스레드로 나눈다
    def run_thread_get_name(self) -> dict:
        clsO = ConnectionCheck()
        online = clsO.check_online()
        
        lstThreads = [
            Thread(target=self._get_api_addr_fm_coord, args=(orginName, tplGPS4API))
            for orginName, tplGPS4API in self._dctName2GPS4API.items()
        ] if online else []

        lstThreads.append(Thread(target=self._get_db_addr_fm_coord))

        for thread in lstThreads:
            thread.start()

        self.log.INFO('threads started')


        for thread in lstThreads:
            try:
                thread.join()
            except Exception as e:
                self.log.CRITICAL(e, '/ caught error while joining')


if __name__ == '__main__':
    import time
    now = time.time()
    n = LocationInfo()
    # elapsedTime = time.time() - now

    # print(f'{elapsedTime = }')
    # time.sleep(5)
    # print(FileProp('1 (2).jpg').name2AddrAPIOrigin())

    # n.run_thread_get_name()