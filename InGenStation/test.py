#!/usr/bin/env python3


import json
import logging
import logstash
from logstash_formatter import LogstashFormatterV1


class MyLogstashFormatter(logstash.formatter.LogstashFormatterBase):

    def format(self, record):
        # Create message dict
        message = {
            '@timestamp': self.format_timestamp(record.created),
            '@version': '1',
            'message': record.getMessage(),
            'host': self.host,
            'path': record.pathname,
            'tags': self.tags,
            'type': self.message_type,

            # Extra Fields
            'args': record.args,
            'filename': record.filename,
            'funcName': record.funcName,
            'level': record.levelname,
            'levelno': record.levelno,
            'lineno': record.lineno,
            'logger_name': record.name,
            'module': record.module,
            'process': record.process,
            'processName': record.processName,
            'relativeCreated': record.relativeCreated,
            'thread': record.thread,
            'threadName': record.threadName,
            'filename': record.filename,
            'name': record.name,
            'pathname': record.pathname,
        }

        # Add extra fields
        message.update(self.get_extra_fields(record))

        # If exception, add debug info
        if record.exc_info:
            message.update(self.get_debug_fields(record))

        return self.serialize(message)


log = logging.getLogger('Tester')
log.setLevel(logging.DEBUG)

formatter = logging.Formatter('{asctime} {levelname} {filename}:{lineno} {message}', style='{')
sh = logstash.TCPLogstashHandler('192.168.1.2', 5003)
# sh = MySocketHandler('192.168.1.2', 5003)
# sh = logging.handlers.SocketHandler('192.168.1.2', 5003)
# sh = logging.handlers.HTTPHandler('192.168.1.2:5003', "/", "POST")
sh.setFormatter(MyLogstashFormatter())
# sh.setFormatter(formatter)
log.addHandler(sh)

formatter = logging.Formatter('{asctime} {levelname} {filename}:{lineno} {message}', style='{')
ch = logging.StreamHandler()
# ch.setFormatter(formatter)
ch.setFormatter(LogstashFormatterV1())
log.addHandler(ch)

log.info("test")
print("fin")