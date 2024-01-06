import machine
from machine import Pin, SPI, SoftI2C
import time
from pyb import Timer
from micropython import const
import time
import utime
import usys
import ustruct as struct

from bmp280 import BMP280
from lsm9ds1 import LSM9DS1
from nrf24l01 import NRF24L01


_RX_POLL_DELAY = const(15)
_RESPONDER_SEND_DELAY = const(10)

if usys.platform == "OpenMV3-M7":
    spi = SPI(2)  # miso : P1, mosi : P0, sck : P2
    cfg = {"spi": spi, "csn": "P3", "ce": "P6"}

else:
    raise ValueError("Unsupported platform {}".format(usys.platform))

pipes = (b"\xe1\xf0\xf0\xf0\xf0", b"\xd2\xf0\xf0\xf0\xf0")

csn = Pin(cfg["csn"], mode=Pin.OUT, value=1)
ce = Pin(cfg["ce"], mode=Pin.OUT, value=0)
spi = cfg["spi"]
nrf = NRF24L01(spi, csn, ce, payload_size=16)
nrf.open_tx_pipe(pipes[1])
nrf.open_rx_pipe(1, pipes[0])
nrf.start_listening()
print("NRF24L01 responder mode, waiting for packets... (ctrl-C to stop)")


BMP280_CASE_INDOOR = const(5)
#bus1 = machine.I2C(scl=machine.Pin("P7"), sda=machine.Pin("P8"))
bus1 = SoftI2C(scl=Pin("P7"), sda=Pin("P8"))
bmp = BMP280(bus1)
bmp.use_case(BMP280_CASE_INDOOR)
#bus2 = machine.I2C(scl=machine.Pin("P4"), sda=machine.Pin("P5"))
bus2 = SoftI2C(scl=Pin("P4"), sda=Pin("P5"))
lsm = LSM9DS1(bus2)

PWM1 = 0
PWM2 = 0
PWM3 = 0
PWM4 = 0
UPP = 1
STEP = 0.5

def rr(s):
    global PWM1, PWM2
    PWM1 = round(PWM1, 2) + s
    PWM2 = round(PWM2, 2) + s
    return PWM1, PWM2

def rl(s):
    global PWM3, PWM4
    PWM3 = round(PWM3, 2) + s
    PWM4 = round(PWM4, 2) + s
    return PWM3, PWM4

def pu(s):
    global PWM1, PWM4
    PWM1 = round(PWM1, 2) + s
    PWM4 = round(PWM4, 2) + s
    return PWM1, PWM4

def pd(s):
    global PWM2, PWM3
    PWM2 = round(PWM2, 2) + s
    PWM3 = round(PWM3, 2) + s
    return PWM2, PWM3


while True:

    p_mmHg=bmp.pressure
    pressure=round(p_mmHg/133.32, 1)

    acc_z = int(1000*lsm.read_accel()[2])
    acc_y = int(1000*lsm.read_accel()[1])
    acc_x = int(1000*lsm.read_accel()[0])


    if nrf.any():
        while nrf.any():
            buf = nrf.recv()
            xValue, yValue, xValue_, yValue_ = struct.unpack("iiii", buf)
            print("Joy Stick RF Received Signal:", xValue, yValue, xValue_, yValue_)
            utime.sleep_ms(_RX_POLL_DELAY)

        utime.sleep_ms(_RESPONDER_SEND_DELAY)
        nrf.stop_listening()
        millis = utime.ticks_ms()
        try:
            nrf.send(struct.pack("iii", acc_z, acc_y, acc_x))
            nrf.send(struct.pack("iiii", int(100*PWM1), int(100*PWM2), int(100*PWM3), int(100*PWM4)))
        except OSError:
            pass
        nrf.start_listening()


    if UPP == 1 :
        if acc_z > 970:
            PWM1 = round(PWM1, 2) + STEP
            PWM2 = round(PWM2, 2) + STEP
            PWM3 = round(PWM3, 2) + STEP
            PWM4 = round(PWM4, 2) + STEP
        else :
            if acc_y < 100 and acc_y > -100 :
                if acc_x > 100 :
                    pu(STEP)
                elif acc_x < -100 :
                    pd(STEP)
            elif acc_x < 100 and acc_x > -100 :
                if acc_y > 100 :
                    rl(STEP)
                elif acc_y < -100 :
                    rr(STEP)
            elif acc_x > 100 and acc_y > 100 :
                PWM4 = round(PWM4, 2) + STEP
            elif acc_x > 100 and acc_y < -100 :
                PWM1 = round(PWM1, 2) + STEP
            elif acc_x < -100 and acc_y > 100 :
                PWM3 = round(PWM3, 2) + STEP
            elif acc_x < -100 and acc_y < -100 :
                PWM2 = round(PWM2, 2) + STEP

        if pressure < 758 or PWM1 > 45 or PWM2 > 45 or PWM3 > 45 or PWM4 > 45 : UPP = 0

    elif UPP == 0 :
        if acc_z > 970:
            PWM1 = round(PWM1, 2) - STEP
            PWM2 = round(PWM2, 2) - STEP
            PWM3 = round(PWM3, 2) - STEP
            PWM4 = round(PWM4, 2) - STEP
        else :
            if acc_y < 100 and acc_y > -100 :
                if acc_x > 100 :
                    pu(-STEP)
                elif acc_x < -100 :
                    pd(-STEP)
            elif acc_x < 100 and acc_x > -100 :
                if acc_y > 100 :
                    rl(-STEP)
                elif acc_y < -100 :
                    rr(-STEP)
            elif acc_x > 100 and acc_y > 100 :
                PWM4 = round(PWM4, 2) - STEP
            elif acc_x > 100 and acc_y < -100 :
                PWM1 = round(PWM1, 2) - STEP
            elif acc_x < -100 and acc_y > 100 :
                PWM3 = round(PWM3, 2) - STEP
            elif acc_x < -100 and acc_y < -100 :
                PWM2 = round(PWM2, 2) - STEP

        if PWM1 < 5 or PWM2 < 5 or PWM3 < 5 or PWM4 < 5 : break

    print("         ")
    print("Take-Off (1) or Landing (0)  : ", UPP)
    print("Pressure (mmHg) ", pressure)
    print("Accelerometer Reading :", "Z-Axis - ", acc_z, "     Y-Axis - ", acc_y, "     X-Axis - ", acc_x)
    print("PWM1 : ", PWM1, "    PWM2 : ", PWM2, "     PWM3 : ", PWM3, "     PWM4 : ", PWM4)




    time.sleep_ms(2000)
