# 유선으로 연결된 핸드폰(mtp)에서 파일을 가저온다.
# TODO: TimeInfo클래스를 이용해서 가져올 파일들 확인

import os
from datetime import datetime
from ppadb.client import Client as AdbClient

from . import utils



class BridgePhone(object):
    def __init__(self):

        self.DCIMpath = '/sdcard/DCIM/Camera'
        self.PCpath  = '.'
        self.adbServerPath = utils.resource_path('') + '\\platform-tools\\adb.exe'
        
        try:
            os.system(f'{self.adbServerPath} devices')
            # Default is "127.0.0.1" and 5037
            self._client = AdbClient(host="127.0.0.1", port=5037)
            print(self._client.version())
            self._devices = self._client.devices()
        except RuntimeError:
            self._devices = [ 1 ]
            print('adb init failed')
            return

        # 연결된 장치가 없으면 더 이상 초기화하지 않는다.
        if not self._devices:
            return
        
        self._dctName2Date = self._init_get_pics()
        self.lstNamesTookToday = self._init_filter_today_pic()
        
        # print(f'files from phone = {self._dctName2Date}')
        print(f'BRIDGE_PHONE files today = {self.lstNamesTookToday}')

    def __del__(self):
        os.system(f'"{self.adbServerPath}" kill-server')
        print('adb server killed')

    # 전체 파일을 리턴
    def _init_get_pics(self) -> dict[str,str]:
        dctRet = {}
        fileExt = utils.get_valid_file_ext()
        try:
            lsRet = self._devices[0].shell(f'ls -hal {self.DCIMpath}').split('\n')
        except RuntimeError:
            print('usb debugging not allowed')
            return dctRet

        for line in lsRet:
            try:
                records = line.split(' ')
                fName = records[-1]
                fDate = records[-3]
                if not fName.endswith(fileExt):
                    continue
                dctRet[fName] = fDate
            except IndexError as ie:
                print(ie)
            
        return dctRet

    # 오늘 날짜의 파일을 리스트로 리턴
    def _init_filter_today_pic(self) -> list:
        todayDate = utils.get_today_date_formated('-')

        return [ fName for fName, fDate in self._dctName2Date.items() if fDate==todayDate ]

    @property
    def connected(self) -> bool:
        return bool(len(self._devices)) # false -> 연결되지 않았습니다. USB디버깅 기능을 켜 주세요

    @property
    def executable(self) -> bool:
        return len(self._devices) == 1 # false -> 한 대의 기기만 처리가 가능합니다. 

    @property
    def files(self) -> list:
        return self.lstNamesTookToday

    @staticmethod
    def _get_root_permission(device):
        device.shell('root')

    def transfer_files(self) -> bool:
        try: 
            dst = utils.extract_dir()
            phone = self._devices[0]
            self._get_root_permission(phone)

            for fName in self.files:
                targetPath = self.DCIMpath + '/' + fName
                dstPath = dst + '/' + fName
                print(targetPath)
                # print(phone.shell(f'pull {targetPath} {dstPath}'))
                phone.pull(targetPath, dstPath)
            
        except Exception:
            print('transfer file failed')
            return False

        return True


'''
import shutil
import os

filename = 'moveTest'
fileFormat = '.txt'
src = "C:/Users/Users/Desktop/"
destination = "F:/test/"

try:
	
    isCurrentPathFileExist = os.path.isfile(src + filename + fileFormat)
    #현재경로에 옮기려는 파일이 존재하는지 확인
    isDestinationFileExist = os.path.isfile(destination + filename + fileFormat)
    #도착경로에 동일한 파일이 존재하는지 확인
    if isCurrentPathFileExist:
    	#도착경로에 동일한 파일이 존재하지 않는 경우에는 옮긴다.
        if not isDestinationFileExist:
            shutil.move(src + filename + fileFormat, destination + filename + fileFormat)
        #도착경로에 동일한 파일이 존재하는 경우
        else:
            i = 1
            while True:
                if os.path.isfile(destination + filename + " ({})".format(i) + fileFormat):
                    i += 1
                else:
                    break
            shutil.move(src + filename + fileFormat, destination + filename + " ({})".format(i) + fileFormat)

except Exception as e:
    print(e)
'''

if __name__ == '__main__':
    bc = BridgePhone()

    # bc.transfer_files()
