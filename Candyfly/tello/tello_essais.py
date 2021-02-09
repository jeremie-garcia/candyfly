import multiprocessing
import socket
import threading
import time

INTERVAL = 0.2

if __name__ == "__main__":

    def logger():
        run = True
        INTERVAL = 0.2

        local_ip = '0.0.0.0'
        state_port = 8890
        state_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # socket for sending cmd
        state_socket.bind((local_ip, state_port))

        try:
            index = 0
            while run:
                index += 1
                response, ip = socket.recvfrom(1024)
                if response == 'ok':
                    continue
                out = response.replace(';', ';\n')
                out = 'Tello State:\n' + out
                print(out)
                time.sleep(INTERVAL)
        except KeyboardInterrupt:
            run = False


    #server for sending and receiving data to/from the drone
    tello_ip = '192.168.10.1'
    tello_port = 8889
    cmd_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # socket for sending cmd
    tello_address = (tello_ip, tello_port)
    cmd_socket.bind(tello_address)

    #start python comands
    socket.sendto('command'.encode(encoding='utf-8'), tello_address)
    time.sleep(2)


    #start logger

    # server for receving data from the drone
    log_thread = multiprocessing.Process(target = logger)
    log_thread.start()

    # Takeoff
    socket.sendto('takeoff'.encode(encoding="utf-8"), tello_address)
    time.sleep(5)

    # Rotate clockwise 360
    socket.sendto('cw 360'.encode(encoding="utf-8"), tello_address)
    time.sleep(5)

    # Land
    socket.sendto('land'.encode(encoding="utf-8"), tello_address)
    time.sleep(5)
    log_thread.terminate()