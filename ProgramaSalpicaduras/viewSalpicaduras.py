import sys
from PyQt5.QtWidgets import QApplication, QDialog
from salpicaduras import Ui_Dialog
from modelSalpicaduras import Model
import os
import sys
import json
#importo lo necesario para abrir un QFileDialog
from PyQt5.QtWidgets import QFileDialog


class GUI_Salpicaduras(QDialog, Ui_Dialog):
    def __init__(self):
        print(os.getcwd())
        model=Model()
        super().__init__()
        self.setupUi(self)
        self.configLimitesliders("ambos")
        #prohibo que la aplicación se redimensione
        self.setFixedSize(self.size())
        self.comboBoxVelocidadesCalib.setEnabled(False)
        self.comboBoxVelocidadesCalib.currentIndexChanged.connect(self.actualizarValoresPorcomboBox)
        self.horizontalSliderDelayPasos.valueChanged.connect(self.configSliderDelayPasos)
        self.horizontalSliderTiempoEnsayo.valueChanged.connect(self.configSliderTiempoEnsayo)
        self.pushButtonResetDelayPasos.clicked.connect(lambda: self.configLimitesliders("delayPasos"))
        self.pushButtonResetTiempoEnsayo.clicked.connect(lambda: self.configLimitesliders("tiempoEnsayo"))
        self.pushButtonCargarConfigCalib.clicked.connect(self.cargarConfiguracion)
        self.pushButtonGuardarConfigCalib.clicked.connect(self.guardarConfiguracionCalibracion)
    
    
    def guardarConfiguracionCalibracion(self):
        self.calibracion[self.comboBoxVelocidadesCalib.currentText()]["delayPasos"]=self.horizontalSliderDelayPasos.value()
        self.calibracion[self.comboBoxVelocidadesCalib.currentText()]["tiempoEnsayo"]=self.horizontalSliderTiempoEnsayo.value()
        #abro un dialogo para guardar el archivo
        file = QFileDialog.getSaveFileName(self, "Guardar archivo de calibración", "", "JSON Files (*.json)")
        self.nombreArchivoCalibracion=os.path.splitext(file[0])[0]
        print(self.nombreArchivoCalibracion)
        print(self.calibracion)
        with open(f'{self.nombreArchivoCalibracion}.json','w') as file:
            json.dump(self.calibracion,file)
        print("archivo guardado!")
        
    
    def cargarConfiguracion(self):
        file = QFileDialog.getOpenFileName(self, "Abrir archivo de calibración", "", "JSON Files (*.json)")
        self.nombreArchivoCalibracion=os.path.splitext(file[0])
        print(file)
        try :
            with open(file[0],'r') as data:
                print("archivo seleccionado")
                self.calibracion=json.load(data)
                self.comboBoxVelocidadesCalib.setEnabled(True)
                self.pushButtonGuardarConfigCalib.setEnabled(True)
                self.comboBoxVelocidadesCalib.clear()
                self.comboBoxVelocidadesCalib.addItems(self.calibracion.keys())
                self.horizontalSliderDelayPasos.setValue(self.calibracion[self.comboBoxVelocidadesCalib.currentText()]["delayPasos"]) 
                self.horizontalSliderTiempoEnsayo.setValue(self.calibracion[self.comboBoxVelocidadesCalib.currentText()]["tiempoEnsayo"])
                print("archivo cargado")
        except:
            print("error al cargar el archivo Json, o error al leer los valores")
            
    def actualizarValoresPorcomboBox(self):
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
            self.horizontalSliderDelayPasos.setMinimum(self.delayPasosMin) #valor del tiempo en microSegundos
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
