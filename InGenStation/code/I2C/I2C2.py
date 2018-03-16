
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
    ADDRESS = 4 # P Set I2C address to P
    FALGS = 5
    READ = 6    # P Read P bytes of data
    WRITE = 7   # P ... Write P bytes of data


    def __init__(self, address=0):
        self.address = address


    def __enter__(self):
        try:
            self.handle = self.i2c.bb_i2c_open(2, 3, 100000)
        except pigpio.error:
            self.i2c.bb_i2c_close(2)
            self.handle = self.i2c.bb_i2c_open(2, 3, 100000)
            
        return self


    def __exit__(self, exception_type, exception_value, traceback):
        self.i2c.bb_i2c_close(2)


    def Si7021_humidity(self):
        data = [
                self.ADDRESS,
                self.address,
                self.START,
                self.WRITE,
                1,
                0xE5, # 0xE5: RH Hold Master, 0xF5: RH No Hold Master
                self.START,
                self.READ,
                3,
                self.STOP,
                self.END]
        return self.i2c.bb_i2c_zip(2,data)


    def Si7021_temperature(self):
        data = [
                self.ADDRESS,
                self.address,
                self.START,
                self.WRITE,
                1,
                0xE3, # 0xE3, Temp. Hold Master, 0xF3: Temp. No Hold Master
                self.START,
                self.READ,
                3,
                self.STOP,
                self.END]
        return self.i2c.bb_i2c_zip(2,data)


