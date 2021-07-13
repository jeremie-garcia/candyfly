
from PyQt5.QtCore import pyqtSignal, QObject
import re
import socket
import sys
from threading import Thread

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication, QPushButton

from drone import Drone

import pyttsx3 as py
import speech_recognition as sr
import vocal_controler_class as vc
import vosk
import argparse
import os
import queue
import sounddevice as sd

import sys
import tello
import threading as Thread


"""
import threading
import concurrent.futures


import time
start = time.perf_counter()
def ecrire_nom(sec):
    print(f'bonjour je dors {sec}')
    time.sleep(sec)
    return('drone is sleeping')

threads = []

for _ in range(10):
    t = threading.Thread(target=ecrire_nom, args=[1.5])
    t.start()
    threads.append(t)

for thread in threads:
    thread.join()



with concurrent.futures.ThreadPoolExecutor() as excecutor:
    f1 = [excecutor.submit(ecrire_nom,1) for _ in range(10)]
    for f in concurrent.futures.as_completed(f1):
        print(f.result())



finish=time.perf_counter()
print(finish)
"""


class A(QObject):
    pass

class B(A):
    pass


class professeur(B):
    valeur = pyqtSignal(str,str)
    def __init__(self):
        B.__init__(self)
        self.age = 20
        self.valeur.connect(self.handle)

        self.engine = py.init()
        self.voices = self.engine.getProperty('voices')
        self.indice = int(38)
        self.lang = self.voices[self.indice].languages
        self.engine.setProperty('voice', self.voices[38].id)

    def prevenir(self):
        self.valeur.emit("bonjour","aurevoir")

    def handle(self,str1,str2):
        print("trigger",str1,str2)

    # def speak(self,str):
    #     """entrer un string pour que l'assistant vocal le dit à voix haute"""
    #     self.engine.say(str)
    #     self.engine.runAndWait()
    def affichage(self,valu):
        print(valu)

    def speak(self):
        """entrer un string pour que l'assistant vocal le dit à voix haute"""
        print(2)

    def affichage(self):
        print("bonjour",type("bonjour"),False)




if __name__=='__main__':
    a="bonjour"
    professeur().prevenir()
    print(professeur.mro())
    print("hello %s, %d" %("yas",50))
    os.system('say %s' % a)

    # professeur().speak("bonjour")
    print(type({"bonjou":2}))



    
