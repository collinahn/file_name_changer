# 파일 정보에서 gps 및 시간 확인한다

from PIL import Image
from PIL.ExifTags import TAGS
from pyproj import Proj
from pyproj import transform
from functools import partial

from . import utils
from .log_gongik import Logger
from .file_detect import FileDetector
from .file_property import FileProp

class MetaData(object):
    def __new__(cls, *args):
        cls.__instance = super().__new__(cls)
        cls.log = Logger()
        cls.log.INFO(cls.__instance, "super")
        return cls.__instance

    def __init__(self, targetDir) -> None:
        super().__init__()
        self.targetDir = targetDir
        self.clsFD: FileDetector = FileDetector(targetDir)
        self.lstFiles: list[str] = self.clsFD.file_list

        self._dctMetaData: dict[str, str] = {}
        self._dctDecodedMeta: dict[str, str] = {}

        self._init_meta_data()


    #메타데이터가 있는 사진 파일들의 이름과 메타데이터를 저장한다.
    def _init_meta_data(self):
        for fileName in self.lstFiles:
            fPath = self.targetDir + '/' + fileName
            fileImage = utils.open_image(fPath)

            if not fileImage:
                self.log.ERROR('Failed to open empty image file', fPath)
                continue

            self._dctMetaData[fileName] = fileImage._getexif()

    def _decode_meta_data(self, metadata: dict):
        for key, value in metadata.items():
            decodedData = TAGS.get(key, key)
            self._dctDecodedMeta[decodedData] = value

    def show_image(self, name):
        image: Image = utils.open_image(name)
        if image:
            image.show()


class TimeInfo(MetaData):
    __dctDir2Instance: dict = {}
    __setIsInit: set = set()

    def __new__(cls, targetDir=utils.extract_dir()):
        if targetDir in cls.__dctDir2Instance:
            return cls.__dctDir2Instance[targetDir]

        cls._instance: TimeInfo = super().__new__(cls) 
        cls.__dctDir2Instance[targetDir] = cls._instance

        cls.log.INFO(cls._instance, f'{targetDir = }')
        return cls._instance

    def __init__(self, targetDir=utils.extract_dir()):
        cls = type(self)
        if targetDir not in cls.__setIsInit:
            super().__init__(targetDir)

            self._init_time_info()

            cls.__setIsInit.add(targetDir)

    def _init_time_info(self) -> None:
        for fName, meta in self._dctMetaData.items():
            if not meta:
                continue
            

            self._decode_meta_data(meta)
            
            #시간 메타데이타 초기화
            timeData = self._dctDecodedMeta['DateTimeOriginal'] or self._dctDecodedMeta['DateTimeDigitized'] or self._dctDecodedMeta['DateTime']

            fProperty = FileProp(fName)
            fProperty.time = timeData



class GPSInfo(MetaData):
    def __new__(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)

        cls.log.INFO(cls._instance)
        return cls._instance

    def __init__(self):
        cls = type(self)
        if not hasattr(cls, '_init'):
            super().__init__(utils.extract_dir())
            self.clsFD: FileDetector = FileDetector()
            self.lstFiles: list[str] = self.clsFD.file_list

            self._dctGPSInfoWGS84: dict[str, tuple] = {}
            self._dctGPSInfoGRS80: dict[str, tuple] = {}

            self.__init_gps_WGS84() # 초기화
            self.__init_WGS84_to_GRS80() # 초기화 - 변환

            cls._init = True

    def __init_gps_WGS84(self) -> None:
        for fName, meta in self._dctMetaData.items():
            if not meta:
                continue
            
            self._decode_meta_data(meta)
            self.log.DEBUG(f'{meta}')
            self.log.DEBUG(f'{self._dctDecodedMeta}')
            
            try:
                exifGPS = self._dctDecodedMeta['GPSInfo']
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

                self._dctGPSInfoWGS84[fName] = (Lon, Lat) # 카카오API는 이 순서대로 파라미터를 보냄
            except (ZeroDivisionError, KeyError) as es:
                self.log.ERROR(fName, 'gps data error', es)
                self._dctGPSInfoWGS84[fName] = (0, 0)
            

        self.log.INFO('decode to WGS84 complete')

    # 로컬 DB에서 사용하는 좌표계로 변환한다.
    # TODO: deprecated되었으므로 새로운 버전의 pyproj에서 권장하는 방식으로 업데이트한다.
    def __init_WGS84_to_GRS80(self):
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

        for fName, WGS84xy in self._dctGPSInfoWGS84.items():
            # trans = Transformer(WGS84, GRS80)
            self._dctGPSInfoGRS80[fName] =  trans(WGS84xy[0], WGS84xy[1])
            if WGS84xy == (0, 0):
                self._dctGPSInfoGRS80[fName] = (0, 0) 
        
        self.log.INFO('transfrom to GRS80 complete')
        self.log.INFO(f'{self._dctGPSInfoGRS80 = }')

    @property
    def gps(self):
        return self._dctGPSInfoWGS84

    @property
    def gps_GRS80(self):
        # 로컬 데이터베이스를 사용하는 새로운 모듈에서 활용
        return self._dctGPSInfoGRS80



if __name__ == '__main__':
    gps = GPSInfo()


    # time = TimeInfo(".")
    # time1 = TimeInfo("..")
    # time2 = TimeInfo(".")
    # time4 = TimeInfo(".")