import socket
from time import sleep
import re

INTERVAL = 0.2

if __name__ == "__main__":


    local_ip = ''
    local_port = 8890
    socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # socket for sending cmd
    socket.bind((local_ip, local_port))

    tello_ip = '192.168.10.1'
    tello_port = 8889
    tello_adderss = (tello_ip, tello_port)

    socket.sendto('command'.encode('utf-8'), tello_adderss)

    try:
        index = 0
        while True:
            index += 1
            response, ip = socket.recvfrom(1024)
            response = response.decode('utf-8')
            if response == 'ok':
                continue

            regex = r"bat:(\d*)"
            bat = re.search(r"bat:(\d*)", response).group()[4:]
            print(bat)
            sleep(INTERVAL)
    except KeyboardInterrupt:
       print('stopped')


