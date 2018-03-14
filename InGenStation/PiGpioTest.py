#!/usr/bin/env python3

import pigpio

i2c = pigpio.pi()

tmp102 = i2c.i2c_open(0, 0x48)

print(i2c.i2c_write_byte(tmp102,0))

print(i2c.i2c_read_device(tmp102, 2))