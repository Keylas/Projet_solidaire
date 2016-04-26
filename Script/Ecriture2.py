# coding=utf8

import threading


class Timer(threading.Thread):
    def __init__(self, time, fonction):
        threading.Thread.__init__(self)
        self.stop = threading.Event()
        self.temps = time
        self.function = fonction

    def run(self):
        self.stop.wait(self.temps)
        self.function()

    def executer(self):
        self.stop.set()

class SwitchWriter(object):
    instruction = []
    timer = None
    nbInstructionMax = 50
    tpsAttente = 10
    mutex = threading.Lock()
    ip = ""

    @classmethod
    def start(cls):
        cls.mutex.release()

    @classmethod
    def remplir(cls, chaine):
        cls.mutex.acquire()
        if cls.instruction == []:
            cls.timer = Timer(cls.tpsAttente, cls.ecrire)
            cls.timer.start()
        cls.instruction.append(chaine)
        if len(cls.instruction) >= cls.nbInstructionMax:
            cls.timer.executer()
        cls.mutex.release()

    @classmethod
    def ecrire(cls):
        cls.mutex.acquire()
        print('Appel du script d\'écriture sur {0}'.format(cls.ip))  # Script pour écrire sur le switch
        cls.instruction = []
        cls.mutex.release()

class SwitchA1(SwitchWriter):
    ip = "192.168.255.11"

class SwitchA2(SwitchWriter):
    ip = "192.168.255.12"

class SwitchB1(SwitchWriter):
    ip = "192.168.255.21"

class SwitchB2(SwitchWriter):
    ip = "192.168.255.22"

class SwitchC1(SwitchWriter):
    ip = "192.168.255.31"

class SwitchC2(SwitchWriter):
    ip = "192.168.255.32"

class SwitchD1(SwitchWriter):
    ip = "192.168.255.41"

class SwitchD2(SwitchWriter):
    ip = "192.168.255.42"

class SwitchH1(SwitchWriter):
    ip = "192.168.255.51"



def testScript():
    SwitchA1.remplir("blabla")
    print(SwitchA1.instruction)
    SwitchA1.ecrire()