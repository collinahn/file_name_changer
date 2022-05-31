# 진행율 정보 저장소

from threading import Lock

from lib.log_gongik import Logger
from lib.meta_classes import MetaSingletonThreaded

class ProgressSignalSingleton(metaclass=MetaSingletonThreaded):
    def __init__(self) -> None:
        self.log = Logger()
        self._hint: str = ''
        self._total_work_load: int = 0
        self._current_work_load: int = -1

    @property
    def hint(self) -> str:
        return self._hint

    @hint.setter
    def hint(self, pushed_str):
        self._hint = str(pushed_str)
        self.log.INFO(f'{self._hint = }')

    @property
    def total(self) -> int:
        return self._total_work_load
    
    @total.setter
    def total(self, mass: int):
        if type(mass) != int:
            self.log.CRITICAL(f'wrong value entered {mass = }')
            self._total_work_load = 0
            return
        self.log.INFO(f'total work load set to {mass}')
        self._total_work_load = mass

    @property
    def current(self) -> int:
        return self._current_work_load

    @current.setter
    def current(self, idx: int):
        if type(idx) != int:
            self.log.CRITICAL(f'wrong value entered {idx = }')
            self._current_work_load = -1
            return
        with type(self)._lock:
            self._current_work_load = idx
        
        self.log.INFO(f'current work load set to {idx}')


if __name__ == '__main__':

    prs = ProgressSignalSingleton()
    prs2 = ProgressSignalSingleton()

    print(prs, prs2)
    print(prs is prs2)