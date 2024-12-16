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
        self.horizontalSliderDelayPasos.valueChanged.connect(self.configSliderDelayPasos)
        self.horizontalSliderTiempoEnsayo.valueChanged.connect(self.configSliderTiempoEnsayo)
        self.pushButtonResetDelayPasos.clicked.connect(lambda: self.configLimitesliders("delayPasos"))
        self.pushButtonResetTiempoEnsayo.clicked.connect(lambda: self.configLimitesliders("tiempoEnsayo"))
        self.pushButtonCargarConfigCalib.clicked.connect(self.cargarConfiguracion)
        
    def cargarConfiguracion(self):
        #abro una ventana de dialogo que me permita seleccionar un archivo json para luego abrirlo
        #y cargar los valores en los widgets correspondientes
        
        #abro la ventana de dialogo
        file = QFileDialog.getOpenFileName(self, "Abrir archivo de calibración", "", "JSON Files (*.json)")
        
        
    def configLimitesliders(self,slider): #en función del argumento reseteo, o configuro uno/los dos sliders
        if slider=="ambos":
            self.horizontalSliderDelayPasos.setMinimum(400) #valor del tiempo en microSegundos
            self.horizontalSliderDelayPasos.setMaximum(2000) #valor del tiempo en microSegundos
            self.horizontalSliderTiempoEnsayo.setMinimum(400) #valor del tiempo en milisegundos
            self.horizontalSliderTiempoEnsayo.setMaximum(1000) #valor del tiempo en milisegundos
        elif slider=="delayPasos":
            self.horizontalSliderDelayPasos.setMinimum(400) #valor del tiempo en microSegundos
            self.horizontalSliderDelayPasos.setMaximum(2000) #valor del tiempo en microSegundos
        else :
            self.horizontalSliderTiempoEnsayo.setMinimum(400) #valor del tiempo en milisegundos
            self.horizontalSliderTiempoEnsayo.setMaximum(1000) #valor del tiempo en milisegundos
    
    def configSliderDelayPasos(self):
        self.labelValorDelayPasos.setText(str(self.horizontalSliderDelayPasos.value()))
        self.guardarConfiguracion()
        
    def configSliderTiempoEnsayo(self):
        self.labelValorTiempoEnsayo.setText(str(self.horizontalSliderTiempoEnsayo.value()))
        self.guardarConfiguracion()
        
    def guardarConfiguracion(self):
        #verifico que tanto el otro slider como el lineedit esten OK
        if self.horizontalSliderTiempoEnsayo.value()!=0 and self.horizontalSliderDelayPasos.value()!=0:
            self.pushButtonGuardarConfigCalib.setEnabled(True)
        else:
            self.pushButtonGuardarConfigCalib.setEnabled(False)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = GUI_Salpicaduras()
    window.show()
    sys.exit(app.exec_())
