from machine import Pin, PWM, Timer, ADC
import utime
import time
from display import Display
from tastatura import citajSaTastature
from buzzer import start_buzzer, stop_buzzer
from homeSistem import homeSistem
import ujson
import network
from machine import Pin, PWM
from umqtt.robust import MQTTClient
import ubinascii
import socket


# Inicijalizacija pinova
triggerUnutra = Pin(6, Pin.OUT)
echoUnutra = Pin(7, Pin.IN)

triggerVani = Pin(8, Pin.OUT)
echoVani = Pin(9, Pin.IN)

BuzzerObj = PWM(Pin(5))
ledUnutra = Pin(10, Pin.OUT)

fotoAdc = ADC(Pin(28))
svjetloVani = Pin(4, Pin.OUT)
# =======================================

# Inicijalizacija potrebnih klasa
sistem = homeSistem()
displej = Display()
brojAktivacija = []
brojPokusaja = 3

# ======================================

# Varijable za spasavanje pocetka i kraja procitanog impulsa
start_time_unutra = 0
end_time_unutra = 0
start_time_vani = 0
end_time_vani = 0
# ====================================================

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
    if topic == b'sistem/alarmSistem':
        if message == b'ugasi buzzer':
            print("Gasim!")
            stop_buzzer(BuzzerObj)
        elif message == b'deaktiviraj':
            sistem.adminDeaktivirajAlarm()
            stop_buzzer(BuzzerObj)
            displej.postaviBoju(255, 255, 255)
            displej.prikaziGlavniEkran()
        elif message == b'aktiviraj':
            sistem.adminAktivirajAlarm()
            displej.prikaziNaEkranu("Alarm aktivan!!")
            brojAktivacija.append(utime.ticks_ms())
            print("All recorded tick values: ", brojAktivacija[0])
            soundAlarm()
            
    else:
        print(topic)
    

def publish(message):
    mqtt_conn.publish("sistem/alarmSistemObavijesti", message)

unique_id = ubinascii.hexlify(machine.unique_id()).decode('utf-8')
client_id = 'alarmSistem_' + unique_id

mqtt_conn = MQTTClient(client_id=client_id, server='broker.hivemq.com', user='', password='', port=1883)
mqtt_conn.set_callback(sub)
mqtt_conn.connect()
mqtt_conn.subscribe('sistem/alarmSistem')
print("Uspjesno")

# =============================================================

# Provjeravanje fotorezistora
def provjeriFoto(timer):
    print("provjervam", fotoAdc.read_u16())
    print("vrijednost", sistem.getPeriodPaljenja())
    vrijednostFoto = fotoAdc.read_u16()
    if vrijednostFoto > sistem.getPeriodPaljenja():
        svjetloVani.value(1)
    else:
        svjetloVani.value(0)
        
# Prikljucivanje vremenskog prekida funkciji za provjeravanje fotorezistora
timer = Timer(-1)
timer.init(period = 10000, mode = Timer.PERIODIC, callback = provjeriFoto)
# =================================================================

# Logika za provjeravanje udaljenosti na senzoru
# Slanje impulsa senzoru
def trigger_sensor(trigger):
    trigger.low()
    utime.sleep_us(2)
    trigger.high()
    utime.sleep_us(10)
    trigger.low()

def echo_callback_unutra(pin):
    global start_time_unutra, end_time_unutra
    if pin.value():
        start_time_unutra = utime.ticks_us()
    else:
        end_time_unutra = utime.ticks_us()

def echo_callback_vani(pin):
    global start_time_vani, end_time_vani
    if pin.value():
        start_time_vani = utime.ticks_us()
    else:
        end_time_vani = utime.ticks_us()

# Prikljucivanje prekida echo pinovima senzora
echoUnutra.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=echo_callback_unutra)
echoVani.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=echo_callback_vani)

# Racunanje udaljenosti
def calculate_distance(start_time, end_time):
    if start_time and end_time:
        time_passed = utime.ticks_diff(end_time, start_time)
        distance = (time_passed * 0.0343) / 2
        return distance
    return -1

def provjeriSenzore():
    global start_time_unutra, end_time_unutra, start_time_vani, end_time_vani
    
    trigger_sensor(triggerUnutra)
    utime.sleep_ms(100)
    distance_unutra = calculate_distance(start_time_unutra, end_time_unutra)
    
    trigger_sensor(triggerVani)
    utime.sleep_ms(100)
    distance_vani = calculate_distance(start_time_vani, end_time_vani)
    
    return distance_unutra, distance_vani
    
# =======================================================================

# Logika za aktivnu sirenu/alarm
def soundAlarm():
    publish("Aktivan alarm")
    global brojPokusaja
    start_buzzer(BuzzerObj, 450)
    entered_code = ""
    while sistem.isAlarmAktivan():
        mqtt_conn.check_msg()
        key = citajSaTastature()
        if key:
            print(f"Key pressed: {key}")
            if key != "#":
                entered_code += key
            print(f"Entered code: {entered_code}")
            if key == "#":
                if sistem.deaktivirajAlarm(entered_code):
                    displej.postaviBoju(255, 255, 255)
                    displej.prikaziNaEkranu("Deaktiviran")
                    print("Alarm deaktiviran.")
                    stop_buzzer(BuzzerObj)
                    ledUnutra.value(0)
                    time.sleep(1)
                    displej.prikaziGlavniEkran()
                    return
                else:
                    print("Incorrect code entered.")
                    entered_code = ""
                    brojPokusaja -= 1
    
# Alarm ceka unos ili ceka da se aktivira
def checkAlarm():
    global brojPokusaja
    print("Uoceno kretanje! Ukucajte sifru...")
    start_time = utime.ticks_ms()
    entered_code = ""

    while sistem.isAlarmAktivan():
        key = citajSaTastature()
        if key:
            if brojPokusaja == 0:
                displej.prikaziPoruku("Potrebna admin sifra!", tt24)
            print(f"Key pressed: {key}")
            if key != "#":
                entered_code += key
            print(f"Entered code: {entered_code}")
            if key == "#":
                if sistem.deaktivirajAlarm(entered_code):
                    displej.postaviBoju(255, 255, 255)
                    displej.prikaziNaEkranu("Deaktiviran")
                    print("Alarm deaktiviran.")
                    stop_buzzer(BuzzerObj)
                    ledUnutra.value(0)
                    time.sleep(1)
                    displej.prikaziGlavniEkran()
                    return
                else:
                    print("Incorrect code entered.")
                    entered_code = ""
                    brojPokusaja -= 1
        
        distance_unutra, distance_vani = provjeriSenzore()
        print(f"Distance inside: {distance_unutra}, Distance outside: {distance_vani}")
        if distance_unutra > 15 and distance_vani > 15:
            displej.postaviBoju(255, 255, 255)
            displej.prikaziNaEkranu("Ok")
            time.sleep(0.5)
            displej.prikaziNaEkranu("Alarm aktivan")
            return
            
        
        if utime.ticks_diff(utime.ticks_ms(), start_time) > 15000:
            displej.prikaziNaEkranu("Alarm aktivan!!")
            brojAktivacija.append(utime.ticks_us())
            print("All recorded tick values: ", brojAktivacija[0])
            soundAlarm()
            return
            
# Logika za mijenjanje sifre
def promjenaSifre():
    print("Ukucajte novu sifru: ")
    entered_code = ""
    while sistem.isUnos():
        key = citajSaTastature()
        if key:
            print(f"Key pressed: {key}")
            if key != "#":
                entered_code += key
            print(f"Entered code: {entered_code}")
            if key == "#" and len(entered_code) == 4:
                sistem.promjeniSifruAlarm(entered_code)
                displej.prikaziNaEkranu("Sifra promijenjena")
                time.sleep(1)
                sistem.setUnos(False)
                displej.prikaziGlavniEkran()
                return
            if key == "C":
                entered_code = ""

# Provjeravanje senzora kada je alarm aktivan
def alarmAktivanState():
    distance_unutra, distance_vani = provjeriSenzore()
    print(f"Distance inside: {distance_unutra}, Distance outside: {distance_vani}")
    ledUnutra.value(1)
    time.sleep(0.2)
    ledUnutra.value(0)
            
    if distance_unutra < 15 or distance_vani < 15:
        displej.prikaziAlarmUpozorenje()
        checkAlarm()
# ======================================================================


# Izbor vrijednosti za fotorezistor
def izaberiPeriodSvjetlo():
    while sistem.getMijenjajPeriod:
        key = citajSaTastature()
        if key:
            print(f"Key pressed: {key}")
            if key == "A":
                sistem.setPeriodPaljenja(58000)
                displej.prikaziNaEkranu("Uspjesno promijenjeno")
                displej.prikaziGlavniEkran()
                time.sleep(1)
                sistem.setMijenjajPeriod(False)
                return
            if key == "B":
                sistem.setPeriodPaljenja(55000)
                displej.prikaziNaEkranu("Uspjesno promijenjeno")
                time.sleep(1)
                displej.prikaziGlavniEkran()
                sistem.setMijenjajPeriod(False)
                return
            if key == "C":
                sistem.setPeriodPaljenja(63000)
                displej.prikaziNaEkranu("Uspjesno promijenjeno")
                time.sleep(1)
                displej.prikaziGlavniEkran()
                sistem.setMijenjajPeriod(False)
                return
# ==================================================================


# Citanje vrijednosti na pocetnom ekranu
def pocetniEkran():
    key = citajSaTastature()
    if key:
        print(f"Key pressed: {key}")
        if key == "A":
            displej.prikaziNaEkranu("Alarm aktivan!")
            sistem.adminAktivirajAlarm()
            publish("zakljucaj")
        if key == "B":
            displej.prikaziPaljenja(brojAktivacija[-3:])
            time.sleep(10)
            displej.prikaziGlavniEkran()
        if key == "C":
            displej.prikaziIzborPerioda()
            sistem.setMijenjajPeriod(True)
            izaberiPeriodSvjetlo()
        if key == "D":
            displej.prikaziNaEkranu("Unesite novu sifru: ")
            sistem.setUnos(True)
            promjenaSifre()
# ==============================================================


def pocetnaValidacija():
    global brojPokusaja
    displej.prikaziValidacijuKorisnika()
    entered_code = ""
    while brojPokusaja > 0:
        key = citajSaTastature()
        if key:
            print(f"Key pressed: {key}")
            if key != "#":
                entered_code += key
            print(f"Entered code: {entered_code}")
            if key == "#":
                if sistem.isValidnaAdminSifra(entered_code):
                    displej.prikaziNaEkranu("Dobro dosli!")
                    sistem.setPocetniEkran(True)
                    displej.prikaziGlavniEkran()
                    return
                else:
                    brojPokusaja -= 1
                    displej.prikaziValidacijuKorisnika(brojPokusaja)
                    entered_code = ""  # Reset entered code
            if key == "C":
                entered_code = ""

displej.showStartupMessage()

pocetnaValidacija()

while True:
    if sistem.isPocetniEkran():
        mqtt_conn.check_msg()
        pocetniEkran()
    if sistem.isAlarmAktivan():
        alarmAktivanState()
    
    utime.sleep(1)


