# DB에서 정보를 읽어 반환한다

import sqlite3
from sqlite3.dbapi2 import Connection
from haversine import haversine

from gps_loc import GPSInfo
import utils

class LocalDB(object):
    def __new__(cls, *args):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)

        print('LOCALDB', cls._instance)
        return cls._instance

    def __init__(self, flagThread=None):
        cls = type(self)
        if not hasattr(cls, '_init'):
            self.DB_FILE = utils.resource_path('db/addr.db')

            clsGpsInfo = GPSInfo()
            self.gpsData = clsGpsInfo.gps_GRS80

            cls._init = True

    @property
    def gps_radius(self):
        return 130

    # 도로명주소를 반환한다.
    def get_addr(self, tplCoord: tuple[float,float]) -> str:
        lstDBRet = self.__query_db(tplCoord)

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

        # 도로명 + 공백 + 건물번호
        return lstDBRet[minIdx][7] + " " + lstDBRet[minIdx][9]

            

    
    # 지정된 범위 내의 좌표를 가진 레코드들을 전부 불러온다
    def __query_db(self, tplCoord: tuple[float,float]) -> list[tuple]:
        conn: Connection = None
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

        except sqlite3.Error as e: 
            print(e)
        finally:
            if conn: 
                conn.close()

        print(f'{lstRet = }')
        print(f'{len(lstRet) = }')
        return lstRet



if __name__ == '__main__':
    ld = LocalDB()
    print(ld.get_addr((931254.5667955369, 1945608.675514717)))