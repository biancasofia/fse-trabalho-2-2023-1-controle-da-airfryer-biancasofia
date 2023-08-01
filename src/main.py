from controle.pid import PID
from airfrayer.air import AirFrayer
import time
import datetime
from random import randint
from threading import Event, Thread 
from rpi_lcd import LCD
from uartMod.uart import Uart
import struct
import math
from airfrayer.i2c import get_temp_ambiente
from csvGerador.csv_arq import CSV
from airfrayer.manipuladorTemperatura import trata_temp_int, trata_tempe_referencia_air
from airfrayer.controladorLcd import seta_lcd_automatico, seta_lcd_manual

class AirFryer:

    matricula = [5, 2, 9, 8]
    porta = '/dev/serial0'
    baudrate = 9600
    timeout = 0.5
    
    ### variáveis de tempo
    temp_segundos = 0
    temp_referencia = 0

    ## controla outros eventos
    se_acabou=0
    modo_uso = "M"
    se_acabou_automatico=0
    ainda_nao_chamou = 1


    alimento=''
    
    tempe_referencia_air_auto=0
    ## eventos
    ligado = Event()
    cronometro = Event()
    enviando = Event()
    executando = Event()
    esquentando = Event()
    resfriando = Event()
    sorteou_alimento = Event()
    ## lcd
    lcd = LCD()

    ### variáveis de temperatura
    tempe_referencia_air = 0
    tempe_interna_air = 0
    

    def __init__(self):
        self.uart = Uart(self.porta, self.baudrate, self.timeout)
        self.pid = PID()
        self.airFrayer = AirFrayer()
        self.csv = CSV()
        self.liga_rotinas()

    def manda_temperatura_ambiente(self):
        self.enviando.set()
        #### pega a temp do sensor
        self.temp_ambiente = get_temp_ambiente()
        comando = b'\x01\x16\xd6'
        elem = struct.pack('!f', self.temp_ambiente)
        elem = elem[::-1]
        self.uart.envia(comando, self.matricula, elem, 11)
        self.uart.recebe()
        print(f'Temp ambiente {self.temp_ambiente}' )
        self.enviando.clear()

    def cronometra_tempo(self):
        contador=0
        while self.temp_segundos > 0:
            contador+=1
            if contador==60:
                self.manda_tempo(self.temp_referencia-1)
                contador=0
            time.sleep(1)
            
            self.temp_segundos -= 1
            
        ## para zerar
        self.temp_segundos =0
        if self.temp_segundos == 0:
            #print('acabou o tempo')
            self.se_acabou=1
            self.ainda_nao_chamou=1
    
    def manda_tempo(self, tempo):
        self.enviando.set()
        comando = b'\x01\x16\xd7'
        elem = tempo.to_bytes(4, 'little')
        self.uart.envia(comando, self.matricula, elem, 11)
        msg = self.uart.recebe()
        #print('envei tempo')
        self.temp_referencia = tempo
        self.temp_segundos = tempo * 60

        self.enviando.clear()

    def liga(self):
        self.enviando.set()
        comando = b'\x01\x16\xd3'
        self.uart.envia(comando, self.matricula, b'\x01', 8)
        msg = self.uart.recebe()
        if msg is not None:
            self.interrompe()
            self.manda_tempo(0)
            self.ligado.set()
        self.enviando.clear()

    def inicia(self):
        self.enviando.set()
        comando = b'\x01\x16\xd5'
        self.uart.envia(comando, self.matricula, b'\x01', 8)
        msg = self.uart.recebe()
        if msg is not None:
            self.executando.set()

        self.enviando.clear()



    def finaliza(self):
        self.enviando.set()
        comando = b'\x01\x16\xd3'
        self.uart.envia(comando, self.matricula, b'\x00', 8)
        msg = self.uart.recebe()
        if msg is not None:
            self.interrompe()
            self.ligado.clear()
        self.enviando.clear()

    
    def interrompe(self):
        self.enviando.set()
        comando = b'\x01\x16\xd5'
        self.uart.envia(comando, self.matricula, b'\x00', 8)
        msg = self.uart.recebe()
        if msg is not None:
            self.executando.clear()
        self.enviando.clear()
        # automatico
        self.para_automatico()

######## Automatico ############
    def para_automatico(self):
        self.enviando.set()
        comando = b'\x01\x16\xd4'
        self.uart.envia(comando, self.matricula, b'\x00', 8)
        msg = self.uart.recebe()
        if msg is not None:
            self.executando.clear()
        self.modo_uso = "M"

        self.enviando.clear()

    def envia_modo_automatico(self):
        self.enviando.set()
        comando = b'\x01\x16\xd4'
        #print('aquii')
        self.uart.envia(comando, self.matricula, b'\x01', 8)
        msg = self.uart.recebe()
        self.modo_uso= 'A'
        self.automatico()
        
        if msg is not None:
            pass

        self.enviando.clear()

    def envia_sinal_controle(self, pid):
        self.enviando.set()
        comando = b'\x01\x16\xd1'
        elem = (round(pid)).to_bytes(4, 'little', signed=True)

        self.uart.envia(comando, self.matricula, elem, 11)
        msg = self.uart.recebe()

        self.enviando.clear()

    def envia_temp_automatica_dash(self):
        self.enviando.set()
        comando = b'\x01\x16\xd2'
        elem = struct.pack('!f', self.tempe_referencia_air_auto)
        elem = elem[::-1]
        self.uart.envia(comando, self.matricula, elem, 11)

        self.enviando.clear()

    def automatico(self):
        tempo=0
        if self.modo_uso == "A":
            p = randint(1,4)
        
            if p==1:
                self.tempe_referencia_air_auto= 55
                tempo=1
                self.alimento= 'Frango'
                self.sorteou_alimento.set()
            if p==2:
                self.tempe_referencia_air_auto= 50
                self.alimento= 'Pao'
                tempo=1
                self.sorteou_alimento.set()
            if p==3:
                self.tempe_referencia_air_auto= 40
                self.alimento= 'Batata'
                tempo=1
                self.sorteou_alimento.set()
            if p==4:
                self.tempe_referencia_air_auto= 45
                self.alimento= 'Mandioca'
                tempo=1
                self.sorteou_alimento.set()
            else:
                pass
            self.envia_temp_automatica_dash()
            self.manda_tempo(tempo)
#########################

    def controla_airFrayer_executando(self):
        if self.temp_segundos > 0 and self.executando.is_set():
          
            pid = self.pid.pid_controle(self.tempe_referencia_air, self.tempe_interna_air)
            print('pid f', pid)
            self.envia_sinal_controle(pid)
        
            if math.isclose(self.tempe_interna_air, self.tempe_referencia_air, rel_tol=1e-2):
                self.esquentando.clear()
                self.resfriando.clear()
                self.cronometro.set()  

            elif self.tempe_interna_air < self.tempe_referencia_air and not self.cronometro.is_set():
                self.esquentando.set()
                self.resfriando.clear()
            elif self.tempe_interna_air > self.tempe_referencia_air and not self.cronometro.is_set():
                self.esquentando.clear()
                self.resfriando.set()
            if pid > 0:
                self.airFrayer.aquecer_air(pid)
                self.airFrayer.resfriar_air(0)
            else:
                pid *= -1
                self.airFrayer.aquecer_air(0)
                if pid < 40.0:
                    self.airFrayer.resfriar_air(40.0)
                else:
                    self.airFrayer.resfriar_air(pid)
        else:
            if self.se_acabou == 1:
                self.interrompe()
                self.se_acabou = 0
                self.manda_tempo(0)
            pid = self.pid.pid_controle(27.0, self.tempe_interna_air)
            print('pid ', pid)

            if pid < 0:
                self.envia_sinal_controle(pid)
                pid *= -1
                self.airFrayer.resfriar_air(pid)
                self.resfriando.set()
            else:
                self.resfriando.clear()
            self.airFrayer.aquecer_air(0)
            self.esquentando.clear()
            self.cronometro.clear()



    def seta_airFrayer(self):
        if self.ligado.is_set():
            self.controla_airFrayer_executando()
        else:
            self.airFrayer.aquecer_air(0)
            self.airFrayer.resfriar_air(0.0)
            self.executando.clear()
            self.esquentando.clear()
            self.resfriando.clear()

    
    
    def volta_manual(self):
        self.enviando.set()
        comando = b'\x01\x16\xd4'
        self.uart.envia(comando, self.matricula, b'\x00', 8)
        msg = self.uart.recebe()
        if msg is not None:
            self.executando.clear()
        self.modo_uso="M"
        self.enviando.clear()
        self.se_acabou_automatico=0

    def manipula_modo_automatico(self):
        self.se_acabou_automatico+=1
        if self.se_acabou_automatico == 2:
            self.volta_manual()        
        else:
            self.envia_modo_automatico()
            
    def pede_temperatura_referencia(self):
        comando = b'\x01\x23\xc2'
        self.uart.envia(comando, self.matricula, b'', 7)
        msg = self.uart.recebe()
        if msg is not None:
            trata_tempe_referencia_air(self, msg)

    def pede_temperatura_interna(self):
        comando = b'\x01\x23\xc1'
        self.uart.envia(comando, self.matricula, b'', 7)
        msg = self.uart.recebe()
        if msg is not None:
            trata_temp_int(self, msg)

    def trata_opcao(self, bytes):
        opcao = int.from_bytes(bytes, 'little')
        #botão de ligar
        if opcao == 1:
            self.liga()
        # botão de desligar
        if opcao == 2:
           self.finaliza()
        # botão de iniciar
        if opcao == 3:
            self.inicia()
        # botão de interromper
        if opcao == 4:
            self.interrompe()
        # botão de mandar tempo
        if opcao == 5:
            tempo = self.temp_referencia + 1
            self.manda_tempo(tempo)
        # botão de mandar tempo
        if opcao == 6:
            tempo = self.temp_referencia - 1
            if tempo < 0:
                tempo = 0
            self.manda_tempo(tempo)
        # ativa automatico
        if opcao == 7:
            self.manipula_modo_automatico()

    
    def le_comandos_usuario(self):
        comando = b'\x01\x23\xc3'
        self.uart.envia(comando, self.matricula, b'', 7)
        msg = self.uart.recebe()
        if msg is not None:
            self.trata_opcao(msg)


    def envia_lcd(self):
        while True:

            if self.ligado.is_set() and self.modo_uso == "M":
                seta_lcd_manual(self)
            elif self.ligado.is_set() and self.modo_uso == 'A':
                seta_lcd_automatico(self)
            else:
                self.lcd.clear()
            time.sleep(1)
    

    def salva_csv(self):
        header = ['data', 'Temp_I', 'Temp_R', 'resistor_ventoinha']
        self.csv.write(header)
        
        while True:
            data = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            linha = [data, self.tempe_interna_air, self.tempe_referencia_air, self.pid.sinal_de_controle]
            self.csv.write(linha)
            print("Guardando log em csv\n")
            time.sleep(1)

        
    def procedimento(self):
        while True:

            self.le_comandos_usuario()
            ##### dorme 0,5
            time.sleep(0.5)
            self.le_comandos_usuario()
            #### dorme 0,5
            time.sleep(0.5)
            #### solicitação das temps
            self.pede_temperatura_interna()
            self.pede_temperatura_referencia()
            self.manda_temperatura_ambiente()  # enviar a temp ambiente
            
    
    def liga_rotinas(self):
        self.liga()

        ### para rotina
        thd_rotina = Thread(target=self.procedimento, args=())
        thd_rotina.start()

        ### para o lcd
        thd_lcd = Thread(target=self.envia_lcd, args=())
        thd_lcd.start()

        ## para o CSV
        thd_csv = Thread(target=self.salva_csv, args=())
        thd_csv.start()

        print('AirFryer iniciada')

AirFryer()


#biancaoliveira
#190025298