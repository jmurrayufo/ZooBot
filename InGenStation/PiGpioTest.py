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
delay = 0.06

while 1:
    print(f"\nDelay: {delay}")

    print(i2c.i2c_write_byte(h,MEASURE_TEMPERATURE_NO_HOLD))

    time.sleep(delay)

    count, data = i2c.i2c_read_device(h, 3)
    print(count)
    print(data)

    for i in data:
        print(i)

    delay *= .95