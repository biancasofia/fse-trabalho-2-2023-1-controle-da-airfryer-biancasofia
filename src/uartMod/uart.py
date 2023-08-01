import serial
import time
from controle.crc16 import calcula_CRC

class Uart:
    conectado = False
    def __init__(self, port, baudrate, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.conecta()

    def conecta(self):
        self.serial = serial.Serial(self.port, self.baudrate, timeout=self.timeout)

        if (self.serial.isOpen()):
            self.conectado = True
            print('Porta aberta, conexao realizada')
        else:
            self.conectado = False
            print('Porta fechada, conexao nao realizada')
    
    def desconecta(self):
        self.serial.close()
        self.conectado = False
        print('Porta desconectada')

    def envia(self, comando, matricula, valor, tamanho):
        if (self.conectado):
            msg_part1 = comando + bytes(matricula) + valor
            msg_part2 = calcula_CRC(msg_part1, tamanho).to_bytes(2, 'little')
            msg = msg_part1 + msg_part2
            self.serial.write(msg)
            # print('Mensagem enviada: {}'.format(msg))
        else:
            self.conecta()

    def recebe(self):
        if (self.conectado):
            time.sleep(0.2)
            buffer = self.serial.read(9)
            buffer_tam = len(buffer)
            if buffer_tam == 9:
                data = buffer[3:7]
                crc_lido = buffer[7:9]
                crc_gerado = calcula_CRC(buffer[0:7], 7).to_bytes(2, 'little')
                if crc_lido == crc_gerado:
                    return data
                else:
                    print('CRC16 não válido')
                    return None
            else:
                return None
        else:
            self.conecta()
            return None