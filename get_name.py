# 추출한 파일 정보를 토대로 api요청을 보낸 뒤 {원래 파일 명:바뀔 파일 명} 형식으로저장한다

from gps_loc import GPSInfo
from local_db_gps import LocalDB
from reverse_geocode import LocationRequest # 사용안함
from threading import Thread


class Name(object):
    def __new__(cls, *args):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)

        print('GPSINFO', cls._instance)
        return cls._instance

    def __init__(self, flagThread=None):
        cls = type(self)
        if not hasattr(cls, '_init'):
            self.clsGPS = GPSInfo()
            self.clsDB = LocalDB()

            self.dctName = {}
            self.dctName = self.get_new_name_thread()

            cls._init = True

    # 사용안함
    def get_name_procedure(self):
        for orginName, tplGPS in self.clsGPS.gps_GRS80.items():
            self.dctName[orginName] = self.clsDB.get_addr(tplGPS)
        
        return self.dctName

    # 스레드 재료
    def get_name_thread(self, orignName, tplLatLon):
        addr = self.clsDB.get_addr(tplLatLon)

        self.dctName[orignName] = addr

    # TODO: 적당한 수의 스레드로 나눈다
    def get_new_name_thread(self) -> dict:
        lstThreads = [
            Thread(target=self.get_name_thread, args=(orginName, tplGPS))
            for orginName, tplGPS in self.clsGPS.gps_GRS80.items()
        ]

        for thread in lstThreads:
            thread.start()

        print('\nthread start')

        for thread in lstThreads:
            thread.join()

        return self.dctName

    @property
    def new_name(self) -> dict:
        return self.dctName

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
    