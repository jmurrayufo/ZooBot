#!/bin/bash

# Loop forever unless we can talk to google
until ping -c1 www.google.com &>/dev/null; do :; done
git pull
# pipenv uninstall --all
# pipenv install --skip-lock
pipenv run ./ZooBot.py --purpose bug
