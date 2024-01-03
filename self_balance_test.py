import machine
import time
from pyb import Timer
from micropython import const
import time

from bmp280 import BMP280
from lsm9ds1 import LSM9DS1

BMP280_CASE_INDOOR = const(5)
bus1 = machine.I2C(scl=machine.Pin("P7"), sda=machine.Pin("P8"))
bmp = BMP280(bus1)
bmp.use_case(BMP280_CASE_INDOOR)
bus2 = machine.I2C(scl=machine.Pin("P4"), sda=machine.Pin("P5"))
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


    print(UPP, pressure, acc_z, acc_y, acc_x, PWM1, PWM2, PWM3, PWM4)

    time.sleep_ms(200)
