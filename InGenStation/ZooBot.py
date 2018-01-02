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

from code.CustomLogging import Log
from code.Menu import Screen
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

parser.add_argument('--update-freq', 
                    type=float,
                    default=1.0,
                    help='Minumum time between sensor updates')

parser.add_argument('--log-freq', 
                    type=float,
                    default=60.0,
                    help='Minumum time between metric logging')

args = parser.parse_args()

sanic_mgr = SanicMgr(args)

# Run forever
sanic_mgr.app.run(debug=False, access_log=False, port=args.port, host=args.host)
