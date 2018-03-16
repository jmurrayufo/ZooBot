#!/usr/bin/env python3

import pigpio
import time

from code.I2C import I2C2

ch = 0x81

while 1:
    for i in range(101):
        print(i)
        with I2C2(0x3F) as i2c:
            i2c.dimmer_setting(ch, i)
        time.sleep(0.01)
