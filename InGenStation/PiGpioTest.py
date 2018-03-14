#!/usr/bin/env python3

import pigpio
import time

i2c = pigpio.pi()

h = i2c.i2c_open(1, 0x40)



MEASURE_HUMIDITY_HOLD = 0xE5
MEASURE_HUMIDITY_NO_HOLD = 0xF5
MEASURE_TEMPERATURE_HOLD = 0xE3
MEASURE_TEMPERATURE_NO_HOLD = 0xF3
READ_TEMPERATURE_FROM_RH = 0xE0
RESET = 0xFE

print(i2c.i2c_write_byte(h,MEASURE_HUMIDITY_HOLD))

time.sleep(0.1)

count, data = i2c.i2c_read_device(h, 2)
print(count)
print(data)
for i in data:
    print(i)