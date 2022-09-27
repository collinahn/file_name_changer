# 유선으로 연결된 핸드폰(mtp)에서 파일을 가저온다.
# ADB 서버를 통해 파일을 가져옴

import contextlib
import subprocess
from ppadb.client import Client as AdbClient
import time

import lib.utils as utils
from lib.log_gongik import Logger
from lib.base_folder import WorkingDir


class BridgePhone(object):
    def __init__(self):

        self.log = Logger()

        self.DCIMpath = '/sdcard/DCIM/Camera'
        self.PCpath = '.'
        self.adbPath = utils.resource_path('') + 'platform-tools\\adb.exe'

        self._init_start_adb_server()
        self._devices = self._init_get_adb_devices()

        # 연결된 장치가 없으면 더 이상 초기화하지 않는다.
        if not self._devices:
            self.log.WARNING('there is no device connected')
            return

        self.log.INFO('ADB connect success')
        self._dctName2Date = self._init_peek_files()
        self.lstNamesTookToday = self._init_filter_today_pic()
        self.log.DEBUG(
            f'total pics: {len(self._dctName2Date)} {self._dctName2Date = }')
        self.log.INFO(
            f'{len(self.lstNamesTookToday)} pictures from today: {self.lstNamesTookToday}')

    def __del__(self):
        with contextlib.suppress(Exception):
            # ctypes.windll.shell32.ShellExecuteW(0, 'open', self.adbPath, 'kill-server', None, 0)
            subprocess.call([self.adbPath, 'kill-server'],
                            creationflags=subprocess.CREATE_NO_WINDOW)

    def _init_start_adb_server(self):
        try:
            # ret = ctypes.windll.shell32.ShellExecuteW(0, 'open', self.adbPath, 'start-server', './platform-tools', 0)
            ret = subprocess.call(
                [self.adbPath, 'start-server'], creationflags=subprocess.CREATE_NO_WINDOW)
            self.log.INFO('ADB server start',
                          f'{ret = } / success if ret is 0')
        except RuntimeError as re:
            self.log.ERROR(re)
        except Exception as e:
            self.log.CRITICAL(e)

    def kill_adb_server(self):
        try:
            # ret = ctypes.windll.shell32.ShellExecuteW(0, 'open', self.adbPath, 'start-server', './platform-tools', 0)
            ret = subprocess.call(
                [self.adbPath, 'kill-server'], creationflags=subprocess.CREATE_NO_WINDOW)
            self.log.WARNING('ADB server halt',
                             f'{ret = } / success if ret is 0')
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
            devices = [1]
            self.log.ERROR(re, 'device connected but ADB bridge failed')
        except Exception as e:
            self.log.CRITICAL(e)

        return devices

    # 전체 파일을 리턴
    def _init_peek_files(self) -> dict[str, str]:
        dctRet = {}
        fileExt = utils.get_valid_file_ext()
        try:
            lsRet = self._devices[0].shell(
                f'ls -hal {self.DCIMpath}').split('\n')
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
                self.log.WARNING(
                    ie, '/ ignoring meaningless standard output, "', line, '"')
            except Exception as e:
                self.log.CRITICAL(e)

        return dctRet

    # 오늘 날짜의 파일을 리스트로 리턴
    def _init_filter_today_pic(self) -> list:
        todayDate = utils.get_today_date_formated('-')

        return [fName for fName, fDate in self._dctName2Date.items() if fDate == todayDate]

    @property
    def connected(self) -> bool:
        # false -> 연결되지 않았습니다. USB디버깅 기능을 켜 주세요
        return bool(len(self._devices))

    @property
    def executable(self) -> bool:
        return len(self._devices) == 1  # false -> 한 대의 기기만 처리가 가능합니다.

    @property
    def files(self) -> list:
        return self.lstNamesTookToday

    def _get_root_permission(self, device):
        try:
            device.shell('root')
        except RuntimeError as re:
            self.log.ERROR(re)
        except Exception as e:
            self.log.CRITICAL(e)

    def transfer_files(self) -> bool:
        if not self._devices:
            self.log.WARNING('Attempted Transfer While 0 Connection!')
            return False
        try:
            dst = WorkingDir().abs_path
            phone = self._devices[0]
            self._get_root_permission(phone)

            for fName in self.files:
                targetPath = f'{self.DCIMpath}/{fName}'
                dstPath = f'{dst}/{fName}'
                phone.pull(targetPath, dstPath)
                self.log.INFO('file transfered', targetPath, '->', dstPath)
                time.sleep(0.05)

        except Exception as e:
            self.log.ERROR('file transfer failed,', e)
            return False

        return True


if __name__ == '__main__':
    bc = BridgePhone()

    bc.transfer_files()
