from machine import Pin, PWM
from mfrc522 import MFRC522
import utime
import time
from umqtt.robust import MQTTClient
import ubinascii
import ujson
import network

servo = PWM(Pin(12, mode=Pin.OUT))
servo.freq(50)
       

rfid_reader = MFRC522(spi_id=0,sck=2,miso=4,mosi=7,cs=5,rst=18)

brojPristupa = 5

button1 = Pin(0, Pin.IN)



# Spajanje sa MQTT
nic = network.WLAN(network.STA_IF)
nic.active(True)
nic.connect('ETF-Logosoft', '')

while not nic.isconnected():
    print("Cekam konekciju")
    time.sleep(5)
   
print("WLAN konekcija uspostavljena")
ipaddr = nic.ifconfig()[0]

print("Mrezne postavke")
print(nic.ifconfig())

def sub(topic, message):
    print('Tema: ' + str(topic))
    print('Poruka: ' + str(message))
    if topic == b'sistem/alarmSistemObavijesti':
        if message == b'zakljucaj':
            time.sleep(2)
            servo.duty_u16(1638)
            time.sleep(15)
            servo.duty_u16(7000)

           
def publish(message):
    print("publisham")
    mqtt_conn.publish("sistem/alarmSistem", message)

# Generate a unique client_id
unique_id = ubinascii.hexlify(machine.unique_id()).decode('utf-8')
client_id = 'alarmSistem_' + unique_id

mqtt_conn = MQTTClient(client_id=client_id, server='broker.hivemq.com', user='', password='', port=1883)
mqtt_conn.set_callback(sub)
mqtt_conn.connect()
mqtt_conn.subscribe('sistem/alarmSistemObavijesti')
print("Uspjesno")

 

while True:
    if button1.value() == 1:
        time.sleep(2)
        servo.duty_u16(1638)
        time.sleep(10)
        servo.duty_u16(7000)
    rfid_reader.init()
    if brojPristupa == 0:
        brojPristupa = 3
        publish("aktiviraj")
    print("poceo")
    (card_status, card_type) = rfid_reader.request(rfid_reader.REQIDL)
    if card_status == rfid_reader.OK:
        (card_status, card_id) = rfid_reader.SelectTagSN()
        if card_status == rfid_reader.OK:
            rfid_card = int.from_bytes(bytes(card_id),"little",False)
            if rfid_card == 474653859:
                print("oK")
                time.sleep(2)
                servo.duty_u16(1638)
                time.sleep(10)
                servo.duty_u16(7000)
               
            else:
                print("Ne")
                brojPristupa = brojPristupa - 1
               
    utime.sleep(1)
    mqtt_conn.check_msg()
