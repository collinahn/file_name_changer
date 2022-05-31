# 순서에 관여하는 클래스

import lib.utils as utils
from lib.log_gongik import Logger
from lib.file_property import FileProp


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
        
        cls.log.INFO(cls._instance)
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

    #초기화시 큐에 데이터를 집어넣는다.
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
        try:
            for idx, ele in enumerate(self._lstQueue):
                self.log.DEBUG(f'{idx} : {ele.name}')
            return self._lstQueue[self._refPoint]
        except IndexError as ie:
            self.log.WARNING(ie, '/ calling invalid refPoint')
            self._refPoint = len(self._lstQueue) -1
            return self._lstQueue[-1]

    # get oldest push
    @property
    def current_preview(self):
        try:
            return self._lstQueue[self._refPoint]
        except IndexError as ie:
                self.log.WARNING(ie, '/ calling invalid refPoint')
                self._refPoint = len(self._lstQueue) -1
                return self._lstQueue[-1]

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
                PropsQueue(correctedLocDB, tuple(nameLst))
                for correctedLocDB, nameLst in dctLoc2Names.items()
            )) # 여기서 loc변수는 유일, 이미 보정된 위치 이름(DB-도로명주소 기준)

            super().__init__('master', tplSingleLocQueeue)
            self._lstQueue: list[PropsQueue] = [None] * len(tplSingleLocQueeue)
            self._queueSize = len(tplSingleLocQueeue)

            for element in tplSingleLocQueeue:
                self._push(element)
            
            self.log.INFO(f'MstQueue init, size = {self.size}, queue = {self.queue}')
            cls._init = True

    @classmethod
    def is_init(cls):
        return hasattr(cls, '_init')

    @property
    def total_size(self):
        ret = 0
        try:
            for file in self.queue:
                file:PropsQueue
                ret += file.size
        except Exception as e:
            self.log.ERROR(e, '/ while getting total number')
            return -1

        return ret

    def add(self, locationKey, fNameKey) -> bool:
        try:
            targetIdx = self._lstQueue.index(PropsQueue(locationKey)) # 마스터 큐에 위치한 장소큐의 위치를 찾는다
            self._lstQueue[targetIdx].append_props(FileProp(fNameKey)) # 찾은 위치에 props 객체 삽입
        except ValueError as ve:
            self.log.ERROR(ve)
            return 1
        return 0 #나중에 모두 더해서 실행 결과 피드백을 준다

    def remove_location(self, instance: QueueReadOnly) -> bool:
        if not self._lstQueue:
            return 1

        try:
            self._lstQueue.remove(instance) #propsQueue객체를 제거
            self.log.INFO(instance.name, 'removed from', self.name)
        except ValueError as ve:
            self.log.ERROR(ve)
            return 2
        
        self._queueSize -= 1

        return 0
    
    def new(self, location: str, tplNames: tuple[str]):
        for name in tplNames:
            if FileProp(name).locationFmDB == location:
                for fName in tplNames: # 추가 전 위치 보정(보통은 초기화 때 보정되는데 나중에 추가되는 애들은 그렇지 않음)
                    fProps = FileProp(fName)
                    fProps.correct_address(dbAddr=location, apiAddr=FileProp(name).locationFmAPI)
                    self.log.INFO(fName, 'Location Updated,', fProps.locationFmDB, 'to', location)
                break
            
                
        self._lstQueue.append(PropsQueue(location, tplNames)) #추가한다.
        self._queueSize += 1

class PropsQueue(QueueReadOnly): # 이미 생성된 FileProp인스턴스를 잡아다 넣어준다.
    _setInstance4Init = set()

    def __init__(self, queueName: str, tplFileNames4Props: tuple[str]=None):
        if queueName not in self._setInstance4Init:

            if not tplFileNames4Props:
                self.log.ERROR('attempting to initialize PropsQueue before files init ')
                return # 초기화가 안됐는데 실행되면 안된다

            self._queueSize = len(tplFileNames4Props)
            self._lstQueue = [None] * self._queueSize
            self._sharedDetail = ''

            super().__init__(queueName, tplFileNames4Props)

            for element in tplFileNames4Props:
                prop = FileProp(element)
                self._push(prop)

                if not hasattr(self, '_tplLocApiDB'):
                    self._tplLocApiDB = prop.location4Display # 맨 처음 나오는 거 대표로 지정

                prop.locationFmAPI, prop.locationFmDB = self._tplLocApiDB # 같은 큐에 있으면 같은 주소로 보여짐

            self.log.INFO(f'{queueName} Queue init, size = {self.size}, queue = {self.queue}')
            self._setInstance4Init.add(queueName) # 도로명주소

    def set_common_details(self, inputDetail):
        '''유저의 입력에 따라 공통 세부사항을 업데이트한다.'''
        for prop in self.queue:
            prop: FileProp
            prop.details = inputDetail
            self._sharedDetail = inputDetail

    def set_common_location(self, inputLocation):
        '''지도 입력으로부터 얻은 공통 신주소로 주소를 업데이트한다'''
        for prop in self.queue:
            prop: FileProp
            prop.locationFmDB = inputLocation

    def append_props(self, instance: FileProp):
        if not isinstance(instance, FileProp):
            self.log.ERROR(f'weired value has inserted to terminal queue {instance}, expecting FileProp instance')
            return

        instance.details = self._sharedDetail
        instance.correct_address(apiAddr=self._tplLocApiDB[0],dbAddr=self._tplLocApiDB[1])
        self._lstQueue.append(instance)
        self._queueSize += 1


    def remove(self, instance: FileProp) -> int:
        if not self._lstQueue:
            return 1
            
        try:
            self._setInstance4Init.discard(self.name)
            self._setInstance4InitParent.discard(self.name)
            self._lstQueue.remove(instance) # list element remove
            self.log.INFO(instance.name, 'removed from', self.name)
            self.log.DEBUG(f'{self._setInstance4InitParent = }, {self._setInstance4Init}')
        except ValueError as ve:
            self.log.ERROR(ve)
            return 2
        
        self._queueSize -= 1
        return 0 

    def remove_many(self, tplNames: tuple) -> int:
        if not self._lstQueue:
            return 1

        ret = 0
        try:
            for fName in tplNames:
                ret += self.remove(FileProp(fName))
        except Exception as e:
            self.log.CRITICAL(e)
        
        return ret

if __name__ == '__main__':
    mq0 = MstQueue((1, None, 3))
    mq1 = MstQueue()
    mq2 = MstQueue((1, 2, 3))
    mq3 = PropsQueue('not master1', (1, 2, 3))
    mq4 = PropsQueue('not master', (1, 2, 3))
    mq5 = PropsQueue('not master2', (1, None, 3))
    mq6 = PropsQueue('not master2')
    print(mq6)

    print(mq0.size)
    print(mq1.size)