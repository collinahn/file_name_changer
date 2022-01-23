# 1. ~/change-file-name-api-server/version.text에 버전 이름이 들어가야함.
# 2. 버전 이름과 같은 exe파일이 ~/change-file-name-api-server/release/ 폴더 내에 위치해야 함.
import paramiko
from scp import SCPClient, SCPException
import getpass 
import os

from qMain import VERSION_INFO
from lib.__PRIVATE import IP, PORT_SSH

class SSHManager:
    """ 
    usage: 
        >>> import SSHManager 
        >>> ssh_manager = SSHManager() 
        >>> ssh_manager.create_ssh_client(hostname, username, password) 
        >>> ssh_manager.send_command("ls -al") 
        >>> ssh_manager.send_file("/path/to/local_path", "/path/to/remote_path") 
        >>> ssh_manager.get_file("/path/to/remote_path", "/path/to/local_path") ... 
        >>> ssh_manager.close_ssh_client() 
    """ 
    
    def __init__(self): 
        self.ssh_client = None 
        
    def create_ssh_client(self, hostname, portname, username, password): 
        """Create SSH client session to remote server""" 
        if self.ssh_client is None: 
            self.ssh_client = paramiko.SSHClient() 
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
            self.ssh_client.connect(hostname, portname, username, password) 
        else: 
            print("SSH client session exist.") 

    def close_ssh_client(self): 
        """Close SSH client session""" 
        self.ssh_client.close() 

    def send_file(self, local_path, remote_path): 
        """Send a single file to remote path""" 
        try: 
            with SCPClient(self.ssh_client.get_transport()) as scp:
                scp.put(local_path, remote_path, preserve_times=True) 
        except SCPException: 
            raise SCPException.message 
    
    def get_file(self, remote_path, local_path): 
        """Get a single file from remote path""" 
        try: 
            with SCPClient(self.ssh_client.get_transport()) as scp: 
                scp.get(remote_path, local_path) 
        except SCPException: 
            raise SCPException.message 
        
    def send_command(self, command): 
        """Send a single command""" 
        stdin, stdout, stderr = self.ssh_client.exec_command(command) 
        return stdout.readlines()


if __name__ == '__main__':

    print('===============================')
    print(VERSION_INFO)
    print('===============================')

    with open('version.txt', 'a', encoding='UTF-8') as f:
        f.write(f'{VERSION_INFO}\n')

    print('file updated with', VERSION_INFO)
    print('getting ready to a scp session')

    pw = getpass.getpass('enter passwd for ssh: ')

    buildRes = os.system('pyinstaller -F --clean qMain.spec')
    if buildRes != 0:
        print('build failed')
        raise(RuntimeError)

    clsSM = SSHManager()
    clsSM.create_ssh_client(IP, PORT_SSH, 'pi', pw)

    targetFile = './dist/qMain.exe'
    dstFileName = f'./dist/{VERSION_INFO}.exe'
    if not os.path.exists(targetFile):
        raise(FileNotFoundError)
    if os.path.exists(dstFileName):
        print('delete previous file')
        raise(FileExistsError)

    os.rename(targetFile, dstFileName)
    print(f'file renamed to ./dist/{VERSION_INFO}.exe, preparing to send')

    clsSM.send_file('./version.txt', '/home/pi/change-file-name-api-server/')
    clsSM.send_file(f'./dist/{VERSION_INFO}.exe', '/home/pi/change-file-name-api-server/release/')
    print('transfer complete')

    clsSM.close_ssh_client()

    print('=============================')
    print(VERSION_INFO, 'released')
    print('=============================')