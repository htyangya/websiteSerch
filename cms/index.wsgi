import sys, os
import logging

logging.basicConfig(stream = sys.stderr)
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from run import app as application
