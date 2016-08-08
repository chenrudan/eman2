#!/usr/bin/env python

import os
sxreal = "{}/sx_real.py".format(os.path.dirname(os.path.abspath(__file__)))
os.execlp("ipython","ipython","-i",sxreal)

