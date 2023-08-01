
from threading import  Thread 
import struct


def trata_temp_int(self, bytes):
        temp = struct.unpack('f', bytes)[0]
        print('temperatura int:', self.tempe_interna_air)

        if temp > 0 and temp < 100:
            self.tempe_interna_air = temp
        
        self.seta_airFrayer()
        if self.cronometro.is_set():
            if self.ainda_nao_chamou==1:
                self.ainda_nao_chamou=0
                threadTimer = Thread(target=self.cronometra_tempo)
                #print('testando entrando dnv')
                threadTimer.start()
            

def trata_tempe_referencia_air(self, bytes):
    temp = struct.unpack('f', bytes)[0]

    if self.modo_uso == 'A':
        self.tempe_referencia_air = self.tempe_referencia_air_auto
    elif temp > 0 and temp < 100:
        self.tempe_referencia_air = temp
    print('temperatura ref:', self.tempe_referencia_air)