#include <EEPROM.h>

#define dir 11
#define pasos 13
#define enable 12

#define FinCarreraSup 7
#define FinCarreraInf 6

#define BotComenzar 3
#define BotSeleccion 2
  
String a,b,c;
int velocidad,tinicial,d,velPasos,velEnsayo;

int v_10=2800;
int v_4=1360;

bool comenzar,origen,avanzar,retroceder,lubricar;

void movimientoMotor(int vel)
{
digitalWrite(pasos,HIGH);
delayMicroseconds(vel);
digitalWrite(pasos,LOW);
delayMicroseconds(vel);    
}
  
void movimientoHaciaOrigen()
{//Serial.println("hacia origen");
  while(digitalRead(FinCarreraSup)==LOW)
  {
    digitalWrite(enable,LOW); //activo el motor  
    digitalWrite(dir,HIGH);
    movimientoMotor(800);   
   }//endWhile
   digitalWrite(enable,HIGH); //activo el motor 
}

void salpicar(int tiempoSalpicado,String direccion)
{  
   if (direccion=="avanzar")
   {
   digitalWrite(dir,LOW);
   }
   else
   {
   if (direccion=="retroceder")
   {
   digitalWrite(dir,HIGH);
   }
   }
   
   unsigned long t0=millis();
   while (millis()-t0<tiempoSalpicado)
   { 
     if (digitalRead(FinCarreraInf)==LOW)
       {
         digitalWrite(enable,LOW); //activo el motor  
         movimientoMotor(velPasos); 
       }
     else
       {
        origen=true; 
       }
   }
  }

void lecturaSerial()
{
 if (Serial.available() > 0) 
  {String lectura = Serial.readStringUntil('\n');
      int i=lectura.indexOf("Init");
      if (i!=-1) //si se encuentra la palabra Init en el mensaje, se inicializa el core del programa
        {
          delay(50);
          //conectado=true;
          Serial.println("salpicaduraInitOK");
        }
       else
        {
          parsearMensaje(lectura);
        }
        }
        }


void parsearMensaje(String msg) 
{  int index1 = msg.indexOf("velPasos");
   int index2 = msg.indexOf(",velEnsayo");
  if (index1!=-1 && index2!=-1) //si encuentra las palabras clave en el mensaje
  {
      String strVelPasos=msg.substring(index1+8,index2);
      String strVelEnsayo=msg.substring(index2+10);
      velPasos=strVelPasos.toInt();
      velEnsayo=strVelEnsayo.toInt();
      //Serial.println("Se recibió las velocidades de configuración");
    }
  else 
  {
    if (msg.indexOf("origen")!=-1)
    {
    origen=true;
    //Serial.println("origen"); 
    }
    else
    {
      if (msg.indexOf("avanzar")!=-1)
        {
        avanzar=true; 
        //Serial.println("avanzar"); 
        }
      else
      {
      if (msg.indexOf("retroceder")!=-1)
        {
        retroceder=true;
        //Serial.println("retroceder");  
        }
      if (msg.indexOf("comenzar")!=-1)
        {
        comenzar=true;
        //Serial.println("comenzar");  
        }
      else
      {
      if (msg.indexOf("lubricar")!=-1)
        {
        lubricar=true;
        //Serial.println("comenzar");  
        }  
      }
       
      }
    }
    
  }
}
  
void setup() {
  Serial.begin(9600);
  pinMode(dir,OUTPUT);
  pinMode(pasos,OUTPUT);
  pinMode(enable,OUTPUT);
  digitalWrite(enable,HIGH);  
  comenzar=false;
  origen=true;
  avanzar=false;
  retroceder=false;
  pinMode(FinCarreraSup,INPUT); //bot7
  pinMode(FinCarreraInf,INPUT); //bpot6
  pinMode(BotComenzar,INPUT);  //bot3
  pinMode(BotSeleccion,INPUT); //bot2
}

void loop() {
lecturaSerial();


if (origen==true)
  {
   //Serial.println("subiendo"); //para debug
   movimientoHaciaOrigen();
   //Serial.println("subido y en posicion"); //para debug
   origen=false;
  }


if (avanzar==true)
{
  velocidad=800; //velocidad de avance
  salpicar(200,"avanzar"); 
  avanzar=false;
}


if (retroceder==true)
{
  velocidad=800; //velocidad de avance
  salpicar(200,"retroceder"); 
  retroceder=false;
}


if (comenzar==true)
{
  //Serial.println("comenzando ensayo");
  velocidad=velPasos;
  salpicar(velEnsayo,"avanzar");
  digitalWrite(enable,HIGH); //activo el motor  
  //Serial.println("Ensayo finalizado"); //debug
  comenzar=false;
}

if (lubricar==true)
{lubricar=false;
  for(byte i=0;i<2;i++)
    {
    digitalWrite(enable,LOW);
    digitalWrite(dir,LOW);
    while(digitalRead(FinCarreraInf)==LOW)
    {
    movimientoMotor(800);
    }
    digitalWrite(dir,HIGH);
    while(digitalRead(FinCarreraSup)==LOW)
    {
    movimientoMotor(800);
    }
    }
    digitalWrite(enable,HIGH);
}


}//endLoop

 /////////////////////////////////FIN DE LOOP/////////////////////////////////////////
