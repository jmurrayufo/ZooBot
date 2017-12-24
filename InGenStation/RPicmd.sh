#!/bin/bash

git pull
pipenv uninstall --all
pipenv install --skip-lock
pipenv run ./ZooBot.py --purpose bug
