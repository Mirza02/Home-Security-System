from ili934xnew import ILI9341, color565
from machine import Pin, SPI
from micropython import const
import glcdfont
import tt14
import tt24
import tt32
import time
import utime

class Display:      # staticki atributi za displej
    SCR_WIDTH = 320
    SCR_HEIGHT = 240
    SCR_ROT = 2
    CENTER_Y = int(SCR_HEIGHT / 2)
    CENTER_X = int(SCR_WIDTH / 2)
    LEFT_MARGIN = 10
    TOP_MARGIN = 20
    TFT_CLK_PIN = const(18)
    TFT_MOSI_PIN = const(19)
    TFT_MISO_PIN = const(16)
    TFT_CS_PIN = const(17)
    TFT_RST_PIN = const(20)
    TFT_DC_PIN = const(15)
    fonts = [glcdfont, tt14, tt24, tt32]

    def __init__(self):     # incijalizacija displeja kao na vjezbama
        self.spi = SPI(
            0,
            baudrate=62500000,
            miso=Pin(self.TFT_MISO_PIN),
            mosi=Pin(self.TFT_MOSI_PIN),
            sck=Pin(self.TFT_CLK_PIN)
        )

        self.display = ILI9341(
            self.spi,
            cs=Pin(self.TFT_CS_PIN),
            dc=Pin(self.TFT_DC_PIN),
            rst=Pin(self.TFT_RST_PIN),
            w=self.SCR_WIDTH,
            h=self.SCR_HEIGHT,
            r=self.SCR_ROT
        )
        print("SPI initialized:", self.spi)
        self.display.erase()

    def prikaziPoruku(self, message, font):
        self.display.set_font(font)
        totalLength = font.get_width(message)
        startPosition = (self.SCR_HEIGHT - totalLength) // 2
        self.display.set_pos(startPosition, self.display._y)
        self.display.print(message)


    def showStartupMessage(self) -> None:
        self.display.erase()
        self.display.set_pos(self.LEFT_MARGIN, self.TOP_MARGIN)
        self.prikaziPoruku("Sigurnosni sistem", tt32)

        self.display.set_pos(self.LEFT_MARGIN, self.TOP_MARGIN + 80)
        self.prikaziPoruku("Ucitava se...", tt24)
        time.sleep(1)

    def prikaziGlavniEkran(self):
        self.display.erase()
        self.display.set_pos(self.LEFT_MARGIN, self.TOP_MARGIN)
        self.prikaziPoruku("Izaberite opciju", tt24)

        self.display.set_pos(self.LEFT_MARGIN, self.TOP_MARGIN + 160)
        self.prikaziPoruku("A - aktivacija alarma", tt14)
        self.display.set_pos(self.LEFT_MARGIN, self.TOP_MARGIN + 180)
        self.prikaziPoruku("B - pregled pristupa", tt14)
        self.display.set_pos(self.LEFT_MARGIN, self.TOP_MARGIN + 200)
        self.prikaziPoruku("C - podesavanje paljenja svjetla", tt14)
        self.display.set_pos(self.LEFT_MARGIN, self.TOP_MARGIN + 220)
        self.prikaziPoruku("D - promjena sifre", tt14)

    def prikaziAlarmUpozorenje(self):
        self.display.erase()
        self.display.set_pos(self.LEFT_MARGIN, self.TOP_MARGIN + 150)
        self.display.set_color(color565(255, 20, 0), color565(0, 0, 0))
        self.prikaziPoruku("Uoceno kretanje!", tt24)

    def prikaziValidacijuKorisnika(self):
        self.display.erase()
        self.display.set_pos(self.LEFT_MARGIN, self.TOP_MARGIN)
        self.prikaziPoruku("Aktivacija sistema", tt32)

        self.display.set_pos(self.LEFT_MARGIN, self.TOP_MARGIN + 80)
        self.prikaziPoruku("Unesite sifru: ", tt24)
        time.sleep(1)


    def prikaziNaEkranu(self, message):
        self.display.erase()
        self.display.set_pos(self.LEFT_MARGIN, self.TOP_MARGIN + 150)
        self.prikaziPoruku(message, tt24)

        
    def postaviBoju(self, red, green, blue):
        self.display.set_color(color565(red, green, blue), color565(0, 0, 0))
        
    def prikaziIzborPerioda(self):
        self.display.erase()
        self.display.set_pos(self.LEFT_MARGIN, self.TOP_MARGIN)
        self.prikaziPoruku("Period paljenja", tt24)

        self.display.set_pos(self.LEFT_MARGIN, self.TOP_MARGIN + 160)
        self.prikaziPoruku("A - ujutru", tt14)
        self.display.set_pos(self.LEFT_MARGIN, self.TOP_MARGIN + 180)
        self.prikaziPoruku("B - poslije podne", tt14)
        self.display.set_pos(self.LEFT_MARGIN, self.TOP_MARGIN + 200)
        self.prikaziPoruku("C - navecer", tt14)
        
    def prikaziPaljenja(self, paljenja):
        self.display.erase()
        self.display.set_pos(self.LEFT_MARGIN, self.TOP_MARGIN)
        self.prikaziPoruku("Zadnje tri aktivacije", tt24)
    
        current_time = utime.ticks_us()
    
    
        if len(paljenja) == 0:
            self.display.set_pos(self.LEFT_MARGIN, self.TOP_MARGIN + 160)
            self.prikaziPoruku("Nije bilo paljenja", tt14)
        elif len(paljenja) == 1:
            print(current_time)
            print(paljenja[0])
            self.display.set_pos(self.LEFT_MARGIN, self.TOP_MARGIN + 160)
            delta_time1 = (current_time - paljenja[0]) // 60000000  # Pretvaranje ticks u minute
            self.prikaziPoruku(f"Prije {delta_time1} min", tt14)
        
        if len(paljenja) == 2:
            self.display.set_pos(self.LEFT_MARGIN, self.TOP_MARGIN + 200)
            delta_time2 = (current_time - paljenja[1]) // 60000000
            self.prikaziPoruku(f"Prije {delta_time2} min", tt14)
        
        if len(paljenja) >= 3:
            self.display.set_pos(self.LEFT_MARGIN, self.TOP_MARGIN + 240)
            delta_time3 = (current_time - paljenja[2]) // 60000000  
            self.prikaziPoruku(f"Prije {delta_time3} min", tt14)

        






