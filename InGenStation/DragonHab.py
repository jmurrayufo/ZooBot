#!/usr/bin/env python3
import json
import datetime
import platform
import logging
import logstash
import socket

# Only here for test code.
import random

from Menu import Screen

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
        # Construct menus for use
        self.screen = Screen(self)
        self.log.debug(self.screen)
        self.screen.enter()
        self.log.debug(self.screen)
        self.screen.up()
        self.log.debug(self.screen)
        self.screen.up()
        self.log.debug(self.screen)
        self.screen.enter()
        self.log.debug(self.screen)
        self.screen.cancel()
        self.log.debug(self.screen)


    def run(self):
        self.log.info(f'Begin main loop')
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


    def get_reading(self, name):
        pass


    def update_readings(self):
            self.log.debug("Check temperature")
            self.log.debug("Check humidity")







if __name__ == '__main__':

    log = logging.getLogger('DragonHab')
    log.setLevel(logging.DEBUG)
    log.addHandler(logstash.LogstashHandler(DragonHab.host, 5002, version=1))
    formatter = logging.Formatter('%(asctime)s %(process)d %(levelname)s %(filename)s %(message)s')
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    log.addHandler(ch)
    try:
        x = DragonHab()
        x.run()
    except:
        log.exception("Something died")