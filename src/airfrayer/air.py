import RPi.GPIO as GPIO

class AirFrayer:
    def __init__(self):
        GPIO.setwarnings(False)
    
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(23, GPIO.OUT)
        GPIO.setup(24, GPIO.OUT)

        ## aquecedor
        self.aquecedor = GPIO.PWM(23, 100)
        self.aquecedor.start(0)

        ## ventoinha
        self.ventoinha = GPIO.PWM(24, 100)
        self.ventoinha.start(0)

    def aquecer_air(self, pid):
        self.aquecedor.ChangeDutyCycle(pid)

    def resfriar_air(self, pid):
        self.ventoinha.ChangeDutyCycle(pid)