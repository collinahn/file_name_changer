# 추출한 파일 정보를 토대로 api요청을 보낸 뒤 {원래 파일 명:바뀔 파일 명} 형식으로저장한다

from gps_loc import GPSInfo
from reverse_geocode import LocationRequest


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
            self.clsAPI = LocationRequest()

            self.dctName = {}
            if flagThread is None:
                self.dctName = self.get_new_name()
            else:
                self.dctName = self.get_new_name_thread()

            cls._init = True

    def get_new_name(self) -> dict:
        for orginName, tplGPS in self.clsGPS.gps.items():
            addr = self.clsAPI.parse_addr_response(tplGPS[0], tplGPS[1]) # 위도, 경도 튜플

            self.dctName[orginName] = addr

        return self.dctName

    def get_a_name(self, orignName, lat, lon):
        addr = self.clsAPI.parse_addr_response(lat, lon)

        self.dctName[orignName] = addr

    def get_new_name_thread(self) -> dict:
        from threading import Thread
        lstThreads = []

        for orginName, tplGPS in self.clsGPS.gps.items():
            lstThreads.append(Thread(target=self.get_a_name, args=(orginName, tplGPS[0], tplGPS[1])))

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

    del n

    # now = time.time()
    # n = Name("threaded")
    # elapsedTime = time.time() - now

    # print(n.new_name)
    # print(f'threaded : {elapsedTime = }')
    