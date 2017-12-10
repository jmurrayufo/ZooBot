import logging
import logstash
from . import VerboseLogstashFormatter


class Log:
    __shared_state = {}
    def __init__(self, _type=None):
        self.__dict__ = self.__shared_state
        if _type is None:
            return

        self._log = logging.getLogger(_type)
        self._log.setLevel(logging.DEBUG)

        sh = logstash.TCPLogstashHandler('192.168.1.2', 5003)
        sh.setFormatter(VerboseLogstashFormatter())
        self._log.addHandler(sh)

        formatter = logging.Formatter('{asctime} {levelname} {filename}:{lineno} {message}', style='{')
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        self._log.addHandler(ch)

    def __getattr__(self, name):
        return getattr(self._log, name)


