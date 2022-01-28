# 순서에 관여하는 클래스

from . import utils
from .log_gongik import Logger
from .file_property import FileProp


class QueueReadOnly(object):
    # 읽기 전용 큐
    _setInstance4InitParent = set()
    _dctInstance4New = {}

    def __new__(cls, queueName:str, *args):
        if queueName in cls._dctInstance4New:
            return cls._dctInstance4New[queueName]

        cls.log = Logger()
        cls._instance = super().__new__(cls)
        cls._dctInstance4New[queueName] = cls._instance
        
        cls.log.INFO('calling', cls._instance)
        return cls._instance

    def __init__(self, queueName:str, tplElements: tuple[str]):
        if queueName not in self._setInstance4InitParent:
            self._name = queueName
            self._lstQueue = [None] * len(tplElements)
            self._queueSize = len(tplElements)
            self._insertPoint = 0
            self._refPoint = 0

            self.log = Logger()

            self._setInstance4InitParent.add(queueName)

    def __str__(self) -> str:
        return self._name if hasattr(self, '_name') else super().__str__()

    #큐에 데이터를 집어넣는다.
    def _push(self, value) -> bool:
        nextInsPoint = (self._insertPoint+1) % self._queueSize

        if self.isOverflow():
            self.log.WARNING("Queue Full") 
            return False

        self._lstQueue[self._insertPoint] = value    # 테일포인터가 가르키는 자리에 value삽입
        self._insertPoint = nextInsPoint             # 다음 자리로 테일포인터 이동.

        return True
        
    #큐에서 데이터를 빼고(함수 앞에서 getHead로) 헤드포인트를 옮긴다.
    def view_next(self) -> object:
        nextRefPoint = (self._refPoint+1) % self._queueSize

        self._refPoint = nextRefPoint
        return self._lstQueue[self._refPoint]

    def view_previous(self) -> object:
        prevRefPoint = self._queueSize-1 if self._refPoint == 0 else self._refPoint-1
        
        self._refPoint = prevRefPoint
        return self._lstQueue[self._refPoint]

    def refresh(self) -> object:
        return self._lstQueue[self._refPoint]

    # get oldest push
    @property
    def current_preview(self):
        return self._lstQueue[self._refPoint]
    
    @property
    def current_pos(self) -> int:
        return self._refPoint + 1

    @property
    def size(self) -> int:
        return sum(bool(file) for file in self.queue)
    
    @property
    def name(self) -> str:
        return self._name

    @property
    def queue(self) -> list:
        return self._lstQueue

    def isEmpty(self) -> bool:
        return self._refPoint == self._insertPoint

    def isOverflow(self) -> bool:
        return False if self.isEmpty() else self._insertPoint == 0

    def add(self, loc, name) -> bool:
        raise NotImplementedError()

    def detach(self, loc, name) -> bool:
        raise NotImplementedError()

class MstQueue(QueueReadOnly): # 분류해서 집어넣음
    def __new__(cls, *args):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls, 'master')
        
        cls.log.INFO('calling singleton queue:', cls._instance)
        return cls._instance

    def __init__(self):
        cls = type(self)
        if not hasattr(cls, '_init'):

            dctLoc2Names = utils.invert_dict(FileProp.name2AddrDBCorrected()) #도로명주소를 기준으로 정렬 후 초기화
            tplSingleLocQueeue = tuple((
                PropsQueue(loc, tuple(nameLst))
                for loc, nameLst in dctLoc2Names.items()
            )) # 여기서 loc변수는 유일, 이미 보정된 위치 이름(DB-도로명주소 기준)

            super().__init__('master', tplSingleLocQueeue)
            self._lstQueue = [None] * len(tplSingleLocQueeue)
            self._queueSize = len(tplSingleLocQueeue)

            for element in tplSingleLocQueeue:
                self._push(element)
            
            self.log.INFO(f'MstQueue init, size = {self.size}, queue = {self.queue}')
            cls._init = True

    @property
    def total_size(self):
        ret = 0
        try:
            for file in self.queue:
                ret += file.size
        except Exception as e:
            self.log.ERROR(e, '/ while getting total number')

        return ret

    def add(self, locationKey, fNameKey) -> bool:
        try:
            targetIdx = self._lstQueue.index(PropsQueue(locationKey))
            self._lstQueue[targetIdx].append(FileProp(fNameKey))
        except ValueError as ve:
            self.log.ERROR(ve)
            return False
        return True

    def remove(self, instance: QueueReadOnly) -> bool:
        if not self._lstQueue:
            return False
        try:
            self._lstQueue.remove(instance)
            self.log.DEBUG(instance.name, 'removed from', self.name)
        except ValueError as ve:
            self.log.ERROR(ve)
            return False
        
        self._queueSize -= 1

        return True  
    
    def new(self):
        raise NotImplementedError()
class PropsQueue(QueueReadOnly): # 이미 생성된 FileProp인스턴스를 잡아다 넣어준다.
    _setInstance4Init = set()

    def __init__(self, queueName: str, tplElements: tuple[str]=(None, )):
        if queueName not in self._setInstance4Init:

            if tplElements == (None, ):
                raise RuntimeError() # 초기화가 안됐는데 실행되면 안된다

            self._lstQueue = [None] * len(tplElements)
            self._queueSize = len(tplElements)
            self._sharedDetail = ''

            super().__init__(queueName, tplElements)

            for element in tplElements:
                prop = FileProp(element)
                self._push(prop)

                if not hasattr(type(self), '_tplLocApiDB'):
                    self._tplLocApiDB = prop.location4Display

            self.log.INFO(f'{queueName} Queue init, size = {self.size}, queue = {self.queue}')
            self._setInstance4Init.add(queueName) # 도로명주소

    def common_details(self, inputDetail):
        for prop in self.queue:
            prop: FileProp
            prop.details = inputDetail
            self._sharedDetail = inputDetail

    def append(self, instance: FileProp):
        if not isinstance(instance, FileProp):
            raise ValueError()

        instance.details = self._sharedDetail
        instance.correct_address(apiAddr=self._tplLocApiDB[0],dbAddr=self._tplLocApiDB[1])
        self._lstQueue.append(instance)
        self._queueSize += 1


    def remove(self, instance: FileProp) -> bool:
        if not self._lstQueue:
            return False
        try:
            self._lstQueue.remove(instance)
            self.log.DEBUG(instance.name, 'removed from', self.name)
        except ValueError as ve:
            self.log.ERROR(ve)
            return False
        
        self._queueSize -= 1

        return True  


if __name__ == '__main__':
    mq0 = MstQueue((1, None, 3))
    mq1 = MstQueue()
    mq2 = MstQueue((1, 2, 3))
    mq3 = PropsQueue('not master1', (1, 2, 3))
    mq4 = PropsQueue('not master2', (1, 2, 3))
    mq5 = PropsQueue('not master2', (1, None, 3))
    mq6 = PropsQueue('not master2')
    print(mq6)

    print(mq0.size)
    print(mq1.size)