# 파일 정보에서 gps 및 시간 확인한다
# TODO: 부모 클래스 만들어서 상속받기 -> utils로 간 open_image도 다시 가져오기

from PIL import Image
from PIL import UnidentifiedImageError
from PIL.ExifTags import TAGS
from pyproj import Proj
from pyproj import transform
from functools import partial

from . import utils
from .file_detect import FileDetector

class TimeInfo(object):
    __dctDir2Instance: dict = {}
    __setIsInit: set = set()

    def __new__(cls, targetDir=utils.extract_dir()):
        if targetDir in cls.__dctDir2Instance:
            return cls.__dctDir2Instance[targetDir]

        cls._instance: TimeInfo = super().__new__(cls) 
        cls.__dctDir2Instance[targetDir] = cls._instance
        print(f'TIME_INFO {targetDir =}', cls._instance)
        return cls._instance

    def __init__(self, targetDir=utils.extract_dir()):
        cls = type(self)
        if targetDir not in cls.__setIsInit:
            self.targetDir = targetDir
            self.clsFD = FileDetector(targetDir)
            self.fileList = self.clsFD.fileList
            print(f'{self.fileList = }')

            self.dctMetaData: dict = {}
            self.dctDecodedMeta: dict = {}
            self.dctTimeFilesMade: dict = {}

            self.init_meta_data()
            self.extract_time_info()

            cls.__setIsInit.add(targetDir)

    #메타데이터가 있는 사진 파일들의 이름과 메타데이터를 저장한다.
    def init_meta_data(self):
        for fileName in self.fileList:
            fileImage = utils.open_image(self.targetDir+'/'+fileName)

            if not fileImage:
                continue

            self.dctMetaData[fileName] = fileImage._getexif()

    def decode_meta_data(self, metadata):
        for key, value in metadata.items():
            decodedData = TAGS.get(key, key)
            self.dctDecodedMeta[decodedData] = value

    def extract_time_info(self) -> None:
        for fName, meta in self.dctMetaData.items():
            if not meta:
                continue

            self.decode_meta_data(meta)
            
            #시간 메타데이타 초기화
            timeFile = self.dctDecodedMeta['DateTimeOriginal'] or self.dctDecodedMeta['DateTimeDigitized'] or self.dctDecodedMeta['DateTime']
            self.dctTimeFilesMade[fName] = timeFile
    
    @property
    def time_as_str(self):
        return self.dctTimeFilesMade

    @property
    def time(self):
        dctRet: dict[str,int] = {}
        for fName, time in self.dctTimeFilesMade.items():
            tmp = time.split()
            try:
                hhmmss = tmp[1].split(':') #시 분 초 추출
                timeAsSeconds = int(hhmmss[0]) * 3600 + int(hhmmss[1]) * 60 + int(hhmmss[2])
            except (AttributeError, IndexError) as ae:
                print(f'error: invalid time metadata - {ae}')
                continue

            dctRet[fName] = timeAsSeconds

        return dctRet



class GPSInfo(object):
    def __new__(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)

        print('GPS_INFO', cls._instance)
        return cls._instance

    def __init__(self):
        cls = type(self)
        if not hasattr(cls, '_init'):
            self.clsFD: FileDetector = FileDetector()
            self.lstFiles: list[str] = self.clsFD.fileList

            self.dctTimeFilesMade: dict[str, str] = {} #디코딩할 때 초기화

            self.dctMetaData: dict[str, str] = {}
            self.dctDecodedMeta: dict[str, str] = {}
            self.__dctGPSInfoWGS84: dict[str, tuple] = {}
            self.dctGPSInfoGRS80: dict[str, tuple] = {}

            self.init_meta_data()
            self.extract_gps_data() # 초기화 -deprecated
            self.set_WGS84_to_GRS80()

            cls.__init = True

    #메타데이터가 있는 사진 파일들의 이름과 메타데이터를 저장한다.
    def init_meta_data(self):
        for fileName in self.lstFiles:
            fileImage = utils.open_image(fileName)

            # if not fileImage:
            #     continue
            try:
                self.dctMetaData[fileName] = fileImage._getexif()
            except AttributeError:
                continue
        # print(f"{self.dctMetaData = }")

    def decode_meta_data(self, metadata):
        for key, value in metadata.items():
            decodedData = TAGS.get(key, key)
            self.dctDecodedMeta[decodedData] = value

    def extract_gps_data(self) -> None:
        for fName, meta in self.dctMetaData.items():
            if not meta:
                continue

            self.decode_meta_data(meta)
            
            try:
                exifGPS = self.dctDecodedMeta['GPSInfo']
                latData = exifGPS[2]
                lonData = exifGPS[4]

            # 도, 분, 초 계산
                latDeg = float(latData[0])
                latMin = float(latData[1])
                latSec = float(latData[2])

                lonDeg = float(lonData[0])
                lonMin = float(lonData[1])
                lonSec = float(lonData[2])

                # 도 decimal로 나타내기
                # 위도 계산
                Lat = (latDeg + (latMin + latSec / 60.0) / 60.0)
                # 북위, 남위인지를 판단, 남위일 경우 -로 변경
                if exifGPS[1] == 'S': 
                    Lat = Lat * -1

                # 경도 계산
                Lon = (lonDeg + (lonMin + lonSec / 60.0) / 60.0)
                # 동경, 서경인지를 판단, 서경일 경우 -로 변경
                if exifGPS[3] == 'W': 
                    Lon = Lon * -1

                self.__dctGPSInfoWGS84[fName] = (Lon, Lat) # 카카오API는 이 순서대로 파라미터를 보냄
            except (ZeroDivisionError, KeyError) as ze:
                print(ze)
                print(f'{fName} gps info not found.')
                self.__dctGPSInfoWGS84[fName] = (0, 0)
            

        print('decode to WGS84 done')
        # print(f'{self.__dctGPSInfoWGS84 = }')
        # print(f'{self.dctTimeFilesMade = }')

    # 로컬 DB에서 사용하는 좌표계로 변환한다.
    # TODO: deprecated되었으므로 새로운 버전의 pyproj에서 권장하는 방식으로 업데이트한다.
    def set_WGS84_to_GRS80(self):
        WGS84 = {
            'proj':'latlong', 
            'datum':'WGS84', 
            'ellps':'WGS84', 
        }
        GRS80 = { 
            'proj':'tmerc', 
            'lat_0':'38', 
            'lon_0':'127.5', 
            'k':0.9996, 
            'x_0':1_000_000, 
            'y_0':2_000_000, 
            'ellps':'GRS80', 
            'units':'m' 
        }

        projWGS84 = Proj(**WGS84) #'epsg:4326'
        projGRS80 = Proj(**GRS80)
        trans = partial(transform, projWGS84, projGRS80)

        for fName, WGS84xy in self.__dctGPSInfoWGS84.items():
            # trans = Transformer(WGS84, GRS80)
            self.dctGPSInfoGRS80[fName] =  trans(WGS84xy[0], WGS84xy[1])
        
        print('transfrom to GRS80 complete')
        # print(f'{self.dctGPSInfoGRS80 = }')

    @property
    def gps(self):
        return self.__dctGPSInfoWGS84

    @property
    def gps_GRS80(self):
        # 로컬 데이터베이스를 사용하는 새로운 모듈에서 활용
        return self.dctGPSInfoGRS80



if __name__ == '__main__':
    gps = GPSInfo()

    time = TimeInfo(".")
    time1 = TimeInfo("..")
    time2 = TimeInfo(".")
    time4 = TimeInfo(".")
    print(time.dctTimeFilesMade)

