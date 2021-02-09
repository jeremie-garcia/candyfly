#
# Tello Python3 Demo
#

import socket, time

host = ''
port = 9000
locaddr = (host,port)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tello_address = ('192.168.10.1', 8889)
sock.bind(locaddr)

sock.sendto('command'.encode(encoding="utf-8"), tello_address)
time.sleep(5)

# Takeoff
sock.sendto('takeoff'.encode(encoding="utf-8"), tello_address)
time.sleep(8)

print('down')
sock.sendto('down 50'.encode(encoding="utf-8"), tello_address)
time.sleep(5)
print('there')

print('up')
# Rotate clockwise 360
sock.sendto('up 50'.encode(encoding="utf-8"), tello_address)
time.sleep(5)

print('left')
# Rotate clockwise 360
sock.sendto('left 20'.encode(encoding="utf-8"), tello_address)
time.sleep(5)

print('right')
# Rotate clockwise 360
sock.sendto('right 20'.encode(encoding="utf-8"), tello_address)
time.sleep(5)

print('turn')
# Rotate clockwise 360
sock.sendto('cw 360'.encode(encoding="utf-8"), tello_address)
time.sleep(5)

print('Remote control')
# Rotate clockwise 360
sock.sendto('rc 10 -10 10 -10'.encode(encoding="utf-8"), tello_address)
time.sleep(5)
sock.sendto('rc 0 0 0 0'.encode(encoding="utf-8"), tello_address)
time.sleep(2)
# Land
sock.sendto('land'.encode(encoding="utf-8"), tello_address)
time.sleep(5)