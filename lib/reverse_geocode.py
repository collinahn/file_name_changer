# 추출된 gps 위도 및 경도 정보로 카카오맵 api를 활용하여 주소 이름을 가져온다.
# 오프라인 환경으로 인해 진행하지 않고 로컬 저장소에서 검색하는 파이썬 파일로 대체함.

import requests
import json


from .__api import API_KEY
from .log_gongik import Logger
from .meta_data import GPSInfo


class LocationRequest(object):
    def __new__(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)

        cls.log = Logger()
        cls.log.INFO(cls._instance)
        return cls._instance

    def __init__(self):
        cls = type(self)
        if not hasattr(cls, '_init'):
            gpsInfo = GPSInfo()

            self.gpsData = gpsInfo.gps # 테스트 모듈에서만 사용

            # REST API 키 설정
            self.apiKey = API_KEY
            self.headers = {"Authorization": f"KakaoAK {self.apiKey}" }

            # 서비스 별 URL 설정

            # 01 주소 검색
            self.URL_01 = "https://dapi.kakao.com/v2/local/search/address.json"
            # 02 좌표-행정구역정보 변환
            self.URL_02 = "https://dapi.kakao.com/v2/local/geo/coord2regioncode.json"
            # 03 좌표-주소 변환
            self.URL_03 = "https://dapi.kakao.com/v2/local/geo/coord2address.json"
            # 04 좌표계 변환
            self.URL_04 = "https://dapi.kakao.com/v2/local/geo/transcoord.json"
            # 05 키워드 검색
            self.URL_05 = "https://dapi.kakao.com/v2/local/search/keyword.json"
            # 06 카테고리 검색
            self.URL_06 = "https://dapi.kakao.com/v2/local/search/category.json"

            cls._init = True

# 다음과 같은 형식으로 결과를 받는다
# {
#     'meta': {'total_count': 1}, 
#     'documents': [ 
#         {
#             'road_address': None,
#             'address': {
#                 'address_name': '인천 부평구 부평동 879', 
#                 'region_1depth_name': '인천', 
#                 'region_2depth_name': '부평구', 
#                 'region_3depth_name': '부평동', 
#                 'mountain_yn': 'N', 
#                 'main_address_no': '879', 
#                 'sub_address_no': '', 
#                 'zip_code': ''
#             }
#         }
#     ]
# }        
    def _send_request_addr4gps(self, x, y, option=None): #option = input coord
        params = {
            'x': x,
            'y': y
        }

        if option:
            params['input_coord'] = option

        res = requests.get(self.URL_03, headers=self.headers, params=params)

        self.log.INFO(f'{params = } / {json.loads(res.text) = }')

        return json.loads(res.text)

    # 들어온 정보가 없으면 False
    def _check_valid(self, json) -> bool:
        try:
            if json['meta']['total_count'] == 0:
                return False
        except (AttributeError, KeyError) as ae:
            self.log.ERROR(ae)

        return True

    # 도로명주소가 있으면 도로명 주소를, 없으면 지번주소를 반환한다
    def parse_addr_response(self, x, y, option=None):
        jsonData = self._send_request_addr4gps(x, y, option)
        ret = 'Undefined'

        if not self._check_valid(jsonData):
            return ret

        try:
            # if jsonData['documents'][0]['road_address'] is not None: #도로명 주소인경우
            #     addrAll = jsonData['documents'][0]['road_address']['address_name']
            #     addrRoad = addrAll.split(' ', -1)[-2:]
            #     ret = ' '.join(addrRoad)

            # else: # 지번 주소인 경우(인천은 주로 지번주소)
            ret = jsonData['documents'][0]['address']['address_name']
            filterCity = jsonData['documents'][0]['address']['region_1depth_name']
            filterProvince = jsonData['documents'][0]['address']['region_2depth_name']

            cnt2Reduce = len(filterCity) + len(filterProvince) + 2 # 띄어쓰기 포함

            ret = ret[cnt2Reduce:]
            
            # ret = jsonData['documents'][0]['road_address']['address_name'] or jsonData['documents'][0]['address']['address_name']

        except (AttributeError, IndexError, KeyError) as es:
            self.log.ERROR(es)
        except Exception as e:
            self.log.CRITICAL(e)

        return ret


if __name__ == '__main__':
    lr = LocationRequest()
    print(next(iter(lr.gpsData.values())))
    # ret = lr.parse_addr_response(next(iter(lr.gpsData.values()))[0], next(iter(lr.gpsData.values()))[1])
    ret = lr.parse_addr_response(127.1086228, 37.401219)
    # ret = lr.send_request_addr4gps(124.74, 37.01)

    print(ret)