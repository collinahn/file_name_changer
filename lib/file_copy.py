# 유선으로 연결된 핸드폰에서 파일을 가저온다.
# TODO: TimeInfo클래스를 이용해서 가져올 파일들 확인

import sys
from ctypes import windll
from shutil import copy2

from .meta_data import TimeInfo

# gracefully handle it when pymtp doesn't exist
class MTPDummy():
    def detect_devices(self):
        return []

class DriveDetector(object):
    def __init__(self) -> None:
        self.bitmask = windll.kernel32.GetLogicalDrives()


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
    dd = DriveDetector()

    print('{0:b}'.format(dd.bitmask))

    try:
        import pymtp
        mtp = pymtp.MTP()
    except ImportError:
        mtp = MTPDummy()
        print('dummy')
    # GNOME GVFS mount point for MTP devices

    if sys.platform != 'win32':
        # this crashes windows in the ntpath sys lib
        mtp.gvfs_mountpoint = os.path.join(os.getenv('HOME'), '.gvfs', 'mtp')