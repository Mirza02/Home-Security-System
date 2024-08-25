import utime
from machine import Pin, PWM
import time

def start_buzzer(buzzerPinObject, frequency, ledObject):
    buzzerPinObject.duty_u16(int(65536 * 0.5)) 
    buzzerPinObject.freq(frequency)
    ledObject.value(1)

def stop_buzzer(buzzerPinObject):
    buzzerPinObject.duty_u16(0)
