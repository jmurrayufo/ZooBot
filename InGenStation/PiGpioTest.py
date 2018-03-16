#!/usr/bin/env python3

import pigpio
import time

from code.I2C import I2C2

while 1:
    time.sleep(0)
    print()
    with I2C2(0x40) as i2c:
        count, data = i2c.Si7021_humidity()
        if count<0:
            print(pigpio.error_text(count))
        else:
            for i in data:
                print(i)