
int velocidad, t0, tiempo;
String lecturaSerial;

void setup() {
  Serial.begin(9600);
  pinMode(13,OUTPUT);
}

void loop() {
  // Si el serial está disponible:
  if (Serial.available() > 0) 
  {
    // Leer la cadena desde el puerto serial
    lecturaSerial = Serial.readString();
    // Imprimir la cadena leída
    // Me fijo si en lectura está la palabra "Init"
    int i=lecturaSerial.indexOf("Init");
    String ensayo=lecturaSerial.substring(0, i);
    if (ensayo=="salpicadura"){
      digitalWrite(13,HIGH);
      delay(200);
      Serial.println("salpicaduraInitOK");
      digitalWrite(13,LOW);
    }
    else{
      digitalWrite(13,HIGH);
      delay(200); 
      Serial.println("salpicaduraInitFail");
      digitalWrite(13,LOW);
    }
  }
}
