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

bool comenzar,origen,avanzar,retroceder,conectado;

void movimiento_motor(int vel)
{
digitalWrite(pasos,HIGH);
delayMicroseconds(vel);
digitalWrite(pasos,LOW);
delayMicroseconds(vel);    
}
  
void movimientoHaciaOrigen()
{
  while(digitalRead(FinCarreraSup)==LOW)
  {
  //Serial.println("subiendo");
    digitalWrite(enable,LOW); //activo el motor  
    digitalWrite(dir,HIGH);
    //Serial.println("Subiendo motor hasta que cierre el final de carrera");
    movimiento_motor(800);   
   }//endWhile
   digitalWrite(enable,HIGH); //activo el motor 
   origen=false;
}

void salpicar(int tiempoSalpicado)
{  
   unsigned long t0=millis();
   while (millis()-t0<tiempoSalpicado)
   {   //Serial.println("moviendo!!");
     if (digitalRead(FinCarreraInf)==LOW)
       {
         digitalWrite(enable,LOW); //activo el motor  
         digitalWrite(dir,LOW);
         //Serial.println("Bajando hasta que cierre el final de carrera de abajo");
         movimiento_motor(velPasos); 
       }
     else
       {
        origen=true; 
       }
   }
  }

void lecturaSerial(String condicion)
{
 if (Serial.available() > 0) 
  {String lectura = Serial.readStringUntil('\n');
    if (condicion=="loop")
    {
      int i=lectura.indexOf("Init");
      if (i!=-1) //si se encuentra la palabra Init en el mensaje, se inicializa el core del programa
        {
          delay(200);
          conectado=true;
          Serial.println("salpicaduraInitOK");
        }
       else if (conectado==true) //si no se encuentra la palabra Init, pero ya se inicializó, se parsea el mensaje
        {
          parsearMensaje(lectura);
        }
       
    }
     else if (condicion=="ensayo")
     {
       if (conectado==true)
        {
          parsearMensaje(lectura);
        }
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
      //comenzar=true;
    }
  else 
  {
    if (msg.indexOf("origen")!=-1)
    {
    origen=true;
    comenzar=true;  
    }
    else
    {
      if (msg.indexOf("avanzar")!=-1)
        {
        avanzar=true; 
        comenzar=true;   
        }
      else
      {
      if (msg.indexOf("retroceder")!=-1)
        {
        retroceder=true;
        comenzar=true;     
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
//entro al loop que me posibilita mover el psito hacia arriba
if (origen==true)
{
 //Serial.println("sub");
 movimientoHaciaOrigen();
}
//Serial.println("-");
 lecturaSerial("loop");

 if (conectado==true)
 {
  lecturaSerial("ensayo");
  //Serial.println("assaas");

  
   while (digitalRead(FinCarreraInf)==LOW)
   {  lecturaSerial("ensayo");
     //empiezo cuando apreto el boton de comienzo
     //Serial.println("esperando a que se aprete el boton");
     if (digitalRead(BotComenzar)==HIGH)
       {//Serial.println("se presionó el boton para comenzar el ensayo!!!!");
        //Serial.println("comenzado");
       velocidad=velPasos;
       salpicar(velEnsayo);
       digitalWrite(enable,HIGH); //activo el motor  
      }//endif
    //Serial.println("No se presionó el boton para comenzar!");
   if (digitalRead(FinCarreraInf==HIGH))
   {
   origen=true;
   }
  }
}


}//endLoop

 /////////////////////////////////FIN DE LOOP/////////////////////////////////////////
