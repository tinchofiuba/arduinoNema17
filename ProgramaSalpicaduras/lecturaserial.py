import serial

#escrito por serial a un arduino, a 9600 baud y por el COM8 "salpicadiuraInit" y leo lo que recibo del arduino
ser = serial.Serial('COM8', 9600)
ser.write('salpicaduraInit'.encode())
#le doy un tiempo para que el arduino responda
ser.timeout = 1
print(ser.readline())
ser.close()
