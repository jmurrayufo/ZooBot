#!/usr/bin/env python3

import time


for vObj in [0x7fff, 0x0001, 0, 0xffff, 0x8000]:
    print()
    print(hex(vObj))
    if vObj & 0x8000:
        vObj = (vObj - (1 << 16))
    vObj = vObj/2**15 * 5.12e-3 
    print(vObj)