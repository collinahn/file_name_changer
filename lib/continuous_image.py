from PIL import Image

class ContinuousImage:
    '''
    파일 경로가 같으면 같은 Image 객체를 반환한다.
    '''
    __instances = {}

    @classmethod
    def open(cls, fp, *args, **kwargs):
        if img:=cls.__instances.get(fp):
            return img

        cls.__instances[fp] = Image.open(fp, *args, **kwargs)
        return cls.__instances[fp]
