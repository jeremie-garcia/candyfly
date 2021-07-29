
import tellovoice_reco
from PyQt5.QtWidgets import *
import tello
import sys
import cv2
import socket
CASCADE_FILE = "data_face_frontal.xml"

FRAME_WIDTH = 1600
FRAME_HEIGHT = 1080
PATH = "/Users/alaintai/Desktop/Candyfly/Candyfly/image_dection"
PATH_data_face = "/Users/alaintai/Desktop/Candyfly/Candyfly/data_face/data_face_frontal.xml"

class telloVoiceObjectReco(tellovoice_reco.TelloVoiceReco):
    """classe responsable de la reconnaissance de visage pour quelques metres"""
    def __init__(self):
        tellovoice_reco.TelloVoiceReco.__init__(self)

        #redefinition of host,IP and port
        self.streaming_host = ''
        self.streaming_IP = '0.0.0.0'
        self.tello_IP = '192.168.10.1'
        self.streaming_port = 11111
        self.address_schema = 'udp://@{ip}:{port}'
        self.address = self.address_schema.format(ip=self.streaming_IP, port=self.streaming_port)
        self.tello_address = (self.tello_IP, 8889)

        #redefining a socket
        self.streaming_adress = (self.streaming_host, 1111)
        self.streaming_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.streaming_sock.bind(self.streaming_adress)

        #send valide message and allow the camera for drone
        self.streaming_sock.sendto('command'.encode(' utf-8 '), self.tello_address)
        self.streaming_sock.sendto('streamon'.encode(' utf-8 '), self.tello_address)
        print("Start streaming video")

        self.detection_signal.connect(self.chemin_retour)

    def _thread_streaming_data(self):
        self.capture = cv2.VideoCapture(self.address, cv2.CAP_FFMPEG)
        if not self.capture.isOpened():
            self.capture.open(self.address)
        self.process_show_image()

    def process_show_image(self):
        print("capture ouvert")
        while True:
            ret, frame = self.capture.read()
            if (ret):
                cv2.imshow('frame', frame)
                #print("oui")
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    #self.capture.release()
                    cv2.destroyAllWindows()
                    self.streaming_sock.sendto('streamoff'.encode(' utf-8 '), self.tello_address)
                elif cv2.waitKey(1) & 0xFF == ord('c'):  # save on pressing 'c'
                    self.process_facial_recognition(frame)
                    self.detection_signal.emit(self.valeur_aller)
                    print("capuré image")

    def process_facial_recognition(self, img):
        """fonction for facial detection"""
        human_counter=0
        self.face_cascade = cv2.CascadeClassifier(PATH_data_face)
        imgGay = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(imgGay, 1.2, 1)  # 1.1 = scale ,4 = nimimum neighbours = 4px
        for (x, y, w, h) in faces:
            xy = "{},{}".format(x,y)
            cv2.rectangle(img, (x, y), (x + w, y + h), (225, 0, 0), 2)  # 2 = thiknes
            human_counter+=1
            cv2.putText(img, xy, (x, y), cv2.FONT_HERSHEY_PLAIN,
                        1.0, (0, 255, 0), thickness=2)
        cv2.imwrite(PATH + '/c1.png', img)
        cv2.imshow("Detection facial", img)
        self.speak("il y a {} personnes".format(human_counter),240)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            self.capture.release()
            cv2.destroyAllWindows()
            self.streaming_sock.sendto('streamoff'.encode(' utf-8 '), self.tello_address)

if __name__=='__main__':
    app = QApplication([])

    tello = telloVoiceObjectReco()
    button = QPushButton("start")
    stp_button = QPushButton("stop")
    button.clicked.connect(tello.take_off)
    stp_button.clicked.connect(tello.land)
    button.show()
    stp_button.show()

    tello.battery_low_signal.connect(lambda value : tello.warning_batterie(value))
    #tello.batteryValue.connect(lambda status: print('batt', status))
    tello.is_flying_signal.connect(lambda status: print('flying?', status))
    tello.connection.connect(lambda status: print('connection', status))
    tello._thread_streaming_data()
    # tello.init()

    sys.exit(app.exec_())
    tello.stop()
