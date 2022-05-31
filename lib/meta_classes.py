from threading import Lock

class MetaSingleton(type):
    __instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls.__instances:
            cls.__instances[cls] = super().__call__(*args, **kwargs)
        return cls.__instances[cls]

class MetaSingletonThreaded(MetaSingleton):
    _lock = Lock()
    def __call__(cls, *args, **kwargs):
        with cls._lock:
            return super().__call__(*args, **kwargs)
            