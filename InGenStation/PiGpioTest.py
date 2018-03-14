#!/usr/bin/env python3

import pigpio

i2c = pigpio.pi()

print(i2c.write_byte(0x48,0))

print(i2c.i2c_read_device(0x48, 2))