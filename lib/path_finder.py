import os

import lib.utils as utils
from lib.log_gongik import Logger


class PathFinder(object):
    def __init__(self) -> None:
        self.log = Logger()
        
        self.year, self.month, self.day = utils.get_year_month_day()
        self.base_dir = utils.extract_dir()
        self.path_1st = f'{self.base_dir}{self.find_path(self.base_dir, f"{self.month}월")}'
        self.path_2nd = f'{self.path_1st}{self.find_path(self.path_1st, f"{self.month}.{self.day}")}'

    def find_path(self, base: str, key: str):
        with os.scandir(base) as entries:
            self.log.DEBUG(f'scaning {base}: {os.listdir(base)}')
            for entry in entries:
                if entry.is_file():
                    continue
                
                if key in entry.name:
                    return f'/{entry.name}'
            
            return ''
                



if __name__ == '__main__':

    print(PathFinder().path_2nd)