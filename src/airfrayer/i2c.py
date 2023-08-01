import smbus2
import bmp280

def get_temp_ambiente():
    port = 1
    address = 0x76
    bus = smbus2.SMBus(port)
    # Inicializar o sensor BMP280
    sensor = bmp280.BMP280(i2c_dev=bus, i2c_addr=address)

    # Realizar a leitura da temperatura
    temperatura = sensor.get_temperature()

    return temperatura