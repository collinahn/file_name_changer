from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from PIL import UnidentifiedImageError

from lib.continuous_image import ContinuousImage
from lib.file_property import FileProp
from lib.log_gongik import Logger
import lib.utils as utils

class Stamp:
    '''
    사진에 스탬프를 추가한다
    '''
    def __init__(self, file_prop: FileProp) -> None:
        self.log: Logger = Logger()
        self.file: FileProp = file_prop
        self.text: str = ''
        self.text_width = 0
        self.text_height = 0
        self.fontsize = 60
        self.fontcolor = (0, 0, 0)
        self.font = self._update_font()
        try:
            self.img: Image = ContinuousImage.open(self.file.abs_path)
            self.draw: ImageDraw = ImageDraw.Draw(self.img)
        except (FileNotFoundError, UnidentifiedImageError) as ie:
            self.log.ERROR(ie)
            self.img = None
            self.draw = None
        except Exception as e:
            self.log.CRITICAL(e)
            self.img = None
            self.draw = None
        
        self.img_width, self.img_height = 0, 0
        if self.img:
            self.img_width, self.img_height = self.img.size

    def _set_text(self, text):
        self.text = text
        self.text_width, self.text_height = self.font.getsize(text)

    def _update_font(self):
        return ImageFont.truetype(utils.resource_path('fonts/NanumBarunGothic.ttf'), size=int(self.fontsize))

    def set_fontsize(self, size):
        self.fontsize = size
        self.font = self._update_font()
        self.log.INFO(f'font size changed to {self.fontsize}')

    def flip_color(self):
        self.fontcolor = tuple( abs(color-255) for color in self.fontcolor )
        self.font = self._update_font()
        self.log.INFO(f'font color changed to {self.fontcolor}')

    def align(self):
        '''텍스트 선정 위치를 결정한다. 기본은 가운데(사용안함)'''
        return (self.img_width/2-self.text_width/2, self.img_height/2-self.text_height/2)

    def stamp(self):
        try:
            self.draw.text(self.align(), self.text, font=self.font, fill=self.fontcolor)
            self.log.INFO(f'{self.align() = }, {self.text = }, {self.fontcolor = }')
        except AttributeError as ae:
            self.log.ERROR(ae)

    def save_img(self):
        raise NotImplementedError()

class TimeStamp(Stamp):
    '''
    좌측 상단 타임스탬프
    '''
    def __init__(self, file_prop: FileProp) -> None:
        super().__init__(file_prop)

        self.text = self.file.time.strftime('%Y-%m-%d %H:%M:%S')
        super()._set_text(self.text)

    def align(self):
        return (self.text_width/10, self.text_height/5)

class LocalStamp(Stamp):
    '''
    우측 상단 지역 스탬프
    '''
    def __init__(self, file_prop: FileProp) -> None:
        super().__init__(file_prop)
        
        self.text = self.file.locationFmAPI
        super()._set_text(self.text)

    def align(self):
        return (self.img_width-self.text_width*11/10, self.text_height/5)

class DetailStamp(Stamp):
    '''
    우측 하단 입력사항 스탬프
    '''
    def __init__(self, file_prop: FileProp) -> None:
        super().__init__(file_prop)

        self.text = self.file.specific_details or self.file.details
        super()._set_text(self.text)

    def align(self):
        return (self.img_width-self.text_width*11/10, self.img_height-self.text_height*6/5)

if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    from lib.base_folder import WorkingDir
    WorkingDir('.', '.')
    app = QApplication(sys.argv)

    file = FileProp('2.jpg')
    file.details = '랜덤 txt'
    file.locationFmAPI = 'api 주소'

    ts = TimeStamp(file)
    ts.stamp()
    ts.img.show()

    ls = LocalStamp(file)
    ls.stamp()
    ls.img.show()

    cm = DetailStamp(file)
    cm.flip_color()
    cm.stamp()
    cm.img.show()