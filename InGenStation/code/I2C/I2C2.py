
import pigpio

class I2C2:

    i2c = pigpio.pi()

    """
    Name    Cmd & Data  Meaning
    End 0   No more commands
    Escape  1   Next P is two bytes
    Start   2   Start condition
    Stop    3   Stop condition
    Address 4 P Set I2C address to P
    Flags   5 lsb msb   Set I2C flags to lsb + (msb << 8)
    Read    6 P Read P bytes of data
    Write   7 P ... Write P bytes of data
    """
    END = 0
    ESCAPE = 1
    START = 2
    STOP = 3
    ADDRESS = 4
    FALGS = 5
    READ = 6
    WRITE = 7

    def __init__(self, address=0):
        self.address = address


    def __enter__(self):
        self.handle = self.i2c.bb_i2c_open(3, 5, 10000)
        return self


    def __exit__(self, exception_type, exception_value, traceback):
        self.i2c.bb_i2c_close(3)


    def Si7021_humidity(self):
        data = [
                self.ADDRESS,
                self.address,
                self.START,
                self.WRITE,
                1,
                0xE5, # 0xE5: RH Hold Master, 0xF5: RH No Hold Master
                self.ADDRESS,
                self.address,
                self.START,
                self.READ,
                3,
                self.STOP]
        return self.i2c.bb_i2c_zip(3,data)

