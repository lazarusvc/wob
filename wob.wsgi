#!/usr/bin/python
activate_this = 'var/www/wob/venv/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))


import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"var/www/wob/")

from run import app as application
application.secret_key = 'dfdfdfdfdfdfdfdfdfdfdfdf'

