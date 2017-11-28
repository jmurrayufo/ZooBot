

class LCD:
    """CFA533
    """
    def __init__(self, address=0x2A):
        self.address = address
        pass

    # Low Level Commands

    def _ping(self):
        cmd = CMD(0x00, [])
        print(f"Result Command: {cmd}")
        # Read back 4 bytes of data


    def _get_version(self):
        cmd = CMD(0x01, [])
        print(f"Result Command: {cmd}")
        # Read back 20 bytes


    def _write_flash(self, data):
        assert type(data) in [list,tuple]
        cmd = CMD(0x02, data)
        print(f"Result Command: {cmd}")
        # Read back 4 bytes


    def _read_flash(self):
        cmd = CMD(0x03, [])
        print(f"Result Command: {cmd}")
        # Read back 20 bytes


    def _store_to_boot(self):
        cmd = CMD(0x04, [])
        print(f"Result Command: {cmd}")
        # Read back 20 bytes


    def _clear_lcd(self):
        cmd = CMD(0x06, [])
        print(f"Result Command: {cmd}")
        # Read back 4 bytes


    def _set_lcd_line(self, data):
        raise NotImplemented("Don't use this command")
        cmd = CMD(0x07, data)
        print(f"Result Command: {cmd}")
        # Read back 4 bytes


    def _set_special_character(self, char, data):
        assert type(data) in [list,tuple]
        assert char in range(8),"Must be in range 0-7"
        cmd = CMD(0x09, [char,*data])
        print(f"Result Command: {cmd}")
        # Read back 4 bytes


    def _set_lcd_curosr_position(self, col, row):
        assert col in range(16),"Must be in range 0-15"
        assert row in range(2),"Must be in range 0-1"
        cmd = CMD(0x0B, [col,row])
        print(f"Result Command: {cmd}")
        # Read back 4 bytes


    def _set_lcd_curosr_style(self, style):
        assert style in range(4),"Must be in range 0-3"
        cmd = CMD(0x0C, [col,row])
        print(f"Result Command: {cmd}")
        # Read back 4 bytes


    def _set_lcd_contrast(self, level):
        """This command sets the contrast or vertical viewing angle of the display.
        level:
               0-99 = lighter
                100 = no correction
            101-200 = darker
        """
        assert level in range(201),"Must be in range 0-200"
        cmd = CMD(0x0D, [0,level])
        print(f"Result Command: {cmd}")
        # Read back 4 bytes


    def _set_lcd_backlight(self, level):
        """This command sets the brightness of the LCD and keypad backlights.
        level:
               0 = off
            1-99 = variable brightness
             100 = on
        """
        assert level in range(101),"Must be in range 0-100"
        cmd = CMD(0x0E, [level])
        print(f"Result Command: {cmd}")
        # Read back 4 bytes


    def _poll_keypad(self):
        """Poll the keypad.
        """
        cmd = CMD(0x18, [])
        print(f"Result Command: {cmd}")
        # Read back 7 bytes
        """
        Defines
            KP_UP = 0x01
            KP_ENTER = 0x02
            KP_CANCEL = 0x04
            KP_LEFT = 0x08
            KP_RIGHT = 0x10
            KP_DOWN = 0x20
        The return packet will be:
            type: 0x40 | 0x18 = 0x58 = 88 10
            data_length: 3
            data[0] = bitmask showing the keys currently pressed
            data[1] = bitmask showing the keys that have been pressed since the last poll
            data[2] = bitmask showing the keys that have been released since the last poll
        """


    def _write_lcd(self, col, row, data):
        """Write to the LCD.
        """
        assert col in range(16),"Must be in range 0-15"
        assert row in range(2),"Must be in range 0-1"
        assert len(data) in range(1,16),"Must be in range 1-16"
        cmd = CMD(0x1F, [col,row,*data])
        print(f"Result Command: {cmd}")
        # Read back 4 bytes



    """
    # 0 (0x00): Ping Command
    # 1 (0x01): Get Hardware & Firmware Version 
    # 2 (0x02): Write User Flash Area 
    # 3 (0x03): Read User Flash Area 
    # 4 (0x04): Store Current State as Boot State 
    5 (0x05): Reboot CFA533, Reset Host, or Power Off Hos
    # 6 (0x06): Clear LCD Screen 
    # 7 (0x07): Set LCD Contents, Line 1 (Deprecated) 
    9 (0x09): Set LCD Special Character Data 
    10 (0x0A): Read 8 Bytes of LCD Memory 
    # 11 (0x0B): Set LCD Cursor Position 
    # 12 (0x0C): Set LCD Cursor Style 
    # 13 (0x0D): Set LCD Contrast 
    # 14 (0x0E): Set LCD & Keypad Backlight 
    15 (0x0F): Read Temperature 
    18 (0x12): Read DOW Device Information 
    20 (0x14): Arbitrary DOW Transaction 
    21 (0x15): Set Up Live Temperature Display 
    22 (0x16): Send Command Directly to the LCD Controller 
    23 (0x17): Enable Key Ready Flag 
    # 24 (0x18): Read Keypad, Polled Mode 
    28 (0x1C): Set ATX Switch Functionality 
    29 (0x1D): Enable/Feed Host Watchdog Reset 
    30 (0x1E): Read Reporting/ATX/Watchdog (debug) 
    # 31 (0x1F): Send Data to LCD 
    33 (0x21): Set I2C Address 
    34 (0x22): Set/Configure GPIO 
    """

class CMD:
    def __init__(self, _type, data):
        assert type(data) in [list,tuple]

        self._type = _type & 0xFF
        self.length = len(data)
        self.data = [x & 0xFF for x in data]
        self.crc()


    def __repr__(self):
        ret_val = "CMD<"
        ret_val += f"0x{self._type:02x}"
        if len(self.data):
            ret_val += f" ,0x{len(self.data):02x}"
            for d in self.data:
                ret_val += f" ,0x{d:02x}"
        ret_val += f" ,0x{self.crc_lsb:02x}"
        ret_val += f" ,0x{self.crc_msb:02x}"
        ret_val += ">"
        return ret_val


    def bytes(self):
        data = [self._type,len(self.data),*self.data,self.crc_lsb,self.crc_msb]
        return data


    def crc(self): 
        lookup = (0x00000,0x01189,0x02312,0x0329B,0x04624,0x057AD,0x06536,0x074BF,
                  0x08C48,0x09DC1,0x0AF5A,0x0BED3,0x0CA6C,0x0DBE5,0x0E97E,0x0F8F7,
                  0x01081,0x00108,0x03393,0x0221A,0x056A5,0x0472C,0x075B7,0x0643E,
                  0x09CC9,0x08D40,0x0BFDB,0x0AE52,0x0DAED,0x0CB64,0x0F9FF,0x0E876,
                  0x02102,0x0308B,0x00210,0x01399,0x06726,0x076AF,0x04434,0x055BD,
                  0x0AD4A,0x0BCC3,0x08E58,0x09FD1,0x0EB6E,0x0FAE7,0x0C87C,0x0D9F5,
                  0x03183,0x0200A,0x01291,0x00318,0x077A7,0x0662E,0x054B5,0x0453C,
                  0x0BDCB,0x0AC42,0x09ED9,0x08F50,0x0FBEF,0x0EA66,0x0D8FD,0x0C974,
                  0x04204,0x0538D,0x06116,0x0709F,0x00420,0x015A9,0x02732,0x036BB,
                  0x0CE4C,0x0DFC5,0x0ED5E,0x0FCD7,0x08868,0x099E1,0x0AB7A,0x0BAF3,
                  0x05285,0x0430C,0x07197,0x0601E,0x014A1,0x00528,0x037B3,0x0263A,
                  0x0DECD,0x0CF44,0x0FDDF,0x0EC56,0x098E9,0x08960,0x0BBFB,0x0AA72,
                  0x06306,0x0728F,0x04014,0x0519D,0x02522,0x034AB,0x00630,0x017B9,
                  0x0EF4E,0x0FEC7,0x0CC5C,0x0DDD5,0x0A96A,0x0B8E3,0x08A78,0x09BF1,
                  0x07387,0x0620E,0x05095,0x0411C,0x035A3,0x0242A,0x016B1,0x00738,
                  0x0FFCF,0x0EE46,0x0DCDD,0x0CD54,0x0B9EB,0x0A862,0x09AF9,0x08B70,
                  0x08408,0x09581,0x0A71A,0x0B693,0x0C22C,0x0D3A5,0x0E13E,0x0F0B7,
                  0x00840,0x019C9,0x02B52,0x03ADB,0x04E64,0x05FED,0x06D76,0x07CFF,
                  0x09489,0x08500,0x0B79B,0x0A612,0x0D2AD,0x0C324,0x0F1BF,0x0E036,
                  0x018C1,0x00948,0x03BD3,0x02A5A,0x05EE5,0x04F6C,0x07DF7,0x06C7E,
                  0x0A50A,0x0B483,0x08618,0x09791,0x0E32E,0x0F2A7,0x0C03C,0x0D1B5,
                  0x02942,0x038CB,0x00A50,0x01BD9,0x06F66,0x07EEF,0x04C74,0x05DFD,
                  0x0B58B,0x0A402,0x09699,0x08710,0x0F3AF,0x0E226,0x0D0BD,0x0C134,
                  0x039C3,0x0284A,0x01AD1,0x00B58,0x07FE7,0x06E6E,0x05CF5,0x04D7C,
                  0x0C60C,0x0D785,0x0E51E,0x0F497,0x08028,0x091A1,0x0A33A,0x0B2B3,
                  0x04A44,0x05BCD,0x06956,0x078DF,0x00C60,0x01DE9,0x02F72,0x03EFB,
                  0x0D68D,0x0C704,0x0F59F,0x0E416,0x090A9,0x08120,0x0B3BB,0x0A232,
                  0x05AC5,0x04B4C,0x079D7,0x0685E,0x01CE1,0x00D68,0x03FF3,0x02E7A,
                  0x0E70E,0x0F687,0x0C41C,0x0D595,0x0A12A,0x0B0A3,0x08238,0x093B1,
                  0x06B46,0x07ACF,0x04854,0x059DD,0x02D62,0x03CEB,0x00E70,0x01FF9,
                  0x0F78F,0x0E606,0x0D49D,0x0C514,0x0B1AB,0x0A022,0x092B9,0x08330,
                  0x07BC7,0x06A4E,0x058D5,0x0495C,0x03DE3,0x02C6A,0x01EF1,0x00F78)
        new_crc = 0xFFFF
        data = [self._type,len(self.data),*self.data]
        # $crc = ($crc >> 8) ^ $CRC_LOOKUP[($crc ^ ord($char) ) & 0xFF] ;o
        for i in data:
            new_crc = (new_crc >> 8) ^ lookup[ (new_crc ^ i ) & 0xFF ]
        new_crc = (~new_crc) & 0xFFFF
        data = list(new_crc.to_bytes(2,byteorder='little'))
        self.crc_msb = data[1]
        self.crc_lsb = data[0]




