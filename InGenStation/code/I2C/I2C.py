
import pigpio

class I2C:

    i2c = pigpio.pi()

    def __init__(self, bus=1, address=0):
        self.bus = bus
        self.address = address


    def read_byte(self):
        return self.i2c.i2c_read_byte(self.handle)


    def read_register(self, reg):
        return self.i2c.i2c_read_byte(self.handle, reg)


    def read_bytes(self, count):
        """The returned value is a tuple of the number of bytes read and a 
        bytearray containing the bytes. If there was an error the number of 
        bytes read will be less than zero (and will contain the error code). 
        """
        return self.i2c.i2c_read_device(self.handle, count)


    def read_register_bytes(self, reg, count):
        return self.i2c.i2c_read_i2c_block_data(self.handle, reg, count)


    def write_byte(self, byte_val):
        self.i2c.i2c_write_byte(self.handle, byte_val)


    def write_bytes(self, data):
        self.i2c.i2c_write_device(self.handle, data)


    def __enter__(self):
        self.handle = self.i2c.i2c_open(self.bus, self.address)
        return self


    def __exit__(self, exception_type, exception_value, traceback):
        print(exception_type)
        print(exception_value)
        print(traceback)
        self.i2c.i2c_close(self.handle)
