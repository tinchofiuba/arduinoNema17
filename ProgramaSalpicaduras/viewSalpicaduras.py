import sys
from PyQt5.QtWidgets import QApplication, QDialog
from salpicaduras import Ui_Dialog
from modelSalpicaduras import Model
import os
import sys
import json
#importo lo necesario para abrir un QFileDialog
from PyQt5.QtCore import Qt,QTimer,QThread,pyqtSignal
from PyQt5.QtWidgets import QFileDialog,QTableWidgetItem
import pandas as pd
import time
import serial

try:
    arduino=serial.Serial('COM8',9600)
    time.sleep(2)
    print(f"Conectado al puerto {arduino.port}")
    #imprimo el puerto seriel al que se conecto el arduino
    arduino.write('salpicaduraInit'.encode()) #envio un mensaje al arduino para que sepa que se vinculo con la aplicación
except:
    print("No se pudo conectar con el arduino")

dictDataFrame={"Nº Repeticion":[],"Velocidad":[],"Resultado":[],"Observaciones":[]}
class GUI_Salpicaduras(QDialog, Ui_Dialog):
    def __init__(self):
        #escribo "salpicaduraInit" para vincular con el arduino y luego leo lo que me dice el arduino con un serial.read
        self.dfResultados=pd.DataFrame(dictDataFrame) #creo por 1era vez un dataFrame 
        model=Model()
        super().__init__()
        
        self.timer = QTimer(self)
        self.timer.start(1000) 
        self.timer.timeout.connect(self.lecturaSerialArduino)
        self.setupUi(self)
        self.configLimitesliders("ambos")
        #prohibo que la aplicación se redimensione
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
        self.pushButtonResetDelayPasos.clicked.connect(lambda: self.configLimitesliders("delayPasos"))
        self.pushButtonResetTiempoEnsayo.clicked.connect(lambda: self.configLimitesliders("tiempoEnsayo"))
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
        velPasos=self.horizontalSliderDelayPasos.value()
        velEnsayo=self.horizontalSliderTiempoEnsayo.value()
        if self.velPasosAnt!=velPasos or self.velEnsayoAnt!=velEnsayo:
            mensaje=f'velPasos{velPasos},velEnsayo{velEnsayo}'
            self.velPasosAnt=velPasos
            self.velEnsayoAnt=velEnsayo
            arduino.write(mensaje.encode())
            time.sleep(1)
            arduino.write(mje.encode())
        else:
            arduino.write(mje.encode())


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
            mensaje=mje
            arduino.write(mensaje.encode())    
        except:
            print("No se pudo enviar el mensaje al arduino")

    def lecturaSerialArduino(self):
        print("...esperando respuesta del arduino...")
        while True:
            try:
                #me fijo si recibo algo del arduino
                time.sleep(1)
                if arduino.inWaiting() > 0:
                    print("Intentando leer el mensaje del arduino")
                    lectura=arduino.readline().decode("utf-8").strip()
                    if lectura == "salpicaduraInitOK":
                        print("Equipo vinculado listo para comenzar ensayo")
                        self.timer.stop()
                        break
                    else:
                        print(arduino.readline().decode("utf-8").strip())
            except:
                break

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
        #►agrego una fila al dataframe
        self.nuevaFila=pd.DataFrame([{"Nº Repeticion":self.numeroRepeticion,"Velocidad":self.velocidadEnsayo,"Resultado":self.resultado,"Observaciones":"No"}])
        self.dfResultados=pd.concat([self.dfResultados,self.nuevaFila],ignore_index=True)
        print(self.dfResultados)
        #hago un delay de 1 seg
        time.sleep(1)  #emu
        #aca habría que ver de recibir la señal de arduino y hacer algo.
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
            self.pushButtonLubricar.setEnabled(False)
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
        #abro un dialogo para guardar el archivo
        file = QFileDialog.getSaveFileName(self, "Guardar archivo de calibración", "", "JSON Files (*.json)")
        self.nombreArchivoCalibracion=os.path.splitext(file[0])[0]
        with open(f'{self.direccionArchivoConfiguración}','w') as file:
            json.dump(self.calibracion,file)
        print("archivo guardado!")
        self.actualizarValoresPorcomboBoxEnsayo()
        
    
    def cargarConfiguracion(self):
        file = QFileDialog.getOpenFileName(self, "Abrir archivo de calibración", "", "JSON Files (*.json)")
        self.nombreArchivoCalibracion=os.path.splitext(file[0])
        self.direccionArchivoConfiguración=self.nombreArchivoCalibracion[0]
        if len(file[0])>0: #si se selecciono un archivo
            try :
                with open(file[0],'r') as data:
                    print("archivo seleccionado")
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
                    print("archivo cargado")
            except:
                print("error al cargar el archivo Json, o error al leer los valores")
                
    def actualizarValoresPorcomboBoxCalibracion(self):
        if self.comboBoxVelocidadesCalib.currentText()!="": #esto es por que al borrar el combobox, para poblarlo con nuevos items, al ppio no va a tener items
            self.horizontalSliderDelayPasos.setValue(self.calibracion[self.comboBoxVelocidadesCalib.currentText()]["delayPasos"]) 
            self.horizontalSliderTiempoEnsayo.setValue(self.calibracion[self.comboBoxVelocidadesCalib.currentText()]["tiempoEnsayo"])
              
    def configLimitesliders(self,slider): #en función del argumento reseteo, o configuro uno/los dos sliders
        self.delayPasosMin=400
        self.delayPasosMax=2000
        self.tiempoEnsayoMin=400
        self.tiempoEnsayoMax=1000
        if slider=="ambos":
            self.horizontalSliderDelayPasos.setMinimum(self.delayPasosMin) #valor del tiempo en microSegundos
            self.horizontalSliderDelayPasos.setMaximum(self.delayPasosMax) #valor del tiempo en microSegundos
            self.horizontalSliderTiempoEnsayo.setMinimum(self.tiempoEnsayoMin) #valor del tiempo en milisegundos
            self.horizontalSliderTiempoEnsayo.setMaximum(self.tiempoEnsayoMax) #valor del tiempo en milisegundos
        elif slider=="delayPasos":
            self.horizontalSliderDelayPasos.setvalue(self.delayPasosMin) #valor del tiempo en microSegundos
            self.horizontalSliderDelayPasos.setMaximum(self.delayPasosMax) #valor del tiempo en microSegundos
        else :
            self.horizontalSliderTiempoEnsayo.setMinimum(self.tiempoEnsayoMin) #valor del tiempo en milisegundos
            self.horizontalSliderTiempoEnsayo.setMaximum(self.tiempoEnsayoMax) #valor del tiempo en milisegundos
    
    def configSliderDelayPasos(self):
        self.labelValorDelayPasos.setText(str(self.horizontalSliderDelayPasos.value()))
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
