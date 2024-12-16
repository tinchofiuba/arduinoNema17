#model
import pandas as pd
import serial
import queue
import threading
import time
import numpy as np
import json
import sys
import os

#intento leer los archivos 


class Model:
    def __init__(self):
        self.ensayosAnteriores=None
        self.resultados=None
        #imprimo la ubicacion de ejcucion
        with open('json/ensayosAnteriores.json','r') as file:
            self.ensayosAnteriores=json.load(file)
        with open('json/calibracion.json','r') as file:
            self.calibracion=json.load(file)
            
    def resetTiempoPasos(self):
        print("hola")
    def resetTiempoEnsayo(self):
        print("hola")
        
        
    