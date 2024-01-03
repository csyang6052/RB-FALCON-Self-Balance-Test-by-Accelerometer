from machine import Pin, I2C, SPI
import usys
import machine
import time
from pyb import Timer
from micropython import const
import utime
import ustruct as struct
from bmp280 import BMP280
from lsm9ds1 import LSM9DS1

BMP280_CASE_INDOOR = const(5)

tim4 = Timer(4, freq=1000)
tim5 = Timer(5, freq=1000)

bus = I2C(2)
lsm = LSM9DS1(bus)

i2c = machine.I2C(scl=machine.Pin("P7"), sda=machine.Pin("P8"))
bmp = BMP280(i2c)
bmp.use_case(BMP280_CASE_INDOOR)


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
    pressure=p_mmHg/133.3224

    acc_z = int(1000*lsm.read_accel()[2])
    acc_y = int(1000*lsm.read_accel()[1])
    acc_x = int(1000*lsm.read_accel()[0])
    print(pressure, acc_z, acc_y, acc_x, UPP, PWM1, PWM2, PWM3, PWM4)

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

        if pressure < 760.6 or PWM1 > 45 or PWM2 > 45 or PWM3 > 45 or PWM4 > 45 : UPP = 0

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


    #ch1 = tim5.channel(3, Timer.PWM, pin=Pin("M1"), pulse_width_percent=PWM1)
    #ch2 = tim5.channel(4, Timer.PWM, pin=Pin("M2"), pulse_width_percent=PWM2)
    #ch3 = tim4.channel(3, Timer.PWM, pin=Pin("M3"), pulse_width_percent=PWM3)
    #ch4 = tim4.channel(4, Timer.PWM, pin=Pin("M4"), pulse_width_percent=PWM4)

    time.sleep_ms(500)
