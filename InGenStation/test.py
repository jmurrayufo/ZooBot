#!/usr/bin/env python3

import smbus2

MEASURE_HUMIDITY_HOLD = 0xE5
MEASURE_HUMIDITY_NO_HOLD = 0xF5
MEASURE_TEMPERATURE_HOLD = 0xE3
MEASURE_TEMPERATURE_NO_HOLD = 0xF3
READ_TEMPERATURE_FROM_RH = 0xE0
RESET = 0xFE

WRITE_HEATER_CONTROL_REGISTER = 0x51
READ_HEATER_CONTROL_REGISTER = 0x51
HEATER_MASK = 0x0F # 0x00 for minimal heat, 0x0F for max. Must set heater 
# to on before use!

WRITE_USER_REGISTER = 0xE6
READ_USER_REGISTER = 0xE7
RES_1 = 0x01
RES_2 = 0x10
RES_3 = 0x11
RES_4 = 0x00
CHIP_HEATER_ENABLE = 0x04
VDDS = 0x40

address = 0x40

with smbus2.SMBusWrapper(1) as bus:
    bus.write_byte(address, 0, MEASURE_HUMIDITY_NO_HOLD)
    humidity = bus.read_i2c_block_data(address, 0, 2)
    bus.write_byte(address, 0, READ_TEMPERATURE_FROM_RH)
    temperature = bus.read_i2c_block_data(address, 0, 2)

print(f"{humidity} {humidity:X}")
print(f"{temperature} {temperature:X}")
