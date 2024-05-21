import time
import RPi.GPIO as GPIO

PIN_SELENOID = 21 #Variable al cual conectamos la señal del Solenoide

def _setup():
    GPIO.setmode(GPIO.BCM)   #Establecemos el modo según el cual nos refiriremos a los GPIO de nuestra RPi            
    GPIO.setup(PIN_SELENOID, GPIO.OUT) #Configuramos el GPIO18 como salida

def unlockSelenoid():
    """
        Función para activar el seguro selenoide por 2.5 segundos y poder abrir la caja
    """
    try:
        _setup()
        print("Abriendo caja...")
        GPIO.output( PIN_SELENOID , GPIO.LOW )
        time.sleep(3)
        print("Cerrando caja...")
        GPIO.cleanup(PIN_SELENOID)
    except:
        print("Error al activar selenoide")
        time.sleep(2.5)

if __name__ == '__main__':
    try:
        print("Testing selenoid")
        unlockSelenoid()
    finally:
        GPIO.cleanup()