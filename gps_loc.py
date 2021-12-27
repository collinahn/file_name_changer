# 파일 정보에서 gps 확인한다

from PIL import Image
from PIL import UnidentifiedImageError
from PIL.ExifTags import TAGS

from file_detect import FileDetector


class GPSInfo(object):
    def __new__(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)

        print('GPS_INFO', cls._instance)
        return cls._instance

    def __init__(self):
        cls = type(self)
        if not hasattr(cls, '_init'):
            self.clsDetect: FileDetector = FileDetector()
            self.lstFiles: list[str] = self.clsDetect.fileList

            self.dctMetaData: dict[str, str] = {}
            self.dctDecodedMeta: dict[str, str] = {}
            self.dctGPSInfo: dict[str,tuple] = {}

            self.init_meta_data()
            self.decode_meta_data() # 초기화

            cls.__init = True

    #메타데이터가 있는 사진 파일들의 이름과 메타데이터를 저장한다.
    def init_meta_data(self):
        for fileName in self.lstFiles:
            fileImage = self._open_image(fileName)

            if not fileImage:
                continue

            self.dctMetaData[fileName] = fileImage._getexif()
        
        print(f"{self.dctMetaData = }")

    @staticmethod
    def _open_image(name):
        image: Image = None
        try:
            image = Image.open(name)
        except UnidentifiedImageError as ue:
            print(ue, name)
        
        return image

    def decode_meta_data(self):
        for fName, meta in self.dctMetaData.items():

            for key, value in meta.items():
                decodedData = TAGS.get(key, key)
                self.dctDecodedMeta[decodedData] = value

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

            self.dctGPSInfo[fName] = (Lon, Lat) # 카카오API는 이 순서대로 파라미터를 보냄

        print('decode done')
        print(f'{self.dctGPSInfo = }')

    @property
    def gps(self):
        return self.dctGPSInfo




if __name__ == '__main__':
    gps = GPSInfo()

