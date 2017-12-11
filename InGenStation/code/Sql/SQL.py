import asyncio
import csv
import hashlib
import json
import logging
import os
import os.path
import random
import re
import sqlite3
import time

from ..CustomLogging import Log

class SQL:

    __shared_state = {}


    def __init__(self):
        self.__dict__ = self.__shared_state
        if hasattr(self, 'initialized'):
            return

        self.initialized = True
        self.conn = None
        self.connected = False
        self.log = Log()


    def connect(self, db_name="hab.db"):
        self.log.info("Connect to db")
        if not self.connected:
            if not os.path.isfile(db_name):
                self.log.warning(f"Creating new db: {db_name}")
                self.conn = sqlite3.connect(db_name)
                self.setup()
                self.conn.close()
            self.conn = sqlite3.connect(db_name)
            self.log.info("Connection established")
            self.conn.row_factory = sqlite3.Row
            self.c = self.conn.cursor()
            self.log.info("Cursor created, connection complete")
            self.connected = True


    def disconnect(self):
        self.log.info("Disconnect from db")
        if self.conn and self.connected:
            self.conn.close()
            self.conn = None
            self.connected = False


    def setup(self):
        self.log.info("Begining DB setup")
