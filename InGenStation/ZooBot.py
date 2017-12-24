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
from __version__ import __version__


parser = argparse.ArgumentParser(description='Host ZooBot Instance')

parser.add_argument('--purpose', required=True, 
                    choices=['dragon','bug','test'],
                    default='test',
                    help='What type of instance are we running')

parser.add_argument('--port', metavar='N', type=int, default=8000,
                    help='Port to host Sanic on')

parser.add_argument('--host', metavar='addr', type=str, default='0.0.0.0',
                    help='Address to host Sanic on')

parser.add_argument('--__version__', default=__version__,
                    help=argparse.SUPPRESS)

parser.add_argument('--update-freq', type=float,
                    default=60.0,
                    help='Minumum time between sensor updates')

args = parser.parse_args()

if args.purpose == 'dragon':
    log = Log(args)
    hab = RoachHab(args)

elif  args.purpose == 'bug':
    log = Log(args)
    hab = RoachHab(args)

elif  args.purpose == 'test':
    log = Log(args)
    hab = RoachHab(args)

log.info(f"Finished boot as {args.purpose}")

sanic_mgr = SanicMgr(args)
log.debug("Booted with Manager")
if  args.purpose in ['test', 'bug']:
    
    view = CompositionView()
    view.add(['GET'], hab.all_temperature_handler)
    sanic_mgr.app.add_route(view,'/temp/')

    view = CompositionView()
    view.add(['GET'], hab.temperature_handler)
    sanic_mgr.app.add_route(view,'/temp/<sensor_id>')

    view = CompositionView()
    view.add(['GET'], hab.heater_on)
    sanic_mgr.app.add_route(view,'/heater/on')

    view = CompositionView()
    view.add(['GET'], hab.heater_off)
    sanic_mgr.app.add_route(view,'/heater/off')

    view = CompositionView()
    view.add(['GET'], hab.heater_disable)
    sanic_mgr.app.add_route(view,'/heater/disable')


    sanic_mgr.app.add_task(hab.run)

# hab = DragonHab()

# Run forever
sanic_mgr.app.run(debug=False, access_log=False, port=args.port, host=args.host)
# try:
#     sanic_mgr = DragonHab()
#     sanic_mgr.run()
# except:
#     log.exception("Something died")
