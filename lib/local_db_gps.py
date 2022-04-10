# DB에서 정보를 읽어 반환한다

import sqlite3
from sqlite3.dbapi2 import Connection
from haversine import haversine


from .log_gongik import Logger
from .meta_data import GPSInfo
from . import utils

class LocalDB(object):
    def __new__(cls, *args):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)

        cls.log = Logger()
        cls.log.INFO(cls._instance)
        return cls._instance

    def __init__(self, flagThread=None):
        cls = type(self)
        if not hasattr(cls, '_init'):
            self.DB_FILE = utils.resource_path('db/addr.db')

            clsGPS = GPSInfo() #두 번째 호출
            self.gpsData = clsGPS.gps_GRS80

            cls._init = True

    @property
    def gps_radius(self):
        return 130
    
    # 지정된 범위 내의 좌표를 가진 레코드들을 전부 불러온다
    def _query_db(self, tplCoord: tuple[float,float]) -> list[tuple]:
        conn: Connection or None = None
        lstRet: list = []

        xCoord = tplCoord[0]
        yCoord = tplCoord[1]

        try:
            conn = sqlite3.connect(self.DB_FILE)
            curs = conn.cursor()
            query = f"SELECT * FROM tMstSpecs \
                    WHERE xCoord >= {xCoord - self.gps_radius} \
                        AND xCoord <= {xCoord + self.gps_radius} \
                        AND yCoord >= {yCoord - self.gps_radius} \
                        AND yCoord <= {yCoord + self.gps_radius};"
            curs.execute(query)
            lstRet = curs.fetchall()
            # self.log.INFO(f'{lstRet = }')

        except sqlite3.Error as e: 
            self.log.ERROR(e)
        finally:
            if conn: 
                conn.close()

        # print(f'{len(lstRet) = }')
        return lstRet


    # 도로명주소를 반환한다.
    def get_addr(self, tplCoord: tuple[float,float]) -> str:
        lstDBRet = self._query_db(tplCoord)

        if not lstDBRet:
            return 'Undefined'

        minDistance = 999_999_999_999
        minIdx = 0

        for tryIdx, record in enumerate(lstDBRet):
            # 타깃 x, y좌표
            coordFmDB = record[-2:]
            distance = haversine(tplCoord, coordFmDB)
            if minDistance > distance:
                minDistance = distance
                minIdx = tryIdx # 인덱스 추적

        try:
            roadName = lstDBRet[minIdx][7]
        except (AttributeError, IndexError) as es:
            self.log.ERROR(es)
            roadName = 'UndefinedRoadName'

        try:
            buildingNo = lstDBRet[minIdx][9]
        except (AttributeError, IndexError) as es:
            self.log.ERROR(es)
            buildingNo = 'UndefinedBuildingNo'

        try: 
            subBuildingNo: int = int(lstDBRet[minIdx][10])
        except(AttributeError, IndexError) as es:
            self.log.ERROR(es)
            subBuildingNo: int = 0

        # 도로명 + 공백 + 건물번호 + 0이 아닌경우 부속건물번호
        return (
            f'{roadName} {buildingNo}-{subBuildingNo}'
            if subBuildingNo
            else f'{roadName} {buildingNo}'
        )



if __name__ == '__main__':
    ld = LocalDB()
    print(ld.get_addr((931254.5667955369, 1945608.675514717)))