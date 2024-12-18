#include <EEPROM.h>

#define dir 11
#define pasos 13
#define enable 12

#define FinCarreraSup 7
#define FinCarreraInf 6
#define BotReset 4
#define BotComenzar 3
#define BotSeleccion 2
#define lapsoTiempo 600
#define V_salpicaduras 900

int velocidad,t0,tiempo;

void movimiento_motor()
{ 
digitalWrite(enable,LOW); //habilito el motor
if (digitalRead(FinCarreraInf)==LOW)
{
digitalWrite(pasos,HIGH);
delayMicroseconds(velocidad);
digitalWrite(pasos,LOW);
delayMicroseconds(velocidad);    
}
digitalWrite(enable,HIGH); //deshabilito el motor
}

void movimientoHaciaOrigen()
{
Serial.println("moviendo hacia origen");
while(digitalRead(FinCarreraSup)==LOW) //mientras el FC esté abierto
{
//Serial.println(digitalRead(FinCarreraSup));
//Serial.println(digitalRead(FinCarreraInf));

//Serial.println("Subiendo motor hasta que cierre el final de carrera");
velocidad=800;
movimiento_motor();
}
Serial.println("ya en orgien");
//digitalWrite(dir,LOW); //direcciono el movimiento hacia arriba/atrás
}

void setup() {
  digitalWrite(dir,HIGH); //direcciono el movimiento hacia adelante/abajo
  Serial.begin(9600);
  pinMode(dir,OUTPUT);
  pinMode(pasos,OUTPUT);
  pinMode(enable,OUTPUT);
  digitalWrite(enable,HIGH);  
  
  pinMode(FinCarreraSup,INPUT); //pin7
  pinMode(FinCarreraInf,INPUT); //pin6
  pinMode(BotComenzar,INPUT);  //pin3
  pinMode(BotSeleccion,INPUT); //pin2
  pinMode(BotReset,INPUT); //pin4
}

void loop() {
Serial.println(digitalRead(BotComenzar));
Serial.println(digitalRead(FinCarreraInf));
Serial.println(digitalRead(FinCarreraSup));
Serial.println(digitalRead(BotComenzar));
Serial.println("iniciado");
//------------POSICIONAMIENTO INICIAL---------//
movimientoHaciaOrigen(); // primera etapa del ensayo, se vuelve a origen
}
