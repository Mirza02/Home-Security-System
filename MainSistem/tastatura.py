from machine import Pin
import time

kolone = [Pin(0, Pin.IN), Pin(1, Pin.IN), Pin(2, Pin.IN), Pin(3, Pin.IN)]
redovi = [Pin(21, Pin.OUT), Pin(22, Pin.OUT), Pin(26, Pin.OUT), Pin(27, Pin.OUT)]

tastaturaVrijednosti = [
    ['1', '2', '3', 'A'],
    ['4', '5', '6', 'B'],
    ['7', '8', '9', 'C'],
    ['*', '0', '#', 'D']
]

def citajSaTastature():
    for indeksReda, red in enumerate(redovi):
        red.value(1)
        for indeksKolone, kolona in enumerate(kolone):
            if kolona.value() == 1:
                while kolona.value() == 1:
                    time.sleep(0.01)
                red.value(0)
                return tastaturaVrijednosti[indeksReda][indeksKolone]
        red.value(0)
    return None
