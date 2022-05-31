# working dir 를 저장하는 싱글턴 클래스

from dataclasses import (
    dataclass,
    field
)
from lib.meta_classes import MetaSingletonThreaded


@dataclass(frozen=True)
class WorkingDir(metaclass=MetaSingletonThreaded):
    abs_path: str = field(default_factory='')
    rel_path: str = field(default_factory='')



if __name__ == '__main__':

    import utils
    p1 = WorkingDir(utils.extract_dir(), utils.get_relative_path('.'))
    print(p1)  # Config(name='John', age='25')
    p2 = WorkingDir('', '')
    print(p2)  # Config(name='John', age='25')

    print(p1 == p2)  # True
    print(p1 is p2)  # True