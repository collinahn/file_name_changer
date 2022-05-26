# json 에서 값을 읽어온다

import json


class ValueParser(object):

    def __init__(self, file_name: str, key_name: str) -> None:
        with open(file_name, 'r', encoding='utf-8') as f:
            json_data: dict = json.loads(f.read())

        self.value = json_data.get(key_name)

class TextParser(object):
    def __init__(self, file_name: str) -> None:
        with open(file_name, 'r', encoding='utf-8') as f:
            txt_data = f.read()
        
        self.value = txt_data

