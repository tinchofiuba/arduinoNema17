#include <EEPROM.h>

#define dir 11
#define pasos 13
#define enable 12

#define FinCarreraSup 7
#define FinCarreraInf 6

#define BotComenzar 3
#define BotSeleccion 2
  
String a,b,c;
int velocidad,tinicial,d,velocidad_serial;

int v_10=2800;
int v_4=1360;

void movimiento_motor()
{
digitalWrite(enable,LOW);  
digitalWrite(pasos,HIGH);
delayMicroseconds(velocidad);
digitalWrite(pasos,LOW);
delayMicroseconds(velocidad);    
  }

void setup() {
  Serial.begin(9600);
  pinMode(dir,OUTPUT);
  pinMode(pasos,OUTPUT);
  pinMode(enable,OUTPUT);
  digitalWrite(enable,LOW);  
  
  pinMode(FinCarreraSup,INPUT); //bot7
  pinMode(FinCarreraInf,INPUT); //bpot6
  
  pinMode(BotComenzar,INPUT);  //bot3
  pinMode(BotSeleccion,INPUT); //bot2
}

void loop() {
//entro al loop que me posibilita mover el psito hacia arriba
while(digitalRead(FinCarreraSup)==LOW)
{
digitalWrite(dir,HIGH);
//Serial.println("Subiendo motor hasta que cierre el final de carrera");
velocidad=800;
movimiento_motor();   
  }//endWhile

 //empiezo cuando apreto el boton de comienzo
 if (digitalRead(BotComenzar)==HIGH)
 {//Serial.println("se presionó el boton para comenzar el ensayo!!!!");
 if(digitalRead(BotSeleccion)==HIGH)
 {
 //Serial.println("bajando con delay de 800");
 velocidad=800; 
  }
 else
 {
  //Serial.println("Bajando con delay de 2000");
 velocidad=1600; 
  }

 //while(digitalRead(FinCarreraInf)==LOW)
 {
 digitalWrite(dir,LOW);
 //Serial.println("Bajando hasta que cierre el final de carrera de abajo");
 movimiento_motor(); 
 }

while(digitalRead(FinCarreraSup)==LOW)
{
digitalWrite(dir,HIGH);
//Serial.println("Subiendo motor hasta que cierre el final de carrera");
velocidad=750;
movimiento_motor();   
  }//endWhile
  
}//endif
//Serial.println("No se presionó el boton para comenzar!");
}
 /////////////////////////////////FIN DE LOOP/////////////////////////////////////////
