#!/usr/bin/env python3

import pigpio

i2c = pigpio.pi()

tmp102 = i2c.i2c_open(1, 0x48)

print(i2c.i2c_write_byte(tmp102,0))

data = i2c.i2c_read_device(tmp102, 2)

print(data)
for i in data[1]:
    print(i)