# 유선으로 연결된 핸드폰(mtp)에서 파일을 가저온다.
# ADB 서버를 통해 파일을 가져옴

import os
from ppadb.client import Client as AdbClient

from . import utils
from .log_gongik import Logger


class BridgePhone(object):
    def __init__(self):

        self.log = Logger()

        self.DCIMpath = '/sdcard/DCIM/Camera'
        self.PCpath  = '.'
        self.adbServerPath = utils.resource_path('') + '\\platform-tools\\adb.exe'
        
        self._init_start_adb_server()
        self._devices = self._init_get_adb_devices()

        # 연결된 장치가 없으면 더 이상 초기화하지 않는다.
        if not self._devices:
            self.log.WARNING('there is no device connected')
            return
        
        self.log.INFO('ADB connect success')
        self._dctName2Date = self._init_get_pics()
        self.lstNamesTookToday = self._init_filter_today_pic()
        self.log.INFO('pictures from today:', self.lstNamesTookToday)
        
    def __del__(self):
        try:
            os.system(f'"{self.adbServerPath}" kill-server')
        except RuntimeError:
            pass

    def _init_start_adb_server(self):
        try:
            self.log.INFO('ADB server start')
            os.system(f'"{self.adbServerPath}" devices')
        except RuntimeError as re:
            self.log.ERROR(re)
        except Exception as e:
            self.log.CRITICAL(e)

    def _init_get_adb_devices(self) -> list:
        try:
            self.log.INFO('ADB bridge exec')
            # Default is "127.0.0.1" and 5037
            client = AdbClient(host="127.0.0.1", port=5037)
            devices = client.devices()
            self.log.INFO('client version:', client.version())
            self.log.INFO('device list:', devices)
        except RuntimeError as re:
            devices = [ 1 ]
            self.log.ERROR(re, 'device connected but ADB bridge failed')
        except Exception as e:
            self.log.CRITICAL(e)

        return devices

    # 전체 파일을 리턴
    def _init_get_pics(self) -> dict[str,str]:
        dctRet = {}
        fileExt = utils.get_valid_file_ext()
        try:
            lsRet = self._devices[0].shell(f'ls -hal {self.DCIMpath}').split('\n')
        except RuntimeError as re:
            self.log.ERROR(re, 'USB debugging not allowed')
            return dctRet
        except Exception as e:
            self.log.CRITICAL(e)
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
                self.log.WARNING(ie, '/ ignoring meaningless standard output, "', line, '"')
            except Exception as e:
                self.log.CRITICAL(e)
            
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
        try:
            device.shell('root')
        except RuntimeError as re:
            Logger.ERROR(re)
        except Exception as e:
            Logger.CRITICAL(e)

    def transfer_files(self) -> bool:
        try: 
            dst = utils.extract_dir()
            phone = self._devices[0]
            self._get_root_permission(phone)

            for fName in self.files:
                targetPath = self.DCIMpath + '/' + fName
                dstPath = dst + '/' + fName
                phone.pull(targetPath, dstPath)
                self.log.INFO('file transfered', targetPath, '->', dstPath)

        except Exception as e:
            self.log.ERROR('file transfer failed,', e)
            return False

        return True

if __name__ == '__main__':
    bc = BridgePhone()

    bc.transfer_files()
