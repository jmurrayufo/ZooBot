#!/usr/bin/env python3
import argparse
import asyncio
import datetime
import json
import platform
import random
import sanic
import socket
from sanic.response import text
from sanic.views import CompositionView

from code.CustomLogging import Log
from code.Menu import Screen
from code.RoachHab import RoachHab
from code.WebServer import SanicMgr


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

if args.purpose == 'dragon':
    log = Log('DragonHab')
    hab = RoachHab()

elif  args.purpose == 'bug':
    log = Log('BugHab')
    hab = RoachHab()

elif  args.purpose == 'test':
    log = Log('DevHab')
    hab = RoachHab()

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
sanic_mgr.app.run(debug=False, port=args.port, host=args.host)
# try:
#     sanic_mgr = DragonHab()
#     sanic_mgr.run()
# except:
#     log.exception("Something died")
