########### encoder feito em laboratório por Bianca Sofia e Daniel ######################
# Não integrado com o código

import RPi.GPIO as GPIO
import sys
import time
from datetime import datetime

CLK_PIN = 25
DT_PIN = 24
SW_PIN = 23


GPIO.setmode(GPIO.BCM)
GPIO.setup(CLK_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(DT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(SW_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

estado_anterior_CLK = GPIO.input(CLK_PIN)


def ler_encoder(channel):
    global estado_anterior_CLK

    estado_CLK = GPIO.input(CLK_PIN)
    estado_DT = GPIO.input(DT_PIN)

    if estado_CLK != estado_anterior_CLK:
        if estado_DT != estado_CLK:
            print("girou pra horario\a")
            sys.stdout.write('\a')
        else:
            print("girou pra anti-horario\a")
            sys.stdout.write('\a')

    estado_anterior_CLK = estado_CLK
contador = 0

def lidar_com_botao(channel):
    global contador
    print("Botão pressionado!\a")
    if contador == 0:
        contador = datetime.now()
    else:
        print(datetime.now() - contador)
        contador = 0


GPIO.add_event_detect(CLK_PIN, GPIO.BOTH, callback=ler_encoder)
GPIO.add_event_detect(SW_PIN, GPIO.BOTH, callback=lidar_com_botao, bouncetime=200)

# Loop principal do programa
try:
    while True:
  

        time.sleep(0.1)  

except KeyboardInterrupt:
    pass


GPIO.cleanup()
