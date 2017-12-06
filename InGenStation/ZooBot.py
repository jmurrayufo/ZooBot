#!/usr/bin/env python3
import argparse
import asyncio
import datetime
import json
import logging
import logstash
import platform
import socket
from logstash_formatter import LogstashFormatterV1


# Only here for test code.
import random
import sanic
from sanic.response import text
from sanic.views import CompositionView
from CustomLogging import VerboseLogstashFormatter

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

# log.addHandler(logstash.LogstashHandler('192.168.1.2', 5002, version=1))

sh = logstash.TCPLogstashHandler('192.168.1.2', 5003)
sh.setFormatter(VerboseLogstashFormatter())
log.addHandler(sh)


formatter = logging.Formatter('{asctime} {levelname} {filename}:{lineno} {message}', style='{')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
# ch.setFormatter(LogstashFormatterV1())

# TODO: File handler

log.addHandler(ch)

log.info(f"Finished boot as {args.purpose}")

sanic_mgr = SanicMgr(args)
log.debug("Booted with Manager")
if  args.purpose == 'test':
    view = CompositionView()
    view.add(['GET'], hab.all_temperature_handler)
    sanic_mgr.app.add_route(view,'/temp/')

    view = CompositionView()
    view.add(['GET'], hab.temperature_handler)
    sanic_mgr.app.add_route(view,'/temp/<sensor_id>')


    sanic_mgr.app.add_task(hab.run)

# hab = DragonHab()

# Run forever
sanic_mgr.app.run(debug=False, log_config=None, port=args.port, host=args.host)
# try:
#     sanic_mgr = DragonHab()
#     sanic_mgr.run()
# except:
#     log.exception("Something died")
