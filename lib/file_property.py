# 파일들의 속성(=유저의 입력값)을 저장한다
# TODO: gui프로그램에서 MVC 패턴을 적용한다

from threading import Lock
from datetime import (
    datetime, 
    timedelta
)

from .log_gongik import Logger
import qWordBook as const
from . import utils

class FileProp(object):
    _setInstance4Init = set()
    _dctInstace4New = {}
    _prefix = utils.get_car_no_from_parent_dir()
    _lock = Lock()

    def __new__(cls, fileName:str, *args):
        with cls._lock:
            if fileName in cls._dctInstace4New:
                return cls._dctInstace4New[fileName]

            cls.log = Logger()
            cls._instance = super().__new__(cls)
            cls._dctInstace4New[fileName] = cls._instance
            cls.log.INFO(fileName, cls._instance)
            return cls._instance

    def __init__(self, name:str, *args) -> None:
        if name not in self._setInstance4Init:
            self._name: str = name
            self._time: datetime = datetime.strptime('0001:01:01 00:00:00', '%Y:%m:%d %H:%M:%S')
            self._originLocAPI: str = '' #파일 기본 지번주소
            self._originLocDB: str = ''  #파일 기본 도로명주소
            self._locationAPI: str = ''  #보정된 지번주소
            self._locationDB: str = ''   #보정된 도로명주소
            self._details: str = ''          #상세(같은 주소면 동일한 상세)
            self._details_priority: str = '' #단일 인스턴스 상세(우선순위 높음)
            self._suffix: str = ''

            self._setInstance4Init.add(name)
            self.log.INFO(name, 'fileProp init', f'{self._name = }, {self._originLocAPI = }')


    def __str__(self) -> str:
        return self._name if hasattr(self, '_name') else super().__str__()

    @property
    def name(self) -> str:
        return self._name

    @property
    def time(self) -> datetime:
        return self._time

    @time.setter
    def time(self, newTime:str):
        try:
            self._time = datetime.strptime(newTime, '%Y:%m:%d %H:%M:%S')
        except Exception as e:
            self.log.CRITICAL(e)

    @property
    def prefix(self):
        return self._prefix

    @prefix.setter
    def prefix(self, newPrefix):
        if newPrefix not in utils.get_car_candidates():
            self.log.WARNING('wrong car number received,', newPrefix)

        self._prefix = newPrefix

    @property
    def location4Display(self):
        return self._locationAPI, self._locationDB

    @property
    def locationAPI(self):
        return self._originLocAPI

    @locationAPI.setter
    def locationAPI(self, newLoc):
        if self._originLocAPI == newLoc:
            self.log.WARNING('attempting to do meaningless insert,', newLoc)

        if not self._originLocAPI:
            self._originLocAPI = newLoc
        self._locationAPI = newLoc

    @property
    def locationDB(self):
        return self._originLocDB

    @locationDB.setter
    def locationDB(self, newLoc):
        if self._originLocDB == newLoc:
            self.log.WARNING('attempting to do meaningless insert,', newLoc)

        if not self._originLocDB:
            self._originLocDB = newLoc
        self._locationDB = newLoc

    @property
    def details(self):
        return self._details

    @details.setter
    def details(self, newDetail):
        self._details = newDetail

    @property
    def specific_details(self):
        return self._details_priority

    @specific_details.setter
    def specific_details(self, newDetail):
        self._details_priority = newDetail

    @property
    def suffix(self):
        return self._suffix

    @suffix.setter
    def suffix(self, newSuf):
        self._suffix = newSuf


    @classmethod
    def name2AddrAPIOrigin(cls):
        return {
            name: instance._originLocAPI
            for name, instance in cls._dctInstace4New.items()
        }

    @classmethod
    def name2AddrDBOrigin(cls):
        return {
            name: instance._originLocDB
            for name, instance in cls._dctInstace4New.items()
        }

    @classmethod
    def name2AddrDBCorrected(cls):
        return {
            name: instance._locationDB
            for name, instance in cls._dctInstace4New.items()
        }

    @classmethod
    def name2Time(cls):
        return {
            name:instance._time
            for name, instance in cls._dctInstace4New.items()
        }

    @classmethod
    def get_names(cls):
        return list(cls._setInstance4Init)

    @property
    def final_road_name(self): # 간략화
        details = f' {self._details}' if self._details else ''
        suffix = f' {self._suffix}' if self._suffix else ''
        
        return ''.join((
            self._prefix,
            '_',
            self._locationDB or 'Undefined',
            details if not self._details_priority else f' {self._details_priority}',
            suffix
        ))
    
    @property
    def final_normal_name(self): # 간략화
        details = f' {self._details}' if self._details else ''
        suffix = f' {self._suffix}' if self._suffix else ''
        
        return ''.join((
            self._prefix,
            '_',
            self._locationAPI or 'Undefined',
            details if not self._details_priority else f' {self._details_priority}',
            suffix
        ))
    
    @property
    def final_full_name(self): #상세 버전
        details = f' {self._details}' if self._details else ''
        suffix = f' {self._suffix}' if self._suffix else ''
        
        return ''.join((
            self._prefix,
            '_',
            self._locationAPI or 'Undefined',
            f'({self._locationDB})',
            details if not self._details_priority else f' {self._details_priority}',
            suffix
        ))

    # 수정할 땐 이걸로
    def correct_address(self, apiAddr:str='', dbAddr:str=''):
        if apiAddr:
            self._locationAPI = apiAddr
        if dbAddr:
            self._locationDB = dbAddr
  

    @classmethod
    def self_correct_address(cls):
        dctName2Time = cls.name2Time()
        lstTimePicTakenSorted = sorted(list(dctName2Time.values()))
        cls.log.DEBUG(lstTimePicTakenSorted)
        cls.log.DEBUG(dctName2Time)
        dctTimeLaps: dict[datetime,str] = {} #기준 시간과 주소 삽입
        timeStandard = lstTimePicTakenSorted[0] #for루프를 돌 때 기준이 되는 시간
        
        for datePic in lstTimePicTakenSorted:
            timeGap: timedelta = datePic - timeStandard
            if timeGap.total_seconds() > const.TIME_GAP:
                timeStandard: datetime = datePic
                for fName, tDate in dctName2Time.items():
                    if tDate == timeStandard:
                        fProp: FileProp = cls._dctInstace4New[fName]
                        dctTimeLaps[timeStandard] = fProp.locationDB, fProp.locationAPI

        for fName, tDate in dctName2Time.items():
            for tMin, (addrDB, addrAPI) in dctTimeLaps.items():
                tGap: timedelta = tDate - tMin
                if tGap.total_seconds() < const.TIME_GAP and tGap.total_seconds() >= 0:
                    try:
                        fProp = FileProp(fName)
                        cls.log.INFO(fName, fProp.locationDB, '->', addrDB, ', ', fProp.locationAPI, '->', addrAPI)
                        fProp.correct_address(dbAddr=addrDB, apiAddr=addrAPI) #sorting 기준 = db addr
                        break
                    except AttributeError as ae:
                        cls.log.ERROR(ae)



    @classmethod
    def debug_info(cls):
        for name, instance in cls._dctInstace4New.items():
            instance: FileProp

            cls.log.DEBUG()
            cls.log.DEBUG()
            cls.log.DEBUG()
            cls.log.DEBUG(f'instance {name = }')
            cls.log.DEBUG()
            cls.log.DEBUG(f'attribute {instance._name = }')
            cls.log.DEBUG(f'attribute {instance._time = }')
            cls.log.DEBUG(f'attribute {instance._originLocAPI = }')
            cls.log.DEBUG(f'attribute {instance._originLocDB = }')
            cls.log.DEBUG(f'attribute {instance._locationAPI = }')
            cls.log.DEBUG(f'attribute {instance._locationDB = }')
            cls.log.DEBUG(f'attribute {instance._details = }')
            cls.log.DEBUG(f'attribute {instance._suffix = }')
            cls.log.DEBUG()
            cls.log.DEBUG(f'property {instance.name = }')
            cls.log.DEBUG(f'property {instance.prefix = }')
            cls.log.DEBUG(f'property {instance.locationAPI = }')
            cls.log.DEBUG(f'property {instance.locationDB = }')
            cls.log.DEBUG(f'property {instance.details = }')
            cls.log.DEBUG(f'property {instance.suffix = }')
            cls.log.DEBUG()
            cls.log.DEBUG()
            cls.log.DEBUG()
