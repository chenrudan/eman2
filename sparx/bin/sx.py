#!/usr/bin/env python

import os
from site import getsitepackages

sxreal = "{}/sparx/bin/sx_real.py".format(getsitepackages()[0])
os.execlp("ipython","ipython","-i",sxreal)


