#!/usr/bin/env python3

import pigpio
import time

from code.I2C import I2C2

loop = 0
while 1:
    i2c = I2C2()
    loop += 1
    print(f"\nLoop: {loop}")
    count, data = i2c.Si7021_humidity(0x40)
    print(list(data))
    count, data = i2c.Si7021_temperature(0x40)
    print(list(data))
    count, data = i2c.TMP102_temperature(0x48)
    print(list(data))
    count, data = i2c.dimmer_setting(0x3f, 0x81, 100%loop)
    print(list(data))
    time.sleep(0.1)