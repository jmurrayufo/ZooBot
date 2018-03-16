#!/usr/bin/env python3

import pigpio
import time

from code.I2C import I2C2

with I2C2(0x40) as i2c:
    count, data = i2c.Si7021_humidity()
    print(count)
    print(data)
    if count<0:
        print(pigpio.error_text(count))