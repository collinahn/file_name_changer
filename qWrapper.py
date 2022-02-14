# 버튼 등으로 트리거되는 함수들의 예외 처리를 위한 래퍼 함수

import functools
import time

from lib.log_gongik import Logger

def catch_except(original_func):
    @functools.wraps(original_func)
    def wrapper(*args, **kwargs):
        try:
            original_func(*args, **kwargs)
        except Exception as e:
            Logger().CRITICAL(f'Error: {e}, funcName: {original_func.__name__}')

    return wrapper

def elapsed(original_func):
    @functools.wraps(original_func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = original_func(*args, **kwargs)
        end = time.time()
        Logger().INFO(f"{original_func.__name__} elapsed: {end - start} sec")
        return result

    return wrapper


if __name__ == '__main__':
    @elapsed
    @catch_except
    def raise_error() -> None:
        raise NotImplementedError()
    

    raise_error()