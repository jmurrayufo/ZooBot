#!/usr/bin/env python3

import pigpio

i2c = pigpio.pi()

print(i2c.i2c_read_device(0x49, 2))