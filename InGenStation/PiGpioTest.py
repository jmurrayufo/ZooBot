#!/usr/bin/env python3

import pigpio
import time

from code.I2C import I2C2
t1 = time.time()
loops = 0
try:
    while 1:
        loops += 1
        with I2C2(0x40) as i2c:
            count, data = i2c.Si7021_humidity()
            if count<0:
                raise IOError
finally:
    t2 = time.time()
    print(t2-t1)
    print(loops)
    print(loops/(t2-t1))