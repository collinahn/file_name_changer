# 루트폴더의 tesseract-ocr 폴더에 tesseract-ocr-w64-v5.0.1 버전을 설치한다.
#

from PIL import Image 
import pytesseract

import lib.utils as utils
from lib.log_gongik import Logger

pytesseract.pytesseract.tesseract_cmd = rf'{utils.resource_path("")}tesseract-ocr\tesseract.exe'

class ImageOCR(object):
    _setInstance4Init = set()
    _dctInstace4New = {}

    def __new__(cls, fName):
        if fName in cls._dctInstace4New:
            return cls._dctInstace4New[fName]

        cls.log = Logger()
        cls._instance = super().__new__(cls)
        cls._dctInstace4New[fName] = cls._instance
        return cls._instance

    def __init__(self, fName:str) -> None:
        if fName not in self._setInstance4Init:
            self._name: str = fName

            self._image = utils.open_image(fName)
            self._txt = pytesseract.image_to_string(self._image, lang='kor') if self._image else ''

            self._setInstance4Init.add(fName)
            self.log.INFO(fName, 'init')

    @property
    def text(self):
        self.log.INFO(f'called {self._txt = }')
        return self._txt

    def test(self):
        print(f'{self._name = }')
        print(f'{self._txt = }')



if __name__ == '__main__':
    ImageOCR('./1.jpg').test()
    ImageOCR('./2.jpg').test()
    ImageOCR('./3.jpg').test()
    ImageOCR('./4.jpg').test()
    ImageOCR('./5.png').test()