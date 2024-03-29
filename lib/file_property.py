# 파일들의 속성(=유저의 입력값)을 저장한다

from PyQt5.QtGui import QPixmap
from threading import Lock
from datetime import (
    datetime,
    timedelta
)

import lib.utils as utils
import qWordBook as const
from lib.log_gongik import Logger


class FileProp(object):
    _setInstance4Init = set()
    _dctInstace4New = {}
    _lock = Lock()

    def __new__(cls, fileName: str, path: str = None, *args):
        with cls._lock:
            if fileName in cls._dctInstace4New:
                return cls._dctInstace4New[fileName]

            cls.log = Logger()
            cls._instance = super().__new__(cls)
            cls._dctInstace4New[fileName] = cls._instance
            cls.log.INFO(fileName, cls._instance)
            return cls._instance

    def __init__(self, name: str, path: str = None, *args) -> None:
        if name not in self._setInstance4Init:
            self._prefix = utils.get_car_no_from_parent_dir()
            self._name: str = name
            self._path = path or '.'  # unpickling 을 위해 보존
            self._absPath: str = f'{self._path}/{name}'
            self._time: datetime = datetime.strptime(
                '0001:01:01 00:00:00', '%Y:%m:%d %H:%M:%S')
            self._originLocAPI: str = ''  # 파일 기본 지번주소
            self._originLocDB: str = ''  # 파일 기본 도로명주소
            self._locationAPI: str = ''  # 보정된 지번주소
            self._locationDB: str = ''  # 보정된 도로명주소
            self._details: str = ''  # 상세(같은 주소면 동일한 상세)
            self._details_priority: str = ''  # 단일 인스턴스 상세(우선순위 높음)
            self._suffix: str = ''
            self._newPath: str = ''  # 나중에 초기화되는 최종 이름(절대경로)
            self._tplCoordinance: tuple[float,
                                        float] or None = None  # WGS84위도경도값
            self._pixmap: QPixmap = QPixmap(self._absPath)  # 캐싱

            self._setInstance4Init.add(name)
            self.log.INFO(name, 'fileProp init',
                          f'{self._name = }, {self._originLocAPI = }')

    def __str__(self) -> str:
        return self._name if hasattr(self, '_name') else super().__str__()

    def __getnewargs_ex__(self) -> tuple[tuple, dict]:
        '''
        unpickling을 위한 함수
        '''
        return ((self._name, self._path), {})

    @classmethod
    def props(cls) -> dict:
        return cls._dctInstace4New

    @classmethod
    def result_to_clipboard(cls) -> list:
        res_clipboard = set()
        for prop in cls.props().values():
            prop: cls
            details = f' {prop._details}' if prop._details else ''

            indv_res = ''.join(
                (
                    prop._locationDB or 'Undefined',
                    f' {prop._details_priority}' if prop._details_priority else details
                )
            )
            res_clipboard.add(indv_res)

        return list(res_clipboard)

    @classmethod
    def initialize_instances(cls) -> None:
        '''
        복구 클래스에서 파일들을 불러올 때 초기화 해줄 때 호출하는 클래스.
        복구 클래스 이외 다른 클래스에서 호출할 일은 없다.
        '''
        for name in cls._setInstance4Init:
            try:
                del cls._dctInstace4New[name]
            except Exception as e:
                cls.log.CRITICAL(e)

        cls._dctInstace4New.clear()
        cls._setInstance4Init.clear()

    @property
    def name(self) -> str:
        return self._name

    @property
    def abs_path(self) -> str:
        return self._absPath

    @property
    def time(self) -> datetime:
        return self._time

    @time.setter
    def time(self, newTime: str):
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
    def locationFmAPI(self):
        '''보정 전 지번 주소'''
        return self._originLocAPI

    @locationFmAPI.setter
    def locationFmAPI(self, newLoc):
        '''originalLoc 은 처음 한 번만 초기화됨'''
        if self._originLocAPI == newLoc:
            self.log.DEBUG('attempting to do meaningless insert,', newLoc)

        if not self._originLocAPI:
            self._originLocAPI = newLoc
        self._locationAPI = newLoc

    @property
    def locationFmDB(self):
        '''보정 전 도로명 주소'''
        return self._originLocDB

    @locationFmDB.setter
    def locationFmDB(self, newLoc):
        '''originalLoc 은 처음 한 번만 초기화됨'''
        if self._originLocDB == newLoc:
            self.log.DEBUG('attempting to do meaningless insert,', newLoc)

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

    @property
    def new_path(self):
        return self._newPath

    @new_path.setter
    def new_path(self, path: str):
        self._newPath = path

    @property
    def coord(self):
        return self._tplCoordinance

    @coord.setter
    def coord(self, newCoord):
        if self._tplCoordinance:
            return

        self._tplCoordinance = newCoord

    @property
    def pixmap(self) -> QPixmap:
        return self._pixmap

    @pixmap.setter
    def pixmap(self, pixmap: QPixmap):
        self._pixmap = pixmap

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
            name: instance._time
            for name, instance in cls._dctInstace4New.items()
        }

    @classmethod
    def get_names(cls):
        return list(cls._setInstance4Init)

    @property
    def final_road_name(self):  # 간략화
        details = f' {self._details}' if self._details else ''
        suffix = f' {self._suffix}' if self._suffix else ''

        return ''.join(
            (
                self._prefix,
                '_',
                self._locationDB or 'Undefined',
                f' {self._details_priority}' if self._details_priority else details,
                suffix,
            )
        )

    @property
    def final_normal_name(self):  # 간략화
        details = f' {self._details}' if self._details else ''
        suffix = f' {self._suffix}' if self._suffix else ''

        return ''.join(
            (
                self._prefix,
                '_',
                self._locationAPI or 'Undefined',
                f' {self._details_priority}' if self._details_priority else details,
                suffix,
            )
        )

    @property
    def final_full_name(self):  # 상세 버전
        details = f' {self._details}' if self._details else ''
        suffix = f' {self._suffix}' if self._suffix else ''

        return ''.join(
            (
                self._prefix,
                '_',
                f'{self._locationDB or "Undefined"}',
                f'({self._locationAPI or "Undefined"})',
                f' {self._details_priority}' if self._details_priority else details,
                suffix,
            )
        )

    # 수정할 땐 이걸로
    def correct_address(self, apiAddr: str = '', dbAddr: str = ''):
        if apiAddr:
            self._locationAPI = apiAddr
        if dbAddr:
            self._locationDB = dbAddr

    @classmethod
    def delete_pixmap_to_save(cls):
        for prop in cls._dctInstace4New.values():
            prop: FileProp
            prop._pixmap = None

    @classmethod
    def self_correct_address(cls):
        '''
        처음 주소가 바뀐 이후 3분 내에 찍힌 사진들은 같은 지번주소에서 찍힌 것이라 가정하고 
        같은 주소로 묶일 수 있게 보정해줍니다.
        맨 처음 정렬된 리스트를 순회하여 기준이 되는 시간을 저장해 두고
        기준들의 사이에 있는 사진들을 같은 위치로 분류합니다.
        '''
        dctName2Time = cls.name2Time()
        lstTimePicTakenSorted = sorted(
            list(dctName2Time.values()))  # 많아봐야 100장
        cls.log.DEBUG(lstTimePicTakenSorted)
        cls.log.DEBUG(dctName2Time)
        dctTimeLaps: dict[datetime, str] = {}  # 기준 시간과 주소 삽입
        timeStandard = lstTimePicTakenSorted[0]  # for루프를 돌 때 기준이 되는 시간

        for datePic in lstTimePicTakenSorted:
            timeGap: timedelta = datePic - timeStandard
            if timeGap.total_seconds() > const.TIME_GAP:
                timeStandard: datetime = datePic
                for fName, tDate in dctName2Time.items():
                    if tDate == timeStandard:
                        fProp: FileProp = cls._dctInstace4New[fName]
                        dctTimeLaps[timeStandard] = fProp.locationFmDB, fProp.locationFmAPI

        for fName, tDate in dctName2Time.items():
            for tMin, (addrDB, addrAPI) in dctTimeLaps.items():
                tGap: timedelta = tDate - tMin
                if tGap.total_seconds() < const.TIME_GAP and tGap.total_seconds() >= 0:
                    try:
                        fProp = FileProp(fName)
                        cls.log.INFO(fName, fProp.locationFmDB, '->',
                                     addrDB, ', ', fProp.locationFmAPI, '->', addrAPI)
                        # sorting 기준 = db addr
                        fProp.correct_address(dbAddr=addrDB, apiAddr=addrAPI)
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
            cls.log.DEBUG(f'attribute {instance._absPath = }')
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
            cls.log.DEBUG(f'property {instance.locationFmAPI = }')
            cls.log.DEBUG(f'property {instance.locationFmDB = }')
            cls.log.DEBUG(f'property {instance.details = }')
            cls.log.DEBUG(f'property {instance.suffix = }')
            cls.log.DEBUG()
            cls.log.DEBUG()
            cls.log.DEBUG()
