import sys
from PyQt5.QtWidgets import QApplication, QDialog
from salpicaduras import Ui_Dialog
from modelSalpicaduras import Model
import os
import sys
import json
#importo lo necesario para abrir un QFileDialog
from PyQt5.QtCore import Qt,QThread,pyqtSignal
from PyQt5.QtWidgets import QFileDialog,QTableWidgetItem
import pandas as pd
import time
import serial


from PyQt5.QtCore import QThread, pyqtSignal
import serial
import time

class SerialThread(QThread):

    def __init__(self, puerto, bauds):
        super().__init__()
        self.puerto=puerto
        self.bauds=bauds
        self.running=True

    def run(self):
        try:
            self.arduino=serial.Serial(self.puerto, self.bauds)
            time.sleep(1)
            self.arduino.write('salpicaduraInit'.encode())
            while self.running:
                if self.arduino.in_waiting > 0:
                    datos=self.arduino.readline().decode("utf-8").strip()
                    print("Leyendo el mensaje del arduino")
                    if datos=="salpicaduraInitOK":
                        print("Equipo conectado correctamente")
        except Exception as e:
            print(f"Error: {e}")

    def enviarMje(self, mje):
        try:
            self.arduino.write(mje.encode())
        except Exception as e:
            print(f"Error sending message: {e}")

    def stop(self):
        self.running = False
        self.wait()
        self.arduino.close()

dictDataFrame={"Nº Repeticion":[],"Velocidad":[],"Resultado":[],"Observaciones":[]}
class GUI_Salpicaduras(QDialog, Ui_Dialog):
    def __init__(self):
        #escribo "salpicaduraInit" para vincular con el arduino y luego leo lo que me dice el arduino con un serial.read
        self.dfResultados=pd.DataFrame(dictDataFrame) #creo por 1era vez un dataFrame 
        model=Model()
        super().__init__()
        
        #self.timer = QTimer(self)
        #self.timer.start(1000) 
        #self.timer.timeout.connect(self.lecturaSerialArduino)
        self.serialThread=SerialThread('COM8', 9600)
        self.serialThread.start()
        self.setupUi(self)
        self.configLimitesliders("init","ambos")
        self.setFixedSize(self.size())
        self.velPasosAnt=0
        self.velEnsayoAnt=0
        self.calibracion=None
        self.numeroRepeticion=1
        self.comboBoxVelocidadesCalib.setEnabled(False)
        self.pushButtonComenzarEnsayo.setStyleSheet("color: green")
        self.comboBoxVelocidadesCalib.currentIndexChanged.connect(self.actualizarValoresPorcomboBoxCalibracion)
        self.horizontalSliderDelayPasos.valueChanged.connect(self.configSliderDelayPasos)
        self.horizontalSliderTiempoEnsayo.valueChanged.connect(self.configSliderTiempoEnsayo)
        self.pushButtonResetDelayPasos.clicked.connect(lambda: self.configLimitesliders("rst","delayPasos"))
        self.pushButtonResetTiempoEnsayo.clicked.connect(lambda: self.configLimitesliders("rst","tiempoEnsayo"))
        self.pushButtonCargarConfigCalib.clicked.connect(self.cargarConfiguracion)
        self.pushButtonGuardarConfigCalib.clicked.connect(self.guardarConfiguracionCalibracion)
        self.comboBoxVelocidadesEnsayo.currentIndexChanged.connect(self.actualizarValoresPorcomboBoxEnsayo)
        self.lineEditMuestra.textChanged.connect(self.chequeoDatosInicioEnsayo)
        self.lineEditNumeroRepeticiones.textChanged.connect(self.seteoNumRepeticiones)
        self.lineEditOTSOT.textChanged.connect(self.chequeoDatosInicioEnsayo)
        self.pushButtonAceptarResultado.clicked.connect(self.aceptarResultado)
        self.radioButtonFalla.toggled.connect(self.actualizacionRadioButton)
        self.radioButtonPasa.toggled.connect(self.actualizacionRadioButton)
        self.funcionesMotor()

    def funcionesMotor(self):
        self.pushButtonAvanzar.clicked.connect(lambda: self.configPosicionPiston("avanzar"))
        self.pushButtonAvanzarCalib.clicked.connect(lambda: self.configPosicionPiston("avanzar"))
        self.pushButtonRetroceder.clicked.connect(lambda: self.configPosicionPiston("retroceder"))
        self.pushButtonRetrocederCalib.clicked.connect(lambda: self.configPosicionPiston("retroceder"))
        self.pushButtonOrigen.clicked.connect(lambda: self.configPosicionPiston("origen"))  
        self.pushButtonOrigenCalib.clicked.connect(lambda: self.configPosicionPiston("origen"))
        self.pushButtonLubricar.clicked.connect(lambda: self.configPosicionPiston("lubricar"))
        self.pushButtonComenzarEnsayo.clicked.connect(self.comenzarEnsayo)
        self.pushButtonComenzarCalibracion.clicked.connect(self.comenzarEnsayo)

    def chequeoSliderComSerial(self,mje):
        velocidadSeleccionadaEnsayo=self.comboBoxVelocidadesEnsayo.currentText()
        velPasos=self.calibracion[velocidadSeleccionadaEnsayo]["delayPasos"]
        velEnsayo=self.calibracion[velocidadSeleccionadaEnsayo]["tiempoEnsayo"]
        if self.velPasosAnt!=velPasos or self.velEnsayoAnt!=velEnsayo: #mando solamente si se cambio la velocidad
            mensaje=f'velPasos{velPasos},velEnsayo{velEnsayo}'
            self.velPasosAnt=velPasos
            self.velEnsayoAnt=velEnsayo
            self.serialThread.enviarMje(mensaje)
            time.sleep(2)
            self.serialThread.enviarMje(mje)
        else:
            self.serialThread.enviarMje(mje)

        #else: #si no cambio la velocidad de los sliders, no envio esta información
         #   self.serialThread.enviarMje(mje)

    def comenzarEnsayo(self):
        self.chequeoSliderComSerial('comenzar')
        self.radioButtonFalla.setEnabled(True)
        self.radioButtonPasa.setEnabled(True)
        self.pushButtonComenzarEnsayo.setText("Repetir") #esto es para que se pueda repetir y no aceptar el resultado
        #cambio el color del texto del boton pushbuttonComenzarEnsayo a rojo
        self.pushButtonComenzarEnsayo.setStyleSheet("color: red")
        if self.radioButtonFalla.isChecked() or self.radioButtonPasa.isChecked():
            self.actualizacionRadioButton()
            if self.radioButtonFalla.isChecked():
                self.resultado="Falla"
            else:
                self.resultado="Pasa"
            print(self.resultado)

    def configPosicionPiston(self,mje):
        try:
            self.serialThread.enviarMje(mje)
        except:
            print("No se pudo enviar el mensaje al arduino")

    def guardarUltimaConfiguracion(self): #para guardar un json con la última configuación, así se haya o no calibrado, pero no se guarda la calibración
        config = {
            "numeroRepeticion": self.numeroRepeticion,
            "dfResultados": self.dfResultados.to_dict(),
            # Agrega aquí cualquier otra configuración que desees guardar
        }
        with open("data/data.json", "w") as file:
            json.dump(config, file)
    
    def closeEvent(self, event):
        self.guardarUltimaConfiguracion()
        event.accept()
    
    def actualizarTabla(self):
        self.tableWidget.setRowCount(len(self.dfResultados))
        self.tableWidget.setColumnCount(len(self.dfResultados.columns))
        self.tableWidget.setHorizontalHeaderLabels(self.dfResultados.columns)
        print(self.dfResultados)
        for i in range(len(self.dfResultados)):
            for j in range(len(self.dfResultados.columns)):
                item = QTableWidgetItem(str(self.dfResultados.iat[i, j]))
                if j != len(self.dfResultados.columns) - 1:  # Si no es la última columna
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Deshabilitar edición
                self.tableWidget.setItem(i, j, item)
  
    def actualizacionRadioButton(self):
        self.pushButtonAceptarResultado.setEnabled(True)
        self.pushButtonAceptarResultado.setStyleSheet("color: green")  
            
    def aceptarResultado(self):
        self.pushButtonComenzarEnsayo.setText("Comenzar")
        self.pushButtonAceptarResultado.setStyleSheet("color: gray")   
        self.radioButtonFalla.setEnabled(False)
        self.radioButtonPasa.setEnabled(False)
        self.pushButtonAceptarResultado.setEnabled(False)
        if self.radioButtonFalla.isChecked() or self.radioButtonPasa.isChecked():
            if self.radioButtonFalla.isChecked():
                self.resultado="Falla"
            else:
                self.resultado="Pasa"
            print(self.resultado)
        self.nuevaFila=pd.DataFrame([{"Nº Repeticion":self.numeroRepeticion,"Velocidad":self.velocidadEnsayo,"Resultado":self.resultado,"Observaciones":"No"}])
        self.dfResultados=pd.concat([self.dfResultados,self.nuevaFila],ignore_index=True)
        print(self.dfResultados)
        self.actualizarTabla()
        self.incrementarNumeroEnsayo()     
            
    def incrementarNumeroEnsayo(self): #cuando se acepta el ensayo se le suma 1 al numero de repeticiones
        self.numeroRepeticion+=1
        self.labelValorRepeticion.setText(f'{self.numeroRepeticion}/{self.numeroDeRepeticiones}')  
 
    def seteoNumRepeticiones(self):
        if self.lineEditNumeroRepeticiones.text()!="":
            self.numeroDeRepeticiones=int(self.lineEditNumeroRepeticiones.text())
            self.labelValorRepeticion.setText(f'{self.numeroRepeticion}/{self.numeroDeRepeticiones}')
            self.chequeoDatosInicioEnsayo()
    
    def chequeoDatosInicioEnsayo(self):
        if self.lineEditMuestra.text()=="" or self.lineEditNumeroRepeticiones.text()=="" or self.lineEditOTSOT.text()=="": #si no se relleno algun lineEdit
            self.pushButtonComenzarEnsayo.setEnabled(False)
            self.pushButtonAvanzar.setEnabled(False)
            self.pushButtonRetroceder.setEnabled(False)
            self.pushButtonOrigen.setEnabled(False)
        else:
            self.pushButtonComenzarEnsayo.setEnabled(True)
            self.pushButtonAvanzar.setEnabled(True)
            self.pushButtonRetroceder.setEnabled(True)
            self.pushButtonOrigen.setEnabled(True)
            self.pushButtonLubricar.setEnabled(True)


    def actualizarValoresPorcomboBoxEnsayo(self):
        if self.comboBoxVelocidadesEnsayo.currentText()=="": #cargo por primera vez
            self.comboBoxVelocidadesEnsayo.setEnabled(True)
            self.comboBoxVelocidadesEnsayo.addItems(self.calibracion.keys())
            self.chequeoDatosInicioEnsayo()
            self.lineEditMuestra.setEnabled(True)
            self.lineEditNumeroRepeticiones.setEnabled(True)
            self.lineEditOTSOT.setEnabled(True)
            self.velocidadEnsayo=self.comboBoxVelocidadesEnsayo.currentText()
        else:
            self.velocidadEnsayo=self.comboBoxVelocidadesEnsayo.currentText()
        
            
    def guardarConfiguracionCalibracion(self):
        self.delayPasos=self.horizontalSliderDelayPasos.value()
        self.tiempoEnsayo=self.horizontalSliderTiempoEnsayo.value()
        self.calibracion[self.comboBoxVelocidadesCalib.currentText()]["delayPasos"]=self.delayPasos
        self.calibracion[self.comboBoxVelocidadesCalib.currentText()]["tiempoEnsayo"]=self.tiempoEnsayo
        file, _ = QFileDialog.getSaveFileName(self, "Guardar archivo de calibración", "", "JSON Files (*.json)")
        if file:
            if not file.endswith('.json'):
                file+='.json'
            with open(file,'w') as f:
                json.dump(self.calibracion,f,indent=4)
            print("Archivo guardado:",file)
        else:
            print("No se seleccionó ningún archivo")
        self.actualizarValoresPorcomboBoxEnsayo()
        
    
    def cargarConfiguracion(self):
        file = QFileDialog.getOpenFileName(self, "Abrir archivo de calibración", "", "JSON Files (*.json)")
        self.nombreArchivoCalibracion=os.path.splitext(file[0])
        self.direccionArchivoConfiguración=self.nombreArchivoCalibracion[0]
        if len(file[0])>0: #si se selecciono un archivo
            try :
                with open(file[0],'r') as data:
                    print("configuración levantada")
                    self.horizontalSliderDelayPasos.setEnabled(True)
                    self.horizontalSliderTiempoEnsayo.setEnabled(True)
                    self.pushButtonAvanzarCalib.setEnabled(True)
                    self.pushButtonRetrocederCalib.setEnabled(True)
                    self.pushButtonOrigenCalib.setEnabled(True)
                    self.pushButtonLubricar.setEnabled(True)
                    self.pushButtonComenzarCalibracion.setEnabled(True)
                    self.calibracion=json.load(data)
                    self.comboBoxVelocidadesCalib.setEnabled(True)
                    self.pushButtonGuardarConfigCalib.setEnabled(True)
                    self.comboBoxVelocidadesCalib.clear()
                    self.comboBoxVelocidadesCalib.addItems(self.calibracion.keys())
                    self.actualizarValoresPorcomboBoxEnsayo()
                    self.delayPasos=self.calibracion[self.comboBoxVelocidadesCalib.currentText()]["delayPasos"]
                    self.tiempoEnsayo=self.calibracion[self.comboBoxVelocidadesCalib.currentText()]["tiempoEnsayo"]
                    self.horizontalSliderDelayPasos.setValue(self.delayPasos) 
                    self.horizontalSliderTiempoEnsayo.setValue(self.tiempoEnsayo)
            except:
                print("error al cargar el archivo Json, o error al leer los valores")
                
    def actualizarValoresPorcomboBoxCalibracion(self):
        if self.comboBoxVelocidadesCalib.currentText()!="": #esto es por que al borrar el combobox, para poblarlo con nuevos items, al ppio no va a tener items
            self.horizontalSliderDelayPasos.setValue(self.calibracion[self.comboBoxVelocidadesCalib.currentText()]["delayPasos"]) 
            self.horizontalSliderTiempoEnsayo.setValue(self.calibracion[self.comboBoxVelocidadesCalib.currentText()]["tiempoEnsayo"])
              
    def configLimitesliders(self,config,slider): #en función del argumento reseteo, o configuro uno/los dos sliders
        self.delayPasosMin=400
        self.delayPasosMax=2000
        self.tiempoEnsayoMin=400
        self.tiempoEnsayoMax=1000
        if config=="init":
            if slider=="ambos":
                self.horizontalSliderDelayPasos.setMinimum(self.delayPasosMin) #valor del tiempo en microSegundos
                self.horizontalSliderDelayPasos.setMaximum(self.delayPasosMax) #valor del tiempo en microSegundos
                self.horizontalSliderTiempoEnsayo.setMinimum(self.tiempoEnsayoMin) #valor del tiempo en milisegundos
                self.horizontalSliderTiempoEnsayo.setMaximum(self.tiempoEnsayoMax) #valor del tiempo en milisegundos
        if config=="rst":
            if slider=="ambos":
                self.horizontalSliderDelayPasos.setValue(self.delayPasos) #seteo el valor por default de la ultima config
                self.horizontalSliderTiempoEnsayo.setValue(self.tiempoEnsayo) #seteo el valor por default de la ultima config
            elif slider=="delayPasos":
                self.horizontalSliderDelayPasos.setValue(self.delayPasos) #seteo el valor por default de la ultima config
            else :
                self.horizontalSliderTiempoEnsayo.setValue(self.tiempoEnsayo) #seteo el valor por default de la ultima config
    
    def configSliderDelayPasos(self):
        self.labelValorDelayPasos.setText(str(self.horizontalSliderDelayPasos.value()))
        mCalibracion=-0.0028
        bCalibracion=5.9673
        caudal=mCalibracion*self.horizontalSliderDelayPasos.value()+bCalibracion #caudal aproximado
        diametroInterno=0.08 
        area=(3.1416*(diametroInterno**2))/4 
        velocidad=caudal/area
        volumenDescargado=caudal*self.horizontalSliderTiempoEnsayo.value()/1000
        self.labelValorCaudalDeDescarga.setText(f'{caudal:.2f} ml/s')
        self.labelValorVelocidadDeDescarga.setText(f'{velocidad:.2f} cm/s')
        self.verificacionGuardarConfiguracion()
        
    def configSliderTiempoEnsayo(self):
        self.labelValorTiempoEnsayo.setText(str(self.horizontalSliderTiempoEnsayo.value()))
        self.verificacionGuardarConfiguracion()
        
    def verificacionGuardarConfiguracion(self):
        #verifico que tanto el otro slider como el lineedit esten OK
        if self.horizontalSliderTiempoEnsayo.value()>=self.tiempoEnsayoMin and self.horizontalSliderDelayPasos.value()>=self.delayPasosMin and self.comboBoxVelocidadesCalib.isEnabled():
            self.pushButtonGuardarConfigCalib.setEnabled(True)
        else:
            self.pushButtonGuardarConfigCalib.setEnabled(False)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = GUI_Salpicaduras()
    window.show()
    sys.exit(app.exec_())
