
import pigpio
import signal

from ..CustomLogging import Log

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


    def __init__(self):
        pass


    def _bb(self, data):
        with DelayedKeyboardInterrupt():
            self.i2c.bb_i2c_open(2, 3, 100000)
            ret = self.i2c.bb_i2c_zip(2,data)
            self.i2c.bb_i2c_close(2)
        return ret


    def Si7021_humidity(self, address):
        self.address = address
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
        return self._bb(data)


    def Si7021_temperature(self, address):
        self.address = address
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
        return self._bb(data)


    def TMP102_temperature(self, address):
        self.address = address
        data = [
                self.ADDRESS,
                self.address,
                self.START,
                self.WRITE,
                1,
                0x0, # 0x00 Temperature Register (RO)
                self.START,
                self.READ,
                2,
                self.STOP,
                self.END]
        return self._bb(data)


    def dimmer_setting(self, address, channel, value):
        self.address = address
        data = [
                self.ADDRESS,
                self.address,
                self.START,
                self.WRITE,
                2,
                channel,
                value,
                self.STOP,
                self.END]
        return self._bb(data)


# def preexec_function():
#     # Ignore the SIGINT signal by setting the handler to the standard
#     # signal handler SIG_IGN.
#     signal.signal(signal.SIGINT, signal.SIG_IGN)


class DelayedKeyboardInterrupt(object):
    def __enter__(self):
        self.signal_received = False
        self.old_handler = signal.signal(signal.SIGINT, self.handler)
        self.log = Log()

    def handler(self, sig, frame):
        self.signal_received = (sig, frame)
        self.log.critical('SIGINT received. Delaying KeyboardInterrupt.')

    def __exit__(self, type, value, traceback):
        signal.signal(signal.SIGINT, self.old_handler)
        if self.signal_received:
            self.log.critical("Now handling SIGINT")
            self.old_handler(*self.signal_received)