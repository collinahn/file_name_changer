# 순서에 관여하는 클래스

from .log_gongik import Logger


class QueueReadOnly(object):
    # 읽기 전용 큐
    _setInstance4Init = set()
    _dctInstance4New = {}

    def __new__(cls, queueName:str, *args):
        if queueName in cls._dctInstance4New:
            return cls._dctInstance4New[queueName]

        cls.log = Logger()
        cls._instance = super().__new__(cls)
        cls._dctInstance4New[queueName] = cls._instance
        
        cls.log.INFO(cls._instance)
        return cls._instance

    def __init__(self, queueName:str, tplElements: tuple[str]):
        if queueName not in self._setInstance4Init:
            self._name = queueName
            self._lstQueue = [None] * len(tplElements)
            self._queueSize = len(tplElements)
            self._insertPoint = 0
            self._refPoint = 0

            for element in tplElements:
                self._push(element)

            self.log = Logger()
            self.log.INFO(queueName, "Queue init, size:", len(tplElements), self.queue)

            self._setInstance4Init.add(queueName)

    #큐에 데이터를 집어넣고 테일포인트를 옮긴다.
    def _push(self, value) -> bool:
        nextInsPoint = (self._insertPoint+1) % self._queueSize

        # self.log.DEBUG(f'{value = }')
        # self.log.DEBUG(f'{self._queueSize = }')
        # self.log.DEBUG(f'{self._insertPoint = }')
        # self.log.DEBUG(f'{self.queue = }')
        # self.log.DEBUG(f'{self.isOverflow() = }')

        if self.isOverflow():
            self.log.WARNING("Queue Full") 
            return False

        self._lstQueue[self._insertPoint] = value    # 테일포인터가 가르키는 자리에 value삽입
        self._insertPoint = nextInsPoint             # 다음 자리로 테일포인터 이동.

        return True
        
    #큐에서 데이터를 빼고(함수 앞에서 getHead로) 헤드포인트를 옮긴다.
    def view_next(self):
        nextRefPoint = (self._refPoint+1) % self._queueSize

        self._refPoint = nextRefPoint
        return self._lstQueue[self._refPoint]

    def view_previous(self):
        prevRefPoint = self._queueSize-1 if self._refPoint == 0 else self._refPoint-1
        
        self._refPoint = prevRefPoint
        return self._lstQueue[self._refPoint]

    # get oldest push
    @property
    def current_preview(self):
        return self._lstQueue[self._refPoint]
    
    @property
    def current_pos(self) -> int:
        return self._refPoint + 1

    @property
    def queue_size(self) -> int:
        return self._queueSize
    
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