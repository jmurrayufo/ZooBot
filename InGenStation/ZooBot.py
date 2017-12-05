#!/usr/bin/env python3
import argparse
import asyncio
import datetime
import json
import logging
import logstash
import platform
import socket

# Only here for test code.
import random
import sanic
from sanic.response import text
from sanic.views import CompositionView

from Menu import Screen
from RoachHab import RoachHab
from WebServer import SanicMgr

global log

parser = argparse.ArgumentParser(description='Host ZooBot Instance')

parser.add_argument('--purpose', required=True, 
                    choices=['dragon','bug','test'],
                    default='test',
                    help='What type of instance are we running')

parser.add_argument('--port', metavar='N', type=int, default=8000,
                    help='Port to host Sanic on')

parser.add_argument('--host', metavar='addr', type=str, default='0.0.0.0',
                    help='Address to host Sanic on')

args = parser.parse_args()
# print(args)

if args.purpose == 'dragon':
    log = logging.getLogger('DragonHab')
    hab = RoachHab(log)

elif  args.purpose == 'bug':
    log = logging.getLogger('BugHab')
    hab = RoachHab(log)

elif  args.purpose == 'test':
    log = logging.getLogger('DevHab')
    hab = RoachHab(log)

log.setLevel(logging.DEBUG)

log.addHandler(logstash.LogstashHandler('192.168.1.2', 5002, version=1))

# sh = logstash.LogstashHandler('192.168.1.2', 5002)
# sh = logging.handlers.SocketHandler('192.168.1.2',5002)
# sh.setFormatter(LogstashFormatterV1())
# log.addHandler(sh)

formatter = logging.Formatter('{asctime} {levelname} {filename}:{lineno} {message}', style='{')
ch = logging.StreamHandler()
ch.setFormatter(formatter)

# TODO: File handler

log.addHandler(ch)

log.info(f"Finished boot as {args.purpose}")

x = SanicMgr(args)
log.debug("Booted with Manager")
if  args.purpose == 'test':
    view = CompositionView()
    view.add(['GET'], hab.all_temperature_handler)
    x.app.add_route(view,'/temp/')

    view = CompositionView()
    view.add(['GET'], hab.temperature_handler)
    x.app.add_route(view,'/temp/<sensor_id>')


    x.app.add_task(hab.run)

# hab = DragonHab()

x.app.run(debug=False, log_config=None, port=args.port, host=args.host)
# try:
#     x = DragonHab()
#     x.run()
# except:
#     log.exception("Something died")
