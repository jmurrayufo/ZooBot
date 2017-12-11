import logging
import logstash
import platform
import json
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

        self._metric_log = logging.getLogger(_type)
        ch2 = logging.StreamHandler(stream=None)
        self._metric_log.addHandler(ch2)
        self._metric_log.addHandler(logstash.LogstashHandler('192.168.1.2', 5002, version=1))
        self._metric_log.setLevel(logging.DEBUG)
        # self._metric_log.propagate = False


    def __getattr__(self, name):
        return getattr(self._log, name)


    def metric(self, name, **kwargs):
        report_dict = dict({
           "metric": True,
           "app.name":"DevHab",
           "app.version":"0.1.0",
           "env.domain":"dragon",
           "env.infrastructure":"dev",
           "env.name":"isbe",
           "env.platform":platform.platform(),
           "name":name
        })
        for key in kwargs:
            report_dict[key] = kwargs[key]
        self._metric_log.info(json.dumps(report_dict))


    @property
    def report_dict(self):
        return None

