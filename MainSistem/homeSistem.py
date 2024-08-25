class homeSistem:
    def __init__(self):
        self.pocetniEkran = False   # boolovi za stanje
        self.alarmAktivan = False
        self.sifraAdminSistem = "1234"
        self.sifraOtkljucavanjeAlarm = "0000"
        self.unos = False   # bool za stanje mijenjanja sifre
        self.periodPaljenja = 63000
        self.mijenjajPeriod = False     # bool za stanje mijenjanja perioda
        
    def isAlarmAktivan(self) -> bool:
        return self.alarmAktivan
    
    def isPocetniEkran(self) -> bool:
        return self.pocetniEkran

    def deaktivirajAlarm(self, sifra: str) -> bool:
        if self.sifraOtkljucavanjeAlarm == sifra:
            self.alarmAktivan = False
            self.pocetniEkran = True
            return True  
        return False
    
    def adminAktivirajAlarm(self):
        self.alarmAktivan = True
        self.pocetniEkran = False
        
    def adminDeaktivirajAlarm(self):
        self.alarmAktivan = False
        self.pocetniEkran = True

    def aktivirajAlarm(self, sifra: str) -> bool:
        if self.sifraOtkljucavanjeAlarm == sifra:
            self.alarmAktivan = True
            return True
        return False

    def idiNaPocetniEkran(self):
        self.pocetniEkran = True
        self.alarmAktivan = False
        
    def isValidnaAdminSifra(self, sifra: str):
        if self.sifraAdminSistem == sifra:
            return True
        return False
        
    def promjeniSifruAlarm(self, novaSifra: str):
        self.sifraOtkljucavanjeAlarm = novaSifra
        
    def dajSifru(self):
        return self.sifraAdminSistem

    def setPocetniEkran(self, upaljen):
        self.pocetniEkran = upaljen

    def isUnos(self):
        return self.unos
    
    def setUnos(self, upaljen):
        self.unos = upaljen
        
    def setPeriodPaljenja(self, period):
        self.periodPaljenja = period
        
    def getPeriodPaljenja(self):
        return self.periodPaljenja
    
    def setMijenjajPeriod(self, mijenjaj):
        self.mijenjajPeriod = mijenjaj
        
    def getMijenjajPeriod(self):
        return mijenjajPeriod
        


