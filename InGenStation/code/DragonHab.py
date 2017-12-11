#!/usr/bin/env python3
import json
import datetime
import platform
import logging
import logstash
import socket
import asyncio

# Only here for test code.
import random
import sanic
from sanic.response import text

from Menu import Screen

if __name__ == '__main__':
    app = sanic.Sanic(__name__)

class DragonHab:
    report_dict = {
       "metric": True,
       "app.name":"DragonHab",
       "app.version":"1.0.0",
       "env.domain":"home",
       "env.infrastructure":"dev",
       "env.name":"isbe",
       "env.platform":platform.platform(),
       }
    host = '192.168.1.2'

    """
        sent_bytes = conv_bytes(match_dict['sent'], match_dict['sent_units'])
        sent_dict = report_dict.copy()
        sent_dict.update({"name":"bytes_sent","bytes":sent_bytes,"unit":"bytes"})
        test_logger.info(json.dumps(sent_dict))
    """

    def __init__(self):
        # Setup Log
        self.log = logging.getLogger('DragonHab')

        self.log.info(f'DragonHab booted on {socket.gethostname()}')
        self.last_updates = {}
        self.last_updates['LCD'] = datetime.datetime.now()
        
        self.readings = {}
        self.readings['t0'] = -1
        self.readings['t1'] = -1
        self.readings['t2'] = -1

        # Construct menus for use
        self.screen = Screen(self,"Menu/dragonhub.json")


    async def run(self):
        self.log.info(f'Begin main loop')
        self.log.debug(f"Running debug loop for testing")
        while True:
            await asyncio.sleep(1/10.)
            self.log.debug(self.screen)
            self.log.debug("What key do you want to simulate?")
            key = input("> ")
            if key == "u":
                self.screen.up()
            elif key == "d":
                self.screen.down()
            elif key == "l":
                self.screen.left()
            elif key == "r":
                self.screen.right()
            elif key == "e":
                self.screen.enter()
            elif key == "c":
                self.screen.cancel()
            elif key == "h":
                self.screen.home()
            elif key == "q":
                break
            self.update_readings()
        return

        while True:
            self.log.debug("Check LCD")
            self.log.debug(f"Last update was {datetime.datetime.now() - self.last_updates['LCD']} ago")
            if (datetime.datetime.now() - self.last_updates['LCD']).total_seconds() > 1/60.0:
                self.log.debug("Update the LCD")
                # Read LCD keys, and act as needed
                break
            self.log.debug("Check timers")
            self.update_readings()
            break
        self.log.info(f'Main loop ended, shutdown complete')


    def update_readings(self):
            self.log.debug("Check temperature")
            self.readings['t0'] = random.random()*20
            self.readings['t1'] = random.random()*20
            self.readings['t2'] = random.random()*20
            self.log.debug("Check humidity")


@app.route("/")
async def test(request):
    # self.log.info("Root")
    global hab
    hab.log.info("root!")
    return text("hello world")


if __name__ == '__main__':

    log = logging.getLogger('DragonHab')
    log.setLevel(logging.DEBUG)
    log.addHandler(logstash.LogstashHandler(DragonHab.host, 5002, version=1))
    formatter = logging.Formatter('%(asctime)s %(process)d %(levelname)s %(filename)s %(message)s')
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    log.addHandler(ch)

    hab = DragonHab()

    app.add_task(hab.run)

    app.run(port=8000)
    # try:
    #     x = DragonHab()
    #     x.run()
    # except:
    #     log.exception("Something died")